import sys
import scipy.io as spio
import numpy as np
import re
import comecop

def execute_comecop_power(core_num):
    
    print('[Scheduler] [CoMeCop]: Starting the CoMeCop power budgeting process by executing execute_comecop_power.py')

    core_num = int(core_num)
    
    # read configurations from base.cfg, including max_temperature (threshold temperature), ambient_temperature, etc
    file_config = open('../config/base.cfg')
    for line in file_config:
        if line.startswith('max_temperature'):
            line_words = re.split('=|#|\s', line) # split the line into words with splitor '=', '#', and whitespaces
            line_words = list(filter(None, line_words)) # filt out the whitespaces
            temp_max = float(line_words[1])
        if line.startswith('ambient_temperature'):
            line_words = re.split('=|#|\s', line)
            line_words = list(filter(None, line_words))
            temp_amb = float(line_words[1])
        if line.startswith('comecop_mode'):
            line_words = re.split('=|#|\s', line)
            line_words = list(filter(None, line_words))
            comecop_mode = line_words[1]
        if line.startswith('dvfs_epoch'):
            line_words = re.split('=|#|\s', line)
            line_words = list(filter(None, line_words))
            dvfs_epoch = int(line_words[1])
        if line.startswith('inactive_power'):
            line_words = re.split('=|#|\s', line)
            line_words = list(filter(None, line_words))
            inactive_power = float(line_words[1])
        if line.startswith('sniper_config'):
            line_words = re.split('=|#|\s', line)
            line_words = list(filter(None, line_words))
            name_of_chip = re.split('/|\.', line_words[1])[-2]
    file_config.close()
        
    # load the multi-core system's thermal model matrices
    if comecop_mode == 'steady':
        A = spio.loadmat('./model_extract/'+name_of_chip+'/A.mat')['A']
    elif comecop_mode == 'transient':
        if dvfs_epoch == 1000000:
            A = spio.loadmat('./model_extract/'+name_of_chip+'/A_1ms.mat')['A_bar']
        else:
            raise Exception("comecop current only supports dvfs_epoch = 1000000, please modify base.cfg")
    else:
        raise Exception("comecop mode can only be steady and transient, please modify base.cfg")

    # load the current active core distribution in core_map. 'mapping.txt' is writen by SchedulerOpen::periodic in scheduler_open.cc for every DVFS cycle
    core_map = np.loadtxt('./system_sim_state/mapping.txt')
    core_map = np.asarray(core_map, dtype = bool) # use bool type to extract Ai matrix from A

    # total core number of the multi/many core system
    core_num = core_map.shape[0]
    # total memory bank number
    mem_num = A.shape[0] - core_num

    # form the M_mc matrix, which is the mapping of last layer memory banks to cores
    # m2c: mapping of core to memory, manually given now for gainstown_3D
    # later, should form automatically by looking at config files
    # for example, gainestown_3D.cfg->hotspot/3D->mem_bank_8.flp and cores.flp
    m2c = [1, 1, 2, 2, 1, 1, 2, 2, 3, 3, 4, 4, 3, 3, 4, 4]
    M_mc = np.full((core_num,mem_num), 0)
    for i in range(len(m2c)):
        M_mc[m2c(i), i] = 1
    # divide by number of mem banks per core
    for i in range(core_num):
        M_mc[i,:] = M_mc[i,:]/(m2c.count(i))

    # divide A matrix for cores and memory banks
    Amc = A[:mem_num][:,mem_num:]
    Amm = A[:mem_num][:,:mem_num]

    # load the current temperature/power from files, ingore the first line which contains core names
    T_m = np.loadtxt('./combined_insttemperature.trace',skiprows=1)[core_num:] # current temperature of memory banks
    T_mc = M_mc@T_m # average the temperature of the last layer memory banks for each vertical core
    P_k = np.loadtxt('./combined_instpower.trace',skiprows=1)[:core_num] # previous power consumption of cores
    P_m = np.loadtxt('./combined_instpower.trace',skiprows=1)[core_num:] # previous power consumption of memory banks

    # formulate the static power vector: in hotsniper, every core (active or not) has the same static power
    P_s = np.full((core_num,), inactive_power)
    
    # Compute power budget using comecop power budgeting core function
    P = comecop.comecop_power(Amm, Amc, core_map, temp_max, temp_amb, P_s, P_m, P_k, T_c, M_mc, comecop_mode)
    
    print('[Scheduler] [CoMeCop]: Power budget determined by CoMeCop (W): ', P)

    # Write power budget P into file
    file_power = open('./system_sim_state/comecop_power.txt', 'w')
    for power in P:
        file_power.write(str(np.asscalar(power))+' ')
    file_power.close()

if len(sys.argv) != 2:
    raise Exception('Please provide core number when calling comecop_power.py')

execute_comecop_power(sys.argv[1])



