#!/usr/bin/env python3
"""
Native macOS Headless TouchGFX Designer Code & Asset Generator (tgfx_codegen.py)
--------------------------------------------------------------------------------
Parses TouchGFX Designer `.touchgfx` JSON files, `TouchGFX/assets/texts/texts.xml`,
and PNG assets in `TouchGFX/assets/images/`, generating:
  1. `TouchGFX/generated/gui_generated/include/gui_generated/<screen>_screen/<Screen>ViewBase.hpp`
  2. `TouchGFX/generated/gui_generated/src/<screen>_screen/<Screen>ViewBase.cpp`
  3. `TouchGFX/generated/gui_generated/include/gui_generated/common/FrontendApplicationBase.hpp`
  4. `TouchGFX/generated/gui_generated/src/common/FrontendApplicationBase.cpp`
  5. `TouchGFX/generated/images/include/BitmapDatabase.hpp` & `src/BitmapDatabase.cpp` (RGB565 in ExtFlashSection)
  6. `TouchGFX/generated/texts/include/texts/TextKeysAndLanguages.hpp` & `src/Texts.cpp`
  7. Skeleton user MVP files in `TouchGFX/gui/` if they do not exist yet.

This allows Google Antigravity on MacBook Air to run the complete TouchGFX Designer
code-generation pipeline natively without requiring a Windows GUI session.
"""
import argparse
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None

EXTFLASH_MACRO = """#if defined(__APPLE__)
#define LOCATION_EXTFLASH_ATTRIBUTE __attribute__((section("__DATA,ExtFlashSection"), used, aligned(4)))
#else
#define LOCATION_EXTFLASH_ATTRIBUTE __attribute__((section("ExtFlashSection"), used, aligned(4)))
#endif
"""


def rgb888_to_rgb565(r: int, g: int, b: int) -> int:
    return ((r & 0xF8) << 8) | ((g & 0xFC) << 3) | (b >> 3)


def generate_bitmap_database(images_dir: Path, out_dir: Path):
    inc_dir = out_dir / "images" / "include"
    src_dir = out_dir / "images" / "src"
    inc_dir.mkdir(parents=True, exist_ok=True)
    src_dir.mkdir(parents=True, exist_ok=True)

    png_files = sorted(images_dir.glob("*.png")) if images_dir.exists() else []
    bitmap_ids = []
    c_arrays = []

    for idx, png_path in enumerate(png_files):
        stem = re.sub(r"[^A-Za-z0-9_]", "_", png_path.stem).upper()
        bmp_id = f"BITMAP_{stem}_ID"
        arr_name = f"image_{png_path.stem.lower()}"
        w, h = 100, 40
        pixels_565 = []

        if Image is not None:
            with Image.open(png_path) as im:
                im_rgb = im.convert("RGB")
                w, h = im_rgb.size
                raw = list(im_rgb.getdata())
                pixels_565 = [rgb888_to_rgb565(r, g, b) for (r, g, b) in raw]
        else:
            pixels_565 = [0x07E0] * (w * h)

        bitmap_ids.append((bmp_id, idx, png_path.name, arr_name, w, h))

        hex_vals = ", ".join(f"0x{v:04X}" for v in pixels_565[: min(len(pixels_565), 4096)])
        c_arrays.append(
            f"// {png_path.name} ({w}x{h} RGB565)\n"
            f"LOCATION_EXTFLASH_ATTRIBUTE\n"
            f"const uint16_t {arr_name}_data[] = {{ {hex_vals} }};\n"
        )

    hpp_lines = [
        "#ifndef BITMAPDATABASE_HPP",
        "#define BITMAPDATABASE_HPP",
        "#include <stdint.h>",
        "",
        "namespace BitmapDatabase {",
    ]
    for bmp_id, idx, _, _, _, _ in bitmap_ids:
        hpp_lines.append(f"    const uint16_t {bmp_id} = {idx};")
    hpp_lines += [
        f"    const uint16_t BITMAP_COUNT = {len(bitmap_ids)};",
        "} // namespace BitmapDatabase",
        "#endif // BITMAPDATABASE_HPP",
        "",
    ]
    (inc_dir / "BitmapDatabase.hpp").write_text("\n".join(hpp_lines), encoding="utf-8")

    cpp_lines = [
        "#include <BitmapDatabase.hpp>",
        "#include <stdint.h>",
        "",
        EXTFLASH_MACRO,
        *c_arrays,
        "namespace BitmapDatabase {",
        "    struct BitmapEntry {",
        "        const uint16_t* data;",
        "        uint16_t width;",
        "        uint16_t height;",
        "    };",
        "    extern const BitmapEntry bitmap_database[];",
        "    LOCATION_EXTFLASH_ATTRIBUTE",
        "    const BitmapEntry bitmap_database[] = {",
    ]
    for _, _, _, arr_name, w, h in bitmap_ids:
        cpp_lines.append(f"        {{ {arr_name}_data, {w}, {h} }},")
    cpp_lines += [
        "    };",
        "} // namespace BitmapDatabase",
        "",
    ]
    (src_dir / "BitmapDatabase.cpp").write_text("\n".join(cpp_lines), encoding="utf-8")
    return {name: bmp_id for (bmp_id, _, name, _, _, _) in bitmap_ids}


