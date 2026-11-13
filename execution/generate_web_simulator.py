#!/usr/bin/env python3
"""
TouchGFX Web Studio & Visual Layer Editor (480x272)
Features:
  1. AI Text-to-Layers Prompt Engine
  2. Drag & Drop Visual Canvas (Move, Snap)
  3. Layer Hierarchy (Z-Index, Reorder, Add, Delete, Rename)
  4. Asset Manager: Upload custom images & place onto canvas
  5. Property Inspector: X, Y, W, H, Colors, Font Size, Text, Actions
  6. Dual Mode: Edit Mode (WYSIWYG) <-> Play Mode (EVM Simulator)
  7. Two-Way Sync: Exports valid TouchGFX JSON
"""
import base64
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "TouchGFX", "assets", "images")
ARTIFACT_DIR = "/home/antigravity/.gemini/jetski/brain/v1/default/jetski_remote_agents_3p/b9612dd2-3de8-4ae1-a878-41637388e54f"
DOCS_DIR = os.path.join(BASE_DIR, "docs")

assets = {}
asset_filenames = [
    "bg_dashboard.png",
    "btn_action_pressed.png",
    "btn_action_released.png",
    "btn_primary_pressed.png",
    "btn_primary_released.png",
    "card_panel.png",
    "progress_bg.png",
]

