#!/usr/bin/env python3
"""
quantize_ps2_txd.py — Vanilla Texture Compositor (Splicing), PS2 Quantizer (PAL8),
and Binary .TXD Packer for GTA: San Andreas PC (`open.mp` / SA-MP).

Supports external images and the 3 test kitbash presets:
1. `wmydrug_sindacco`:
   - Combines Johnny Sindacco's slicked face/hair (`sindaco`, ID 119) with the white hoodie
     (folded hood and kangaroo pocket) from `wmydrug` (ID 29) and his dark pants.
2. `bmypol1_tenpenny`:
   - Combines the African-American head with cap/beret and goatee from `bmypol1` (ID 66) with the
     navy-blue short-sleeve LSPD uniform, gold badge, and tactical belt from `tenpen` (ID 265),
     matching skin tone across neck, face, and arms.
3. `wmybar_claude`:
   - Combines the `wmybar` head (ID 177) with Claude's open black leather jacket (`claude`, ID 299),
     replacing the green inner tee with white cotton (`tshirtwhite`) and the green cargo pants
     with classic blue jeans (`jeansdenim`) with PS2-style seams and vertical wear.
"""

import argparse
import json
import os
import struct
import sys
from typing import Dict, Optional, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

RW_VERSION_GTASA = 0x1803FFFF

PRESET_TEX_NAMES = {
    "wmydrug_sindacco": "wmydrug_sind",
    "bmypol1_tenpenny": "bmypol_tenp",
    "wmybar_claude": "wmybar_clau",
}


def _rw_chunk(chunk_type: int, payload: bytes, version: int = RW_VERSION_GTASA) -> bytes:
    """Pack a 12-byte RenderWare header (`type`, `size`, `version`) plus payload."""
    return struct.pack("<III", chunk_type, len(payload), version) + payload


