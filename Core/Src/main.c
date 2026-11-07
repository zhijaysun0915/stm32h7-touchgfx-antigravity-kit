/**
 * @file main.c
 * @brief STM32H745I-DISCO / STM32H750B-DK System & Power Supply Guard
 * Reference: UM2488 Rev 10 Section 6.4 (SMPS/LDO Power Supply)
 */
#include <stdint.h>

/*
 * CRITICAL HARDWARE SAFETY GUARD (UM2488 Section 6.4):
 * - STM32H745I-DISCO default hardware requires Direct SMPS:
 *     HAL_PWREx_ConfigSupply(PWR_DIRECT_SMPS_SUPPLY);
 * - STM32H750B-DK default hardware requires LDO:
 *     HAL_PWREx_ConfigSupply(PWR_LDO_SUPPLY);
 */
#if defined(USE_PWR_DIRECT_SMPS_SUPPLY) && defined(USE_PWR_LDO_SUPPLY)
#error "Cannot define both USE_PWR_DIRECT_SMPS_SUPPLY and USE_PWR_LDO_SUPPLY!"
#endif

void SystemClock_PowerSupply_Guard(void) {
#if defined(STM32H745xx)
    /* STM32H745I-DISCO default board configuration: Direct SMPS */
    /* HAL_PWREx_ConfigSupply(PWR_DIRECT_SMPS_SUPPLY); */
#elif defined(STM32H750xx)
    /* STM32H750B-DK default board configuration: LDO */
    /* HAL_PWREx_ConfigSupply(PWR_LDO_SUPPLY); */
#endif
}
