import os
import re

# change directory to config to ensure the flps in lcf can be read
os.chdir('../config/')

# please install hotspot_with_model_extract in parallel if not yet
hotspot_path = '../../hotspot_with_model_extract/'
#hotspot_path = '../hotspot_tool/'

file_config = open('../config/base.cfg')
for line in file_config:
    if line.startswith('sniper_config'):
        line_words = re.split('=|#|\\s', line)
        line_words = list(filter(None, line_words))
        path_sniper_config = line_words[1]
        name_of_chip = re.split('/|\\.', line_words[1])[-2]
file_config.close()

file_sniper_config = open(path_sniper_config)
for line in file_sniper_config:
    if line.startswith('hotspot_config_file_mem'):
        line_words = re.split('=|#|\\s', line)
        line_words = list(filter(None, line_words))
        hotspot_config_file = '../'+line_words[1]
    if line.startswith('power_trace_file'):
        line_words = re.split('=|#|\\s', line)
        line_words = list(filter(None, line_words))
        power_trace_file = line_words[1]
    if line.startswith('steady_temp_file'):
        line_words = re.split('=|#|\\s', line)
        line_words = list(filter(None, line_words))
        steady_temp_file = line_words[1]
    if line.startswith('type_of_stack'):
        line_words = re.split('=|#|\\s', line)
        line_words = list(filter(None, line_words))
        type_of_stack = line_words[1]
    if line.startswith('sampling_interval'):
        line_words = re.split('=|#|\\s', line)
        line_words = list(filter(None, line_words))
        sampling_interval = int(line_words[1])
    if line.startswith('layer_file_mem'):
        line_words = re.split('=|#|\\s', line)
        line_words = list(filter(None, line_words))
        layer_file_mem = '../'+line_words[1]

interval_sec = sampling_interval * 1e-9
executable = hotspot_path + 'hotspot'

hotspot_command = executable  \
                  + ' -c ' + hotspot_config_file \
                  + ' -p ' + power_trace_file \
                  + ' -model_secondary 1 -model_type grid ' \
                  + ' -steady_file ' + steady_temp_file \
                  + ' -grid_steady_file ' + steady_temp_file \
                  + ' -steady_state_print_disable 1 ' \
                  + ' -l 1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1, ' \
                  + ' -type ' + type_of_stack \
                  + ' -sampling_intvl ' + str(interval_sec) \
                  + ' -grid_layer_file ' + layer_file_mem \
                  + ' -detailed_3D on'
print(hotspot_command)

hcmd = hotspot_command
os.system(hcmd)
