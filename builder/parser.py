from pathlib import Path
import argparse

parser = argparse.ArgumentParser(
    prog="font-transcription-builder",
    description="Font with transcription builder"
)

parser.add_argument(
    "input",
    type=Path
)

parser.add_argument(
    "output",
    type=Path,
    help="Output font",
)

parser.add_argument(
    "mapping",
    type=Path,
    help="mapping JSON",
)

args = parser.parse_args()