import json
import logging
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path

from PIL import Image
from PIL import ImageDraw, ImageFont
from PIL import ImageOps
from apischema import deserialize

BACKGROUND_PICTURE_FOLDER: Path = Path()
ROOT_FOLDER = Path(__file__).parent


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

COLOUR_CODE = "#678198cc"


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


FLAG_FOLDER = ROOT_FOLDER / "images" / "country_flags"
SCALE_FLAG = 0.5


def get_flag(country: str) -> Image:
    flag_file = FLAG_FOLDER / (country.upper() + ".png")
    if not flag_file.exists():
        raise RuntimeError("No country flag found: ", country)

    with Image.open(flag_file) as flag_im:
        scaled_im = flag_im.resize(size=(64, 64))

    return scaled_im


NAME_BOX_X = 200
NAME_BOX_Y = 20
NAME_BOX_SIZE_X = 660
NAME_BOX_SIZE_Y = 55
NAME_BOX_MARGIN = 5
UNIT_ICON_FOLDER = ROOT_FOLDER / "images" / "unit_icons"


def draw_name_box(name: str, type_: str) -> Image:
    image = Image.new("RGBA", CARD_SIZE, (255, 0, 0, 0))

    # Draw a half-opaque rectangle
    name_box = ImageDraw.Draw(image)
    name_box.rectangle(
        [
            NAME_BOX_X,
            NAME_BOX_Y,
            NAME_BOX_SIZE_X + NAME_BOX_X,
            NAME_BOX_SIZE_Y + NAME_BOX_Y,
        ],
        fill=COLOUR_CODE,
    )

    # Write the unit name
    font_size = NAME_BOX_SIZE_Y - (2 * NAME_BOX_MARGIN)
    logging.info("Font size is %s", font_size)

    font = ImageFont.truetype(
        str(ROOT_FOLDER / "SourceSansPro-SemiBold.ttf"),
        size=font_size,
    )

    name_box.text(
        (NAME_BOX_X + NAME_BOX_MARGIN, NAME_BOX_Y + NAME_BOX_SIZE_Y / 2),
        name,
        font=font,
        fill=(1, 0, 0),
        anchor="lm",
    )

    # Add the unit icon
    icon_file = UNIT_ICON_FOLDER / (type_.lower() + ".png")
    if not icon_file.exists():
        raise RuntimeError("No unit icon found: ", type_)

    with Image.open(icon_file) as icon_im:
        icon_im = icon_im.crop(icon_im.getbbox())
        scaling_factor = (NAME_BOX_SIZE_Y - 2 * NAME_BOX_MARGIN) / icon_im.height
        logging.info("Rescale icon %s with factor %s", icon_file, scaling_factor)
        rescaled_icon = ImageOps.scale(icon_im, scaling_factor)

        extreme_x = NAME_BOX_X + NAME_BOX_SIZE_X - NAME_BOX_MARGIN
        extreme_y = NAME_BOX_Y + NAME_BOX_SIZE_Y - NAME_BOX_MARGIN

        image.paste(
            rescaled_icon,
            (
                extreme_x - rescaled_icon.width,
                extreme_y - rescaled_icon.height,
                extreme_x,
                extreme_y,
            ),
            rescaled_icon,
        )

    return image


STAT_BOX_X = 20
STAT_BOX_Y = 100
STAT_BOX_SIZE_X = 170
STAT_BOX_SIZE_Y = 430
STAT_BOX_FONT_SIZE = 45
STAT_BOX_MARGIN = 5
STAT_ICON_FOLDER = ROOT_FOLDER / "images" / "stat_icons"


