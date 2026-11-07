#!/usr/bin/env bash
# ==============================================================================
# Headless TouchGFX Designer CLI Runner (Dual-Engine for MacBook Air)
# Engine 1: If Windows tgfx.exe is available via Wine or Parallels VM, invoke it.
# Engine 2: Native macOS Python TouchGFX Codegen (execution/tgfx_codegen.py)
# ==============================================================================
set -e

PROJECT_FILE="${1:-TouchGFX/STM32H7_App.touchgfx}"
mkdir -p temp

echo "[TouchGFX-CLI] Processing UI specification: $PROJECT_FILE"

# Step 1: Ensure procedural UI PNG assets are up to date
if [ -f "directives/ui_assets_manifest.json" ]; then
  python3 execution/generate_ui_assets.py --manifest directives/ui_assets_manifest.json > temp/last_tgfx.log 2>&1
  cat temp/last_tgfx.log
fi

# Step 2: Check if user configured an explicit Windows tgfx.exe under Wine
TGFX_EXE_WINE="${TGFX_EXE_PATH:-$HOME/.wine/drive_c/TouchGFX/4.24.0/designer/tgfx.exe}"
if [ -f "$TGFX_EXE_WINE" ] && command -v wine &> /dev/null; then
  echo "[TouchGFX-CLI] Detected Wine + tgfx.exe at $TGFX_EXE_WINE. Running tgfx.exe generate..."
  wine "$TGFX_EXE_WINE" generate -p "$PROJECT_FILE" >> temp/last_tgfx.log 2>&1 && {
    echo "[TouchGFX-CLI] Official tgfx.exe code generation succeeded."
    exit 0
  }
  echo "[TouchGFX-CLI] Wine tgfx.exe returned non-zero, falling back to Native macOS Codegen..."
fi

# Step 3: Run Native macOS Python TouchGFX Codegen
python3 execution/tgfx_codegen.py -p "$PROJECT_FILE" | tee -a temp/last_tgfx.log
