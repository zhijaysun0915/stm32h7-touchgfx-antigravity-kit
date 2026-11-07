---
name: touchgfx-ui-autopilot
description: Translate natural-language UI requirements into TouchGFX Designer (.touchgfx JSON), text database (texts.xml), procedural UI PNG assets, and C++ MVP (Model-View-Presenter) code for STM32H745I-DISCO and STM32H750B-DK (480x272 RGB LCD). Use whenever the user asks to design, modify, add screens, widgets, animations, or interactions to the STM32 TouchGFX UI from text descriptions.
---

# TouchGFX UI Autopilot Skill (Text-to-Embedded-GUI)

This skill enables Google Antigravity to act as a headless **TouchGFX Designer + Embedded C++ GUI Engineer** on macOS. The user only provides text requirements, and the agent handles asset creation, `.touchgfx` JSON manipulation, code generation, C++ logic, compilation, and flashing.

## 1. Display & Canvas Constraints (UM2488)
- **Resolution**: `480` (Width) × `272` (Height) pixels (`RK043FN48H` / `RK043FN88H` 4.3" RGB capacitive touch LCD).
- **Coordinate System**: Origin `(0, 0)` is Top-Left. Every widget must satisfy `0 <= X < 480`, `0 <= Y < 272`, `X + Width <= 480`, `Y + Height <= 272`.
- **Color Depth**: `16` bpp (RGB565, default high-speed DMA2D) or `24` bpp (RGB888).

## 2. How to Edit `TouchGFX/STM32H7_App.touchgfx` (JSON Schema)

TouchGFX Designer stores the entire UI layout in `TouchGFX/STM32H7_App.touchgfx`. You can add or modify screens, widgets, and interactions directly in this JSON file!

### Screen Structure
```json
{
  "Name": "DashboardScreen",
  "Components": [
    {
      "Type": "Box",
      "Name": "bgBox",
      "Width": 480,
      "Height": 272,
      "Color": { "Red": 15, "Green": 23, "Blue": 42 }
    },
    {
      "Type": "Image",
      "Name": "cardBg",
      "X": 16,
      "Y": 48,
      "Width": 216,
      "Height": 160,
      "RelativeFilename": "card_panel.png"
    },
    {
      "Type": "TextArea",
      "Name": "titleText",
      "X": 20,
      "Y": 12,
      "Width": 280,
      "Height": 28,
      "TextId": "T_DASHBOARD_TITLE",
      "TextRotation": "0",
      "Color": { "Red": 248, "Green": 250, "Blue": 252 },
      "AutoSize": false,
      "Wildcard1": {
        "TextId": "T_TEMP_DEFAULT",
        "UseBuffer": true,
        "BufferSize": 16
      }
    },
    {
      "Type": "ButtonWithLabel",
      "Name": "btnNextScreen",
      "X": 340,
      "Y": 220,
      "Width": 124,
      "Height": 40,
      "Pressed": "btn_primary_pressed.png",
      "Released": "btn_primary_released.png",
      "TextId": "T_BTN_NEXT",
      "ReleasedColor": { "Red": 255, "Green": 255, "Blue": 255 },
      "PressedColor": { "Red": 200, "Green": 230, "Blue": 255 },
      "TextRotation": "0"
    },
    {
      "Type": "BoxProgress",
      "Name": "loadBar",
      "X": 24,
      "Y": 180,
      "Width": 180,
      "Height": 14,
      "Color": { "Red": 56, "Green": 189, "Blue": 248 },
      "Direction": "Right",
      "FileNameBackground": "progress_bg.png",
      "IndicatorPositionX": 0,
      "IndicatorPositionY": 0,
      "IndicatorPositionWidth": 180,
      "IndicatorPositionHeight": 14,
      "ProgressRangeMin": 0,
      "ProgressRangeMax": 100,
      "ProgressRangeSteps": 100,
      "ProgressInitialValue": 65
    }
  ],
  "Interactions": [
    {
      "InteractionName": "OnNextClicked",
      "Trigger": {
        "Type": "TriggerClicked",
        "TriggerComponent": "btnNextScreen"
      },
      "Action": {
        "Type": "ActionGotoScreen",
        "ScreenTransitionType": "ScreenTransitionSlide",
        "ScreenTransitionDirection": "East",
        "ActionComponent": "SettingsScreen"
      }
    },
    {
      "InteractionName": "OnActionTriggered",
      "Trigger": {
        "Type": "TriggerClicked",
        "TriggerComponent": "btnAction"
      },
      "Action": {
        "Type": "ActionCustom",
        "FunctionName": "handleActionClicked"
      }
    }
  ]
}
```

### Supported Component Types in `execution/tgfx_codegen.py` & `tgfx.exe`
1. `Box`: Solid rectangle (`X`, `Y`, `Width`, `Height`, `Color: {Red, Green, Blue}`, `Alpha`).
2. `BoxWithBorder`: Rectangle with border (`Color`, `BorderColor`, `BorderSize`, `Alpha`).
3. `Image`: Bitmap widget (`X`, `Y`, `Width`, `Height`, `RelativeFilename`, `Alpha`).
4. `TextArea`: Static or dynamic wildcard text (`X`, `Y`, `Width`, `Height`, `TextId`, `Color`, `Wildcard1: {TextId, UseBuffer, BufferSize}`).
5. `Button`: Image button (`X`, `Y`, `Width`, `Height`, `Pressed`, `Released`).
6. `ButtonWithLabel`: Button with text overlay (`Pressed`, `Released`, `TextId`, `ReleasedColor`, `PressedColor`).
7. `ToggleButton`: Two-state toggle (`Pressed`, `Released`).
8. `Slider`: Interactive value slider (`BackgroundUnselected`, `BackgroundSelected`, `Indicator`, `ValueMin`, `ValueMax`, `InitValue`).
9. `BoxProgress` / `LineProgress`: Progress indicator (`ProgressRangeMin`, `ProgressRangeMax`, `ProgressInitialValue`, `Color`).
10. `DynamicGraph`: Real-time scrolling data plot (`DataPointCount`, `GraphRangeMinY`, `GraphRangeMaxY`, `Color`).

## 3. Managing Text Resources (`TouchGFX/assets/texts/texts.xml`)

Every `TextId` used in `.touchgfx` MUST have a matching `<Text Id="...">` entry in `TouchGFX/assets/texts/texts.xml`:
```xml
<?xml version="1.0" encoding="utf-8"?>
<TextDatabase xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="texts.xsd" Version="4.24.0">
  <Languages>
    <Language Id="GB" />
  </Languages>
  <Texts>
    <TextGroup Id="Unsorted">
      <Text Id="T_DASHBOARD_TITLE" Alignment="Left" TypographyId="Large">
        <Translation Language="GB">System Temp: &lt;value&gt; C</Translation>
      </Text>
      <Text Id="T_TEMP_DEFAULT" Alignment="Left" TypographyId="Large">
        <Translation Language="GB">25.4</Translation>
      </Text>
      <Text Id="T_BTN_NEXT" Alignment="Center" TypographyId="Default">
        <Translation Language="GB">Settings</Translation>
      </Text>
    </TextGroup>
  </Texts>
  <Typographies>
    <Typography Id="Default" Font="verdana.ttf" Size="16" Bpp="4" WildcardCharacterRanges="0x20-0x7E" />
    <Typography Id="Large" Font="verdana.ttf" Size="24" Bpp="4" WildcardCharacterRanges="0x20-0x7E" />
    <Typography Id="Small" Font="verdana.ttf" Size="12" Bpp="4" WildcardCharacterRanges="0x20-0x7E" />
  </Typographies>
</TextDatabase>
```

## 4. Generating UI Assets via Python (`execution/generate_ui_assets.py`)

Before running `execution/run_tgfx_cli.sh`, generate all PNG files referenced in `RelativeFilename`, `Pressed`, or `Released` using `execution/generate_ui_assets.py`:
- Pass a JSON manifest (`directives/ui_assets_manifest.json`) defining cards, gradients, rounded buttons, and icons, then run:
  ```bash
  python3 execution/generate_ui_assets.py --manifest directives/ui_assets_manifest.json
  ```

## 5. Writing C++ MVP Logic (`TouchGFX/gui/`)

- **View (`TouchGFX/gui/src/<screen>_screen/<Screen>View.cpp`)**:
  - Update dynamic wildcard texts using:
    ```cpp
    Unicode::snprintfFloat(titleTextBuffer, TITLETEXT_SIZE, "%.1f", currentTemp);
    titleText.invalidate();
    ```
  - Update progress bars or graphs:
    ```cpp
    loadBar.setValue(cpuLoadPercent);
    loadBar.invalidate();
    ```
- **Presenter (`TouchGFX/gui/src/<screen>_screen/<Screen>Presenter.cpp`)**:
  - Receives hardware/sensor updates from `ModelListener` and forwards them to `view.updateSensorValue(...)`.
- **Model (`TouchGFX/gui/src/model/Model.cpp`)**:
  - `Model::tick()` runs at 60 Hz (every VSYNC ~16.6 ms). Poll hardware queues, ADC/I2C sensors, or simulated telemetry here and notify `modelListener`.
