#!/usr/bin/env bash
# ==============================================================================
# Linux / Antigravity VM Toolchain & Headless TouchGFX Setup Script
# For STM32H745I-DISCO / STM32H750B-DK
# ==============================================================================
set -e

TOOLCHAIN_DIR="${TOOLCHAIN_DIR:-$HOME/toolchain}"
mkdir -p "$TOOLCHAIN_DIR" "$HOME/.local/bin"

echo "=================================================================="
echo "[1/4] Installing Python Embedded Libraries & Zig/PyOCD..."
echo "=================================================================="
python3 -m pip install --user --break-system-packages \
  ziglang pyocd pillow pyserial pyelftools intelhex

# Symlink zig if not already on PATH
ZIG_PKG_PATH="$(python3 -c "import ziglang, os; print(os.path.dirname(ziglang.__file__))" 2>/dev/null || true)"
if [ -n "$ZIG_PKG_PATH" ] && [ -x "$ZIG_PKG_PATH/zig" ]; then
  ln -sf "$ZIG_PKG_PATH/zig" "$HOME/.local/bin/zig"
  ln -sf "$ZIG_PKG_PATH/zig" "$TOOLCHAIN_DIR/bin/zig" 2>/dev/null || true
fi

echo "=================================================================="
echo "[2/4] Downloading & Configuring Official ARM GNU Toolchain..."
echo "=================================================================="
if [ ! -x "$TOOLCHAIN_DIR/bin/arm-none-eabi-gcc" ]; then
  echo "Downloading Arm GNU Toolchain 13.3.Rel1..."
  curl -L -o "$TOOLCHAIN_DIR/arm-gnu-toolchain.tar.xz" \
    "https://developer.arm.com/-/media/Files/downloads/gnu/13.3.rel1/binrel/arm-gnu-toolchain-13.3.rel1-x86_64-arm-none-eabi.tar.xz"
  tar -xf "$TOOLCHAIN_DIR/arm-gnu-toolchain.tar.xz" -C "$TOOLCHAIN_DIR" --strip-components=1
  rm -f "$TOOLCHAIN_DIR/arm-gnu-toolchain.tar.xz"
else
  echo "Arm GNU Toolchain already installed in $TOOLCHAIN_DIR/bin"
fi

echo "=================================================================="
echo "[3/4] Installing CMSIS-Pack Support for STM32H7 in pyOCD..."
echo "=================================================================="
export PATH="$TOOLCHAIN_DIR/bin:$HOME/.local/bin:$PATH"
pyocd pack install STM32H750XB STM32H745XI || true

echo "=================================================================="
echo "[4/4] Verifying Toolchain Versions..."
echo "=================================================================="
arm-none-eabi-gcc --version | head -n 1
zig version
pyocd --version
cmake --version | head -n 1
ninja --version
python3 --version

echo ""
echo "Setup complete! Ready for STM32H7 + TouchGFX development."
