#include "dramLowpower_multimode.h"
#include <iomanip>
#include <iostream>
#include <map>
#include "dram_cntlr_multimode.h"

using namespace std;

extern UInt64 NUM_OF_MODES;

DramLowpower::DramLowpower(
        const PerformanceCounters *performanceCounters,
        int numberOfBanks,
        float dtmCriticalTemperature,
        float dtmRecoveredTemperature)
    : performanceCounters(performanceCounters),
      numberOfBanks(numberOfBanks),
      dtmCriticalTemperature(dtmCriticalTemperature),
      dtmRecoveredTemperature(dtmRecoveredTemperature) {

}

DramLowpower_multimode::DramLowpower_multimode(
        const PerformanceCounters *performanceCounters,
        int numberOfBanks,
        float dtmCriticalTemperature,
        float dtmRecoveredTemperature)
    : performanceCounters(performanceCounters),
      numberOfBanks(numberOfBanks),
      dtmCriticalTemperature(dtmCriticalTemperature),
      dtmRecoveredTemperature(dtmRecoveredTemperature) {

}

/*
Return the new memory modes, based on current temperatures.
*/
std::map<int,int> DramLowpower::getNewBankModes(std::map<int, int> old_bank_modes) {

    cout << "in DramLowpower::getNewBankModes\n";
    std::map<int,int> new_bank_mode_map;
    for (int i = 0; i < numberOfBanks; i++)
    {
        if (old_bank_modes[i] == LOW_POWER) // if the memory was already in low power mode
        {
            if (performanceCounters->getTemperatureOfBank(i) < dtmRecoveredTemperature) // temp dropped below recovery temperature
            {
                cout << "[Scheduler][dram-DTM]: thermal violation ended for bank " << i << endl;
                new_bank_mode_map[i] = NORMAL_POWER;
            }
            else
            {
                new_bank_mode_map[i] = LOW_POWER;
            }
        }
        else // if the memory was not in low power mode
        {
            if (performanceCounters->getTemperatureOfBank(i) > dtmCriticalTemperature) // temp is above critical temperature
            {
                cout << "[Scheduler][dram-DTM]: thermal violation detected for bank " << i << endl;
                new_bank_mode_map[i] = LOW_POWER;
            }
            else
            {
                new_bank_mode_map[i] = NORMAL_POWER;
            }

        }
        
    }
    return new_bank_mode_map;
}

/*
Return the new memory modes, based on current temperatures.
*/
std::map<int,int> DramLowpower_multimode::getNewBankModes(std::map<int, int> old_bank_modes) {

    cout << "in DramLowpower_multimode::getNewBankModes\n";
    std::map<int,int> new_bank_mode_map;
    for (int i = 0; i < numberOfBanks; i++)
    {
      if (old_bank_modes[i] >= NUM_OF_MODES || old_bank_modes[i] < 0)
	{
	  cout << "[Scheduler][dram-DTM][Error]: bank mode do not exist" << endl;
	  exit (1);
	}
      if (performanceCounters->getTemperatureOfBank(i) < dtmRecoveredTemperature) // temp dropped below recovery temperature
	{
	  if (old_bank_modes[i] == 0) // already mode 0, cannot decrease mode 
	    new_bank_mode_map[i] = old_bank_modes[i];
	  else // decrease mode to boost performance
	    {
	      new_bank_mode_map[i] = old_bank_modes[i]-1;
	      cout << "[Scheduler][dram-DTM]: thermal violation ended for bank " << i << ". Change to mode " << new_bank_mode_map[i] << endl;
	    }
	}
      else if (performanceCounters->getTemperatureOfBank(i) > dtmCriticalTemperature) // temp is above critical temperature
	{
	  
	  if (old_bank_modes[i] == NUM_OF_MODES-1) // already highest (slowest) mode, cannot increase mode 
	    new_bank_mode_map[i] = old_bank_modes[i];
	  else // increase mode to lower power thus lower temperature
	    {
	      new_bank_mode_map[i] = old_bank_modes[i]+1;
	      cout << "[Scheduler][dram-DTM]: thermal violation detected for bank " << i << ". Change to mode " << new_bank_mode_map[i] << endl;
	    }
	}
      else // temp is between the recovery temperature and critical temperature
	new_bank_mode_map[i] = old_bank_modes[i]; // do nothing
    }
    return new_bank_mode_map;
}
