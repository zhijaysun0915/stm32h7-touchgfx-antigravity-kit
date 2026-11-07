#include <gui_generated/settingsscreen_screen/SettingsScreenViewBase.hpp>

SettingsScreenViewBase::SettingsScreenViewBase() :
    buttonCallback(this, &SettingsScreenViewBase::buttonCallbackHandler)
{
    settingsBg.setPosition(0, 0, 480, 272);
    settingsBg.setColor(touchgfx::Color::getColorFromRGB(15, 23, 42));
    add(settingsBg);
    settingsTitle.setPosition(20, 16, 300, 28);
    settingsTitle.setColor(touchgfx::Color::getColorFromRGB(248, 250, 252));
    settingsTitle.setTypedText(touchgfx::TypedText(T_SETTINGS_TITLE));
    add(settingsTitle);
    btnBack.setXY(16, 220);
    btnBack.setBitmaps(touchgfx::Bitmap(BitmapDatabase::BITMAP_BTN_PRIMARY_RELEASED_ID), touchgfx::Bitmap(BitmapDatabase::BITMAP_BTN_PRIMARY_PRESSED_ID));
    btnBack.setLabelText(touchgfx::TypedText(T_BTN_BACK));
    btnBack.setLabelColor(touchgfx::Color::getColorFromRGB(255, 255, 255));
    btnBack.setLabelColorPressed(touchgfx::Color::getColorFromRGB(186, 230, 253));
    btnBack.setAction(buttonCallback);
    add(btnBack);
}

void SettingsScreenViewBase::setupScreen() {}

void SettingsScreenViewBase::buttonCallbackHandler(const touchgfx::AbstractButton& src) {
    if (&src == &btnBack) {
        application().gotoDashboardScreenSlideTransition();
    }
}