def generate_kitbash_atlas(preset: Optional[str] = None, size: int = 256) -> Image.Image:
    """
    Generate the `256x256` Rockstar North (2004) style texture atlas for the requested
    kitbash preset:
    - Top-left quadrant (`0,0 -> 127,127`): Donor head (`sindaco`, `bmypol1`, `wmybar`).
    - Top-right quadrant (`128,0 -> 255,127`): Torso / outer garment + inner sub-region.
    - Bottom-left quadrant (`0,128 -> 127,255`): Pants / jeans (`wmydrug`, `tenpen`, `jeansdenim`).
    - Bottom-right quadrant (`128,128 -> 255,255`): Mitten arms/hands (matched skin) + footwear.
    """
    img = Image.new("RGB", (size, size), (48, 52, 60))
    draw = ImageDraw.Draw(img)

    if preset == "wmydrug_sindacco":
        # 1. Johnny Sindacco head (ID 119): pale olive skin, heavy under-eye circles, sideburns, and a slicked black pompadour
        skin_color = (182, 142, 116)
        draw.rectangle([0, 0, 127, 127], fill=skin_color)
        draw.rectangle([0, 0, 127, 36], fill=(24, 22, 26))          # Black hair slicked back
        draw.rectangle([6, 30, 18, 72], fill=(28, 25, 28))          # Left sideburn
        draw.rectangle([109, 30, 121, 72], fill=(28, 25, 28))       # Right sideburn
        draw.rectangle([24, 44, 52, 58], fill=(64, 42, 36))         # Left eye socket (Sindacco under-eye)
        draw.rectangle([76, 44, 104, 58], fill=(64, 42, 36))        # Right eye socket
        draw.polygon([(64, 46), (53, 82), (75, 82)], fill=(152, 112, 88))
        draw.rectangle([42, 94, 86, 104], fill=(104, 62, 54))       # Tight mouth
        draw.rectangle([28, 108, 100, 125], fill=(132, 98, 78))     # Jaw shadow and full beard

        # 2. wmydrug torso (ID 29): grayish-white hoodie with folds + hood folded onto the upper back
        draw.rectangle([128, 0, 255, 127], fill=(214, 212, 206))    # PS2 white cotton (never >235)
        # Deep fold of the dropped hood on the upper back (`Spine1`)
        draw.rectangle([134, 8, 248, 38], fill=(168, 166, 160))
        draw.line([(140, 22), (242, 22)], fill=(122, 120, 116), width=4)
        # Hoodie drawstrings and front kangaroo pocket with ambient occlusion
        draw.line([(182, 36), (182, 70)], fill=(130, 128, 124), width=3)
        draw.line([(202, 36), (202, 70)], fill=(130, 128, 124), width=3)
        draw.polygon([(148, 82), (236, 82), (244, 120), (140, 120)], fill=(192, 190, 184), outline=(138, 136, 130))

        # 3. Loose dark wmydrug pants
        draw.rectangle([0, 128, 127, 255], fill=(44, 48, 54))
        draw.rectangle([58, 128, 68, 255], fill=(26, 28, 32))
        for yc in (168, 196, 232):
            draw.line([(10, yc), (118, yc + 4)], fill=(30, 32, 38), width=3)

        # 4. Hands (Sindacco tone) + white/gray urban sneakers
        draw.rectangle([128, 128, 255, 190], fill=skin_color)
        draw.rectangle([128, 191, 255, 255], fill=(188, 186, 182))
        draw.rectangle([128, 238, 255, 255], fill=(92, 90, 88))

    elif preset == "bmypol1_tenpenny":
        # 1. bmypol1 head (ID 66): warm African-American skin, black cap/beret, and goatee
        skin_color = (96, 62, 44)
        draw.rectangle([0, 0, 127, 127], fill=skin_color)
        draw.rectangle([0, 0, 127, 38], fill=(22, 24, 28))          # Dark bmypol1 cap/beret
        draw.rectangle([24, 46, 52, 58], fill=(42, 26, 18))         # Eyes and eyebrows
        draw.rectangle([76, 46, 104, 58], fill=(42, 26, 18))
        draw.polygon([(64, 48), (50, 82), (78, 82)], fill=(82, 50, 34))
        # Signature bmypol1 goatee
        draw.rectangle([42, 86, 86, 118], outline=(24, 18, 14), width=5)
        draw.rectangle([46, 94, 82, 103], fill=(58, 34, 24))

        # 2. Tenpenny LSPD uniform (ID 265): dark navy shirt, gold LSPD badge, pockets
        draw.rectangle([128, 0, 255, 127], fill=(24, 30, 44))
        # V-neck with a white police undershirt
        draw.polygon([(176, 0), (208, 0), (192, 28)], fill=(212, 212, 208))
        # Oval gold LSPD badge on the left chest (`x=212..228, y=34..54`)
        draw.ellipse([212, 34, 228, 54], fill=(204, 168, 62), outline=(128, 98, 28))
        # LSPD shoulder patches and tactical belt with silver buckle and holster
        draw.rectangle([128, 106, 255, 127], fill=(18, 18, 20))
        draw.rectangle([184, 108, 200, 125], fill=(176, 178, 182))

        # 3. LSPD uniform pants with a blue side stripe
        draw.rectangle([0, 128, 127, 255], fill=(22, 28, 40))
        draw.rectangle([58, 128, 68, 255], fill=(14, 18, 26))
        draw.line([(16, 128), (16, 255)], fill=(38, 48, 68), width=3)
        draw.line([(112, 128), (112, 255)], fill=(38, 48, 68), width=3)

        # 4. Bare forearms/hands (matched exactly to the bmypol1 African-American tone) + black combat boots
        draw.rectangle([128, 128, 255, 190], fill=skin_color)
        draw.rectangle([128, 191, 255, 255], fill=(20, 20, 22))
        draw.rectangle([128, 240, 255, 255], fill=(14, 14, 16))

    elif preset == "wmybar_claude":
        # 1. wmybar head (ID 177): light Caucasian skin, neat dark-brown barber cut
        skin_color = (196, 152, 124)
        draw.rectangle([0, 0, 127, 127], fill=skin_color)
        draw.rectangle([0, 0, 127, 32], fill=(46, 34, 26))          # wmybar short dark-brown hair
        draw.rectangle([26, 44, 52, 56], fill=(74, 50, 38))
        draw.rectangle([76, 44, 102, 56], fill=(74, 50, 38))
        draw.polygon([(64, 48), (54, 80), (74, 80)], fill=(168, 124, 98))
        draw.rectangle([44, 92, 84, 102], fill=(128, 76, 66))

        # 2. Claude's black leather jacket (ID 299) + WHITE TEE sub-island (`tshirtwhite`)
        draw.rectangle([128, 0, 255, 127], fill=(26, 28, 32))       # Black leather with baked gray highlights
        draw.line([(146, 14), (168, 118)], fill=(54, 58, 64), width=3)  # Lapel and metal zipper
        draw.line([(169, 20), (169, 118)], fill=(156, 160, 164), width=2)
        # White inner-tee UV sub-island (`u in [0.76, 0.96], v in [0.54, 0.74]` -> `x=194..255, y=64..127`)
        draw.rectangle([194, 56, 252, 124], fill=(218, 216, 210))   # PS2 cotton white (`tshirtwhite`)
        for y_rib in (72, 88, 104):
            draw.line([(200, y_rib), (246, y_rib + 3)], fill=(164, 164, 158), width=2)

        # 3. Pants replaced by BLUE JEANS (vanilla `jeansdenim` from player.img)
        draw.rectangle([0, 128, 127, 255], fill=(48, 76, 116))      # Classic PS2 indigo
        # Light vertical wear down the center of the thighs (typical of `jeansdenim` in GTA:SA)
        draw.rectangle([22, 142, 46, 224], fill=(74, 106, 148))
        draw.rectangle([82, 142, 106, 224], fill=(74, 106, 148))
        # Center seam and ochre jean topstitch
        draw.rectangle([58, 128, 68, 255], fill=(30, 48, 78))
        draw.line([(6, 132), (122, 132)], fill=(154, 118, 62), width=2)
        for y_knee in (184, 192):
            draw.line([(12, y_knee), (116, y_knee)], fill=(34, 54, 86), width=3)

        # 4. Hands (wmybar tone) + Claude's black sneakers with a white sole
        draw.rectangle([128, 128, 255, 190], fill=skin_color)
        draw.rectangle([128, 191, 255, 255], fill=(28, 28, 32))
        draw.rectangle([128, 238, 255, 255], fill=(212, 210, 204))

    else:
        # Generic reference atlas
        draw.rectangle([0, 0, 127, 127], fill=(168, 126, 98))
        draw.rectangle([128, 0, 255, 127], fill=(46, 68, 98))
        draw.rectangle([0, 128, 127, 255], fill=(52, 60, 74))
        draw.rectangle([128, 128, 255, 192], fill=(162, 120, 92))
        draw.rectangle([128, 193, 255, 255], fill=(42, 42, 44))

    # Early-2000s photographic grain + PS2 tonal compression (`12..235`)
    arr = np.array(img, dtype=np.int16)
    rng = np.random.default_rng(seed=2004)
    noise = rng.integers(-8, 9, size=arr.shape, dtype=np.int16)
    arr = np.clip(arr + noise, 12, 235).astype(np.uint8)
    return Image.fromarray(arr, mode="RGB").filter(ImageFilter.SMOOTH_MORE)


