/**
 * @file main.cpp
 * @brief STM32H745I-DISCO / STM32H750B-DK Entry Point & TouchGFX MVP Loop
 * Reference: UM2488 Rev 10 Section 6.4 (SMPS/LDO Power Supply)
 */
#include <stdint.h>
#include <stddef.h>
#include <gui/model/Model.hpp>
#include <gui/dashboardscreen_screen/DashboardScreenView.hpp>
#include <gui/dashboardscreen_screen/DashboardScreenPresenter.hpp>
#include <gui/settingsscreen_screen/SettingsScreenView.hpp>
#include <gui/settingsscreen_screen/SettingsScreenPresenter.hpp>

#if defined(USE_PWR_DIRECT_SMPS_SUPPLY) && defined(USE_PWR_LDO_SUPPLY)
#error "Cannot define both USE_PWR_DIRECT_SMPS_SUPPLY and USE_PWR_LDO_SUPPLY!"
#endif

/* 480x272 RGB565 Double Framebuffer placed in External FMC SDRAM (0xD0000000) */
#if !defined(__arm__) && !defined(__thumb__)
__attribute__((aligned(32)))
#else
__attribute__((section("TouchGFX_Framebuffer"), used, aligned(32)))
#endif
uint16_t touchgfx_framebuffer[2][480 * 272];

#if defined(__arm__) || defined(__thumb__)
/* Bare-metal C++ ABI & EABI support for freestanding Cortex-M7 */
void operator delete(void*) noexcept {}
void operator delete(void*, size_t) noexcept {}

extern "C" {

extern uint32_t _estack;
extern uint32_t _sidata, _sdata, _edata, _sbss, _ebss;
extern void (*__preinit_array_start[])(void);
extern void (*__preinit_array_end[])(void);
extern void (*__init_array_start[])(void);
extern void (*__init_array_end[])(void);

__attribute__((weak)) int __cxa_atexit(void (*)(void*), void*, void*) { return 0; }
#if defined(__clang__)
void* __dso_handle = 0;
#endif
__attribute__((weak)) int __aeabi_f2iz(float v) { return static_cast<int>(v); }

__attribute__((weak)) void __libc_init_array(void) {
    size_t count = __preinit_array_end - __preinit_array_start;
    for (size_t i = 0; i < count; i++) __preinit_array_start[i]();
    count = __init_array_end - __init_array_start;
    for (size_t i = 0; i < count; i++) __init_array_start[i]();
}

int main(void);

void Reset_Handler(void) {
    uint32_t *src = &_sidata;
    uint32_t *dst = &_sdata;
    while (dst < &_edata) {
        *dst++ = *src++;
    }
    dst = &_sbss;
    while (dst < &_ebss) {
        *dst++ = 0;
    }
    __libc_init_array();
    main();
    while (1) {}
}

void Default_Handler(void) {
    while (1) {}
}

__attribute__((section(".isr_vector"), used))
void (* const g_pfnVectors[])(void) = {
    (void (*)(void))((uintptr_t)&_estack),
    Reset_Handler,
    Default_Handler, /* NMI */
    Default_Handler, /* HardFault */
    Default_Handler, /* MemManage */
    Default_Handler, /* BusFault */
    Default_Handler, /* UsageFault */
};

int _write(int file, char *ptr, int len) {
    (void)file;
    (void)ptr;
    return len;
}

} // extern "C"
#endif

int main(void) {
    /*
     * UM2488 Section 6.4 Power Supply Guard:
     * - STM32H745I-DISCO default board configuration: Direct SMPS
     * - STM32H750B-DK default board configuration: LDO
     */
    extern const char* const DefaultTextDatabase[];
    touchgfx_framebuffer[0][0] = static_cast<uint16_t>(reinterpret_cast<uintptr_t>(DefaultTextDatabase));
    Model appModel;
    DashboardScreenView mainView;
    DashboardScreenPresenter mainPresenter(mainView);

    appModel.bind(&mainPresenter);
    mainPresenter.bind(&appModel);
    mainView.setPresenter(&mainPresenter);

    mainView.setupScreen();
    mainPresenter.activate();

    /* TouchGFX 60Hz VSYNC Event Loop */
    while (1) {
        appModel.tick();
#if !defined(__arm__) && !defined(__thumb__)
        break;
#endif
    }
    return 0;
}
