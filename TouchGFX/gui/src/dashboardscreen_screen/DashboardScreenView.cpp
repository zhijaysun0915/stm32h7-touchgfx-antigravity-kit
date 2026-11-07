#include <gui/dashboardscreen_screen/DashboardScreenView.hpp>

void DashboardScreenView::setupScreen() {
    DashboardScreenViewBase::setupScreen();
    updateTelemetryDisplay(26.5f, 64);
}

void DashboardScreenView::tearDownScreen() {
    DashboardScreenViewBase::tearDownScreen();
}

void DashboardScreenView::handleBoostClicked() {
    if (presenter != nullptr) {
        presenter->onBoostButtonPressed();
    }
}

void DashboardScreenView::updateTelemetryDisplay(float tempC, int loadPercent) {
    touchgfx::Unicode::snprintfFloat(titleTextBuffer, TITLETEXT_SIZE, "%.1f", tempC);
    titleText.invalidate();
    loadBar.setValue(loadPercent);
    loadBar.invalidate();
}
