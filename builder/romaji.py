from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.transformPen import TransformPen


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
    cmap = font.getBestCmap()

    widths = []

    for char in romaji:
        glyph_name = cmap.get(ord(char))

        if glyph_name is None:
            raise ValueError(
                f"Không tìm thấy glyph Latin: {char!r}"
            )

        widths.append(get_advance(font, glyph_name))

    romaji_width = sum(widths) * scale

    x = (target_width - romaji_width) / 2

    y = target_top + font["head"].unitsPerEm * ROMAJI_GAP

    for char, width in zip(romaji, widths):
        glyph_name = cmap[ord(char)]
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