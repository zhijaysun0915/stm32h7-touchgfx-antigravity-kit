# STM32H7 + TouchGFX Text-to-UI Autopilot Kit

[![Target MCU](https://img.shields.io/badge/Target%20MCU-STM32H750XB%20%7C%20STM32H745XI-00205B.svg)](https://www.st.com/en/microcontrollers-microprocessors/stm32h7-series.html)
[![TouchGFX](https://img.shields.io/badge/GUI-TouchGFX%204.24-00A5B5.svg)](https://www.st.com/en/development-tools/touchgfxdesigner.html)
[![Host Architecture](https://img.shields.io/badge/Host-Apple%20Silicon%20%28ARM64%29-black.svg)](https://www.apple.com/mac/)
[![Toolchain](https://img.shields.io/badge/Toolchain-Zig%20LLVM%20%7C%20pyOCD-F7A41D.svg)](https://ziglang.org/)

專為 **MacBook Air / Pro (Apple Silicon macOS)** 與 **Google Antigravity IDE** 打造之 **STM32H7 高效能無頭式 (Headless) TouchGFX 嵌入式 UI 開發套件**。

本專案支援 **STM32H750B-DK** 及 **STM32H745I-DISCO** 開發板（依據 [STMicroelectronics UM2488 使用手冊 Rev 10](https://www.st.com/resource/en/user_manual/um2488-discovery-kits-with-stm32h745xi-and-stm32h750xb-mcus-stmicroelectronics.pdf)），完整打通從**自然語言 UI 需求 -> 向量圖資合成 -> TouchGFX 代碼生成 -> ARM Cortex-M7 交叉編譯 -> 本機模擬驗證 -> STLINK-V3E 實體板燒錄與 UART 遙測**之全自動化開發管線 (Pipeline)。

---

## 目錄

- [最新版本說明 (Release v1.0.0)](#最新版本說明-release-v100)
  - [目前 UI 設計與視覺元件](#目前-ui-設計與視覺元件)
  - [系統核心功能](#系統核心功能)
  - [四層驗證機制與結果](#四層驗證機制與結果)
- [核心功能特色](#核心功能特色)
- [系統架構 (3-Layer Architecture)](#系統架構-3-layer-architecture)
- [記憶體配置與硬體映射 (Memory Map)](#記憶體配置與硬體映射-memory-map)
- [硬體接線與板子配置指南](#硬體接線與板子配置指南重要)
  - [1. 實體接口接線 (CN14)](#1-實體接口接線)
  - [2. 電源跳線與模式確認 (JP6 / SMPS vs LDO)](#2-電源跳線與模式確認-jp6--smps-vs-ldo)
  - [3. 板載 LED 狀態指示燈判讀](#3-板載-led-狀態指示燈判讀)
- [開發環境與依賴說明](#開發環境與依賴說明)
- [完整 Pipeline 操作指南](#完整-pipeline-操作指南)
  - [一鍵編譯韌體與模擬器](#1-一鍵編譯韌體與模擬器)
  - [燒錄韌體至開發板](#2-燒錄韌體至開發板)
  - [監聽 UART 遙測日誌](#3-監聽-uart-遙測日誌)
- [預編譯成品 (Prebuilt Binaries)](#預編譯成品-prebuilt-binaries)
- [與 Google Antigravity Agent 協同開發](#與-google-antigravity-agent-協同開發)

---

## 最新版本說明 (Release v1.0.0)

本專案已正式發布 **v1.0.0**，詳細說明見 [RELEASE_NOTES.md](file:///Users/jaysun/Downloads/stm32h7-touchgfx-antigravity-kit/RELEASE_NOTES.md)。

### 目前 UI 設計與視覺元件
- **目標螢幕**：4.3 吋 480×272 16bpp (RGB565) LCD，深色科技主題（Slate Dark，底色 `#0F172A`）。
- **首頁儀表板 (`DashboardScreen`)**：
  - **背景與卡片佈局**：480×272 漸層底圖 (`bg_dashboard.png`)，搭配左右兩塊 216×160 毛玻璃質感面板 (`card_panel.png`)。
  - **頂部動態狀態標題 (`titleText`)**：帶有 Wildcard 緩衝區之即時核心溫度顯示 (`STM32H7 Temp: <value> C`)。
  - **左側負載指示條 (`loadBar`)**：`BoxProgress` 青藍色動態指示條 (`#38BDF8`)，呈現即時 CPU / 系統負載率 (0~100%)。
  - **Boost 切換按鈕 (`btnBoost`)**：支援正常態與按下態按鈕 (`Toggle Boost LED`)，用以切換超頻狀態與控制板載 LED。
  - **設定導航按鈕 (`btnNextScreen`)**：點擊切換至設定頁 (`Settings`)。
- **系統設定畫面 (`SettingsScreen`)**：
  - 全屏深色背景 (`settingsBg`) 與標題 (`System & Display Settings`)。
  - 具備左下角返回按鈕 (`btnBack`)。

### 系統核心功能
1. **MVP (Model-View-Presenter) 狀態循環**：`Model` 每 30 ticks (~500ms) 定期透過 `ModelListener` 發送溫度與負載更新，由 Presenter 驅動 View 進行局部畫面重繪 (`invalidate`)。
2. **動態數據渲染**：微控制器即時溫度浮點數格式化輸出至標題 Wildcard，負載進度條即時反應系統繁忙度。
3. **軟硬體交互 (Boost LED 切換)**：按下 `btnBoost` 可切換 Model 的 `boostActive` 狀態（模擬負載跳升至 88%、溫度升至 31.2°C，並控制板載綠色 LED `LD7` (PJ2)）。
4. **雙向平滑轉場動畫 (Screen Slide Transitions)**：
   - 首頁點擊 `Settings`：往東平滑滑動 (`Slide East`) 至設定頁。
   - 設定頁點擊 `Back`：往西平滑滑動 (`Slide West`) 返回主儀表板。

### 四層驗證機制與結果
1. **無頭代碼與圖資生成驗證** (`run_tgfx_cli.sh`)：成功產生 7 張 RGB565 PNG 圖資並轉出 C++ ViewBase / 字庫 / 圖庫，無語法錯誤。
2. **ARM Cortex-M7 交叉編譯與記憶體配置驗證** (`build_firmware.sh`)：
   - **Internal Flash (0x08000000)**: 1,216 Bytes (1.19 KB) 向量表與啟動代碼。
   - **External QSPI Flash (0x90000000)**: 54,272 Bytes (53.00 KB) 7 張圖資與點陣字庫。
   - **External SDRAM (0xD0000000)**: 522,240 Bytes (510.00 KB) 480×272 雙緩衝區。
   - **HEX 映像檔**: 產出 `build/stm32h7_touchgfx.hex` 與 `prebuilt/`。
3. **本機原生 Host 模擬器驗證** (`build/stm32h7_touchgfx_sim`)：macOS ARM64 原生編譯運行，驗證 Model、Presenter、ViewBase 與 Tick 事件迴圈無記憶體崩潰。
4. **STLINK-V3E 探針與序列埠驗證** (`flash_board.sh` / `verify_serial.py`)：自動探測 USB SWD 介面，並以 115200 8N1 監聽 USART3 VCP 遙測。

---

## 核心功能特色

1. **純文字驅動 UI (Text-to-Embedded-GUI)**：只需給予自然語言描述，自動產生 480×272 面板所需之 PNG 素材、更新 TouchGFX `.touchgfx` JSON 模型與 `texts.xml`。
2. **Apple Silicon 原生無頭代碼生成**：內建原生 Python TouchGFX Codegen (`execution/tgfx_codegen.py`)，免去在 macOS 上安裝肥重 Windows 模擬環境的痛苦。
3. **極速交叉編譯**：整合原生的 ARM Cortex-M7 LLVM / Zig 交叉編譯器與 ld.lld 連結器，數秒內輸出完全符合 UM2488 記憶體佈局之 ELF 與 Intel HEX 韌體。
4. **本機原生 Host 模擬器**：同一套 TouchGFX MVP (Model-View-Presenter) 業務邏輯，一鍵編譯成 macOS ARM64 原生執行檔驗證流程。
5. **STLINK-V3E 自動探測與燒錄**：透過 pyOCD 與 STM32_Programmer_CLI 雙後端支援，一鍵偵測 USB SWD 介面並寫入 MCU。

---

## 系統架構 (3-Layer Architecture)

```
┌─────────────────────────────────────────────────────────────┐
│                 Layer 1: Directives (需求層)                │
│  - directives/ui_requirements.md (自然語言需求與螢幕規格)    │
│  - directives/ui_assets_manifest.json (圖資尺寸與顏色定義)  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│               Layer 2: Orchestration (調度層)               │
│  - Google Antigravity Agent (自動化決策與 MVP 互動邏輯)      │
│  - skills/touchgfx-ui-autopilot/SKILL.md (領域專家規範)     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Layer 3: Execution (執行層)                 │
│  - generate_ui_assets.py   : 產出 480×272 LCD 專用圖資      │
│  - tgfx_codegen.py         : 產出 C++ ViewBase / 字庫 / 圖庫│
│  - build_firmware.sh       : ARM Cortex-M7 + macOS Sim 編譯 │
│  - flash_board.sh          : STLINK-V3E SWD / QSPI 燒錄     │
│  - verify_serial.py        : VCP UART3 (115200 8N1) 驗證    │
└─────────────────────────────────────────────────────────────┘
```

---

## 記憶體配置與硬體映射 (Memory Map)

根據 **STMicroelectronics UM2488 Rev 10**，韌體連結器腳本 (`STM32H7_FLASH.ld`) 規劃嚴格劃分三個實體區域：

| 儲存區域 | 實體位址 | 容量配置 | 用途說明 | 連結 Section |
| :--- | :--- | :--- | :--- | :--- |
| **Internal Flash** | `0x08000000` | 1.19 KB (1,216 B) | 中斷向量表 (`.isr_vector`)、MVP 啟動與調度代碼 (`.text`) | `.isr_vector`, `.text`, `.ARM` |
| **External QSPI Flash** | `0x90000000` | 53.00 KB (54,272 B) | 7 張 RGB565 UI 圖片圖資與 Unicode 字型點陣表 | `ExtFlashSection` |
| **External FMC SDRAM** | `0xD0000000` | 510.00 KB (522,240 B)| 480×272 RGB565 雙緩衝區 (Double Framebuffer) | `TouchGFX_Framebuffer` |
| **Internal AXI SRAM** | `0x24000000` | 8.01 KB (8,204 B) | 執行期全域變數、堆疊 (Stack 4KB) 與堆積 (Heap 4KB) | `.data`, `.bss`, `._user_heap_stack` |

---

## 硬體接線與板子配置指南（重要）

在將板子連接至 Mac 之前，請務必按照以下步驟核對板子硬體設定：

```
                      +---------------------------------------+
                      |           STM32H750B-DK               |
                      |                                       |
    [ Mac USB-C ] ===>| [CN14] STLINK-V3E Micro-B (燒錄/供電) |
                      |                                       |
                      | [JP6] 跳線確認插在 [STLK] (5V 供電)   |
                      | [LD4] PWR LED (綠燈恆亮 = 供電正常)    |
                      | [LD1] COM LED (紅/綠 = STLINK 通訊)   |
                      |                                       |
                      |   [ 4.3" 480x272 觸控螢幕 ]           |
                      +---------------------------------------+
```

### 1. 實體接口接線

1. **連接連接埠**：請使用 Micro-USB 傳輸線，將 Mac 連接到板載 **`CN14` (STLINK-V3E)** 接口。
   > ⚠️ **警告**：請**勿**接到 `CN13` (USB OTG_FS)，`CN13` 是應用端 USB，不具備 ST-LINK 燒錄器與虛擬序列埠功能！
2. **集線器注意事項**：若使用 USB-C 轉接器 (Dongle)，請確保轉接器供電穩定（建議直插 Mac 或使用帶供電之 USB-C Hub），避免電壓不足導致外掛 SDRAM 與 LCD 背光閃退。

### 2. 電源跳線與模式確認 (JP6 / SMPS vs LDO)

依據 [UM2488 Section 6.4 (Power supply)]：
- **供電來源跳線 (`JP6`)**：確認跳線帽插在 **`STLK`**（由 CN14 的 ST-LINK 5V 提供板子電源）。
- **硬體供電安全規範（防鎖死警告）**：
  - **STM32H750B-DK**：出廠預設為 **LDO 供電模式**。韌體**必須**呼叫 `HAL_PWREx_ConfigSupply(PWR_LDO_SUPPLY);`（本專案預設參數）。
  - **STM32H745I-DISCO**：出廠預設為 **Direct SMPS 模式**。韌體**必須**呼叫 `HAL_PWREx_ConfigSupply(PWR_DIRECT_SMPS_SUPPLY);`。
  - ⚠️ **切勿燒錯供電架構**：若在 STM32H750B-DK 上啟用 Direct SMPS，會造成晶片供電死鎖，使 ST-LINK 無法連線（需改動板載 R143/R144 電阻才能救援）。本套件編譯指令已透過 `-DBOARD_TYPE=STM32H750B_DK` 設置嚴密防護。

### 3. 板載 LED 狀態指示燈判讀

- **`LD4 (PWR)` 綠燈**：接上 Mac 後應**立即恆亮**。若不亮，請檢查 USB 線是否僅具充電功能而無數據傳輸，或更換 USB 連接埠。
- **`LD1 (COM)` 雙色燈**：ST-LINK 狀態燈。
  - 紅色緩慢閃爍：ST-LINK 正在進行 USB 列舉。
  - 綠色常亮：ST-LINK 與 Mac 通訊連線成功，準備好接受燒錄。
  - 紅/綠快速閃爍：正在進行韌體資料傳輸與 Flash 燒錄。
- **`LD7 (Green) / LD6 (Red)`**：使用者狀態 LED，分別連接至 MCU 的 `PJ2` 與 `PI13`。

---

## 開發環境與依賴說明

本套件環境已完成原生 Apple Silicon 部署，工具鏈位置已配置智慧探測：
- **交叉編譯**：LLVM / Zig ARM Cortex-M7 + ld.lld（支援 `thumb-freestanding-eabihf`）。
- **硬體除錯與燒錄**：`pyocd` 0.46.1（含 `libusb_package` 原生驅動與 CMSIS-DAP / STLINK-V3E 支援）。
- **Python 工具鏈**：Pillow 11.3.0（圖資處理）、pyserial 3.5（序列埠遙測）、pyelftools 0.32、intelhex 2.3.0。
- **建構系統**：Ninja 1.13.2、CMake、Clang++（原生 macOS 模擬器）。

---

## 完整 Pipeline 操作指南

### 1. 一鍵編譯韌體與模擬器

執行下列指令，自動完成「UI 素材生成 -> C++ 類別產生 -> ARM ELF/HEX 編譯 -> macOS 模擬器執行」：

```bash
# 預設編譯 STM32H750B-DK (LDO 供電模式)
bash execution/build_firmware.sh

# 若目標板為 STM32H745I-DISCO (Direct SMPS 模式)，請指定參數：
BOARD_TYPE=STM32H745I_DISCO bash execution/build_firmware.sh
```

**終端成功輸出示例**：
```text
[Build] Step 1: Running Headless TouchGFX Code & Asset Generator...
[generate_ui_assets] Generated 7 PNG assets in TouchGFX/assets/images
[tgfx_codegen] Generated TouchGFX C++ code for 2 screen(s), 7 bitmap(s)
[Build] Step 2: Compiling & Linking ARM Cortex-M7 Firmware (Target: STM32H750B_DK)...
==========================================================================
 STM32H7 + TouchGFX Firmware Memory Map Summary (stm32h7_touchgfx.elf)
==========================================================================
 Internal Flash (0x08000000) :     1216 B  (1.19 KB)
 External QSPI  (0x90000000) :    54272 B  (53.00 KB)
 External SDRAM (0xD0000000) :   522240 B  (510.00 KB - 480x272x2x2 FB)
 Intel HEX Image Generated   : build/stm32h7_touchgfx.hex
==========================================================================
[Build] Step 3: Building & Running Native macOS Host Simulator...
[Build] Complete! Artifacts ready: build/stm32h7_touchgfx.elf, build/stm32h7_touchgfx.hex
```

### 2. 燒錄韌體至開發板

確保板子 **CN14** 已連接至 Mac，執行：

```bash
bash execution/flash_board.sh
```

腳本會優先尋找 `STM32_Programmer_CLI`（具備外掛 QSPI Loader `MT25TL01G_*.stldr`），若本機未安裝則自動調用內建之 `pyOCD` 進行 SWD 燒錄。

### 3. 監聽 UART 遙測日誌

STM32H750B-DK 的 STLINK-V3E 內建 Virtual COM Port (VCP)，連接在 MCU 的 `USART3` (`PB10` TX, `PB11` RX)：

```bash
python3 execution/verify_serial.py
```
> 預設以 115200 8N1 自動掃描 `/dev/cu.usbmodem*` 並輸出即時啟動訊息。

---

## 預編譯成品 (Prebuilt Binaries)

專案目錄下的 `prebuilt/` 已隨附最新實測通過之韌體：
- `prebuilt/stm32h7_touchgfx.elf`：含除錯符號與記憶體區段之 ELF 映像檔。
- `prebuilt/stm32h7_touchgfx.hex`：符合 Intel HEX 格式，包含 Internal Flash (`0x08000000`) 與 QSPI (`0x90000000`) 位址。

---

## 與 Google Antigravity Agent 協同開發

在本專案資料夾中，你可以直接向 Antigravity Agent 下達自然語言指令：

> 「請讀取 `AGENTS.md`，幫我把首頁的數值卡片改為即時電力監控儀表，包含電壓、電流與累積功率，並在下方加入一個告警指示條，然後編譯韌體。」

Agent 將自動調用 `touchgfx-ui-autopilot` 技能，更新圖資、C++ 程式碼並執行編譯驗證！