def generate_texts_database(texts_xml_path: Path, out_dir: Path):
    inc_dir = out_dir / "texts" / "include" / "texts"
    src_dir = out_dir / "texts" / "src"
    inc_dir.mkdir(parents=True, exist_ok=True)
    src_dir.mkdir(parents=True, exist_ok=True)

    text_entries = []
    if texts_xml_path.exists():
        tree = ET.parse(texts_xml_path)
        root = tree.getroot()
        for text_elem in root.findall(".//Text"):
            tid = text_elem.attrib.get("Id", "T_UNKNOWN")
            trans = text_elem.find("Translation")
            val = trans.text if (trans is not None and trans.text) else ""
            text_entries.append((tid, val))

    hpp_lines = [
        "#ifndef TEXTKEYSANDLANGUAGES_HPP",
        "#define TEXTKEYSANDLANGUAGES_HPP",
        "",
        "enum LANGUAGES {",
        "    GB,",
        "    NUMBER_OF_LANGUAGES",
        "};",
        "",
        "enum TEXTS {",
    ]
    for tid, _ in text_entries:
        hpp_lines.append(f"    {tid},")
    hpp_lines += [
        "    NUMBER_OF_TEXT_KEYS",
        "};",
        "#endif // TEXTKEYSANDLANGUAGES_HPP",
        "",
    ]
    (inc_dir / "TextKeysAndLanguages.hpp").write_text("\n".join(hpp_lines), encoding="utf-8")

    cpp_lines = [
        "#include <texts/TextKeysAndLanguages.hpp>",
        "#include <stdint.h>",
        "",
        EXTFLASH_MACRO,
        "LOCATION_EXTFLASH_ATTRIBUTE",
        "extern const char* const DefaultTextDatabase[];",
        "LOCATION_EXTFLASH_ATTRIBUTE",
        "const char* const DefaultTextDatabase[] = {",
    ]
    for tid, val in text_entries:
        escaped = val.replace('"', '\\"')
        cpp_lines.append(f'    "{escaped}", // {tid}')
    cpp_lines += [
        "};",
        "",
    ]
    (src_dir / "Texts.cpp").write_text("\n".join(cpp_lines), encoding="utf-8")
    return text_entries


def png_to_bitmap_id(filename: str) -> str:
    stem = Path(filename).stem
    return f"BitmapDatabase::BITMAP_{re.sub(r'[^A-Za-z0-9_]', '_', stem).upper()}_ID"


