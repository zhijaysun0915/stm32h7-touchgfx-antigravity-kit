#ifndef SETTINGSSCREENVIEWBASE_HPP
#define SETTINGSSCREENVIEWBASE_HPP

#include <gui_generated/common/FrontendApplicationBase.hpp>
#include <BitmapDatabase.hpp>
#include <texts/TextKeysAndLanguages.hpp>
#include <touchgfx/widgets/Box.hpp>
#include <touchgfx/widgets/Image.hpp>
#include <touchgfx/widgets/TextArea.hpp>
#include <touchgfx/widgets/TextAreaWithWildcard.hpp>
#include <touchgfx/widgets/ButtonWithLabel.hpp>
#include <touchgfx/containers/progress_indicators/BoxProgress.hpp>
#include <touchgfx/Color.hpp>

class SettingsScreenViewBase : public touchgfx::ViewBase {
public:
    SettingsScreenViewBase();
    virtual ~SettingsScreenViewBase() {}
    virtual void setupScreen() override;

protected:
    FrontendApplicationBase& application() {
        return *static_cast<FrontendApplicationBase*>(touchgfx::Application::getInstance());
    }
    touchgfx::Box settingsBg;
    touchgfx::TextArea settingsTitle;
    touchgfx::ButtonWithLabel btnBack;

private:
    touchgfx::Callback<SettingsScreenViewBase, const touchgfx::AbstractButton&> buttonCallback;
    void buttonCallbackHandler(const touchgfx::AbstractButton& src);
};
#endif // SETTINGSSCREENVIEWBASE_HPP
