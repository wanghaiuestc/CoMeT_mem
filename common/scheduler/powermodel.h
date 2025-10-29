#ifndef __POWERMODEL_H
#define __POWERMODEL_H

// Copied from HotSniper for CoMeCop core
// Originally not in CoMeT

class PowerModel {
public:
    static int getExpectedGoodFrequency(int currentFrequency, float powerConsumption, float powerBudget, int minFrequency, int maxFrequency, int frequencyStepSize);
    static float estimatePower(int currentFrequency, float currentPowerConsumption, int newFrequency);
};

#endif
