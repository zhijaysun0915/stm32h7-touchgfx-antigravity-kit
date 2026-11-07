#!/usr/bin/env bash
# ==============================================================================
# STM32H7 + TouchGFX Firmware Build Script (execution/build_firmware.sh)
# Builds:
#   1. Full ARM Cortex-M7 ELF + Intel HEX Firmware (build/stm32h7_touchgfx.elf & .hex)
#      using installed Zig/LLVM or arm-none-eabi-gcc toolchain + STM32H7_FLASH.ld
#   2. Native macOS ARM64 Host Simulator (build/stm32h7_touchgfx_sim)
# ==============================================================================
set -e

# Auto-detect Toolchain Directory
TOOLCHAIN_DIR=""
for candidate in "$HOME/toolchain" "/Users/jaysun/.gemini/users/user1/toolchain" "/opt/toolchain"; do
  if [ -d "$candidate/pylib" ]; then
    TOOLCHAIN_DIR="$candidate"
    break
  fi
done

if [ -n "$TOOLCHAIN_DIR" ]; then
  export PYTHONPATH="$TOOLCHAIN_DIR/pylib:${PYTHONPATH:-}"
  export PATH="$TOOLCHAIN_DIR/bin:$TOOLCHAIN_DIR/pylib/bin:$PATH"
fi
export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"

BOARD_TYPE="${BOARD_TYPE:-STM32H750B_DK}" # STM32H750B_DK or STM32H745I_DISCO
if [ "$BOARD_TYPE" = "STM32H745I_DISCO" ]; then
  BOARD_DEFS="-DSTM32H745xx -DUSE_PWR_DIRECT_SMPS_SUPPLY"
else
  BOARD_DEFS="-DSTM32H750xx -DUSE_PWR_LDO_SUPPLY"
fi

mkdir -p temp build

echo "[Build] Step 1: Running Headless TouchGFX Code & Asset Generator..."
bash execution/run_tgfx_cli.sh TouchGFX/STM32H7_App.touchgfx

echo "[Build] Step 2: Compiling & Linking ARM Cortex-M7 Firmware (Target: $BOARD_TYPE)..."
ZIG_BIN=""
if [ -n "$TOOLCHAIN_DIR" ] && [ -x "$TOOLCHAIN_DIR/pylib/ziglang/zig" ]; then
  ZIG_BIN="$TOOLCHAIN_DIR/pylib/ziglang/zig"
elif command -v zig &> /dev/null; then
  ZIG_BIN="$(command -v zig)"
fi

if [ -n "$ZIG_BIN" ]; then
  "$ZIG_BIN" c++ -target thumb-freestanding-eabihf -mcpu=cortex_m7+vfp4d16sp \
    -std=c++17 -Os -fno-exceptions -fno-rtti -fno-threadsafe-statics -ffreestanding -nostdlib \
    -Wl,-T,STM32H7_FLASH.ld -Wl,-e,Reset_Handler -Wl,--gc-sections \
    $BOARD_DEFS \
    -ITouchGFX/stub_framework/include \
    -ITouchGFX/generated/images/include \
    -ITouchGFX/generated/texts/include \
    -ITouchGFX/generated/gui_generated/include \
    -ITouchGFX/gui/include \
    Core/Src/main.cpp \
    TouchGFX/generated/images/src/BitmapDatabase.cpp \
    TouchGFX/generated/texts/src/Texts.cpp \
    TouchGFX/generated/gui_generated/src/common/FrontendApplicationBase.cpp \
    TouchGFX/generated/gui_generated/src/*_screen/*ViewBase.cpp \
    TouchGFX/gui/src/model/Model.cpp \
    TouchGFX/gui/src/*_screen/*View.cpp \
    TouchGFX/gui/src/*_screen/*Presenter.cpp \
    -o build/stm32h7_touchgfx.elf > temp/last_build.log 2>&1
  python3 execution/elf_to_hex_bin.py build/stm32h7_touchgfx.elf | tee -a temp/last_build.log
elif command -v arm-none-eabi-g++ &> /dev/null && command -v cmake &> /dev/null; then
  rm -rf build/CMakeCache.txt build/CMakeFiles
  cmake -S . -B build \
    -DCMAKE_TOOLCHAIN_FILE=arm-none-eabi.cmake \
    -DBOARD_TYPE="$BOARD_TYPE" > temp/last_build.log 2>&1
  cmake --build build -- -j4 >> temp/last_build.log 2>&1
  arm-none-eabi-size build/stm32h7_touchgfx.elf | tee -a temp/last_build.log
else
  echo "[Build] Error: Neither Zig nor arm-none-eabi-gcc toolchain found."
  exit 1
fi

echo "[Build] Step 3: Building & Running Native macOS Host Simulator..."
clang++ -std=c++17 -O2 \
  $BOARD_DEFS \
  -ITouchGFX/stub_framework/include \
  -ITouchGFX/generated/images/include \
  -ITouchGFX/generated/texts/include \
  -ITouchGFX/generated/gui_generated/include \
  -ITouchGFX/gui/include \
  Core/Src/main.cpp \
  TouchGFX/generated/images/src/BitmapDatabase.cpp \
  TouchGFX/generated/texts/src/Texts.cpp \
  TouchGFX/generated/gui_generated/src/common/FrontendApplicationBase.cpp \
  TouchGFX/generated/gui_generated/src/*_screen/*ViewBase.cpp \
  TouchGFX/gui/src/model/Model.cpp \
  TouchGFX/gui/src/*_screen/*View.cpp \
  TouchGFX/gui/src/*_screen/*Presenter.cpp \
  -o build/stm32h7_touchgfx_sim >> temp/last_build.log 2>&1
./build/stm32h7_touchgfx_sim
echo "[Build] Complete! Artifacts ready: build/stm32h7_touchgfx.elf, build/stm32h7_touchgfx.hex, build/stm32h7_touchgfx_sim"
