import re
import numpy as np

def read_config():
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
    return temp_max, temp_amb, comecop_mode, dvfs_epoch, inactive_power, name_of_chip

def form_lastlayer_mapping(core_num, mem_num):
    # form the M_mc matrix, which is the mapping of last layer memory banks to cores
    # m2c: mapping of core to memory, manually given now for gainstown_3D
    # later, should form automatically by looking at config files
    # for example, gainestown_3D.cfg->hotspot/3D->mem_bank_8.flp and cores.flp
    m2c = [0, 0, 1, 1, 0, 0, 1, 1, 2, 2, 3, 3, 2, 2, 3, 3]
    M_mc = np.full((core_num,mem_num), 0.0)
    for i in range(len(m2c)):
        M_mc[m2c[i], i] = 1.0

    # divide by number of mem banks per core
    for i in range(core_num):
        M_mc[i,:] = M_mc[i,:]/(m2c.count(i))
    # print('M_mc: ', M_mc)
    
    return M_mc