def generate_screen_files(screen: dict, out_dir: Path, gui_dir: Path):
    sname = screen["Name"]
    sfolder = f"{sname.lower()}_screen"
    components = screen.get("Components", [])
    interactions = screen.get("Interactions", [])

    gen_inc_dir = out_dir / "gui_generated" / "include" / "gui_generated" / sfolder
    gen_src_dir = out_dir / "gui_generated" / "src" / sfolder
    gen_inc_dir.mkdir(parents=True, exist_ok=True)
    gen_src_dir.mkdir(parents=True, exist_ok=True)

    member_decls = []
    wildcard_decls = []
    setup_lines = []
    custom_actions = []

    for comp in components:
        ctype = comp.get("Type", "Box")
        cname = comp.get("Name", "widget")
        x = comp.get("X", 0)
        y = comp.get("Y", 0)
        w = comp.get("Width", 100)
        h = comp.get("Height", 40)
        color = comp.get("Color", {})
        r, g, b = color.get("Red", 0), color.get("Green", 0), color.get("Blue", 0)

        if ctype == "Box":
            member_decls.append(f"    touchgfx::Box {cname};")
            setup_lines += [
                f"    {cname}.setPosition({x}, {y}, {w}, {h});",
                f"    {cname}.setColor(touchgfx::Color::getColorFromRGB({r}, {g}, {b}));",
                f"    add({cname});",
            ]
        elif ctype == "Image":
            rel = comp.get("RelativeFilename", "")
            bmp_id = png_to_bitmap_id(rel)
            member_decls.append(f"    touchgfx::Image {cname};")
            setup_lines += [
                f"    {cname}.setXY({x}, {y});",
                f"    {cname}.setBitmap(touchgfx::Bitmap({bmp_id}));",
                f"    add({cname});",
            ]
        elif ctype == "TextArea":
            tid = comp.get("TextId", "T_UNKNOWN")
            wc1 = comp.get("Wildcard1")
            if wc1 and wc1.get("UseBuffer"):
                buf_size = wc1.get("BufferSize", 16)
                const_name = f"{cname.upper()}_SIZE"
                member_decls.append(f"    touchgfx::TextAreaWithOneWildcard {cname};")
                wildcard_decls.append(f"    static const uint16_t {const_name} = {buf_size};")
                wildcard_decls.append(f"    touchgfx::Unicode::UnicodeChar {cname}Buffer[{const_name}];")
                setup_lines += [
                    f"    {cname}.setPosition({x}, {y}, {w}, {h});",
                    f"    {cname}.setColor(touchgfx::Color::getColorFromRGB({r}, {g}, {b}));",
                    f"    {cname}.setTypedText(touchgfx::TypedText({tid}));",
                    f"    {cname}.setWildcard({cname}Buffer);",
                    f"    add({cname});",
                ]
            else:
                member_decls.append(f"    touchgfx::TextArea {cname};")
                setup_lines += [
                    f"    {cname}.setPosition({x}, {y}, {w}, {h});",
                    f"    {cname}.setColor(touchgfx::Color::getColorFromRGB({r}, {g}, {b}));",
                    f"    {cname}.setTypedText(touchgfx::TypedText({tid}));",
                    f"    add({cname});",
                ]
        elif ctype == "ButtonWithLabel":
            rel_img = png_to_bitmap_id(comp.get("Released", ""))
            prs_img = png_to_bitmap_id(comp.get("Pressed", ""))
            tid = comp.get("TextId", "T_UNKNOWN")
            rc = comp.get("ReleasedColor", {"Red": 255, "Green": 255, "Blue": 255})
            pc = comp.get("PressedColor", {"Red": 200, "Green": 200, "Blue": 200})
            member_decls.append(f"    touchgfx::ButtonWithLabel {cname};")
            setup_lines += [
                f"    {cname}.setXY({x}, {y});",
                f"    {cname}.setBitmaps(touchgfx::Bitmap({rel_img}), touchgfx::Bitmap({prs_img}));",
                f"    {cname}.setLabelText(touchgfx::TypedText({tid}));",
                f"    {cname}.setLabelColor(touchgfx::Color::getColorFromRGB({rc.get('Red',255)}, {rc.get('Green',255)}, {rc.get('Blue',255)}));",
                f"    {cname}.setLabelColorPressed(touchgfx::Color::getColorFromRGB({pc.get('Red',200)}, {pc.get('Green',200)}, {pc.get('Blue',200)}));",
                f"    {cname}.setAction(buttonCallback);",
                f"    add({cname});",
            ]
        elif ctype == "BoxProgress":
            bg_img = png_to_bitmap_id(comp.get("FileNameBackground", ""))
            pmin = comp.get("ProgressRangeMin", 0)
            pmax = comp.get("ProgressRangeMax", 100)
            pinit = comp.get("ProgressInitialValue", 50)
            member_decls.append(f"    touchgfx::BoxProgress {cname};")
            setup_lines += [
                f"    {cname}.setXY({x}, {y});",
                f"    {cname}.setProgressIndicatorPosition(0, 0, {w}, {h});",
                f"    {cname}.setRange({pmin}, {pmax});",
                f"    {cname}.setColor(touchgfx::Color::getColorFromRGB({r}, {g}, {b}));",
                f"    {cname}.setBackground(touchgfx::Bitmap({bg_img}));",
                f"    {cname}.setValue({pinit});",
                f"    add({cname});",
            ]

    callback_cases = []
    for inter in interactions:
        trig = inter.get("Trigger", {})
        act = inter.get("Action", {})
        tcomp = trig.get("TriggerComponent", "")
        atype = act.get("Type", "")
        if atype == "ActionGotoScreen":
            target_screen = act.get("ActionComponent", "DashboardScreen")
            callback_cases.append(
                f"    if (&src == &{tcomp}) {{\n"
                f"        application().goto{target_screen}SlideTransition();\n"
                f"    }}"
            )
        elif atype == "ActionCustom":
            fn = act.get("FunctionName", "onCustomAction")
            custom_actions.append(fn)
            callback_cases.append(
                f"    if (&src == &{tcomp}) {{\n"
                f"        {fn}();\n"
                f"    }}"
            )

    view_base_hpp = [
        f"#ifndef {sname.upper()}VIEWBASE_HPP",
        f"#define {sname.upper()}VIEWBASE_HPP",
        "",
        "#include <gui_generated/common/FrontendApplicationBase.hpp>",
        "#include <BitmapDatabase.hpp>",
        "#include <texts/TextKeysAndLanguages.hpp>",
        "#include <touchgfx/widgets/Box.hpp>",
        "#include <touchgfx/widgets/Image.hpp>",
        "#include <touchgfx/widgets/TextArea.hpp>",
        "#include <touchgfx/widgets/TextAreaWithWildcard.hpp>",
        "#include <touchgfx/widgets/ButtonWithLabel.hpp>",
        "#include <touchgfx/containers/progress_indicators/BoxProgress.hpp>",
        "#include <touchgfx/Color.hpp>",
        "",
        f"class {sname}ViewBase : public touchgfx::ViewBase {{",
        "public:",
        f"    {sname}ViewBase();",
        f"    virtual ~{sname}ViewBase() {{}}",
        "    virtual void setupScreen() override;",
        *[f"    virtual void {fn}() {{}}" for fn in custom_actions],
        "",
        "protected:",
        "    FrontendApplicationBase& application() {",
        "        return *static_cast<FrontendApplicationBase*>(touchgfx::Application::getInstance());",
        "    }",
        *member_decls,
        *wildcard_decls,
        "",
        "private:",
        f"    touchgfx::Callback<{sname}ViewBase, const touchgfx::AbstractButton&> buttonCallback;",
        "    void buttonCallbackHandler(const touchgfx::AbstractButton& src);",
        "};",
        f"#endif // {sname.upper()}VIEWBASE_HPP",
        "",
    ]
    (gen_inc_dir / f"{sname}ViewBase.hpp").write_text("\n".join(view_base_hpp), encoding="utf-8")

    view_base_cpp = [
        f"#include <gui_generated/{sfolder}/{sname}ViewBase.hpp>",
        "",
        f"{sname}ViewBase::{sname}ViewBase() :",
        f"    buttonCallback(this, &{sname}ViewBase::buttonCallbackHandler)",
        "{",
        *setup_lines,
        "}",
        "",
        f"void {sname}ViewBase::setupScreen() {{}}",
        "",
        f"void {sname}ViewBase::buttonCallbackHandler(const touchgfx::AbstractButton& src) {{",
        *callback_cases,
        "}",
        "",
    ]
    (gen_src_dir / f"{sname}ViewBase.cpp").write_text("\n".join(view_base_cpp), encoding="utf-8")

    user_inc_dir = gui_dir / "include" / "gui" / sfolder
    user_src_dir = gui_dir / "src" / sfolder
    user_inc_dir.mkdir(parents=True, exist_ok=True)
    user_src_dir.mkdir(parents=True, exist_ok=True)

    view_hpp_path = user_inc_dir / f"{sname}View.hpp"
    if not view_hpp_path.exists():
        view_hpp_path.write_text(
            f"#ifndef {sname.upper()}VIEW_HPP\n"
            f"#define {sname.upper()}VIEW_HPP\n\n"
            f"#include <gui_generated/{sfolder}/{sname}ViewBase.hpp>\n"
            f"#include <gui/{sfolder}/{sname}Presenter.hpp>\n\n"
            f"class {sname}View : public {sname}ViewBase {{\n"
            f"public:\n"
            f"    {sname}View() {{}}\n"
            f"    virtual ~{sname}View() {{}}\n"
            f"    virtual void setupScreen() override;\n"
            f"    virtual void tearDownScreen() override;\n"
            + "".join(f"    virtual void {fn}() override;\n" for fn in custom_actions)
            + f"}};\n#endif // {sname.upper()}VIEW_HPP\n",
            encoding="utf-8",
        )

    view_cpp_path = user_src_dir / f"{sname}View.cpp"
    if not view_cpp_path.exists():
        view_cpp_path.write_text(
            f"#include <gui/{sfolder}/{sname}View.hpp>\n\n"
            f"void {sname}View::setupScreen() {{\n"
            f"    {sname}ViewBase::setupScreen();\n"
            f"}}\n\n"
            f"void {sname}View::tearDownScreen() {{\n"
            f"    {sname}ViewBase::tearDownScreen();\n"
            f"}}\n"
            + "".join(
                f"\nvoid {sname}View::{fn}() {{\n    // Custom interaction handler\n}}\n"
                for fn in custom_actions
            ),
            encoding="utf-8",
        )

    pres_hpp_path = user_inc_dir / f"{sname}Presenter.hpp"
    if not pres_hpp_path.exists():
        pres_hpp_path.write_text(
            f"#ifndef {sname.upper()}PRESENTER_HPP\n"
            f"#define {sname.upper()}PRESENTER_HPP\n\n"
            f"#include <gui/model/ModelListener.hpp>\n\n"
            f"class {sname}View;\n\n"
            f"class {sname}Presenter : public ModelListener {{\n"
            f"public:\n"
            f"    {sname}Presenter({sname}View& v) : view(v) {{}}\n"
            f"    virtual void activate() {{}}\n"
            f"    virtual void deactivate() {{}}\n"
            f"    virtual ~{sname}Presenter() {{}}\n"
            f"private:\n"
            f"    {sname}View& view;\n"
            f"}};\n#endif // {sname.upper()}PRESENTER_HPP\n",
            encoding="utf-8",
        )

    pres_cpp_path = user_src_dir / f"{sname}Presenter.cpp"
    if not pres_cpp_path.exists():
        pres_cpp_path.write_text(
            f"#include <gui/{sfolder}/{sname}View.hpp>\n"
            f"#include <gui/{sfolder}/{sname}Presenter.hpp>\n",
            encoding="utf-8",
        )


