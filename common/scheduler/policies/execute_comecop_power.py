import sys
import scipy.io as spio
import numpy as np
import re
import comecop
import comecop_util

def execute_comecop_power(core_num):
    
    print('[Scheduler] [CoMeCop]: Starting the CoMeCop power budgeting process by executing execute_comecop_power.py')

    core_num = int(core_num)

    # read configurations from base.cfg, including max_temperature (threshold temperature), ambient_temperature, etc
    temp_max, temp_amb, comecop_mode, dvfs_epoch, inactive_power, name_of_chip = comecop_util.read_config()
        
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
    M_mc = comecop_util.form_lastlayer_mapping(core_num, mem_num)

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
    P = comecop.comecop_power(Amm, Amc, core_map, temp_max, temp_amb, P_s, P_m, P_k, T_mc, M_mc, comecop_mode)
    
    print('[Scheduler] [CoMeCop]: Power budget determined by CoMeCop (W): ', P)

    # Write power budget P into file
    file_power = open('./system_sim_state/comecop_power.txt', 'w')
    for power in P:
        file_power.write(str(power.item())+' ')
    file_power.close()

if len(sys.argv) != 2:
    raise Exception('Please provide core number when calling comecop_power.py')

execute_comecop_power(sys.argv[1])



