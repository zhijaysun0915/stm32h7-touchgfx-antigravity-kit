#!/usr/bin/env python3
"""
Renders pixel-accurate UI mockups and EVM connection diagrams for documentation.
"""
import os
import sys

# Ensure toolchain/pylib is in sys.path
candidates = [
    os.path.expanduser("~/toolchain/pylib"),
    "/Users/jaysun/.gemini/users/user1/toolchain/pylib",
]
for c in candidates:
    if os.path.isdir(c) and c not in sys.path:
        sys.path.insert(0, c)

from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = "TouchGFX/assets/images"
DOCS_DIR = "docs/images"
os.makedirs(DOCS_DIR, exist_ok=True)

def get_font(size):
    try:
        # Try finding standard macOS font
        for path in [
            "/System/Library/Fonts/Helvetica.ttc",
            "/System/Library/Fonts/SFNSMono.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
        ]:
            if os.path.exists(path):
                return ImageFont.truetype(path, size)
    except Exception:
        pass
    return ImageFont.load_default()

def render_dashboard():
    bg = Image.open(f"{ASSETS_DIR}/bg_dashboard.png").convert("RGBA")
    draw = ImageDraw.Draw(bg)
    font_large = get_font(20)
    font_med = get_font(14)
    font_small = get_font(11)

    # 1. Cards
    card = Image.open(f"{ASSETS_DIR}/card_panel.png").convert("RGBA")
    bg.paste(card, (16, 48), card)
    bg.paste(card, (248, 48), card)

    # 2. Title Text
    draw.text((20, 14), "STM32H7 Temp: 26.5 °C", fill=(248, 250, 252, 255), font=font_large)

    # 3. Left Card Content
    draw.text((34, 62), "SYSTEM TELEMETRY", fill=(148, 163, 184, 255), font=font_small)
    draw.text((34, 82), "MCU Core : 480 MHz", fill=(226, 232, 240, 255), font=font_med)
    draw.text((34, 104), "SDRAM FB : Double 16bpp", fill=(226, 232, 240, 255), font=font_med)
    draw.text((34, 126), "CPU Load : 64%", fill=(56, 189, 248, 255), font=font_med)

    # Progress bar
    prog_bg = Image.open(f"{ASSETS_DIR}/progress_bg.png").convert("RGBA")
    bg.paste(prog_bg, (34, 160), prog_bg)
    # Indicator fill (64% of 180 = ~115px)
    draw.rounded_rectangle([36, 162, 36 + 115, 172], radius=3, fill=(56, 189, 248, 255))

    # 4. Right Card Content
    draw.text((264, 62), "HARDWARE CONTROL", fill=(148, 163, 184, 255), font=font_small)
    # Boost button
    btn_boost = Image.open(f"{ASSETS_DIR}/btn_action_released.png").convert("RGBA")
    bg.paste(btn_boost, (264, 104), btn_boost)
    draw.text((290, 116), "Toggle Boost LED", fill=(255, 255, 255, 255), font=font_med)

    # 5. Next Screen Button
    btn_next = Image.open(f"{ASSETS_DIR}/btn_primary_released.png").convert("RGBA")
    bg.paste(btn_next, (340, 220), btn_next)
    draw.text((375, 232), "Settings", fill=(255, 255, 255, 255), font=font_med)

    out_path = f"{DOCS_DIR}/dashboard_screen_preview.png"
    bg.save(out_path)
    print(f"[Render] Dashboard saved: {out_path}")

def render_settings():
    img = Image.new("RGBA", (480, 272), (15, 23, 42, 255))
    draw = ImageDraw.Draw(img)
    font_large = get_font(20)
    font_med = get_font(14)
    font_small = get_font(11)

    # Header
    draw.rectangle([0, 0, 480, 48], fill=(30, 41, 59, 255))
    draw.text((20, 14), "System & Display Settings", fill=(248, 250, 252, 255), font=font_large)

    # Settings Cards / Items
    draw.rounded_rectangle([20, 64, 460, 116], radius=6, fill=(30, 41, 59, 255), outline=(51, 65, 85, 255))
    draw.text((36, 76), "Display Brightness", fill=(226, 232, 240, 255), font=font_med)
    draw.text((36, 96), "PWM Backlight level: 80%", fill=(148, 163, 184, 255), font=font_small)
    # Slider mockup
    draw.rounded_rectangle([260, 84, 430, 96], radius=6, fill=(15, 23, 42, 255))
    draw.rounded_rectangle([260, 84, 396, 96], radius=6, fill=(56, 189, 248, 255))

    draw.rounded_rectangle([20, 128, 460, 180], radius=6, fill=(30, 41, 59, 255), outline=(51, 65, 85, 255))
    draw.text((36, 140), "Power Mode", fill=(226, 232, 240, 255), font=font_med)
    draw.text((36, 160), "LDO Regulator Active (STM32H750B-DK)", fill=(34, 197, 94, 255), font=font_small)
    draw.text((360, 146), "[ LOCKED ]", fill=(148, 163, 184, 255), font=font_small)

    # Back button
    btn_back = Image.open(f"{ASSETS_DIR}/btn_primary_released.png").convert("RGBA")
    img.paste(btn_back, (16, 220), btn_back)
    draw.text((58, 232), "Back", fill=(255, 255, 255, 255), font=font_med)

    out_path = f"{DOCS_DIR}/settings_screen_preview.png"
    img.save(out_path)
    print(f"[Render] Settings saved: {out_path}")

