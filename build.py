import json
import sys

from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.t2CharStringPen import T2CharStringPen


ROMAJI_FONT_SIZE = 0.35
ROMAJI_GAP = 0.08


def get_bounds(glyph, glyph_set):
    pen = BoundsPen(glyph_set)
    glyph.draw(pen)

    if pen.bounds is None:
        return None

    return pen.bounds


def get_advance(font, glyph_name):
    return font["hmtx"][glyph_name][0]


def draw_romaji(
    font,
    glyph_set,
    target_pen,
    romaji,
    target_width,
    target_top,
):
    scale = ROMAJI_FONT_SIZE

    # Tính tổng width của romaji
    widths = []

    for char in romaji:
        glyph_name = font.getBestCmap().get(ord(char))

        if glyph_name is None:
            raise ValueError(
                f"Không tìm thấy glyph Latin: {char!r}"
            )

        widths.append(get_advance(font, glyph_name))

    romaji_width = sum(widths) * scale

    # Căn giữa romaji theo advance width của glyph Nhật
    x = (target_width - romaji_width) / 2

    # Đặt baseline của romaji phía trên glyph Nhật
    y = target_top + font["head"].unitsPerEm * ROMAJI_GAP

    for char, width in zip(romaji, widths):
        glyph_name = font.getBestCmap()[ord(char)]
        glyph = glyph_set[glyph_name]

        transform = TransformPen(
            target_pen,
            (
                scale,
                0,
                0,
                scale,
                x,
                y,
            ),
        )

        glyph.draw(transform)

        x += width * scale


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

        if is_glyf:
            pen = TTGlyphPen(glyph_set)

        elif "CFF " in font:
            pen = T2CharStringPen(
                target_width,
                glyph_set,
            )

        else:
            pen = T2CharStringPen(
                target_width,
                glyph_set,
                CFF2=True,
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

        if is_glyf:
            font["glyf"][target_name] = pen.glyph()

        elif "CFF " in font:
            cff = font["CFF "].cff
            top_dict = cff.topDictIndex[0]
            char_strings = top_dict.CharStrings

            old_char_string = char_strings[target_name]

            char_string = pen.getCharString(
                private=old_char_string.private,
                globalSubrs=cff.GlobalSubrs,
            )

            char_strings[target_name] = char_string

        else:
            cff = font["CFF2"].cff
            top_dict = cff.topDictIndex[0]
            char_strings = top_dict.CharStrings

            old_char_string = char_strings[target_name]

            char_string = pen.getCharString(
                private=old_char_string.private,
                globalSubrs=cff.GlobalSubrs,
            )

            char_strings[target_name] = char_string

        print(f"{japanese} -> {romaji} ({target_name})")


def main():
    if len(sys.argv) != 4:
        print(
            "Usage:\n"
            "  python main.py input.ttf output.ttf mapping.json"
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