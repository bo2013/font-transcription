from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.t2CharStringPen import T2CharStringPen


def create_pen(font, glyph_set, width):
    if "glyf" in font:
        return TTGlyphPen(glyph_set)

    if "CFF " in font:
        return T2CharStringPen(width, glyph_set)

    if "CFF2" in font:
        return T2CharStringPen(
            width,
            glyph_set,
            CFF2=True,
        )

    raise RuntimeError(
        "Font không dùng glyf hoặc CFF/CFF2."
    )


def store_glyph(font, glyph_name, pen, width):
    if "glyf" in font:
        font["glyf"][glyph_name] = pen.glyph()
        return

    if "CFF " in font:
        cff = font["CFF "].cff
    else:
        cff = font["CFF2"].cff

    top_dict = cff.topDictIndex[0]
    char_strings = top_dict.CharStrings

    old_char_string = char_strings[glyph_name]

    char_string = pen.getCharString(
        private=old_char_string.private,
        globalSubrs=cff.GlobalSubrs,
    )

    char_strings[glyph_name] = char_string