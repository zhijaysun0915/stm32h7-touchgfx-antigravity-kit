#include <gui_generated/dashboardscreen_screen/DashboardScreenViewBase.hpp>

DashboardScreenViewBase::DashboardScreenViewBase() :
    buttonCallback(this, &DashboardScreenViewBase::buttonCallbackHandler)
{
    bgImage.setXY(0, 0);
    bgImage.setBitmap(touchgfx::Bitmap(BitmapDatabase::BITMAP_BG_DASHBOARD_ID));
    add(bgImage);
    leftCard.setXY(16, 48);
    leftCard.setBitmap(touchgfx::Bitmap(BitmapDatabase::BITMAP_CARD_PANEL_ID));
    add(leftCard);
    rightCard.setXY(248, 48);
    rightCard.setBitmap(touchgfx::Bitmap(BitmapDatabase::BITMAP_CARD_PANEL_ID));
    add(rightCard);
    titleText.setPosition(16, 12, 320, 28);
    titleText.setColor(touchgfx::Color::getColorFromRGB(248, 250, 252));
    titleText.setTypedText(touchgfx::TypedText(T_DASHBOARD_TITLE));
    titleText.setWildcard(titleTextBuffer);
    add(titleText);
    loadBar.setXY(34, 160);
    loadBar.setProgressIndicatorPosition(0, 0, 180, 14);
    loadBar.setRange(0, 100);
    loadBar.setColor(touchgfx::Color::getColorFromRGB(56, 189, 248));
    loadBar.setBackground(touchgfx::Bitmap(BitmapDatabase::BITMAP_PROGRESS_BG_ID));
    loadBar.setValue(64);
    add(loadBar);
    btnBoost.setXY(264, 104);
    btnBoost.setBitmaps(touchgfx::Bitmap(BitmapDatabase::BITMAP_BTN_ACTION_RELEASED_ID), touchgfx::Bitmap(BitmapDatabase::BITMAP_BTN_ACTION_PRESSED_ID));
    btnBoost.setLabelText(touchgfx::TypedText(T_BTN_BOOST));
    btnBoost.setLabelColor(touchgfx::Color::getColorFromRGB(255, 255, 255));
    btnBoost.setLabelColorPressed(touchgfx::Color::getColorFromRGB(220, 252, 231));
    btnBoost.setAction(buttonCallback);
    add(btnBoost);
    btnNextScreen.setXY(340, 220);
    btnNextScreen.setBitmaps(touchgfx::Bitmap(BitmapDatabase::BITMAP_BTN_PRIMARY_RELEASED_ID), touchgfx::Bitmap(BitmapDatabase::BITMAP_BTN_PRIMARY_PRESSED_ID));
    btnNextScreen.setLabelText(touchgfx::TypedText(T_BTN_SETTINGS));
    btnNextScreen.setLabelColor(touchgfx::Color::getColorFromRGB(255, 255, 255));
    btnNextScreen.setLabelColorPressed(touchgfx::Color::getColorFromRGB(186, 230, 253));
    btnNextScreen.setAction(buttonCallback);
    add(btnNextScreen);
}

void DashboardScreenViewBase::setupScreen() {}

void DashboardScreenViewBase::buttonCallbackHandler(const touchgfx::AbstractButton& src) {
    if (&src == &btnBoost) {
        handleBoostClicked();
    }
    if (&src == &btnNextScreen) {
        application().gotoSettingsScreenSlideTransition();
    }
}
