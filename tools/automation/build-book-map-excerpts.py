"""Render reader-facing excerpts from the tracked city outline maps.

The city source maps carry machine receipts in their bottom margin. This
publication derivative preserves the route, legend and planning-status line
while leaving the machine footer to the separate ebook receipt.
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
import sys

import cairosvg
from PIL import Image


ROOT = Path(__file__).resolve().parents[2]
MAPS = {
    "samawah": "west-asia/Iraq/Samawah",
    "baghdad": "west-asia/Iraq/Baghdad",
    "basra": "west-asia/Iraq/Basra",
    "erbil": "west-asia/Iraq/Erbil",
    "amman": "west-asia/Jordan/Amman",
    "karachi": "south-asia/Pakistan/Karachi",
    "nairobi": "east-africa/Kenya/Nairobi",
    "lusaka": "east-africa/Zambia/Lusaka",
    "cuenca": "latin-america/Ecuador/Cuenca",
    "san-salvador": "latin-america/El Salvador/San-Salvador",
}


def render(name: str, city: str) -> bytes:
    source = ROOT / "cities/catalogue" / city / "engineering/outline/network.svg"
    png = cairosvg.svg2png(url=str(source), output_width=1400, output_height=1050)
    with Image.open(BytesIO(png)) as image:
        image = image.convert("RGB").crop((0, 0, 1400, 952))
        result = BytesIO()
        image.save(result, format="WEBP", quality=88, method=6)
    return result.getvalue()


def main(check: bool = False) -> int:
    target = ROOT / "docs/book/images"
    target.mkdir(parents=True, exist_ok=True)
    failures = []
    for name, city in MAPS.items():
        path = target / f"city-{name}.webp"
        content = render(name, city)
        if check:
            if not path.exists() or path.read_bytes() != content:
                failures.append(name)
        else:
            path.write_bytes(content)
    if failures:
        print("Map excerpts differ: " + ", ".join(failures), file=sys.stderr)
        return 1
    print(f"{'verified' if check else 'rendered'} {len(MAPS)} city map excerpts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main("--check" in sys.argv[1:]))
