#ifndef DASHBOARDSCREENVIEW_HPP
#define DASHBOARDSCREENVIEW_HPP

#include <gui_generated/dashboardscreen_screen/DashboardScreenViewBase.hpp>
#include <gui/dashboardscreen_screen/DashboardScreenPresenter.hpp>

class DashboardScreenView : public DashboardScreenViewBase {
public:
    DashboardScreenView() {}
    virtual ~DashboardScreenView() {}
    virtual void setupScreen() override;
    virtual void tearDownScreen() override;
    virtual void handleBoostClicked() override;

    void updateTelemetryDisplay(float tempC, int loadPercent);
    void setPresenter(DashboardScreenPresenter* p) { presenter = p; }

protected:
    DashboardScreenPresenter* presenter = nullptr;
};
#endif // DASHBOARDSCREENVIEW_HPP
