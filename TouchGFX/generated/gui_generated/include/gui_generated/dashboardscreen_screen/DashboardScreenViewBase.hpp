#ifndef DASHBOARDSCREENVIEWBASE_HPP
#define DASHBOARDSCREENVIEWBASE_HPP

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

class DashboardScreenViewBase : public touchgfx::ViewBase {
public:
    DashboardScreenViewBase();
    virtual ~DashboardScreenViewBase() {}
    virtual void setupScreen() override;
    virtual void handleBoostClicked() {}

protected:
    FrontendApplicationBase& application() {
        return *static_cast<FrontendApplicationBase*>(touchgfx::Application::getInstance());
    }
    touchgfx::Image bgImage;
    touchgfx::Image leftCard;
    touchgfx::Image rightCard;
    touchgfx::TextAreaWithOneWildcard titleText;
    touchgfx::BoxProgress loadBar;
    touchgfx::ButtonWithLabel btnBoost;
    touchgfx::ButtonWithLabel btnNextScreen;
    static const uint16_t TITLETEXT_SIZE = 16;
    touchgfx::Unicode::UnicodeChar titleTextBuffer[TITLETEXT_SIZE];

private:
    touchgfx::Callback<DashboardScreenViewBase, const touchgfx::AbstractButton&> buttonCallback;
    void buttonCallbackHandler(const touchgfx::AbstractButton& src);
};
#endif // DASHBOARDSCREENVIEWBASE_HPP
