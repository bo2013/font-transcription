import argparse
from pathlib import Path

from fontTools.ttLib import TTCollection


def main():
    parser = argparse.ArgumentParser(
        description="Split a TTC font collection into individual TTF files."
    )

    parser.add_argument(
        "input",
        type=Path,
        help="Input TTC file",
    )

    parser.add_argument(
        "output",
        type=Path,
        help="Output directory",
    )

    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)

    ttc = TTCollection(args.input)

    for i, font in enumerate(ttc.fonts):
        family = next(
            name.toUnicode()
            for name in font["name"].names
            if name.nameID == 1
        )

        filename = f"{family.replace(' ', '-')}.ttf"
        path = args.output / filename

        font.save(path)

        print(f"{i}: {family} -> {path}")


if __name__ == "__main__":
    main()