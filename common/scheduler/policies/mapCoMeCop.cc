#include "mapCoMeCop.h"
#include <algorithm>
#include <iostream>
#include <map>
#include <set>
#include <fstream>

// to create directory for system_sim_state
#include <sys/stat.h>
#include <sys/types.h>

using namespace std;

// Just do initiation. Note that unlike the firstunused method, preferredCoresOrder do not contain the cores not specified by user, because their order should be computed at runtime by MapCoMeCop::map
MapCoMeCop::MapCoMeCop(unsigned int coreRows, unsigned int coreColumns, std::vector<int> preferredCoresOrder)
	: coreRows(coreRows), coreColumns(coreColumns), preferredCoresOrder(preferredCoresOrder) {
	for (unsigned int i = 0; i < coreRows * coreColumns; i++) {
		if (std::find(this->preferredCoresOrder.begin(), this->preferredCoresOrder.end(), i) == this->preferredCoresOrder.end()) {
			this->preferredCoresOrder.push_back(-1); // put "-1", meaning the order has not been determined yet, should be determined by MapCoMeCop::map
		}
	}
}

std::vector<int> MapCoMeCop::map(String taskName, int taskCoreRequirement, const std::vector<bool> &availableCores, const std::vector<bool> &activeCores) {
	std::vector<int> cores;

	/* CoMeCop mapping core code begin */

	// write availableCores and activeCores in info_for_mapping.txt as inputs to comecop_mapping.py
	int create_directory = mkdir("./system_sim_state", 0777);
	if (create_directory == 0)
	  printf("[Scheduler] [CoMeCop]: New directory system_sim_state is created to store info_for_mapping.txt!\n");
	ofstream mapping_info_file("./system_sim_state/info_for_mapping.txt");
	for (unsigned int i=0; i<availableCores.size();i++){
	  mapping_info_file << availableCores[i] << "\t";
	}
	mapping_info_file << endl;
	for (unsigned int i=0; i<activeCores.size();i++){
	  mapping_info_file << activeCores[i] << "\t";
	}
	mapping_info_file << endl;
	for (unsigned int i=0; i<preferredCoresOrder.size();i++){
	    mapping_info_file << preferredCoresOrder[i] << "\t";
	}
	mapping_info_file << endl;

	// execute execute_comecop_mapping.py to compute the active core mapping, the outputs are written in file comecop_map.txt
	string filename = "../common/scheduler/policies/execute_comecop_mapping.py "+to_string(taskCoreRequirement);
	string command = "python3 "+filename;
	system(command.c_str());

	// load the comecop mapping from file, and activate the cores according to the comecop mapping
	int core_to_activate;
	ifstream file_comecop_map("./system_sim_state/comecop_map.txt");
	for (int coreCounter = 0; coreCounter < taskCoreRequirement; coreCounter++)
	  {
	    file_comecop_map >> core_to_activate;
	    cores.push_back(core_to_activate);
	  }
	file_comecop_map.close();
	return cores;

	/* CoMeCop mapping core code end */

	std::vector<int> empty;
	return empty;
}
