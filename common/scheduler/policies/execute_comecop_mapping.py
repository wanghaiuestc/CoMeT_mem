import sys
import scipy.io as spio
import numpy as np
import re
import comecop

def execute_comecop_mapping(taskCoreRequirement):
    
    print('[Scheduler] [CoMeCop]: Starting the CoMeCop mapping process by executing execute_comecop_mapping.py')

    taskCoreRequirement = int(taskCoreRequirement)

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
        if line.startswith('inactive_power'):
            line_words = re.split('=|#|\s', line)
            line_words = list(filter(None, line_words))
            inactive_power = float(line_words[1])
        if line.startswith('floorplan'):
            line_words = re.split('=|#|\s', line)
            line_words = list(filter(None, line_words))
            name_of_chip = re.split('/|\.', line_words[1])[-2]
    file_config.close()

    # load the mapping information from file info_for_mapping.txt, saved in mapCoMeCop::map in mapCoMeCop.cc
    mapping_info = np.loadtxt('./system_sim_state/info_for_mapping.txt', dtype=int)
    availableCores = mapping_info[0,:].astype('bool');
    activeCores = mapping_info[1,:].astype('bool');
    preferredCoresOrder = mapping_info[2,:]

    if np.sum(availableCores) < taskCoreRequirement:
        raise Exception('There are not enough available cores to meet the required core number of this task.')
    
    # load the multi-core system's thermal model matrices
    core_num = availableCores.shape[0]
    A = spio.loadmat('./comecop_thermal_matrices/'+name_of_chip+'_A.mat')['A']

    # formulate the static power vector: in hotsniper, every core (active or not) has the same static power
    P_s = np.full((A.shape[0],), inactive_power)

    # compute the new active core indexes using comecop_mapping
    cores_to_activate = comecop.comecop_map(A, temp_max, temp_amb, taskCoreRequirement, activeCores, availableCores, preferredCoresOrder, P_s)

    print('[Scheduler] [CoMeCop]: CoMeCop determined cores to activate: ', cores_to_activate)
    
    # write the CoMeCop mapping results to file
    file_comecop_map = open('./system_sim_state/comecop_map.txt', 'w')
    for core in cores_to_activate:
        file_comecop_map.write(str(int(core))+' ')
    file_comecop_map.close()

execute_comecop_mapping(sys.argv[1])
