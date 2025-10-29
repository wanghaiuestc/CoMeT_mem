/**
 * This header implements the CoMeCop power DVFS policy
 */

#ifndef __DVFS_COMECOP_H
#define __DVFS_COMECOP_H

#include <vector>
#include "dvfspolicy.h"

class DVFSCoMeCop : public DVFSPolicy {
public:
    DVFSCoMeCop(const PerformanceCounters *performanceCounters, int coreRows, int coreColumns, int minFrequency, int maxFrequency, int frequencyStepSize);
    virtual std::vector<int> getFrequencies(const std::vector<int> &oldFrequencies, const std::vector<bool> &activeCores);

private:
    const PerformanceCounters *performanceCounters;
    unsigned int coreRows;
    unsigned int coreColumns;
    int minFrequency;
    int maxFrequency;
    int frequencyStepSize;
};

#endif
