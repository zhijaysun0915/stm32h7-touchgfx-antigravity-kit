#include <gui/model/Model.hpp>
#include <gui/model/ModelListener.hpp>

Model::Model()
    : modelListener(0),
      tickCounter(0),
      currentTempC(26.5f),
      cpuLoadPercent(64),
      boostActive(false) {}

void Model::tick() {
    tickCounter++;
    // Update telemetry every 30 ticks (~500 ms at 60 FPS VSYNC)
    if (tickCounter % 30 == 0 && modelListener != 0) {
        currentTempC = boostActive ? 31.2f : 26.5f;
        cpuLoadPercent = boostActive ? 88 : 42;
        modelListener->onTelemetryUpdated(currentTempC, cpuLoadPercent);
    }
}

void Model::toggleBoostLed() {
    boostActive = !boostActive;
    if (modelListener != 0) {
        modelListener->onBoostStateChanged(boostActive);
    }
}