def apply_ps2_color_pipeline(
    img: Image.Image,
    target_size: Tuple[int, int] = (256, 256),
    colors: int = 256,
    black_floor: int = 12,
    white_ceiling: int = 235,
) -> Tuple[Image.Image, Image.Image]:
    """Resize, compress levels to `[12, 235]`, and quantize to 256 colors with Floyd-Steinberg dithering."""
    w, h = target_size
    if (w & (w - 1) != 0) or (h & (h - 1) != 0):
        raise ValueError(f"Invalid dimensions (must be powers of two): {w}x{h}")

    rgb_img = img.convert("RGB").resize((w, h), Image.Resampling.BILINEAR)
    arr = np.asarray(rgb_img, dtype=np.float32)
    arr = black_floor + (arr / 255.0) * float(white_ceiling - black_floor)
    arr = np.clip(np.round(arr), black_floor, white_ceiling).astype(np.uint8)
    clamped_rgb = Image.fromarray(arr, mode="RGB")

    pal_img = clamped_rgb.quantize(
        colors=colors,
        method=Image.Quantize.MEDIANCUT,
        dither=Image.Dither.FLOYDSTEINBERG,
    )
    return pal_img, pal_img.convert("RGBA")


def build_gtasa_pc_txd_bytes(
    tex_name: str,
    pal_img: Image.Image,
    rgba_img: Image.Image,
    use_pal8: bool = True,
) -> bytes:
    """Build a native `.txd` (`rwID_TEXDICTIONARY = 0x0016`) for GTA:SA PC (`0x1803FFFF`)."""
    clean_name = os.path.splitext(os.path.basename(tex_name))[0].lower()[:31]
    width, height = pal_img.size
    name_32 = clean_name.encode("ascii").ljust(32, b"\x00")
    mask_32 = b"\x00" * 32

    if use_pal8:
        raster_format = 0x00002500  # RASTER_8888 | RASTER_PAL8
        d3d_format = 22             # D3DFMT_X8R8G8B8
        depth = 8
        comp_flags = 0x00

        raw_pal = pal_img.getpalette() or [0] * (256 * 3)
        raw_pal = (raw_pal + [0] * 768)[:768]
        palette_bytes = bytearray(256 * 4)
        for i in range(256):
            palette_bytes[i * 4 + 0] = raw_pal[i * 3 + 0]
            palette_bytes[i * 4 + 1] = raw_pal[i * 3 + 1]
            palette_bytes[i * 4 + 2] = raw_pal[i * 3 + 2]
            palette_bytes[i * 4 + 3] = 255

        index_bytes = np.asarray(pal_img, dtype=np.uint8).tobytes()
        tex_body = bytes(palette_bytes) + struct.pack("<I", len(index_bytes)) + index_bytes
    else:
        raster_format = 0x00000500
        d3d_format = 21
        depth = 32
        comp_flags = 0x08
        rgba_arr = np.asarray(rgba_img, dtype=np.uint8)
        bgra_arr = rgba_arr[:, :, [2, 1, 0, 3]]
        raw_bytes = bgra_arr.tobytes()
        tex_body = struct.pack("<I", len(raw_bytes)) + raw_bytes

    tex_header = struct.pack(
        "<II32s32sIIHHBBBB",
        9,              # platform_id = 9 (Direct3D 9 GTA:SA PC)
        0x00001102,     # FILTERLINEAR + WRAP
        name_32,
        mask_32,
        raster_format,
        d3d_format,
        width,
        height,
        depth,
        1,
        4,
        comp_flags,
    )

    tex_native_struct = _rw_chunk(0x0001, tex_header + tex_body)
    tex_native_chunk = _rw_chunk(0x0015, tex_native_struct + _rw_chunk(0x0003, b""))
    txd_struct = _rw_chunk(0x0001, struct.pack("<HH", 1, 2))
    return _rw_chunk(0x0016, txd_struct + tex_native_chunk + _rw_chunk(0x0003, b""))


