import json
import sys
import logging
import time

from fontTools.ttLib import TTFont

from .parser import args
from .logger import mainLogger
from .appError import AppError
from .glyph import create_pen, store_glyph
from .romaji import (
    draw_romaji,
    get_advance,
    get_bounds,
)

logging.basicConfig(level=logging.DEBUG, format="[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s", datefmt="%H:%M:%S")

def process(font, mapping):
    cmap = font.getBestCmap()
    glyph_set = font.getGlyphSet()

    is_glyf = "glyf" in font
    is_cff = "CFF " in font or "CFF2" in font

    if not is_glyf and not is_cff:
        mainLogger.error("Font does not use glyf, CFF, or CFF2.")
        raise AppError("Font does not use glyf, CFF, or CFF2.")

    for entry in mapping:
        japanese = entry["japanese"]
        romaji = entry["romaji"]

        if len(japanese) != 1:
            mainLogger.warning(
                f"Skipping {japanese!r}: "
                "only single-character mappings are supported."
            )
            continue

        codepoint = ord(japanese)

        if codepoint not in cmap:
            mainLogger.warning(
                f"Glyph not found: {japanese!r}"
            )
            continue

        target_name = cmap[codepoint]
        target_glyph = glyph_set[target_name]

        target_bounds = get_bounds(
            target_glyph,
            glyph_set,
        )

        if target_bounds is None:
            mainLogger.warning(
                f"Glyph {japanese!r} has no outline; skipping."
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
        )

        mainLogger.debug(
            f"Mapped {japanese} -> {romaji} ({target_name})"
        )


def main():
    input_font = args.input
    output_font = args.output
    mapping_file = args.mapping

    with open(mapping_file, "r", encoding="utf-8") as f:
        mapping = json.load(f)

    font = TTFont(input_font)

    process(font, mapping)

    mainLogger.info(f"Saving font: {output_font}")

    start = time.perf_counter()

    font.save(output_font)

    elapsed = time.perf_counter() - start

    mainLogger.info(f"Created: {output_font} ({elapsed:.2f}s)")


if __name__ == "__main__":
    main()