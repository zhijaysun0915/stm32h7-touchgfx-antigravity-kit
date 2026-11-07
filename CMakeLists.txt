cmake_minimum_required(VERSION 3.22)
project(stm32h7_touchgfx LANGUAGES C CXX ASM)

set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)

set(BOARD_TYPE "STM32H750B_DK" CACHE STRING "Target Discovery Kit: STM32H750B_DK or STM32H745I_DISCO")

if(BOARD_TYPE STREQUAL "STM32H745I_DISCO")
    add_compile_definitions(STM32H745xx USE_PWR_DIRECT_SMPS_SUPPLY)
else()
    add_compile_definitions(STM32H750xx USE_PWR_LDO_SUPPLY)
endif()

include_directories(
    Core/Inc
    TouchGFX/stub_framework/include
    TouchGFX/generated/images/include
    TouchGFX/generated/texts/include
    TouchGFX/generated/gui_generated/include
    TouchGFX/gui/include
)

file(GLOB_RECURSE TGFX_GEN_SRCS
    "TouchGFX/generated/images/src/*.cpp"
    "TouchGFX/generated/texts/src/*.cpp"
    "TouchGFX/generated/gui_generated/src/*.cpp"
)

file(GLOB_RECURSE TGFX_USER_SRCS
    "TouchGFX/gui/src/*.cpp"
)

add_executable(stm32h7_touchgfx.elf
    Core/Src/main.cpp
    ${TGFX_GEN_SRCS}
    ${TGFX_USER_SRCS}
)

target_link_options(stm32h7_touchgfx.elf PRIVATE
    -T${CMAKE_SOURCE_DIR}/STM32H7_FLASH.ld
    -specs=nano.specs
    -specs=nosys.specs
    -Wl,--gc-sections
    -Wl,-Map=${CMAKE_BINARY_DIR}/stm32h7_touchgfx.map
)

add_custom_command(TARGET stm32h7_touchgfx.elf POST_BUILD
    COMMAND ${CMAKE_OBJCOPY} -O ihex $<TARGET_FILE:stm32h7_touchgfx.elf> ${CMAKE_BINARY_DIR}/stm32h7_touchgfx.hex
    COMMAND ${CMAKE_OBJCOPY} -O binary $<TARGET_FILE:stm32h7_touchgfx.elf> ${CMAKE_BINARY_DIR}/stm32h7_touchgfx.bin
    COMMENT "Generating HEX and BIN firmware images for internal + QSPI flash..."
)
