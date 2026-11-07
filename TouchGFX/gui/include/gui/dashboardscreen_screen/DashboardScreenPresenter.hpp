#ifndef DASHBOARDSCREENPRESENTER_HPP
#define DASHBOARDSCREENPRESENTER_HPP

#include <gui/model/ModelListener.hpp>

class DashboardScreenView;

class DashboardScreenPresenter : public ModelListener {
public:
    DashboardScreenPresenter(DashboardScreenView& v) : view(v) {}
    virtual void activate() {}
    virtual void deactivate() {}
    virtual ~DashboardScreenPresenter() {}

    virtual void onTelemetryUpdated(float tempC, int loadPercent) override;
    void onBoostButtonPressed();

private:
    DashboardScreenView& view;
};
#endif // DASHBOARDSCREENPRESENTER_HPP
