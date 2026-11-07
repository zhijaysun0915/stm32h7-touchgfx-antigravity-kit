# AGENTS.md — STM32H7 TouchGFX Text-to-UI Autopilot (MacBook Air Edition)

> **Target Hardware**: STMicroelectronics `STM32H745I-DISCO` (`STM32H745XIH6`) & `STM32H750B-DK` (`STM32H750XBH6`) — [UM2488 User Manual](https://www.st.com/resource/en/user_manual/um2488-discovery-kits-with-stm32h745xi-and-stm32h750xb-mcus-stmicroelectronics.pdf)
> **Display & Graphics**: 4.3" 480×272 RGB TFT LCD with capacitive touch, Chrom-ART Accelerator™ (DMA2D), SDRAM Framebuffer (`0xD0000000`), Dual Quad-SPI NOR Flash Assets (`0x90000000`, 128 MB)
> **Host Environment**: macOS (Apple Silicon MacBook Air) + Google Antigravity IDE

---

## 1. Architecture Overview (The 3-Layer Model)

This workspace enables **pure text-to-embedded-UI development**. The human developer provides high-level natural language UI descriptions, and Google Antigravity autonomously executes the full UI design, asset synthesis, TouchGFX code generation, ARM cross-compilation, QSPI + Internal Flash programming, and UART telemetry verification.

### Layer 1: Directive (`directives/`)
- Defines **what** UI screens, interactions, widgets, and hardware peripherals to build.
- Key files:
  - `directives/ui_requirements.md`: Current natural-language UI prompt, screen hierarchy, color tokens, and interaction flows.
  - `directives/hardware_constraints.md`: Pinout, memory map, and SMPS/LDO power supply safety rules from [UM2488](https://www.st.com/resource/en/user_manual/um2488-discovery-kits-with-stm32h745xi-and-stm32h750xb-mcus-stmicroelectronics.pdf).

### Layer 2: Orchestration (Google Antigravity Agent)
- Reads the user's natural language UI prompt and loads `skills/touchgfx-ui-autopilot/SKILL.md`.
- Translates the prompt into:
  1. **UI Visual Assets**: Calls `python3 execution/generate_ui_assets.py` to generate 480×272 backgrounds, cards, buttons, and icons in `TouchGFX/assets/images/`.
  2. **TouchGFX Designer Project Model**: Updates `TouchGFX/STM32H7_App.touchgfx` (JSON schema) and `TouchGFX/assets/texts/texts.xml`.
  3. **TouchGFX Code Generation**: Runs `bash execution/run_tgfx_cli.sh` (which invokes `tgfx.exe generate` via Wine/VM if present, or natively executes `python3 execution/tgfx_codegen.py` on macOS) to produce `TouchGFX/generated/` (`*ViewBase.hpp/.cpp`, `BitmapDatabase`, `Texts`).
  4. **MVP C++ Business Logic**: Writes custom animations, event handlers, and hardware bindings in `TouchGFX/gui/src/` and `TouchGFX/gui/include/` (`Model`, `Presenter`, `View`).
  5. **Build, Flash & Verify**: Runs `execution/build_firmware.sh`, `execution/flash_board.sh`, and `execution/verify_serial.py`.

### Layer 3: Execution (`execution/`)
Deterministic CLI scripts that perform atomic operations on macOS:
- `execution/setup_macbook_toolchain.sh`: Installs and verifies Homebrew toolchains (`arm-none-eabi-gcc`, `cmake`, `ninja`, `openocd`, `stlink`), Python packages (`pillow`, `pyserial`), and `STM32_Programmer_CLI`.
- `execution/generate_ui_assets.py`: Generates PNG UI components and backgrounds sized for 480×272 LCD.
- `execution/run_tgfx_cli.sh`: Headless TouchGFX Designer CLI bridge (`tgfx.exe generate` via Wine/Parallels or native `execution/tgfx_codegen.py`).
- `execution/tgfx_codegen.py`: Native macOS Python code generator that compiles `.touchgfx` JSON, `texts.xml`, and PNG assets into C++ `gui_generated` classes and RGB565/ARGB8888 `ExtFlashSection` byte arrays.
- `execution/build_firmware.sh`: Runs CMake + Ninja with `arm-none-eabi-gcc` and outputs `.elf`, `.bin`, and `.hex` artifacts plus memory usage statistics.
- `execution/flash_board.sh`: Programs both internal Flash and external MT25TL01G Quad-SPI Flash (`0x90000000`) via `STM32_Programmer_CLI` over STLINK-V3E (CN14).
- `execution/verify_serial.py`: Captures UART3 telemetry (`PB10`/`PB11` Virtual COM Port at 115200 bps) to confirm boot, power supply mode, and active UI screen.

---

## 2. Standard End-to-End Workflow (When User Gives a Text UI Prompt)

Whenever the user asks to create or modify a UI in chat (e.g., *"幫我設計一個智慧家居溫控面板，有圓形溫度計、模式切換按鈕與即時曲線圖"*):

1. **Step 1 — Update Spec & Design Tokens**:
   Record the screen layout (within `480x272` bounds), color palette, and widget list in `directives/ui_requirements.md`.
2. **Step 2 — Generate PNG Assets**:
   Run `python3 execution/generate_ui_assets.py --spec directives/ui_assets_manifest.json` to create crisp PNG assets in `TouchGFX/assets/images/`.
3. **Step 3 — Update `.touchgfx` JSON & `texts.xml`**:
   Modify `TouchGFX/STM32H7_App.touchgfx` (`Screens`, `Components`, `Interactions`) and `TouchGFX/assets/texts/texts.xml` following `skills/touchgfx-ui-autopilot/SKILL.md`.
4. **Step 4 — Run Headless TouchGFX Code Generation**:
   Execute `bash execution/run_tgfx_cli.sh` to regenerate `TouchGFX/generated/`.
5. **Step 5 — Implement C++ MVP Logic**:
   Implement `<Screen>View.hpp/.cpp`, `<Screen>Presenter.hpp/.cpp`, and `Model.hpp/.cpp` under `TouchGFX/gui/`. Never manually edit files inside `TouchGFX/generated/` as they are overwritten on step 4.
6. **Step 6 — Compile & Flash**:
   Run `bash execution/build_firmware.sh`. Once the build succeeds, if the board is connected via USB, run `bash execution/flash_board.sh` and `python3 execution/verify_serial.py`.

---

## 3. Self-Annealing Loop (Autonomous Error Recovery)

If any command in `execution/` returns a non-zero exit code:
1. **Inspect Error Output**: Read `temp/last_build.log` or `temp/last_tgfx.log`.
2. **Diagnose & Patch**:
   - **JSON / XML Schema Error**: Validate `TouchGFX/STM32H7_App.touchgfx` JSON syntax and ensure every `TextId` referenced in a widget exists in `TouchGFX/assets/texts/texts.xml`.
   - **C++ Compilation Error**: Check `ViewBase` member names in `TouchGFX/generated/gui_generated/include/` and match virtual interaction callback signatures in `<Screen>View.hpp`.
   - **Linker Overflow (`FLASH` or `RAM` full)**: Ensure all bitmap arrays and font tables carry `__attribute__((section("ExtFlashSection")))` so they reside in the 128 MB Quad-SPI NOR Flash (`0x90000000`), and framebuffers carry `__attribute__((section("TouchGFX_Framebuffer")))` in SDRAM (`0xD0000000`).
3. **Re-Verify & Document**: Re-run `bash execution/build_firmware.sh` until exit code is `0`. Record any newly discovered hardware or library quirk in `directives/hardware_constraints.md`.

---

## 4. Critical Hardware Safety Guardrail (SMPS vs. LDO Deadlock)

Per [UM2488 Section 6.4 (Power Supply)](https://www.st.com/resource/en/user_manual/um2488-discovery-kits-with-stm32h745xi-and-stm32h750xb-mcus-stmicroelectronics.pdf):
- **STM32H745I-DISCO** default hardware solder bridges use **Direct SMPS**: Firmware MUST call `HAL_PWREx_ConfigSupply(PWR_DIRECT_SMPS_SUPPLY);`.
- **STM32H750B-DK** default hardware solder bridges use **LDO**: Firmware MUST call `HAL_PWREx_ConfigSupply(PWR_LDO_SUPPLY);`.
- **NEVER mix these up!** Flashing mismatched `HAL_PWREx_ConfigSupply` causes a hardware power deadlock after reset where ST-LINK can no longer connect (requiring `R143` -> `R144` BOOT0 resistor rework to recover). Our `CMakeLists.txt` and `Core/Src/main.c` automatically guard this via `-DBOARD_TYPE=STM32H750B_DK` or `-DBOARD_TYPE=STM32H745I_DISCO`.
