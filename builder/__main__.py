import json
import sys

from fontTools.ttLib import TTFont

from .glyph import create_pen, store_glyph
from .romaji import (
    draw_romaji,
    get_advance,
    get_bounds,
)


def process(font, mapping):
    cmap = font.getBestCmap()
    glyph_set = font.getGlyphSet()

    is_glyf = "glyf" in font
    is_cff = "CFF " in font or "CFF2" in font

    if not is_glyf and not is_cff:
        raise RuntimeError(
            "Font không dùng glyf hoặc CFF/CFF2."
        )

    for entry in mapping:
        japanese = entry["japanese"]
        romaji = entry["romaji"]

        if len(japanese) != 1:
            print(
                f"Bỏ qua {japanese!r}: "
                "MVP hiện chỉ hỗ trợ 1 ký tự Nhật."
            )
            continue

        codepoint = ord(japanese)

        if codepoint not in cmap:
            print(
                f"Không tìm thấy glyph cho {japanese!r}"
            )
            continue

        target_name = cmap[codepoint]
        target_glyph = glyph_set[target_name]

        target_bounds = get_bounds(
            target_glyph,
            glyph_set,
        )

        if target_bounds is None:
            print(
                f"Glyph {japanese!r} không có outline."
            )
            continue

        _, _, _, target_top = target_bounds

        target_width = get_advance(
            font,
            target_name,
        )

        pen = create_pen(
            font,
            glyph_set,
            target_width,
        )

        # Giữ glyph Nhật gốc
        target_glyph.draw(pen)

        # Thêm romaji
        draw_romaji(
            font,
            glyph_set,
            pen,
            romaji,
            target_width,
            target_top,
        )

        store_glyph(
            font,
            target_name,
            pen,
            target_width,
        )

        print(
            f"{japanese} -> {romaji} ({target_name})"
        )


def main():
    if len(sys.argv) != 4:
        print(
            "Usage:\n"
            "  python -m builder input.ttf output.ttf mapping.json"
        )
        sys.exit(1)

    input_font = sys.argv[1]
    output_font = sys.argv[2]
    mapping_file = sys.argv[3]

    with open(mapping_file, "r", encoding="utf-8") as f:
        mapping = json.load(f)

    font = TTFont(input_font)

    process(font, mapping)

    font.save(output_font)

    print()
    print(f"Đã tạo: {output_font}")


if __name__ == "__main__":
    main()