def render_evm_diagram():
    # 800x480 high-contrast schematic layout of STM32H750B-DK
    img = Image.new("RGBA", (840, 520), (15, 23, 42, 255))
    draw = ImageDraw.Draw(img)
    font_title = get_font(22)
    font_large = get_font(15)
    font_med = get_font(12)
    font_bold = get_font(13)

    # Header title
    draw.text((20, 18), "STM32H750B-DK / STM32H745I-DISCO EVM Wiring & Jumper Map", fill=(248, 250, 252, 255), font=font_title)
    draw.text((20, 48), "Reference: STMicroelectronics UM2488 User Manual Rev 10", fill=(148, 163, 184, 255), font=font_med)

    # Board PCB outline
    draw.rounded_rectangle([30, 80, 560, 490], radius=12, fill=(16, 85, 154, 255), outline=(56, 189, 248, 255), width=2)
    draw.text((45, 95), "STM32H750B-DK (TOP VIEW)", fill=(240, 249, 255, 255), font=font_bold)

    # 4.3" LCD Touchscreen on PCB
    draw.rectangle([80, 140, 510, 450], fill=(10, 15, 30, 255), outline=(203, 213, 225, 255), width=2)
    draw.text((210, 280), "4.3\" 480x272 RGB LCD", fill=(248, 250, 252, 255), font=font_large)
    draw.text((230, 305), "(TouchGFX Framebuffer)", fill=(148, 163, 184, 255), font=font_med)

    # Ports on the top edge
    # CN14 STLINK-V3E
    draw.rectangle([60, 70, 140, 95], fill=(234, 88, 12, 255), outline=(255, 255, 255, 255), width=2)
    draw.text((70, 75), "CN14 USB", fill=(255, 255, 255, 255), font=font_med)

    # CN13 OTG_FS
    draw.rectangle([450, 70, 530, 95], fill=(71, 85, 105, 255), outline=(148, 163, 184, 255), width=1)
    draw.text((460, 75), "CN13 OTG", fill=(203, 213, 225, 255), font=font_med)

    # JP6 Jumper
    draw.rectangle([160, 98, 220, 124], fill=(22, 163, 74, 255), outline=(255, 255, 255, 255), width=1)
    draw.text((168, 104), "JP6: STLK", fill=(255, 255, 255, 255), font=font_med)

    # LEDs
    # LD4 PWR
    draw.ellipse([235, 103, 251, 119], fill=(34, 197, 94, 255), outline=(255, 255, 255, 255), width=1)
    draw.text((258, 104), "LD4 (PWR)", fill=(226, 232, 240, 255), font=font_med)

    # LD1 COM
    draw.ellipse([325, 103, 341, 119], fill=(250, 204, 21, 255), outline=(255, 255, 255, 255), width=1)
    draw.text((348, 104), "LD1 (COM)", fill=(226, 232, 240, 255), font=font_med)

    # User LEDs
    draw.ellipse([420, 103, 436, 119], fill=(34, 197, 94, 255))
    draw.text((442, 104), "LD7", fill=(226, 232, 240, 255), font=font_med)

    # Explanations Side Panel
    draw.rounded_rectangle([580, 80, 820, 490], radius=8, fill=(30, 41, 59, 255), outline=(51, 65, 85, 255))
    draw.text((595, 96), "TESTING INSTRUCTIONS", fill=(56, 189, 248, 255), font=font_large)

    instructions = [
        "1. CONNECT PORT [CN14]:",
        "   Use Micro-USB to Mac/PC.",
        "   Enables Power, SWD & VCP.",
        "   DO NOT plug into CN13!",
        "",
        "2. CHECK POWER [LD4]:",
        "   Green LED LD4 must stay ON.",
        "   Ensure JP6 jumper is on STLK.",
        "",
        "3. STLINK STATUS [LD1]:",
        "   Flashes red/green during flash.",
        "   Solid green when enumerated.",
        "",
        "4. USER INTERACTION:",
        "   - Tap 'Toggle Boost LED' on LCD",
        "     to flip User LED LD7 (PJ2).",
        "   - Tap 'Settings' -> Slide East",
        "   - Tap 'Back' -> Slide West"
    ]
    y = 130
    for line in instructions:
        draw.text((595, y), line, fill=(241, 245, 249, 255) if line.startswith(tuple("1234")) else (148, 163, 184, 255), font=font_med)
        y += 22

    # Wire arrow from host
    draw.text((50, 496), "==> Connect USB cable from Host Computer (Mac/PC/Linux) directly to CN14 <==", fill=(251, 146, 60, 255), font=font_med)

    out_path = f"{DOCS_DIR}/evm_wiring_diagram.png"
    img.save(out_path)
    print(f"[Render] EVM diagram saved: {out_path}")

if __name__ == "__main__":
    render_dashboard()
    render_settings()
    render_evm_diagram()
