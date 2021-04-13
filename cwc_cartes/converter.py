import json
import logging
import re
from argparse import ArgumentParser
from pathlib import Path

NAME_PATTERN = re.compile(r"^(.*) \((.*)\)$")

ARM_FROM_NAME = {
    "FAO": "fao",
    "FAC": "fac",
    "IFV unit": "ifv",
    "RR": "rr",
    "ATGW": "atgw",
    "Mortar": "mortar",
    "Bridging": "bridging",
    "Mine Clearer": "mine_clearer",
    "Infantry Upgrade": "infantry_upgrade",
    "SPG Unit": "spg",
    "SPAT Unit": "spat",
    "ATGW Unit": "atgw_unit",
    "AA": "aa",
    "SAM": "sam",
    "Attack Helicopter": "attack_helicopter",
    "Truck": "truck",
    "Helicopter": "transport_helicopter",
}


def main():
    logging.basicConfig(level=logging.WARNING)
    parser = ArgumentParser(description="Generate JSON from raw data")
    parser.add_argument(
        "file",
        type=Path,
        help="file containing the raw data",
    )
    parser.add_argument("country", type=str, help="country concerned by those raw data")
    parser.add_argument("army", type=str, help="army list name")
    parser.add_argument("output", type=Path, help="output JSON file")

    args = parser.parse_args()
    if not (args.file.exists() and args.file.is_file()):
        raise RuntimeError("File not found")

    data = []
    stats = []

    with args.file.open(encoding="utf-8") as raw_data_file:
        for index, line in enumerate(raw_data_file.readlines(), 1):
            stats.append(str(line).replace("\n", "").strip())
            if index and index % 9 == 0:
                logging.info(stats)
                name, arm, move, combat, hits, save, _, _, notes = stats

                name_match = NAME_PATTERN.match(name)
                if name_match:
                    first, second = name_match.groups()
                    if first in ARM_FROM_NAME:

                        arm = ARM_FROM_NAME[first]
                    elif "," in second:
                        arm, name = [x.strip() for x in second.split(",", 1)]
                    elif arm.lower() != "command":
                        name = second

                if "/" in combat:
                    attacks, range_ = combat.split("/")
                else:
                    attacks = combat
                    range_ = "-"

                stats = []
                data.append(
                    {
                        "country": args.country,
                        "army": args.army,
                        "name": name,
                        "arm": arm.lower(),
                        "move": move,
                        "attacks": attacks,
                        "range": range_,
                        "hits": hits,
                        "save": save,
                        "notes": notes if notes != "-" else "",
                        "flavour": "",
                        "images": [],
                    }
                )

    json_file: Path = args.output
    args.output.parent.mkdir(exist_ok=True)

    json.dump(data, json_file.open("w"), indent=4)


if __name__ == "__main__":
    main()