def process_and_pack_ps2_txd(
    output_txd_path: str,
    tex_name: str = "mech_ps2",
    preset: Optional[str] = None,
    input_image_path: Optional[str] = None,
    preview_png_path: Optional[str] = None,
    size: int = 256,
    colors: int = 256,
) -> Dict[str, object]:
    """Run atlas splicing/composition, PS2 quantization, and `.txd` packing."""
    if preset and preset in PRESET_TEX_NAMES:
        tex_name = PRESET_TEX_NAMES[preset]

    if input_image_path and os.path.exists(input_image_path):
        src_img = Image.open(input_image_path)
    else:
        src_img = generate_kitbash_atlas(preset=preset, size=size)

    pal_img, rgba_img = apply_ps2_color_pipeline(src_img, target_size=(size, size), colors=colors)

    if preview_png_path:
        os.makedirs(os.path.dirname(os.path.abspath(preview_png_path)), exist_ok=True)
        rgba_img.save(preview_png_path, format="PNG")

    txd_bytes = build_gtasa_pc_txd_bytes(tex_name=tex_name, pal_img=pal_img, rgba_img=rgba_img, use_pal8=True)
    os.makedirs(os.path.dirname(os.path.abspath(output_txd_path)), exist_ok=True)
    with open(output_txd_path, "wb") as f:
        f.write(txd_bytes)

    unique_colors = len(np.unique(np.asarray(rgba_img).reshape(-1, 4), axis=0))
    return {
        "txd_path": output_txd_path,
        "preview_png": preview_png_path,
        "preset": preset or "custom",
        "texture_name": os.path.splitext(os.path.basename(tex_name))[0].lower()[:31],
        "dimensions": f"{size}x{size}",
        "palette_colors_used": int(unique_colors),
        "raster_format": "PAL8 (8-bit Indexed PS2 Style on D3D9 PC)",
        "rw_version": hex(RW_VERSION_GTASA),
        "byte_size": len(txd_bytes),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Vanilla texture compositor, PS2 quantizer, and .TXD packer for GTA:SA PC"
    )
    parser.add_argument("--preset", default=None, choices=list(PRESET_TEX_NAMES.keys()), help="Kitbash preset")
    parser.add_argument("--input", default=None, help="Optional input image")
    parser.add_argument("--output", required=True, help="Output path for the .txd file")
    parser.add_argument("--tex-name", default="mech_ps2", help="Internal texture name inside the .txd")
    parser.add_argument("--preview", default=None, help="Optional path to save the quantized PNG")
    parser.add_argument("--size", type=int, default=256, choices=[64, 128, 256])
    parser.add_argument("--colors", type=int, default=256, choices=[16, 64, 128, 256])
    args = parser.parse_args()

    result = process_and_pack_ps2_txd(
        output_txd_path=args.output,
        tex_name=args.tex_name,
        preset=args.preset,
        input_image_path=args.input,
        preview_png_path=args.preview,
        size=args.size,
        colors=args.colors,
    )
    print(json.dumps({"status": "OK", "txd_summary": result}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())