for filename in asset_filenames:
    filepath = os.path.join(ASSETS_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            assets[filename] = "data:image/png;base64," + base64.b64encode(f.read()).decode("ascii")

html_template = r"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>TouchGFX Web Studio — 視覺化圖層微調編輯器 & 數位雙生模擬器</title>
  <script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>
  <style>
    .led-glow-green {
      background: #22c55e;
      box-shadow: 0 0 10px #22c55e, 0 0 20px rgba(34, 197, 94, 0.5);
    }
    .led-glow-red {
      background: #ef4444;
      box-shadow: 0 0 10px #ef4444, 0 0 20px rgba(239, 68, 68, 0.5);
    }
    .led-off {
      background: #334155;
    }
    .canvas-screen {
      width: 480px;
      height: 272px;
      position: relative;
      overflow: hidden;
      user-select: none;
    }
    .custom-scroll::-webkit-scrollbar {
      width: 5px;
      height: 5px;
    }
    .custom-scroll::-webkit-scrollbar-thumb {
      background: #475569;
      border-radius: 3px;
    }
    .widget-selected {
      outline: 2px dashed #38bdf8 !important;
      outline-offset: 1px;
    }
  </style>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen p-3 antialiased font-sans">
  <div class="max-w-[1500px] mx-auto space-y-3">

    <!-- Top Navigation & Mode Toolbar -->
    <header class="bg-slate-900 border border-slate-800 rounded-xl p-3 shadow-lg flex flex-wrap items-center justify-between gap-3">
      <div class="flex items-center space-x-3">
        <div class="w-9 h-9 rounded-lg bg-gradient-to-br from-cyan-600 to-blue-700 flex items-center justify-center font-bold text-white shadow">
          TG
        </div>
        <div>
          <div class="flex items-center space-x-2">
            <h1 class="text-base font-bold text-white">TouchGFX Web Studio</h1>
            <span class="px-2 py-0.5 text-[11px] font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 rounded-full">WYSIWYG Layer Editor</span>
            <span class="px-2 py-0.5 text-[11px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded-full">STM32H750B-DK</span>
          </div>
          <p class="text-[11px] text-slate-400">文字需求轉圖層群 • 視覺化拖曳微調 • 自訂圖資上傳 • 階層排序 • 雙生硬體模擬</p>
        </div>
      </div>

      <!-- Mode Selector -->
      <div class="flex items-center bg-slate-950 p-1 rounded-lg border border-slate-800 text-xs font-semibold">
        <button id="modeBtnEdit" class="px-3 py-1.5 rounded-md bg-cyan-600 text-white shadow transition flex items-center space-x-1.5">
          <span>🎨</span>
          <span>編輯微調模式 (Editor)</span>
        </button>
        <button id="modeBtnSim" class="px-3 py-1.5 rounded-md text-slate-400 hover:text-white transition flex items-center space-x-1.5">
          <span>▶️</span>
          <span>執行驗證模式 (Simulator)</span>
        </button>
      </div>

      <!-- Quick Actions -->
      <div class="flex items-center space-x-2">
        <button id="btnSyncToH7" class="px-3 py-1.5 text-xs bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-bold shadow flex items-center space-x-1 transition">
          <span>⚡</span>
          <span>一鍵同步至 STM32H7 韌體</span>
        </button>
        <button id="btnExportJson" class="px-3 py-1.5 text-xs bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700 rounded-lg transition font-mono">
          📄 匯出 JSON
        </button>
      </div>
    </header>

    <!-- Main Workspace: 3 Columns (Layers 3 Cols | Canvas 6 Cols | Inspector 3 Cols) -->
    <div class="grid grid-cols-1 lg:grid-cols-12 gap-3">

      <!-- Left Panel: Layer Hierarchy & Add Component (3 Cols) -->
      <div class="lg:col-span-3 bg-slate-900 border border-slate-800 rounded-xl p-3 shadow-lg flex flex-col h-[700px]">

        <!-- Screen Selector -->
        <div class="flex items-center justify-between pb-2 mb-2 border-b border-slate-800 text-xs">
          <span class="font-bold text-slate-300">畫面切換 (Screen)</span>
          <select id="screenSelect" class="bg-slate-950 text-cyan-400 border border-slate-700 rounded px-2 py-1 text-xs outline-none">
            <option value="DashboardScreen">DashboardScreen (首頁)</option>
            <option value="SettingsScreen">SettingsScreen (設定)</option>
          </select>
        </div>

        <!-- Layer Actions Bar -->
        <div class="grid grid-cols-2 gap-1.5 mb-2">
          <!-- Add Component Dropdown -->
          <div class="relative">
            <button id="btnAddWidgetDropdown" class="w-full px-2 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded text-xs font-medium border border-slate-700 flex items-center justify-between">
              <span>➕ 新增元件</span>
              <span>▾</span>
            </button>
            <div id="addWidgetMenu" class="hidden absolute top-full left-0 mt-1 w-44 bg-slate-800 border border-slate-700 rounded-lg shadow-xl z-50 text-xs py-1">
              <button class="w-full text-left px-3 py-1.5 hover:bg-cyan-600 hover:text-white" onclick="addNewWidget('TextArea')">📝 文字標籤 (TextArea)</button>
              <button class="w-full text-left px-3 py-1.5 hover:bg-cyan-600 hover:text-white" onclick="addNewWidget('ButtonWithLabel')">🔘 互動按鈕 (Button)</button>
              <button class="w-full text-left px-3 py-1.5 hover:bg-cyan-600 hover:text-white" onclick="addNewWidget('Image')">🖼️ 圖示素材 (Image)</button>
              <button class="w-full text-left px-3 py-1.5 hover:bg-cyan-600 hover:text-white" onclick="addNewWidget('BoxProgress')">📊 進度條 (BoxProgress)</button>
              <button class="w-full text-left px-3 py-1.5 hover:bg-cyan-600 hover:text-white" onclick="addNewWidget('Box')">⬛ 幾何色塊 (Box)</button>
            </div>
          </div>

          <!-- Upload Image Button -->
          <label class="px-2 py-1.5 bg-blue-950/60 hover:bg-blue-900/70 border border-blue-700/60 text-blue-300 rounded text-xs font-medium cursor-pointer text-center flex items-center justify-center space-x-1">
            <span>🖼️</span>
            <span>放自訂圖上去</span>
            <input id="imageFileInput" type="file" accept="image/png,image/jpeg,image/webp" class="hidden">
          </label>
        </div>

        <!-- Layer Controls (Z-Index / Reorder) -->
        <div class="flex items-center justify-between py-1 px-2 bg-slate-950 rounded border border-slate-800 mb-2 text-[11px] text-slate-400">
          <span>階層排序 (Z-Index):</span>
          <div class="flex items-center space-x-1">
            <button id="btnLayerTop" title="移至頂層" class="px-1.5 py-0.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded">⏫</button>
            <button id="btnLayerUp" title="上移一層" class="px-1.5 py-0.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded">🔼</button>
            <button id="btnLayerDown" title="下移一層" class="px-1.5 py-0.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded">🔽</button>
            <button id="btnLayerBottom" title="移至底層" class="px-1.5 py-0.5 bg-slate-800 hover:bg-slate-700 text-slate-200 rounded">⏬</button>
            <button id="btnLayerDelete" title="刪除元件" class="px-1.5 py-0.5 bg-rose-950 text-rose-300 hover:bg-rose-900 rounded">🗑️</button>
          </div>
        </div>

        <!-- Layer List (Z-Order: Top to Bottom) -->
        <div class="flex-1 overflow-y-auto custom-scroll space-y-1 pr-1" id="layerListContainer">
          <!-- Dynamic layer items rendered here -->
        </div>

        <!-- Natural Language AI Prompt Box -->
        <div class="mt-2 pt-2 border-t border-slate-800 space-y-1.5">
          <div class="flex items-center justify-between text-xs text-slate-300">
            <span class="font-bold flex items-center space-x-1">
              <span>🤖</span> <span>AI 文字需求生成</span>
            </span>
            <span class="text-[10px] text-slate-500">Natural Language</span>
          </div>
          <div class="relative">
            <textarea id="aiPromptInput" rows="2" placeholder="例：在右上角加一個風速滑桿，或把 Boost 按鈕換成青藍色卡片..." class="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-xs text-slate-200 placeholder-slate-600 focus:outline-none focus:border-cyan-500"></textarea>
            <button id="btnAiGenerate" class="mt-1 w-full py-1 text-xs bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-bold rounded shadow transition">
              ✨ 執行文字生成圖層
            </button>
          </div>
        </div>

      </div>

      <!-- Center Panel: 480x272 Interactive Visual Canvas (6 Cols) -->
      <div class="lg:col-span-6 bg-slate-900 border border-slate-800 rounded-xl p-3 shadow-lg flex flex-col items-center justify-between h-[700px]">

        <!-- Canvas Status Header -->
        <div class="w-full flex items-center justify-between text-xs text-slate-400 px-1 mb-1">
          <div class="flex items-center space-x-2">
            <span id="canvasModeBadge" class="px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-950 text-cyan-400 border border-cyan-800">EDIT MODE (可自由拖曳)</span>
            <span id="canvasCoord" class="font-mono text-slate-400">X: -, Y: -</span>
          </div>
          <div class="flex items-center space-x-3 text-xs">
            <label class="flex items-center space-x-1 cursor-pointer">
              <input id="chkGridSnap" type="checkbox" checked class="accent-cyan-400 rounded">
              <span>網格吸附 (4px)</span>
            </label>
            <span class="font-mono text-slate-500">480 × 272 (16bpp)</span>
          </div>
        </div>

        <!-- Display Bezel Wrapper -->
        <div class="p-3 bg-slate-950 border-4 border-slate-800 rounded-2xl shadow-2xl relative">
          <!-- 480x272 LCD Display Canvas -->
          <div id="lcdDisplayCanvas" class="canvas-screen border border-slate-700/80 rounded shadow-inner bg-slate-900" style="width: 480px; height: 272px;">
            <!-- Components are dynamically positioned here -->
          </div>

          <!-- Bottom Bezel Info & Physical Buttons -->
          <div class="mt-2.5 flex items-center justify-between px-1 text-xs text-slate-400 font-mono">
            <div class="flex items-center space-x-2">
              <button id="hwKeyUser" class="px-2 py-0.5 bg-blue-600 hover:bg-blue-500 text-white rounded text-[11px] font-bold shadow">
                [B1] USER KEY
              </button>
              <button id="hwKeyReset" class="px-2 py-0.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded text-[11px] font-bold border border-slate-700">
                [B2] RESET
              </button>
            </div>
            <div class="text-[11px] text-slate-500">Discovery Kit STM32H750B-DK</div>
          </div>
        </div>

        <!-- Bottom Mode Info / Telemetry Bar -->
        <div class="w-full bg-slate-950 border border-slate-800 rounded-lg p-2.5 flex items-center justify-between text-xs font-mono">
          <div class="flex items-center space-x-3">
            <div class="flex items-center space-x-1.5">
              <div id="ld7Led" class="w-3.5 h-3.5 rounded-full led-off"></div>
              <span class="text-slate-300">LD7 (PJ2):</span>
              <span id="ld7StatusText" class="font-bold text-slate-500">OFF</span>
            </div>
            <div class="text-slate-400">Core Temp: <span id="telemetryTempText" class="text-cyan-400 font-bold">26.5 °C</span></div>
            <div class="text-slate-400">CPU: <span id="telemetryLoadText" class="text-emerald-400 font-bold">64%</span></div>
          </div>
          <div class="text-[11px] text-slate-500">VSYNC: 60 FPS • FMC SDRAM FB: 0xD0000000</div>
        </div>

      </div>

      <!-- Right Panel: Property Inspector (3 Cols) -->
      <div class="lg:col-span-3 bg-slate-900 border border-slate-800 rounded-xl p-3 shadow-lg flex flex-col h-[700px]">

        <div class="pb-2 mb-2 border-b border-slate-800 flex items-center justify-between text-xs">
          <span class="font-bold text-slate-200">元件屬性微調 (Inspector)</span>
          <span id="inspectTypeBadge" class="text-[10px] font-mono px-1.5 py-0.5 bg-slate-800 text-cyan-400 rounded">No Selection</span>
        </div>

        <!-- No Selection Placeholder -->
        <div id="inspectEmptyState" class="flex-1 flex flex-col items-center justify-center text-center p-4 text-slate-500 text-xs">
          <span class="text-3xl mb-2">👆</span>
          <span>請在畫布或左側圖層清單點擊選取元件，即可在此微調座標、尺寸、文字與圖資。</span>
        </div>

        <!-- Selected Widget Properties Form -->
        <div id="inspectForm" class="hidden flex-1 overflow-y-auto custom-scroll space-y-3 pr-1 text-xs">

          <!-- Name & Type -->
          <div class="space-y-1">
            <label class="text-[11px] text-slate-400">元件變數名稱 (Variable Name)</label>
            <input id="propName" type="text" class="w-full bg-slate-950 border border-slate-700 rounded px-2 py-1 text-xs font-mono text-cyan-400 focus:outline-none focus:border-cyan-500">
          </div>

          <!-- Position & Size -->
          <div class="grid grid-cols-2 gap-2">
            <div class="space-y-1">
              <label class="text-[11px] text-slate-400">X 座標 (px)</label>
              <input id="propX" type="number" min="0" max="480" class="w-full bg-slate-950 border border-slate-700 rounded px-2 py-1 text-xs font-mono text-slate-200">
            </div>
            <div class="space-y-1">
              <label class="text-[11px] text-slate-400">Y 座標 (px)</label>
              <input id="propY" type="number" min="0" max="272" class="w-full bg-slate-950 border border-slate-700 rounded px-2 py-1 text-xs font-mono text-slate-200">
            </div>
            <div class="space-y-1">
              <label class="text-[11px] text-slate-400">寬度 W (px)</label>
              <input id="propW" type="number" min="4" max="480" class="w-full bg-slate-950 border border-slate-700 rounded px-2 py-1 text-xs font-mono text-slate-200">
            </div>
            <div class="space-y-1">
              <label class="text-[11px] text-slate-400">高度 H (px)</label>
              <input id="propH" type="number" min="4" max="272" class="w-full bg-slate-950 border border-slate-700 rounded px-2 py-1 text-xs font-mono text-slate-200">
            </div>
          </div>

          <!-- Specific Fields for TextArea / ButtonWithLabel -->
          <div id="groupTextFields" class="space-y-2 pt-2 border-t border-slate-800">
            <div class="space-y-1">
              <label class="text-[11px] text-slate-400">顯示文字 (Text Content)</label>
              <input id="propText" type="text" class="w-full bg-slate-950 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200">
            </div>
            <div class="grid grid-cols-2 gap-2">
              <div class="space-y-1">
                <label class="text-[11px] text-slate-400">文字顏色</label>
                <input id="propTextColor" type="color" value="#ffffff" class="w-full h-7 bg-slate-950 border border-slate-700 rounded cursor-pointer">
              </div>
              <div class="space-y-1">
                <label class="text-[11px] text-slate-400">字型大小 (pt)</label>
                <select id="propFontSize" class="w-full bg-slate-950 border border-slate-700 rounded px-2 py-1 text-xs text-slate-200">
                  <option value="11">11px (Small)</option>
                  <option value="12">12px (Regular)</option>
                  <option value="14">14px (Medium)</option>
                  <option value="18">18px (Large)</option>
                  <option value="24">24px (Title)</option>
                </select>
              </div>
            </div>
          </div>

          <!-- Specific Fields for Image / Button Images -->
          <div id="groupImageFields" class="space-y-2 pt-2 border-t border-slate-800">
            <div class="space-y-1">
              <label class="text-[11px] text-slate-400">所選圖資 (Image Asset)</label>
              <select id="propImageAsset" class="w-full bg-slate-950 border border-slate-700 rounded px-2 py-1 text-xs text-cyan-400">
                <!-- Dynamically populated -->
              </select>
            </div>
            <div class="p-2 bg-slate-950 border border-slate-800 rounded flex items-center justify-center">
              <img id="propImagePreview" src="" class="max-h-16 max-w-full object-contain">
            </div>
          </div>

          <!-- Specific Fields for Box (Color) -->
          <div id="groupBoxFields" class="space-y-2 pt-2 border-t border-slate-800">
            <div class="space-y-1">
              <label class="text-[11px] text-slate-400">背景填色 (Fill Color)</label>
              <input id="propBoxColor" type="color" value="#0f172a" class="w-full h-8 bg-slate-950 border border-slate-700 rounded cursor-pointer">
            </div>
          </div>

          <!-- Specific Fields for Progress -->
          <div id="groupProgressFields" class="space-y-2 pt-2 border-t border-slate-800">
            <div class="space-y-1">
              <label class="text-[11px] text-slate-400">進度數值 (%)</label>
              <input id="propProgress" type="number" min="0" max="100" class="w-full bg-slate-950 border border-slate-700 rounded px-2 py-1 text-xs font-mono text-slate-200">
            </div>
          </div>

          <!-- Specific Fields for Button Actions -->
          <div id="groupActionFields" class="space-y-2 pt-2 border-t border-slate-800">
            <label class="text-[11px] text-slate-400">點擊觸發動作 (Trigger Action)</label>
            <select id="propAction" class="w-full bg-slate-950 border border-slate-700 rounded px-2 py-1 text-xs text-amber-400">
              <option value="none">無 (None)</option>
              <option value="toggleBoost">切換 Boost LED (LD7 / PJ2)</option>
              <option value="gotoSettings">轉場至設定頁 (SlideEast)</option>
              <option value="gotoDashboard">轉場至首頁 (SlideWest)</option>
            </select>
          </div>

        </div>

        <!-- Delete Widget Button -->
        <div id="inspectFooter" class="hidden pt-2 border-t border-slate-800">
          <button id="btnDeleteSelected" class="w-full py-1 text-xs bg-rose-950/70 hover:bg-rose-900 text-rose-300 border border-rose-800/60 rounded font-semibold transition">
            🗑️ 刪除此元件
          </button>
        </div>

      </div>

    </div>

    <!-- Bottom UART Telemetry Terminal & Sync Output -->
    <div class="bg-slate-900 border border-slate-800 rounded-xl p-3 shadow-lg">
      <div class="flex items-center justify-between pb-2 mb-2 border-b border-slate-800 text-xs">
        <div class="flex items-center space-x-2">
          <span class="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
          <span class="font-bold text-slate-300">UART3 Telemetry Terminal (115200 bps PB10/PB11)</span>
        </div>
        <div class="flex items-center space-x-2">
          <button id="btnClearUart" class="text-[11px] text-slate-400 hover:text-slate-200">Clear</button>
          <span class="text-slate-600">|</span>
          <span class="text-slate-400 font-mono text-[11px]">VCP Status: CONNECTED</span>
        </div>
      </div>
      <div id="uartConsole" class="h-28 bg-slate-950 rounded-lg p-2 font-mono text-[11px] text-slate-300 overflow-y-auto custom-scroll space-y-0.5">
        <!-- Logs stream here -->
      </div>
    </div>

  </div>

  <!-- Client-side Logic Script -->
  <script>
    // Embedded Base64 Assets Database
    const ASSETS = __ASSETS_JSON__;

    // Helper: RGB <-> Hex
    function rgbToHex(c) {
      if (!c) return "#ffffff";
      const toHex = (n) => Math.max(0, Math.min(255, n | 0)).toString(16).padStart(2, "0");
      return "#" + toHex(c.Red) + toHex(c.Green) + toHex(c.Blue);
    }

    function hexToRgb(hex) {
      const clean = hex.replace("#", "");
      return {
        Red: parseInt(clean.substring(0, 2), 16) || 0,
        Green: parseInt(clean.substring(2, 4), 16) || 0,
        Blue: parseInt(clean.substring(4, 6), 16) || 0
      };
    }

    // TouchGFX Project Model
    let projectModel = {
      "SelectedColorDepth": 16,
      "Resolution": { "Width": 480, "Height": 272 },
      "StartupScreenName": "DashboardScreen",
      "Screens": [
        {
          "Name": "DashboardScreen",
          "Components": [
            { "Type": "Image", "Name": "bgImage", "X": 0, "Y": 0, "Width": 480, "Height": 272, "RelativeFilename": "bg_dashboard.png" },
            { "Type": "Image", "Name": "leftCard", "X": 16, "Y": 48, "Width": 216, "Height": 160, "RelativeFilename": "card_panel.png" },
            { "Type": "Image", "Name": "rightCard", "X": 248, "Y": 48, "Width": 216, "Height": 160, "RelativeFilename": "card_panel.png" },
            { "Type": "TextArea", "Name": "titleText", "X": 16, "Y": 12, "Width": 320, "Height": 28, "Text": "STM32H7 Temp: 26.5 °C", "Color": { "Red": 248, "Green": 250, "Blue": 252 }, "FontSize": 18 },
            { "Type": "TextArea", "Name": "telemetryLabel", "X": 34, "Y": 62, "Width": 180, "Height": 20, "Text": "SYSTEM TELEMETRY", "Color": { "Red": 148, "Green": 163, "Blue": 184 }, "FontSize": 11 },
            { "Type": "TextArea", "Name": "coreSpeedText", "X": 34, "Y": 86, "Width": 180, "Height": 20, "Text": "MCU Core : 480 MHz", "Color": { "Red": 226, "Green": 232, "Blue": 240 }, "FontSize": 12 },
            { "Type": "TextArea", "Name": "sdramText", "X": 34, "Y": 108, "Width": 180, "Height": 20, "Text": "SDRAM FB : Double 16bpp", "Color": { "Red": 226, "Green": 232, "Blue": 240 }, "FontSize": 12 },
            { "Type": "TextArea", "Name": "loadText", "X": 34, "Y": 130, "Width": 180, "Height": 20, "Text": "CPU Load : 64%", "Color": { "Red": 56, "Green": 189, "Blue": 248 }, "FontSize": 12 },
            { "Type": "BoxProgress", "Name": "loadBar", "X": 34, "Y": 160, "Width": 180, "Height": 14, "FileNameBackground": "progress_bg.png", "Progress": 64 },
            { "Type": "TextArea", "Name": "controlLabel", "X": 264, "Y": 62, "Width": 180, "Height": 20, "Text": "HARDWARE CONTROL", "Color": { "Red": 148, "Green": 163, "Blue": 184 }, "FontSize": 11 },
            { "Type": "ButtonWithLabel", "Name": "btnBoost", "X": 264, "Y": 104, "Width": 184, "Height": 42, "Released": "btn_action_released.png", "Pressed": "btn_action_pressed.png", "Text": "Toggle Boost LED", "Color": { "Red": 255, "Green": 255, "Blue": 255 }, "FontSize": 12, "Action": "toggleBoost" },
            { "Type": "ButtonWithLabel", "Name": "btnNextScreen", "X": 340, "Y": 220, "Width": 124, "Height": 40, "Released": "btn_primary_released.png", "Pressed": "btn_primary_pressed.png", "Text": "Settings >", "Color": { "Red": 255, "Green": 255, "Blue": 255 }, "FontSize": 12, "Action": "gotoSettings" }
          ]
        },
        {
          "Name": "SettingsScreen",
          "Components": [
            { "Type": "Box", "Name": "settingsBg", "X": 0, "Y": 0, "Width": 480, "Height": 272, "Color": { "Red": 15, "Green": 23, "Blue": 42 } },
            { "Type": "Box", "Name": "headerBar", "X": 0, "Y": 0, "Width": 480, "Height": 48, "Color": { "Red": 30, "Green": 41, "Blue": 59 } },
            { "Type": "TextArea", "Name": "settingsTitle", "X": 20, "Y": 14, "Width": 300, "Height": 28, "Text": "System & Display Settings", "Color": { "Red": 248, "Green": 250, "Blue": 252 }, "FontSize": 18 },
            { "Type": "ButtonWithLabel", "Name": "btnBack", "X": 16, "Y": 220, "Width": 124, "Height": 40, "Released": "btn_primary_released.png", "Pressed": "btn_primary_pressed.png", "Text": "< Back", "Color": { "Red": 255, "Green": 255, "Blue": 255 }, "FontSize": 12, "Action": "gotoDashboard" }
          ]
        }
      ]
    };

    // State Variables
    let currentScreenName = "DashboardScreen";
    let selectedWidgetIndex = -1;
    let editorMode = "EDIT"; // "EDIT" or "SIM"
    let boostActive = false;
    let isDragging = false;
    let dragStartX = 0, dragStartY = 0, widgetStartX = 0, widgetStartY = 0;
    let tickCounter = 0;

    // DOM References
    const lcdDisplayCanvas = document.getElementById("lcdDisplayCanvas");
    const layerListContainer = document.getElementById("layerListContainer");
    const screenSelect = document.getElementById("screenSelect");
    const inspectEmptyState = document.getElementById("inspectEmptyState");
    const inspectForm = document.getElementById("inspectForm");
    const inspectFooter = document.getElementById("inspectFooter");
    const inspectTypeBadge = document.getElementById("inspectTypeBadge");
    const uartConsole = document.getElementById("uartConsole");
    const canvasCoord = document.getElementById("canvasCoord");
    const chkGridSnap = document.getElementById("chkGridSnap");
    const ld7Led = document.getElementById("ld7Led");
    const ld7StatusText = document.getElementById("ld7StatusText");

    // Inspector Inputs
    const propName = document.getElementById("propName");
    const propX = document.getElementById("propX");
    const propY = document.getElementById("propY");
    const propW = document.getElementById("propW");
    const propH = document.getElementById("propH");
    const propText = document.getElementById("propText");
    const propTextColor = document.getElementById("propTextColor");
    const propFontSize = document.getElementById("propFontSize");
    const propImageAsset = document.getElementById("propImageAsset");
    const propImagePreview = document.getElementById("propImagePreview");
    const propBoxColor = document.getElementById("propBoxColor");
    const propProgress = document.getElementById("propProgress");
    const propAction = document.getElementById("propAction");

    function getActiveScreen() {
      return projectModel.Screens.find(s => s.Name === currentScreenName);
    }

    function escapeHtml(s) {
      return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    }

    function logUart(tag, text, color = "text-slate-300") {
      const line = document.createElement("div");
      line.className = "flex items-start space-x-1 leading-snug";
      const ts = (tickCounter * 0.0166).toFixed(3).padStart(7, "0");
      line.innerHTML =
        `<span class="text-slate-600">[${ts}]</span> ` +
        `<span class="text-cyan-400 font-bold">[${escapeHtml(tag)}]</span> ` +
        `<span class="${color}">${escapeHtml(text)}</span>`;
      uartConsole.appendChild(line);
      uartConsole.scrollTop = uartConsole.scrollHeight;
    }

    // Populate Image Asset Selectors
    function refreshAssetDropdown() {
      propImageAsset.innerHTML = "";
      for (const fname in ASSETS) {
        const opt = document.createElement("option");
        opt.value = fname;
        opt.textContent = fname;
        propImageAsset.appendChild(opt);
      }
    }

    // Render Canvas & Layers
    function render() {
      const screen = getActiveScreen();
      lcdDisplayCanvas.innerHTML = "";
      layerListContainer.innerHTML = "";

      // Render Canvas Elements (in array order, first is back, last is front)
      screen.Components.forEach((comp, idx) => {
        const el = document.createElement("div");
        el.className = "absolute transition-none";
        el.style.left = comp.X + "px";
        el.style.top = comp.Y + "px";
        el.style.width = comp.Width + "px";
        el.style.height = comp.Height + "px";
        el.dataset.index = idx;

        if (editorMode === "EDIT") {
          el.style.cursor = "move";
          if (idx === selectedWidgetIndex) {
            el.classList.add("widget-selected");
          }
        } else {
          el.style.cursor = (comp.Type === "ButtonWithLabel") ? "pointer" : "default";
        }

        // Render Widget Content
        if (comp.Type === "Image") {
          const img = document.createElement("img");
          img.src = ASSETS[comp.RelativeFilename] || "";
          img.className = "w-full h-full pointer-events-none object-fill";
          el.appendChild(img);
        } else if (comp.Type === "Box") {
          const r = comp.Color?.Red ?? 15;
          const g = comp.Color?.Green ?? 23;
          const b = comp.Color?.Blue ?? 42;
          el.style.backgroundColor = `rgb(${r}, ${g}, ${b})`;
        } else if (comp.Type === "TextArea") {
          el.textContent = comp.Text || "";
          const r = comp.Color?.Red ?? 255;
          const g = comp.Color?.Green ?? 255;
          const b = comp.Color?.Blue ?? 255;
          el.style.color = `rgb(${r}, ${g}, ${b})`;
          el.style.fontSize = (comp.FontSize || 12) + "px";
          el.style.fontWeight = (comp.FontSize >= 16) ? "bold" : "normal";
          el.style.display = "flex";
          el.style.alignItems = "center";
        } else if (comp.Type === "ButtonWithLabel") {
          const img = document.createElement("img");
          img.src = (editorMode === "SIM" && comp._pressed) ? (ASSETS[comp.Pressed] || ASSETS[comp.Released]) : (ASSETS[comp.Released] || "");
          img.className = "w-full h-full pointer-events-none object-fill";
          el.appendChild(img);

          const lbl = document.createElement("span");
          lbl.textContent = comp.Text || "";
          const r = comp.Color?.Red ?? 255;
          const g = comp.Color?.Green ?? 255;
          const b = comp.Color?.Blue ?? 255;
          lbl.style.color = `rgb(${r}, ${g}, ${b})`;
          lbl.style.fontSize = (comp.FontSize || 12) + "px";
          lbl.className = "absolute inset-0 flex items-center justify-center font-bold pointer-events-none";
          el.appendChild(lbl);
        } else if (comp.Type === "BoxProgress") {
          const bgImg = document.createElement("img");
          bgImg.src = ASSETS[comp.FileNameBackground] || "";
          bgImg.className = "w-full h-full pointer-events-none";
          el.appendChild(bgImg);

          const fill = document.createElement("div");
          fill.className = "absolute top-[2px] left-[2px] h-[10px] rounded-sm bg-cyan-400";
          fill.style.width = Math.max(0, Math.round(((comp.Progress || 0) / 100) * (comp.Width - 4))) + "px";
          el.appendChild(fill);
        }

        // Edit Mode Events (Selection & Drag)
        if (editorMode === "EDIT") {
          el.addEventListener("mousedown", (e) => {
            e.stopPropagation();
            selectWidget(idx);
            isDragging = true;
            dragStartX = e.clientX;
            dragStartY = e.clientY;
            widgetStartX = comp.X;
            widgetStartY = comp.Y;
          });
        } else {
          // Sim Mode Button Events
          if (comp.Type === "ButtonWithLabel") {
            el.addEventListener("mousedown", () => {
              comp._pressed = true;
              render();
            });
            el.addEventListener("mouseup", () => {
              comp._pressed = false;
              render();
              triggerButtonAction(comp.Action);
            });
          }
        }

        lcdDisplayCanvas.appendChild(el);
      });

      // Render Layer List (Z-Order: Topmost rendered at top of list)
      const reversed = [...screen.Components].map((c, i) => ({ c, originalIndex: i })).reverse();
      reversed.forEach((item) => {
        const idx = item.originalIndex;
        const comp = item.c;
        const row = document.createElement("div");
        row.className = "flex items-center justify-between p-1.5 rounded cursor-pointer text-xs transition " +
          (idx === selectedWidgetIndex ? "bg-cyan-600/30 border border-cyan-500 text-white font-bold" : "bg-slate-950/60 hover:bg-slate-800 text-slate-300 border border-slate-800/80");

        let icon = "📦";
        if (comp.Type === "TextArea") icon = "📝";
        if (comp.Type === "Image") icon = "🖼️";
        if (comp.Type === "ButtonWithLabel") icon = "🔘";
        if (comp.Type === "BoxProgress") icon = "📊";

        row.innerHTML =
          `<div class="flex items-center space-x-1.5 overflow-hidden">` +
          `<span>${icon}</span>` +
          `<span class="truncate text-[11px]">${escapeHtml(comp.Name)}</span>` +
          `</div>` +
          `<span class="text-[10px] text-slate-500 font-mono">#${idx}</span>`;
        row.addEventListener("click", () => selectWidget(idx));
        layerListContainer.appendChild(row);
      });

      updateInspector();
    }

    // Select Widget
    function selectWidget(idx) {
      selectedWidgetIndex = idx;
      render();
    }

    // Inspector Update
    function updateInspector() {
      const screen = getActiveScreen();
      const comp = screen.Components[selectedWidgetIndex];
      if (!comp) {
        inspectEmptyState.classList.remove("hidden");
        inspectForm.classList.add("hidden");
        inspectFooter.classList.add("hidden");
        inspectTypeBadge.textContent = "No Selection";
        return;
      }

      inspectEmptyState.classList.add("hidden");
      inspectForm.classList.remove("hidden");
      inspectFooter.classList.remove("hidden");
      inspectTypeBadge.textContent = comp.Type;

      propName.value = comp.Name || "";
      propX.value = comp.X;
      propY.value = comp.Y;
      propW.value = comp.Width;
      propH.value = comp.Height;

      // Group visibilities
      document.getElementById("groupTextFields").classList.toggle("hidden", !(comp.Type === "TextArea" || comp.Type === "ButtonWithLabel"));
      document.getElementById("groupImageFields").classList.toggle("hidden", !(comp.Type === "Image" || comp.Type === "ButtonWithLabel"));
      document.getElementById("groupBoxFields").classList.toggle("hidden", comp.Type !== "Box");
      document.getElementById("groupProgressFields").classList.toggle("hidden", comp.Type !== "BoxProgress");
      document.getElementById("groupActionFields").classList.toggle("hidden", comp.Type !== "ButtonWithLabel");

      if (comp.Text !== undefined) propText.value = comp.Text;
      if (comp.Type === "TextArea" || comp.Type === "ButtonWithLabel") {
        propTextColor.value = rgbToHex(comp.Color || { Red: 255, Green: 255, Blue: 255 });
        propFontSize.value = String(comp.FontSize || 12);
      }
      if (comp.Type === "Box") {
        propBoxColor.value = rgbToHex(comp.Color || { Red: 15, Green: 23, Blue: 42 });
      }
      if (comp.Type === "BoxProgress") {
        propProgress.value = comp.Progress ?? 50;
      }
      const assetFile = comp.RelativeFilename || comp.Released;
      if (assetFile) {
        propImageAsset.value = assetFile;
        propImagePreview.src = ASSETS[assetFile] || "";
      }
      if (comp.Action) propAction.value = comp.Action;
    }

    // Drag move on canvas
    window.addEventListener("mousemove", (e) => {
      const rect = lcdDisplayCanvas.getBoundingClientRect();
      const curX = Math.round(e.clientX - rect.left);
      const curY = Math.round(e.clientY - rect.top);
      if (curX >= 0 && curX <= 480 && curY >= 0 && curY <= 272) {
        canvasCoord.textContent = `X: ${curX}, Y: ${curY}`;
      }

      if (!isDragging || selectedWidgetIndex < 0) return;
      const screen = getActiveScreen();
      const comp = screen.Components[selectedWidgetIndex];
      if (!comp) return;

      const dx = e.clientX - dragStartX;
      const dy = e.clientY - dragStartY;

      let newX = widgetStartX + dx;
      let newY = widgetStartY + dy;

      if (chkGridSnap.checked) {
        newX = Math.round(newX / 4) * 4;
        newY = Math.round(newY / 4) * 4;
      }

      // Boundary clamp
      newX = Math.max(0, Math.min(480 - comp.Width, newX));
      newY = Math.max(0, Math.min(272 - comp.Height, newY));

      comp.X = newX;
      comp.Y = newY;
      propX.value = newX;
      propY.value = newY;
      render();
    });

    window.addEventListener("mouseup", () => {
      if (isDragging) {
        isDragging = false;
        const comp = getActiveScreen().Components[selectedWidgetIndex];
        if (comp) {
          logUart("EDIT", `Widget moved: ${comp.Name} -> (${comp.X}, ${comp.Y})`);
        }
      }
    });

    // Inspector Bindings
    propName.addEventListener("change", (e) => {
      const comp = getActiveScreen().Components[selectedWidgetIndex];
      if (comp) { comp.Name = e.target.value; render(); }
    });
    propX.addEventListener("input", (e) => {
      const comp = getActiveScreen().Components[selectedWidgetIndex];
      if (comp) { comp.X = parseInt(e.target.value, 10) || 0; render(); }
    });
    propY.addEventListener("input", (e) => {
      const comp = getActiveScreen().Components[selectedWidgetIndex];
      if (comp) { comp.Y = parseInt(e.target.value, 10) || 0; render(); }
    });
    propW.addEventListener("input", (e) => {
      const comp = getActiveScreen().Components[selectedWidgetIndex];
      if (comp) { comp.Width = parseInt(e.target.value, 10) || 10; render(); }
    });
    propH.addEventListener("input", (e) => {
      const comp = getActiveScreen().Components[selectedWidgetIndex];
      if (comp) { comp.Height = parseInt(e.target.value, 10) || 10; render(); }
    });
    propText.addEventListener("input", (e) => {
      const comp = getActiveScreen().Components[selectedWidgetIndex];
      if (comp) { comp.Text = e.target.value; render(); }
    });
    propTextColor.addEventListener("input", (e) => {
      const comp = getActiveScreen().Components[selectedWidgetIndex];
      if (comp) { comp.Color = hexToRgb(e.target.value); render(); }
    });
    propFontSize.addEventListener("change", (e) => {
      const comp = getActiveScreen().Components[selectedWidgetIndex];
      if (comp) { comp.FontSize = parseInt(e.target.value, 10) || 12; render(); }
    });
    propBoxColor.addEventListener("input", (e) => {
      const comp = getActiveScreen().Components[selectedWidgetIndex];
      if (comp) { comp.Color = hexToRgb(e.target.value); render(); }
    });
    propProgress.addEventListener("input", (e) => {
      const comp = getActiveScreen().Components[selectedWidgetIndex];
      if (comp) { comp.Progress = Math.max(0, Math.min(100, parseInt(e.target.value, 10) || 0)); render(); }
    });
    propImageAsset.addEventListener("change", (e) => {
      const comp = getActiveScreen().Components[selectedWidgetIndex];
      if (comp) {
        if (comp.Type === "ButtonWithLabel") {
          comp.Released = e.target.value;
        } else {
          comp.RelativeFilename = e.target.value;
        }
        propImagePreview.src = ASSETS[e.target.value] || "";
        render();
      }
    });
    propAction.addEventListener("change", (e) => {
      const comp = getActiveScreen().Components[selectedWidgetIndex];
      if (comp) { comp.Action = e.target.value; render(); }
    });

    // Layer Hierarchy (Z-Order) Controls
    document.getElementById("btnLayerTop").addEventListener("click", () => {
      if (selectedWidgetIndex < 0) return;
      const comps = getActiveScreen().Components;
      const item = comps.splice(selectedWidgetIndex, 1)[0];
      comps.push(item);
      selectedWidgetIndex = comps.length - 1;
      render();
      logUart("LAYER", `Moved ${item.Name} to TOP layer`);
    });
    document.getElementById("btnLayerUp").addEventListener("click", () => {
      const comps = getActiveScreen().Components;
      if (selectedWidgetIndex < 0 || selectedWidgetIndex >= comps.length - 1) return;
      const temp = comps[selectedWidgetIndex];
      comps[selectedWidgetIndex] = comps[selectedWidgetIndex + 1];
      comps[selectedWidgetIndex + 1] = temp;
      selectedWidgetIndex++;
      render();
    });
    document.getElementById("btnLayerDown").addEventListener("click", () => {
      const comps = getActiveScreen().Components;
      if (selectedWidgetIndex <= 0) return;
      const temp = comps[selectedWidgetIndex];
      comps[selectedWidgetIndex] = comps[selectedWidgetIndex - 1];
      comps[selectedWidgetIndex - 1] = temp;
      selectedWidgetIndex--;
      render();
    });
    document.getElementById("btnLayerBottom").addEventListener("click", () => {
      if (selectedWidgetIndex < 0) return;
      const comps = getActiveScreen().Components;
      const item = comps.splice(selectedWidgetIndex, 1)[0];
      comps.unshift(item);
      selectedWidgetIndex = 0;
      render();
      logUart("LAYER", `Moved ${item.Name} to BOTTOM layer`);
    });
    document.getElementById("btnLayerDelete").addEventListener("click", deleteSelectedWidget);
    document.getElementById("btnDeleteSelected").addEventListener("click", deleteSelectedWidget);

    function deleteSelectedWidget() {
      const comps = getActiveScreen().Components;
      if (selectedWidgetIndex >= 0 && selectedWidgetIndex < comps.length) {
        const name = comps[selectedWidgetIndex].Name;
        comps.splice(selectedWidgetIndex, 1);
        selectedWidgetIndex = -1;
        render();
        logUart("LAYER", `Deleted component: ${name}`, "text-rose-400");
      }
    }

    // Add Widget Function
    window.addNewWidget = function(type) {
      document.getElementById("addWidgetMenu").classList.add("hidden");
      const comps = getActiveScreen().Components;
      const count = comps.length + 1;
      let newComp = {};
      if (type === "TextArea") {
        newComp = { "Type": "TextArea", "Name": "customText" + count, "X": 100, "Y": 100, "Width": 160, "Height": 28, "Text": "New Label", "FontSize": 14, "Color": { "Red": 255, "Green": 255, "Blue": 255 } };
      } else if (type === "ButtonWithLabel") {
        newComp = { "Type": "ButtonWithLabel", "Name": "customBtn" + count, "X": 120, "Y": 120, "Width": 124, "Height": 40, "Released": "btn_primary_released.png", "Pressed": "btn_primary_pressed.png", "Text": "Click Me", "Color": { "Red": 255, "Green": 255, "Blue": 255 }, "FontSize": 12, "Action": "none" };
      } else if (type === "Image") {
        newComp = { "Type": "Image", "Name": "customImg" + count, "X": 50, "Y": 50, "Width": 80, "Height": 80, "RelativeFilename": "btn_action_released.png" };
      } else if (type === "Box") {
        newComp = { "Type": "Box", "Name": "customBox" + count, "X": 40, "Y": 40, "Width": 120, "Height": 80, "Color": { "Red": 30, "Green": 41, "Blue": 59 } };
      } else if (type === "BoxProgress") {
        newComp = { "Type": "BoxProgress", "Name": "customProg" + count, "X": 60, "Y": 180, "Width": 180, "Height": 14, "FileNameBackground": "progress_bg.png", "Progress": 50 };
      }
      comps.push(newComp);
      selectedWidgetIndex = comps.length - 1;
      render();
      logUart("LAYER", `Added new ${type}: ${newComp.Name}`, "text-emerald-400");
    };

    document.getElementById("btnAddWidgetDropdown").addEventListener("click", () => {
      document.getElementById("addWidgetMenu").classList.toggle("hidden");
    });

    // Custom Image Upload Handler ("放圖上去")
    document.getElementById("imageFileInput").addEventListener("change", (e) => {
      const file = e.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = function(evt) {
        const b64 = evt.target.result;
        const cleanName = file.name.replace(/[^a-zA-Z0-9._-]/g, "_");
        ASSETS[cleanName] = b64;
        refreshAssetDropdown();

        // Auto add as Image component
        const comps = getActiveScreen().Components;
        const newImg = {
          "Type": "Image",
          "Name": cleanName.split(".")[0],
          "X": 80,
          "Y": 80,
          "Width": 100,
          "Height": 80,
          "RelativeFilename": cleanName
        };
        comps.push(newImg);
        selectedWidgetIndex = comps.length - 1;
        render();
        logUart("ASSET", `Custom image uploaded & added: ${cleanName}`, "text-emerald-400");
      };
      reader.readAsDataURL(file);
    });

    // Trigger Button Actions in Sim Mode
    function triggerButtonAction(act) {
      if (act === "toggleBoost") {
        boostActive = !boostActive;
        ld7Led.className = "w-3.5 h-3.5 rounded-full " + (boostActive ? "led-glow-green" : "led-off");
        ld7StatusText.textContent = boostActive ? "ON (PJ2)" : "OFF";
        ld7StatusText.className = "font-bold " + (boostActive ? "text-emerald-400" : "text-slate-500");
        const tempVal = boostActive ? 31.2 : 26.5;
        const loadVal = boostActive ? 88 : 42;
        document.getElementById("telemetryTempText").textContent = tempVal + " °C";
        document.getElementById("telemetryLoadText").textContent = loadVal + "%";

        const dash = projectModel.Screens.find(s => s.Name === "DashboardScreen");
        if (dash) {
          const titleW = dash.Components.find(c => c.Name === "titleText");
          const loadW = dash.Components.find(c => c.Name === "loadText");
          const barW = dash.Components.find(c => c.Name === "loadBar");
          if (titleW) titleW.Text = `STM32H7 Temp: ${tempVal} °C`;
          if (loadW) loadW.Text = `CPU Load : ${loadVal}%`;
          if (barW) barW.Progress = loadVal;
          render();
        }

        logUart("HAL", `GPIO_PinWrite(PJ2, ${boostActive ? "1" : "0"}) -> Boost LED LD7 ${boostActive ? "ON" : "OFF"}`, "text-emerald-400");
      } else if (act === "gotoSettings") {
        currentScreenName = "SettingsScreen";
        screenSelect.value = "SettingsScreen";
        selectedWidgetIndex = -1;
        render();
        logUart("VIEW", "Transition to SettingsScreen (SlideEast)", "text-amber-400");
      } else if (act === "gotoDashboard") {
        currentScreenName = "DashboardScreen";
        screenSelect.value = "DashboardScreen";
        selectedWidgetIndex = -1;
        render();
        logUart("VIEW", "Transition to DashboardScreen (SlideWest)", "text-amber-400");
      }
    }

    // Mode Toggle
    document.getElementById("modeBtnEdit").addEventListener("click", () => {
      editorMode = "EDIT";
      document.getElementById("modeBtnEdit").className = "px-3 py-1.5 rounded-md bg-cyan-600 text-white shadow transition flex items-center space-x-1.5";
      document.getElementById("modeBtnSim").className = "px-3 py-1.5 rounded-md text-slate-400 hover:text-white transition flex items-center space-x-1.5";
      document.getElementById("canvasModeBadge").textContent = "EDIT MODE (可自由拖曳)";
      document.getElementById("canvasModeBadge").className = "px-2 py-0.5 rounded text-[10px] font-bold bg-cyan-950 text-cyan-400 border border-cyan-800";
      render();
    });
    document.getElementById("modeBtnSim").addEventListener("click", () => {
      editorMode = "SIM";
      selectedWidgetIndex = -1;
      document.getElementById("modeBtnSim").className = "px-3 py-1.5 rounded-md bg-emerald-600 text-white shadow transition flex items-center space-x-1.5";
      document.getElementById("modeBtnEdit").className = "px-3 py-1.5 rounded-md text-slate-400 hover:text-white transition flex items-center space-x-1.5";
      document.getElementById("canvasModeBadge").textContent = "SIMULATOR MODE (即時觸發與硬體聯動)";
      document.getElementById("canvasModeBadge").className = "px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-950 text-emerald-400 border border-emerald-800";
      render();
    });

    // Screen Select
    screenSelect.addEventListener("change", (e) => {
      currentScreenName = e.target.value;
      selectedWidgetIndex = -1;
      render();
    });

    // Physical Buttons
    document.getElementById("hwKeyUser").addEventListener("click", () => {
      logUart("EXTI", "Physical User Key [B1] Pressed", "text-cyan-400");
      triggerButtonAction("toggleBoost");
    });
    document.getElementById("hwKeyReset").addEventListener("click", () => {
      logUart("PWR", "Hardware Reset Key [B2] Pressed! Rebooting...", "text-rose-400");
      boostActive = true;
      triggerButtonAction("toggleBoost");
    });

    // Export JSON
    document.getElementById("btnExportJson").addEventListener("click", () => {
      const jsonStr = JSON.stringify(projectModel, null, 2);
      if (navigator.clipboard) navigator.clipboard.writeText(jsonStr);
      alert("TouchGFX JSON 專案規格已複製至剪貼簿！");
      logUart("EXPORT", "JSON Specification exported to clipboard");
    });

    // Sync to STM32H7 Button
    document.getElementById("btnSyncToH7").addEventListener("click", () => {
      const jsonStr = JSON.stringify(projectModel, null, 2);
      if (navigator.clipboard) navigator.clipboard.writeText(jsonStr);
      alert("✨ 規格已鎖定！\n請回到 Antigravity 對話框告訴我：『我已完成 UI 調整，請套用此規格並編譯 STM32H7』，我將為您執行自動代碼生成與 ARM 交叉編譯！");
    });

    // AI Prompt Mockup Handler
    document.getElementById("btnAiGenerate").addEventListener("click", () => {
      const prompt = document.getElementById("aiPromptInput").value.trim();
      if (!prompt) return;
      logUart("AI", "Processing prompt: " + prompt, "text-cyan-400");
      const comps = getActiveScreen().Components;
      const count = comps.length + 1;
      comps.push({
        "Type": "TextArea",
        "Name": "aiWidget" + count,
        "X": 20,
        "Y": 180,
        "Width": 200,
        "Height": 30,
        "Text": "AI: " + prompt.slice(0, 15),
        "Color": { "Red": 56, "Green": 189, "Blue": 248 },
        "FontSize": 14
      });
      selectedWidgetIndex = comps.length - 1;
      render();
      document.getElementById("aiPromptInput").value = "";
    });

    // Clear UART
    document.getElementById("btnClearUart").addEventListener("click", () => {
      uartConsole.innerHTML = "";
    });

    // Simulator Tick
    setInterval(() => {
      tickCounter++;
    }, 16.66);

    // Initial Setup
    refreshAssetDropdown();
    render();
    logUart("BOOT", "TouchGFX Web Studio v4.24 initialized (480x272 16bpp)");
  </script>
</body>
</html>
"""

html_code = html_template.replace("__ASSETS_JSON__", json.dumps(assets))

# Write to docs/touchgfx_web_simulator.html and docs/index.html for GitHub Pages
for fname in ["touchgfx_web_simulator.html", "index.html"]:
    out_path = os.path.join(DOCS_DIR, fname)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_code)
    print(f"[Generate] Saved to: {out_path}")

if os.path.isdir(ARTIFACT_DIR):
    artifact_out = os.path.join(ARTIFACT_DIR, "touchgfx_web_simulator.html")
    with open(artifact_out, "w", encoding="utf-8") as f:
        f.write(html_code)
    print(f"[Generate] Saved artifact to: {artifact_out}")