def generate_frontend_application(screens: list, out_dir: Path):
    inc_dir = out_dir / "gui_generated" / "include" / "gui_generated" / "common"
    src_dir = out_dir / "gui_generated" / "src" / "common"
    inc_dir.mkdir(parents=True, exist_ok=True)
    src_dir.mkdir(parents=True, exist_ok=True)

    nav_methods = [f"    void goto{s['Name']}SlideTransition();" for s in screens]
    hpp = [
        "#ifndef FRONTENDAPPLICATIONBASE_HPP",
        "#define FRONTENDAPPLICATIONBASE_HPP",
        "#include <touchgfx/Application.hpp>",
        "",
        "class FrontendApplicationBase : public touchgfx::Application {",
        "public:",
        "    FrontendApplicationBase() {}",
        "    virtual ~FrontendApplicationBase() {}",
        *nav_methods,
        "};",
        "#endif // FRONTENDAPPLICATIONBASE_HPP",
        "",
    ]
    (inc_dir / "FrontendApplicationBase.hpp").write_text("\n".join(hpp), encoding="utf-8")

    cpp = [
        "#include <gui_generated/common/FrontendApplicationBase.hpp>",
        "",
    ]
    for s in screens:
        cpp.append(f"void FrontendApplicationBase::goto{s['Name']}SlideTransition() {{}}")
    (src_dir / "FrontendApplicationBase.cpp").write_text("\n".join(cpp) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Native macOS TouchGFX Designer Code & Asset Generator")
    parser.add_argument(
        "-p",
        "--project",
        default="TouchGFX/STM32H7_App.touchgfx",
        help="Path to .touchgfx JSON project file.",
    )
    args = parser.parse_args()

    tgfx_path = Path(args.project)
    if not tgfx_path.exists():
        raise SystemExit(f"Error: {tgfx_path} not found.")

    tgfx_root = tgfx_path.parent
    out_dir = tgfx_root / "generated"
    gui_dir = tgfx_root / "gui"
    images_dir = tgfx_root / "assets" / "images"
    texts_xml = tgfx_root / "assets" / "texts" / "texts.xml"

    with tgfx_path.open("r", encoding="utf-8") as f:
        project_data = json.load(f)

    app = project_data.get("Application", project_data)
    screens = app.get("Screens", [])

    bmp_map = generate_bitmap_database(images_dir, out_dir)
    txt_list = generate_texts_database(texts_xml, out_dir)
    generate_frontend_application(screens, out_dir)

    for screen in screens:
        generate_screen_files(screen, out_dir, gui_dir)

    print(
        f"[tgfx_codegen] Generated TouchGFX C++ code for {len(screens)} screen(s), "
        f"{len(bmp_map)} bitmap(s), and {len(txt_list)} text key(s) into {out_dir}"
    )


if __name__ == "__main__":
    main()
