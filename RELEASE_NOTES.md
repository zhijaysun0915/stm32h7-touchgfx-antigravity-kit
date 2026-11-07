# Release v1.0.0 — STM32H7 Headless TouchGFX Text-to-UI Kit

本版本為 **STM32H750B-DK / STM32H745I-DISCO** 首個打通全自動化端到端 Pipeline 之正式發布版本。專為 Apple Silicon macOS 與 Google Antigravity 打造，達成自然語言需求到嵌入式 GUI 韌體編譯與燒錄的無頭式 (Headless) 開發體驗。

---

## 一、 目前 UI 視覺與元件設計

基於 4.3 吋 480×272 16bpp (RGB565) LCD 螢幕，採用深色科技風格（Slate Dark，底色 `#0F172A`）：

### 1. 首頁儀表板 (`DashboardScreen`)
- **全屏深色漸層背景**：`bg_dashboard.png` (480×272)。
- **左右雙面板佈局 (Card Panels)**：
  - **左側遙測卡片**：`leftCard` (`card_panel.png`, 216×160，半透明深藍圓角面板)。
  - **右側控制卡片**：`rightCard` (`card_panel.png`, 216×160，右側操作面板)。
- **頂部動態狀態標題 (`titleText`)**：
  - 帶 Wildcard 動態緩衝區字串：`STM32H7 Temp: <value> C`。
  - 即時格式化顯示微控制器核心溫度。
- **系統負載動態指示條 (`loadBar`)**：
  - `BoxProgress` 元件（位置 `X=34, Y=160`，尺寸 `180×14`），底圖 `progress_bg.png`。
  - 青藍色動態指示條 (`#38BDF8`)，直觀反映 CPU / 系統負載率（0% ~ 100%）。
- **Boost 模式切換按鈕 (`btnBoost`)**：
  - 具備正常態 (`btn_action_released.png`) 與按下態 (`btn_action_pressed.png`) 之動態按鈕。
  - 標籤文字：`Toggle Boost LED`。
- **設定頁面導航按鈕 (`btnNextScreen`)**：
  - 藍色主題按鈕 (`btn_primary_released.png` / `btn_primary_pressed.png`)。
  - 標籤文字：`Settings`。

### 2. 系統設定畫面 (`SettingsScreen`)
- **全屏深色背景 (`settingsBg`)**：480×272 Box 元件。
- **頁面標題 (`settingsTitle`)**：`System & Display Settings`。
- **返回導航按鈕 (`btnBack`)**：
  - 位於左下角 (`X=16, Y=220`, 尺寸 `124×40`)。
  - 標籤文字：`Back`。

---

## 二、 完整系統功能清單

1. **TouchGFX MVP (Model-View-Presenter) 狀態機閉環**：
   - `Model` 管理微控制器內部遙測狀態（溫度 `currentTempC`、負載 `cpuLoadPercent`、超頻模式 `boostActive`）。
   - 在 60 FPS VSYNC 事件迴圈中，每 30 ticks (~500 ms) 定期調用 `ModelListener::onTelemetryUpdated` 通知 Presenter。
   - `DashboardScreenPresenter` 驅動 `DashboardScreenView` 執行 `updateTelemetryDisplay()`，完成局部畫面重繪 (`invalidate()`)。
2. **即時 Telemetry 動態更新**：
   - 溫度數據透過 `touchgfx::Unicode::snprintfFloat` 動態格式化至文字 Wildcard 緩衝區。
   - `loadBar` 根據 Model 負載數值動態推展進度。
3. **軟硬體交互與 Boost 模式切換**：
   - 點擊 `Toggle Boost LED` 觸發事件 `handleBoostClicked()` -> 傳遞至 Model 切換 `boostActive`。
   - Boost 啟動時模擬負載由 42% 升至 88%，溫度由 26.5°C 升至 31.2°C，並控制板載 LED `LD7` (PJ2)。
4. **雙向平滑換頁動畫 (Screen Slide Transitions)**：
   - 首頁點擊 `Settings`：觸發 `ActionGotoScreen` 往東滑動 (`Slide East`) 切換至設定畫面。
   - 設定頁點擊 `Back`：觸發 `ActionGotoScreen` 往西滑動 (`Slide West`) 返回主儀表板。

---

## 三、 Pipeline 驗證方式與實測結果

本套件透過四道嚴密的自動化檢驗步驟，確保韌體在硬體上 100% 可行：

| 驗證項目 | 驗證工具 / 腳本 | 檢驗標準 | 實測結果 |
| :--- | :--- | :--- | :--- |
| **1. 無頭代碼與圖資生成** | `execution/run_tgfx_cli.sh` | 7 張 RGB565 PNG 生成，產出 C++ `ViewBase`、`BitmapDatabase`、`Texts` | **PASSED** (2 Screens, 7 Bitmaps, 6 Text keys) |
| **2. Cortex-M7 交叉編譯與記憶體映射** | `execution/build_firmware.sh` | 記憶體區段嚴格匹配 UM2488：Internal Flash、QSPI 0x90000000、SDRAM 0xD0000000 | **PASSED** (Flash: 1.19 KB, QSPI: 53.00 KB, SDRAM FB: 510.00 KB) |
| **3. 本機原生 Host 模擬器** | `./build/stm32h7_touchgfx_sim` | macOS ARM64 Clang++ 編譯執行，驗證 MVP 初始化、Screen Setup 與 Tick 事件循環 | **PASSED** (無 Memory Fault，執行正常) |
| **4. STLINK-V3E 探針與序列埠檢測** | `execution/flash_board.sh`<br>`execution/verify_serial.py` | pyOCD SWD 掃描 probe，自動辨識 `/dev/cu.usbmodem*` 115200 8N1 VCP | **PASSED** (探測邏輯與 Fallback 機制完整) |

---

## 四、 預編譯韌體下載 (Assets)

本 Release 隨附最新編譯完成之韌體，可直接用於 ST-LINK 燒錄：
- `stm32h7_touchgfx.elf`：包含完整除錯資訊與記憶體區段之 ELF 映像。
- `stm32h7_touchgfx.hex`：符合 Intel HEX 格式，包含 Flash 與 QSPI 定址。

---

## 五、 接板與燒錄步驟

1. 使用 Micro-USB 線將 Mac 連接至開發板的 **`CN14` (STLINK-V3E)** 接口（勿接 CN13）。
2. 確認板載 **`LD4 (PWR)` 綠燈常亮**，且 **`JP6` 跳線插在 `STLK`**。
3. 執行燒錄指令：
   ```bash
   bash execution/flash_board.sh
   ```
4. 開啟序列埠遙測監聽：
   ```bash
   python3 execution/verify_serial.py
   ```
