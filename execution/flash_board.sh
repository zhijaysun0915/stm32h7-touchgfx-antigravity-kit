#!/usr/bin/env bash
# ==============================================================================
# STM32H745I-DISCO / STM32H750B-DK Automated Board Flasher (execution/flash_board.sh)
# Supports:
#   1. STM32_Programmer_CLI (with external QSPI loader MT25TL01G_*.stldr)
#   2. Installed pyOCD (STLINK-V3E native macOS USB programmer)
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

ELF_FILE="${1:-build/stm32h7_touchgfx.elf}"
if [ ! -f "$ELF_FILE" ] && [ -f "prebuilt/stm32h7_touchgfx.elf" ]; then
  ELF_FILE="prebuilt/stm32h7_touchgfx.elf"
fi
BOARD_TYPE="${BOARD_TYPE:-STM32H750B_DK}" # STM32H750B_DK or STM32H745I_DISCO

# Locate STM32_Programmer_CLI on macOS if installed
ST_PROG_PATHS=(
  "/Applications/STMicroelectronics/STM32Cube/STM32CubeProgrammer/STM32CubeProgrammer.app/Contents/MacOs/bin"
  "/opt/ST/STM32CubeCLT/STM32CubeProgrammer/bin"
  "/Applications/STMicroelectronics/STM32CubeCLT/STM32CubeProgrammer/bin"
)

STM32_CLI=""
if command -v STM32_Programmer_CLI &> /dev/null; then
  STM32_CLI="$(command -v STM32_Programmer_CLI)"
else
  for p in "${ST_PROG_PATHS[@]}"; do
    if [ -x "$p/STM32_Programmer_CLI" ]; then
      STM32_CLI="$p/STM32_Programmer_CLI"
      break
    fi
  done
fi

if [ -n "$STM32_CLI" ]; then
  BIN_DIR="$(dirname "$STM32_CLI")"
  if [ "$BOARD_TYPE" = "STM32H745I_DISCO" ]; then
    EXT_LOADER="$BIN_DIR/ExternalLoader/MT25TL01G_STM32H745I-DISCO.stldr"
  else
    EXT_LOADER="$BIN_DIR/ExternalLoader/MT25TL01G_STM32H750B-DISCO.stldr"
  fi
  echo "[Flash] Using STM32_Programmer_CLI to program $BOARD_TYPE (with QSPI Loader: $EXT_LOADER)..."
  "$STM32_CLI" -c port=SWD mode=UR reset=HWrst -el "$EXT_LOADER" -w "$ELF_FILE" -v -rst
  echo "[Flash] Programming & Verification Complete!"
  exit 0
fi

# Fallback to local pyOCD (installed in toolchain/pylib)
echo "[Flash] Probing connected STLINK-V3E USB probes via pyOCD..."
PROBES=$(python3 -m pyocd list --probes 2>&1 || true)
echo "$PROBES"
if echo "$PROBES" | grep -q "No available debug probes"; then
  echo "[Flash] Notice: No STLINK-V3E board is currently plugged into USB (CN14)."
  echo "        Connect the EVM's CN14 Micro-B port to MacBook Air and re-run 'bash execution/flash_board.sh'."
  exit 0
fi

if [ "$BOARD_TYPE" = "STM32H745I_DISCO" ]; then
  TARGET_MCU="stm32h743xx"
else
  TARGET_MCU="stm32h750xx"
fi

echo "[Flash] Flashing $ELF_FILE to $TARGET_MCU via pyOCD..."
python3 -m pyocd load -t "$TARGET_MCU" "$ELF_FILE"
python3 -m pyocd reset -t "$TARGET_MCU"
echo "[Flash] Board flashed and reset!"
