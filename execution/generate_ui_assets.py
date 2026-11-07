#!/usr/bin/env python3
"""
Procedural UI Asset Generator for TouchGFX (480x272 RGB LCD)
Allows Google Antigravity to synthesize modern UI cards, gradients, buttons,
and progress bars directly from JSON design tokens.
Includes a zero-dependency pure-Python PNG encoder fallback (struct + zlib)
so it works out-of-the-box on any macOS Python installation even before Pillow is installed.
"""
import argparse
import json
import struct
import zlib
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    Image = None
    ImageDraw = None


def hex_to_rgba(hex_str: str, alpha: int = 255):
    h = hex_str.lstrip("#")
    if len(h) == 6:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), alpha)
    elif len(h) == 8:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(h[6:8], 16))
    return (15, 23, 42, alpha)


def write_png_pure_python(path: Path, width: int, height: int, rgba_rows: list):
    """Write a valid RGBA PNG using only Python standard library (zlib + struct)."""
    def png_chunk(chunk_type: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", crc)

    raw_data = bytearray()
    for row in rgba_rows:
        raw_data.append(0)  # Filter type 0 (None)
        raw_data.extend(row)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    compressed = zlib.compress(bytes(raw_data), level=6)
    png_bytes = (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", ihdr)
        + png_chunk(b"IDAT", compressed)
        + png_chunk(b"IEND", b"")
    )
    path.write_bytes(png_bytes)


def save_gradient_rect(path: Path, width: int, height: int, top_hex: str, bottom_hex: str):
    c1 = hex_to_rgba(top_hex)
    c2 = hex_to_rgba(bottom_hex)
    if Image is not None:
        img = Image.new("RGBA", (width, height))
        draw = ImageDraw.Draw(img)
        for y in range(height):
            t = y / max(height - 1, 1)
            r = int(c1[0] + (c2[0] - c1[0]) * t)
            g = int(c1[1] + (c2[1] - c1[1]) * t)
            b = int(c1[2] + (c2[2] - c1[2]) * t)
            draw.line([(0, y), (width - 1, y)], fill=(r, g, b, 255))
        img.save(path, "PNG")
    else:
        rows = []
        for y in range(height):
            t = y / max(height - 1, 1)
            r = int(c1[0] + (c2[0] - c1[0]) * t)
            g = int(c1[1] + (c2[1] - c1[1]) * t)
            b = int(c1[2] + (c2[2] - c1[2]) * t)
            rows.append(bytes([r, g, b, 255]) * width)
        write_png_pure_python(path, width, height, rows)


def save_rounded_card(
    path: Path,
    width: int,
    height: int,
    fill_hex: str,
    border_hex: str,
    border_width: int = 1,
    radius: int = 12,
):
    fill_rgba = hex_to_rgba(fill_hex)
    border_rgba = hex_to_rgba(border_hex) if border_hex else fill_rgba
    if Image is not None:
        img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw.rounded_rectangle(
            [0, 0, width - 1, height - 1],
            radius=radius,
            fill=fill_rgba,
            outline=border_rgba,
            width=border_width,
        )
        img.save(path, "PNG")
    else:
        rows = []
        for y in range(height):
            row = bytearray()
            is_border_y = (y < border_width) or (y >= height - border_width)
            for x in range(width):
                is_border_x = (x < border_width) or (x >= width - border_width)
                c = border_rgba if (is_border_y or is_border_x) else fill_rgba
                row.extend(c)
            rows.append(bytes(row))
        write_png_pure_python(path, width, height, rows)


def main():
    parser = argparse.ArgumentParser(description="Generate TouchGFX PNG UI assets from JSON manifest.")
    parser.add_argument(
        "--manifest",
        default="directives/ui_assets_manifest.json",
        help="Path to UI asset manifest JSON file.",
    )
    parser.add_argument(
        "--out-dir",
        default="TouchGFX/assets/images",
        help="Output directory for generated PNGs.",
    )
    args = parser.parse_args()

    manifest_path = Path(args.manifest)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    with manifest_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    generated = []
    for item in data.get("assets", []):
        fname = item["filename"]
        atype = item.get("type", "rounded_card")
        w = int(item.get("width", 100))
        h = int(item.get("height", 40))
        out_path = out_dir / fname

        if atype == "gradient_rect":
            save_gradient_rect(
                out_path,
                w,
                h,
                item.get("color_top", "#0F172A"),
                item.get("color_bottom", "#1E293B"),
            )
        else:
            save_rounded_card(
                out_path,
                w,
                h,
                item.get("fill", "#1E293B"),
                item.get("border", "#334155"),
                int(item.get("border_width", 1)),
                int(item.get("radius", 10)),
            )

        generated.append(str(out_path))

    print(f"[generate_ui_assets] Generated {len(generated)} PNG assets in {out_dir}:")
    for p in generated:
        print(f"  - {p}")


if __name__ == "__main__":
    main()
