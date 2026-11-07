#ifndef FRONTENDAPPLICATIONBASE_HPP
#define FRONTENDAPPLICATIONBASE_HPP
#include <touchgfx/Application.hpp>

class FrontendApplicationBase : public touchgfx::Application {
public:
    FrontendApplicationBase() {}
    virtual ~FrontendApplicationBase() {}
    void gotoDashboardScreenSlideTransition();
    void gotoSettingsScreenSlideTransition();
};
#endif // FRONTENDAPPLICATIONBASE_HPP
