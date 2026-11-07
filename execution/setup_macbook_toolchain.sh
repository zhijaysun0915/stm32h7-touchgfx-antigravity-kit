#!/usr/bin/env bash
# ==============================================================================
# MacBook Air (Apple Silicon) Toolchain & Headless TouchGFX Setup Script
# For Google Antigravity IDE + STM32H745I-DISCO / STM32H750B-DK
# ==============================================================================
set -e

echo "=================================================================="
echo "[1/5] Checking & Installing Homebrew Embedded Toolchain..."
echo "=================================================================="
if ! command -v brew &> /dev/null; then
  echo "Error: Homebrew is not installed. Please install from https://brew.sh"
  exit 1
fi

# Install ARM GCC toolchain, CMake, Ninja, OpenOCD, STLink
brew list --cask gcc-arm-embedded &>/dev/null || brew install --cask gcc-arm-embedded
for pkg in cmake ninja openocd stlink python3; do
  brew list "$pkg" &>/dev/null || brew install "$pkg"
done

echo "=================================================================="
echo "[2/5] Installing Python Dependencies for UI Asset & Codegen..."
echo "=================================================================="
python3 -m pip install --upgrade --quiet pillow pyserial

echo "=================================================================="
echo "[3/5] Checking Optional Wine Bridge for Windows tgfx.exe CLI..."
echo "=================================================================="
if command -v wine &> /dev/null || command -v wine64 &> /dev/null; then
  echo "  -> Wine detected: $(command -v wine || command -v wine64)"
else
  echo "  -> Wine not installed (optional). Antigravity will use the built-in"
  echo "     Native macOS Python TouchGFX Codegen Engine (execution/tgfx_codegen.py)."
  echo "     (To install Wine for official tgfx.exe CLI: brew install --cask wine-stable)"
fi

echo "=================================================================="
echo "[4/5] Checking STM32CubeCLT / STM32CubeProgrammer CLI..."
echo "=================================================================="
ST_PROG_PATHS=(
  "/Applications/STMicroelectronics/STM32Cube/STM32CubeProgrammer/STM32CubeProgrammer.app/Contents/MacOs/bin"
  "/opt/ST/STM32CubeCLT/STM32CubeProgrammer/bin"
  "/Applications/STMicroelectronics/STM32CubeCLT/STM32CubeProgrammer/bin"
)

FOUND_ST_PROG=""
for p in "${ST_PROG_PATHS[@]}"; do
  if [ -x "$p/STM32_Programmer_CLI" ]; then
    FOUND_ST_PROG="$p/STM32_Programmer_CLI"
    break
  fi
done

if command -v STM32_Programmer_CLI &> /dev/null; then
  FOUND_ST_PROG="$(command -v STM32_Programmer_CLI)"
fi

if [ -n "$FOUND_ST_PROG" ]; then
  echo "  -> Found STM32_Programmer_CLI: $FOUND_ST_PROG"
else
  echo "  -> Notice: STM32_Programmer_CLI not found in standard paths."
  echo "     OpenOCD / st-flash is installed as fallback, but for QSPI External Flash"
  echo "     (0x90000000 MT25TL01G), please install STM32CubeCLT or STM32CubeProgrammer for macOS:"
  echo "     https://www.st.com/en/development-tools/stm32cubeclt.html"
fi

echo "=================================================================="
echo "[5/5] Verifying Toolchain Versions..."
echo "=================================================================="
arm-none-eabi-gcc --version | head -n 1
cmake --version | head -n 1
ninja --version
python3 --version
echo "Setup complete! Ready for Google Antigravity."
