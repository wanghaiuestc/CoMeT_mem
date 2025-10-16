/**
 * This header implements the CoMeCop policy
 */

#ifndef __MAP_COMECOP_H
#define __MAP_COMECOP_H

#include "mappingpolicy.h"

class MapCoMeCop : public MappingPolicy {
public:
    MapCoMeCop(unsigned int coreRows, unsigned int coreColumns, std::vector<int> preferredCoresOrder);
    virtual std::vector<int> map(String taskName, int taskCoreRequirement, const std::vector<bool> &availableCores, const std::vector<bool> &activeCores);

private:
    unsigned int coreRows;
    unsigned int coreColumns;
    std::vector<int> preferredCoresOrder;
};

#endif
