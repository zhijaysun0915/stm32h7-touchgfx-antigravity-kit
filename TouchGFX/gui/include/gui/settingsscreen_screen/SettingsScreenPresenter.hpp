#ifndef SETTINGSSCREENPRESENTER_HPP
#define SETTINGSSCREENPRESENTER_HPP

#include <gui/model/ModelListener.hpp>

class SettingsScreenView;

class SettingsScreenPresenter : public ModelListener {
public:
    SettingsScreenPresenter(SettingsScreenView& v) : view(v) {}
    virtual void activate() {}
    virtual void deactivate() {}
    virtual ~SettingsScreenPresenter() {}
private:
    SettingsScreenView& view;
};
#endif // SETTINGSSCREENPRESENTER_HPP