def draw_stat_box(
    move: str,
    attacks: str,
    range_: str,
    hits: str,
    save: str,
) -> Image:
    image = Image.new("RGBA", CARD_SIZE, (255, 0, 0, 0))

    # Draw a half-opaque rectangle
    box = ImageDraw.Draw(image)
    box.rectangle(
        [
            STAT_BOX_X,
            STAT_BOX_Y,
            STAT_BOX_SIZE_X + STAT_BOX_X,
            STAT_BOX_SIZE_Y + STAT_BOX_Y,
        ],
        fill=COLOUR_CODE,
    )

    # Draw lines
    for index in range(1, 5):
        y_position = (
            STAT_BOX_Y
            + STAT_BOX_MARGIN
            + (2 * index) * ((STAT_BOX_SIZE_Y - 2 * STAT_BOX_MARGIN) / 10)
        )
        box.line(
            (
                STAT_BOX_X + STAT_BOX_MARGIN,
                y_position,
                STAT_BOX_X + STAT_BOX_SIZE_X - STAT_BOX_MARGIN,
                y_position,
            ),
            fill=(1, 0, 0),
        )

    # Add icons
    for index, icon in enumerate(["move", "attacks", "range", "hits", "save"]):
        x_position = int(STAT_BOX_X + (STAT_BOX_SIZE_X / 4))
        y_position = int(
            STAT_BOX_Y
            + STAT_BOX_MARGIN
            + (1 + 2 * index) * ((STAT_BOX_SIZE_Y - 2 * STAT_BOX_MARGIN) / 10)
        )
        icon_file = STAT_ICON_FOLDER / (icon + ".png")
        with Image.open(icon_file) as icon_im:
            icon_im = icon_im.crop(icon_im.getbbox())
            scaling_factor = 35 / icon_im.height
            logging.info("Rescale icon %s with factor %s", icon_file, scaling_factor)
            rescaled_icon = ImageOps.scale(icon_im, scaling_factor)
        image.paste(
            rescaled_icon,
            (
                x_position - rescaled_icon.width // 2,
                y_position - rescaled_icon.height // 2,
            ),
            rescaled_icon,
        )

    # Write the stats
    font = ImageFont.truetype(
        str(ROOT_FOLDER / "SourceSansPro-SemiBold.ttf"),
        size=STAT_BOX_FONT_SIZE,
    )

    for index, stat in enumerate([move, attacks, range_, hits, save]):
        y_position = (
            STAT_BOX_Y
            + STAT_BOX_MARGIN
            + (1 + 2 * index) * ((STAT_BOX_SIZE_Y - 2 * STAT_BOX_MARGIN) / 10)
        )
        box.text(
            (STAT_BOX_X + (3 * STAT_BOX_SIZE_X / 4), y_position),
            stat,
            font=font,
            fill=(1, 0, 0),
            anchor="mm",
        )
    return image


TEXT_BOX_X = 20
TEXT_BOX_Y = 600
TEXT_BOX_SIZE_X = 1010
TEXT_BOX_SIZE_Y = 130
TEXT_BOX_MARGIN = 10
TEXT_BOX_FONT_SIZE = 30


def draw_text_box(notes: str, flavour: str) -> Image:
    image = Image.new("RGBA", CARD_SIZE, (255, 0, 0, 0))

    # Draw a half-opaque rectangle
    box = ImageDraw.Draw(image)
    box.rectangle(
        [
            TEXT_BOX_X,
            TEXT_BOX_Y,
            TEXT_BOX_SIZE_X + TEXT_BOX_X,
            TEXT_BOX_SIZE_Y + TEXT_BOX_Y,
        ],
        fill=COLOUR_CODE,
    )
    # Write the notes
    font = ImageFont.truetype(
        str(ROOT_FOLDER / "SourceSansPro-SemiBold.ttf"),
        size=TEXT_BOX_FONT_SIZE,
    )

    box.text(
        (TEXT_BOX_X + TEXT_BOX_MARGIN, TEXT_BOX_Y + TEXT_BOX_MARGIN),
        notes,
        font=font,
        fill=(1, 0, 0),
        anchor="lt",
    )
    return image


def generate_card(unit: Unit) -> None:
    for index, infile in enumerate(unit.images):
        card_image = Image.new("RGBA", CARD_SIZE)

        # Copy generated parts onto final image
        for image, box, has_transparency in [
            (fit_background_image(infile), (0, 0), False),
            (get_flag(unit.country), (964, 14), True),
            (draw_name_box(unit.name, unit.arm), (0, 0), True),
            (
                draw_stat_box(
                    unit.move, unit.attacks, unit.range, unit.hits, unit.save
                ),
                (0, 0),
                True,
            ),
            (draw_text_box(unit.notes, unit.flavour), (0, 0), True),
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
