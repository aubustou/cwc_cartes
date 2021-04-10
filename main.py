import json
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path

from apischema import deserialize

BACKGROUND_PICTURE_FOLDER: Path = Path()


@dataclass
class Unit:
    country: str
    army: str

    name: str
    arm: str
    move: str
    attacks: str
    range: str
    hits: str
    save: str
    notes: str

    flavour: str

    images: list[Path]

    def __post_init__(self):
        self.images = [BACKGROUND_PICTURE_FOLDER / x for x in self.images]


from PIL import Image


def generate_card(unit: Unit) -> None:
    print(unit.images)
    for infile in unit.images:
        try:
            with Image.open(infile) as im:
                print(infile, im.format, f"{im.size}x{im.mode}")
        except OSError:
            pass


def main():
    global BACKGROUND_PICTURE_FOLDER
    parser = ArgumentParser(description="Generate cards from info")
    parser.add_argument('folder', type=Path,
                        help='folder containing the background pictures')

    args = parser.parse_args()
    BACKGROUND_PICTURE_FOLDER = args.folder

    unit_list = json.load(Path("units.json").open())
    for unit in [deserialize(Unit, x) for x in unit_list]:
        generate_card(unit)


if __name__ == "__main__":
    main()
