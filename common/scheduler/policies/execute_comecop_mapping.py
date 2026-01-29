import sys
import scipy.io as spio
import numpy as np
import re
import comecop
import comecop_util
import os

def execute_comecop_mapping(taskCoreRequirement):
    
    print('[Scheduler] [CoMeCop]: Starting the CoMeCop mapping process by executing execute_comecop_mapping.py')

    taskCoreRequirement = int(taskCoreRequirement)

    # read configurations from base.cfg, including max_temperature (threshold temperature), ambient_temperature, etc
    temp_max, temp_amb, _, _, inactive_power, name_of_chip = comecop_util.read_config()

    # load the mapping information from file info_for_mapping.txt, saved in mapCoMeCop::map in mapCoMeCop.cc
    mapping_info = np.loadtxt('./system_sim_state/info_for_mapping.txt', dtype=int)
    availableCores = mapping_info[0,:].astype('bool');
    activeCores = mapping_info[1,:].astype('bool');
    preferredCoresOrder = mapping_info[2,:]

    if np.sum(availableCores) < taskCoreRequirement:
        raise Exception('There are not enough available cores to meet the required core number of this task.')
    
    # load the multi-core system's thermal model matrices
    core_num = availableCores.shape[0]
    A = spio.loadmat('./model_extract/'+name_of_chip+'/A.mat')['A']

    # total core number of the multi/many core system
    core_num = availableCores.shape[0]
    # total memory bank number
    mem_num = A.shape[0] - core_num

    # form the M_mc matrix, which is the mapping of last layer memory banks to cores
    M_mc = comecop_util.form_lastlayer_mapping(core_num, mem_num)

    # divide A matrix for cores and memory banks
    Amc = A[:mem_num][:,mem_num:]
    Amm = A[:mem_num][:,:mem_num]

    # formulate the static power vector: in hotsniper, every core (active or not) has the same static power
    P_s = np.full((core_num,), inactive_power)
    # The power of memory banks.
    P_m = np.loadtxt('./combined_instpower.trace',skiprows=1)[core_num:]
    #P_m = np.full((mem_num,), 0)

    # compute the new active core indexes using comecop_mapping
    cores_to_activate = comecop.comecop_map(Amm, Amc, temp_max, temp_amb, taskCoreRequirement, activeCores, availableCores, preferredCoresOrder, P_s, P_m, M_mc)

    print('[Scheduler] [CoMeCop]: CoMeCop determined cores to activate: ', cores_to_activate)
    
    # write the CoMeCop mapping results to file
    file_comecop_map = open('./system_sim_state/comecop_map.txt', 'w')
    for core in cores_to_activate:
        file_comecop_map.write(str(int(core))+' ')
    file_comecop_map.close()

execute_comecop_mapping(sys.argv[1])
