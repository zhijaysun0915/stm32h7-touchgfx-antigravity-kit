#include <gui/dashboardscreen_screen/DashboardScreenView.hpp>
#include <gui/dashboardscreen_screen/DashboardScreenPresenter.hpp>

void DashboardScreenPresenter::onTelemetryUpdated(float tempC, int loadPercent) {
    view.updateTelemetryDisplay(tempC, loadPercent);
}

void DashboardScreenPresenter::onBoostButtonPressed() {
    if (model != nullptr) {
        model->toggleBoostLed();
    }
}
