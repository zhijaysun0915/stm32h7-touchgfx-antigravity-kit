#include <texts/TextKeysAndLanguages.hpp>
#include <stdint.h>

#if defined(__APPLE__)
#define LOCATION_EXTFLASH_ATTRIBUTE __attribute__((section("__DATA,ExtFlashSection"), used, aligned(4)))
#else
#define LOCATION_EXTFLASH_ATTRIBUTE __attribute__((section("ExtFlashSection"), used, aligned(4)))
#endif

LOCATION_EXTFLASH_ATTRIBUTE
extern const char* const DefaultTextDatabase[];
LOCATION_EXTFLASH_ATTRIBUTE
const char* const DefaultTextDatabase[] = {
    "STM32H7 Temp: <value> C", // T_DASHBOARD_TITLE
    "26.5", // T_TEMP_DEFAULT
    "Toggle Boost LED", // T_BTN_BOOST
    "Settings", // T_BTN_SETTINGS
    "System & Display Settings", // T_SETTINGS_TITLE
    "Back", // T_BTN_BACK
};
