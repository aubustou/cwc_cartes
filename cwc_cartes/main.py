import json
import logging
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path

from PIL import Image
from PIL import ImageOps
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

    def camelcase_name(self):
        return self.name.replace(" ", "_")


CARD_X = 1050
CARD_Y = 750
CARD_SIZE = (CARD_X, CARD_Y)
CARD_RATIO = CARD_SIZE[0] / CARD_SIZE[1]
FLAG_FOLDER = Path(__file__).parent / "images/country_flags"
SCALE_FLAG = 0.5


def fit_background_image(file_: Path) -> Image:
    with Image.open(file_) as im:
        logging.info(
            "Found picture %s, %s, %sx%s in %s",
            file_,
            im.format,
            im.size[0],
            im.size[1],
            im.mode,
        )
        fit_im = ImageOps.fit(im, CARD_SIZE)

        logging.info("Image %s resized to %sx%s", file_, fit_im.size[0], fit_im.size[1])

    return fit_im


def add_flag(country: str) -> Image:
    flag_file = FLAG_FOLDER / (country.upper() + ".png")
    if not flag_file.exists():
        raise RuntimeError("No country flag found: ", country)

    with Image.open(flag_file) as flag_im:
        scaled_im = flag_im.resize(size=(64, 64))

    return scaled_im


def generate_name_box(name: str, type_: str) -> Image:
    image = Image.new("RGBA", CARD_SIZE, (255, 0, 0, 0))
    return image


def generate_card(unit: Unit) -> None:
    for index, infile in enumerate(unit.images):
        card_image = Image.new("RGBA", CARD_SIZE)

        # Copy generated parts onto final image
        for image, box, has_transparency in [
            (fit_background_image(infile), (0, 0), False),
            (add_flag(unit.country), (964, 14), True),
        ]:
            card_image.paste(image, box, image if has_transparency else None)

        card_image.save(
            str(
                BACKGROUND_PICTURE_FOLDER
                / "generated"
                / (
                    "_".join(
                        [unit.country.upper(), unit.camelcase_name(), str(index + 1)]
                    )
                    + ".png"
                )
            ),
            "PNG",
        )


def main():
    global BACKGROUND_PICTURE_FOLDER

    logging.basicConfig(level=logging.INFO)
    parser = ArgumentParser(description="Generate cards from info")
    parser.add_argument(
        "folder",
        type=Path,
        help="folder containing the background pictures and the JSON units.json",
    )

    args = parser.parse_args()
    BACKGROUND_PICTURE_FOLDER = args.folder
    (BACKGROUND_PICTURE_FOLDER / "generated").mkdir(exist_ok=True)
    json_file = args.folder / "units.json"

    unit_list = json.load(json_file.open())
    for unit in [deserialize(Unit, x) for x in unit_list]:
        generate_card(unit)


if __name__ == "__main__":
    main()
