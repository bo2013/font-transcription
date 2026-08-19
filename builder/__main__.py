import json
import sys

from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.t2CharStringPen import T2CharStringPen


ROMAJI_FONT_SIZE = 0.35
ROMAJI_GAP = 0.08
LIGATURE_PREFIX = "transcription_liga_"


def get_bounds(glyph, glyph_set):
    pen = BoundsPen(glyph_set)
    glyph.draw(pen)

    if pen.bounds is None:
        return None

    return pen.bounds


def get_advance(font, glyph_name):
    return font["hmtx"][glyph_name][0]


def make_pen(font, glyph_set, width):
    if "glyf" in font:
        return TTGlyphPen(glyph_set)

    if "CFF " in font:
        return T2CharStringPen(width, glyph_set)

    return T2CharStringPen(width, glyph_set, CFF2=True)


def store_glyph(font, glyph_name, pen, width, source_name=None):
    font["hmtx"][glyph_name] = (width, 0)

    if glyph_name not in font.getGlyphOrder():
        font.setGlyphOrder(font.getGlyphOrder() + [glyph_name])

    if "glyf" in font:
        font["glyf"][glyph_name] = pen.glyph()
        return

    if "CFF " in font:
        cff = font["CFF "].cff
        top_dict = cff.topDictIndex[0]
        char_strings = top_dict.CharStrings
        old_char_string = char_strings[source_name] if source_name else None
        char_strings[glyph_name] = pen.getCharString(
            private=old_char_string.private if old_char_string else None,
            globalSubrs=cff.GlobalSubrs,
        )
        return

    cff = font["CFF2"].cff
    top_dict = cff.topDictIndex[0]
    char_strings = top_dict.CharStrings
    old_char_string = char_strings[source_name] if source_name else None
    char_strings[glyph_name] = pen.getCharString(
        private=old_char_string.private if old_char_string else None,
        globalSubrs=cff.GlobalSubrs,
    )


def draw_romaji(
    font,
    glyph_set,
    target_pen,
    romaji,
    target_width,
    target_top,
):
    scale = ROMAJI_FONT_SIZE
    cmap = font.getBestCmap()
    widths = []

    for char in romaji:
        glyph_name = cmap.get(ord(char))

        if glyph_name is None:
            raise ValueError(f"Không tìm thấy glyph Latin: {char!r}")

        widths.append(get_advance(font, glyph_name))

    romaji_width = sum(widths) * scale
    x = (target_width - romaji_width) / 2
    y = target_top + font["head"].unitsPerEm * ROMAJI_GAP

    for char, width in zip(romaji, widths):
        glyph_name = cmap[ord(char)]
        glyph = glyph_set[glyph_name]

        transform = TransformPen(
            target_pen,
            (scale, 0, 0, scale, x, y),
        )
        glyph.draw(transform)
        x += width * scale


def build_single(font, glyph_set, entry):
    japanese = entry["japanese"]
    romaji = entry["romaji"]
    cmap = font.getBestCmap()
    codepoint = ord(japanese)

    if codepoint not in cmap:
        print(f"Không tìm thấy glyph cho {japanese!r}")
        return

    target_name = cmap[codepoint]
    target_glyph = glyph_set[target_name]
    target_bounds = get_bounds(target_glyph, glyph_set)

    if target_bounds is None:
        print(f"Glyph {japanese!r} không có outline.")
        return

    _, _, _, target_top = target_bounds
    target_width = get_advance(font, target_name)
    pen = make_pen(font, glyph_set, target_width)

    target_glyph.draw(pen)
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
        source_name=target_name,
    )

    print(f"{japanese} -> {romaji} ({target_name})")


def build_ligature(font, glyph_set, entry, index):
    japanese = entry["japanese"]
    romaji = entry["romaji"]
    cmap = font.getBestCmap()
    source_names = []

    for char in japanese:
        glyph_name = cmap.get(ord(char))
        if glyph_name is None:
            print(f"Không tìm thấy glyph cho {char!r} trong {japanese!r}")
            return None
        source_names.append(glyph_name)

    source_glyphs = [glyph_set[name] for name in source_names]
    advances = [get_advance(font, name) for name in source_names]
    target_width = sum(advances)

    top = None
    x = 0
    for glyph, advance in zip(source_glyphs, advances):
        bounds = get_bounds(glyph, glyph_set)
        if bounds is not None:
            glyph_top = bounds[3]
            top = glyph_top if top is None else max(top, glyph_top)
        x += advance

    if top is None:
        print(f"Glyph sequence {japanese!r} không có outline.")
        return None

    ligature_name = f"{LIGATURE_PREFIX}{index:04d}"
    pen = make_pen(font, glyph_set, target_width)

    x = 0
    for glyph, advance in zip(source_glyphs, advances):
        transform = TransformPen(
            pen,
            (1, 0, 0, 1, x, 0),
        )
        glyph.draw(transform)
        x += advance

    draw_romaji(
        font,
        glyph_set,
        pen,
        romaji,
        target_width,
        top,
    )
    store_glyph(
        font,
        ligature_name,
        pen,
        target_width,
        source_name=source_names[0],
    )

    print(f"{japanese} -> {romaji} ({ligature_name})")
    return source_names, ligature_name


def add_ligatures(font, ligature_entries):
    if not ligature_entries:
        return

    feature_lines = ["feature liga {"]

    for source_names, ligature_name in ligature_entries:
        feature_lines.append(
            "    sub "
            + " ".join(source_names)
            + f" by {ligature_name};"
        )

    feature_lines.append("} liga;")
    addOpenTypeFeaturesFromString(font, "\n".join(feature_lines))


def process(font, mapping):
    cmap = font.getBestCmap()
    glyph_set = font.getGlyphSet()

    is_glyf = "glyf" in font
    is_cff = "CFF " in font or "CFF2" in font

    if not is_glyf and not is_cff:
        raise RuntimeError("Font không dùng glyf hoặc CFF/CFF2.")

    single_entries = []
    sequence_entries = []

    for entry in mapping:
        japanese = entry["japanese"]
        if len(japanese) == 1:
            single_entries.append(entry)
        else:
            sequence_entries.append(entry)

    ligature_entries = []
    for index, entry in enumerate(sequence_entries, 1):
        result = build_ligature(font, glyph_set, entry, index)
        if result is not None:
            ligature_entries.append(result)

    add_ligatures(font, ligature_entries)

    for entry in single_entries:
        build_single(font, glyph_set, entry)


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
