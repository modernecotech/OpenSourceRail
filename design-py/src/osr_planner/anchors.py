"""Demand anchors — what OSR tries to connect.

An "anchor" is any OSM feature that represents passenger demand:
residential neighbourhoods, universities, hospitals, markets,
railway stations, major workplaces. Each anchor gets a numeric
weight reflecting its relative pull on rail traffic:

- Railway station / airport / major intermodal hub: 100
- University: 80
- Hospital: 60
- Market / shopping mall: 40
- Suburb (larger than a neighbourhood): 20
- Neighbourhood: 10

These weights are tuned to match real-world demand ratios — a
university is about an order of magnitude less daily-trip-
generator than an intermodal rail hub, but more than a single
neighbourhood. Operators can override per-city if local data
warrants.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

OVERPASS_ENDPOINT = "https://overpass-api.de/api/interpreter"

# Default demand-generator weights by OSM anchor kind.
#
# Tuned against real-world demand ratios + OSM data quality:
# - Railway station / airport / university: singular, unambiguous.
# - "Hospital" is often mis-tagged (pharmacies + clinics land here
#   in many MENA cities) — weight kept moderate so it doesn't
#   crowd out neighbourhood coverage.
# - Neighbourhood / city: the backbone of coverage. Bumped up so
#   a 220 k-person city with 100+ neighbourhoods gets realistic
#   station density.
DEFAULT_WEIGHTS: dict[str, float] = {
    "railway-station":    100.0,
    "intermodal":         95.0,
    "airport":            90.0,
    "university":         80.0,
    "city":               70.0,
    "suburb":             40.0,
    "hospital":           35.0,
    "mall":               30.0,
    "marketplace":        22.0,
    "neighbourhood":      18.0,
}


@dataclass(frozen=True)
class Anchor:
    """One demand anchor with its demand weight."""

    kind: str
    name: str
    lat: float
    lon: float
    weight: float


def fetch_anchors(
    bbox: tuple[float, float, float, float],
    cache_dir: Path,
) -> list[Anchor]:
    """Return all anchor points inside `bbox` from Overpass. Cached by
    bbox hash so repeated calls are offline."""
    import requests

    south, west, north, east = bbox
    key = hashlib.sha256(
        f"{south},{west},{north},{east}:anchors:v1".encode()
    ).hexdigest()[:16]
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / f"anchors-{key}.json"

    if cache_path.exists():
        raw = json.loads(cache_path.read_text())
    else:
        q = f"""
        [out:json][timeout:180];
        (
          node["amenity"="university"]({south},{west},{north},{east});
          way["amenity"="university"]({south},{west},{north},{east});
          node["amenity"="hospital"]({south},{west},{north},{east});
          way["amenity"="hospital"]({south},{west},{north},{east});
          node["amenity"="marketplace"]({south},{west},{north},{east});
          node["shop"="mall"]({south},{west},{north},{east});
          node["railway"="station"]({south},{west},{north},{east});
          way["railway"="station"]({south},{west},{north},{east});
          node["aeroway"="aerodrome"]({south},{west},{north},{east});
          node["place"~"^(city|town|suburb|neighbourhood)$"]({south},{west},{north},{east});
        );
        (._;>;);
        out body;
        """
        r = requests.post(
            OVERPASS_ENDPOINT,
            data=q,
            headers={"User-Agent": "OpenSourceRail-planner/0.1"},
            timeout=240,
        )
        r.raise_for_status()
        raw = r.json()
        cache_path.write_text(json.dumps(raw))

    return _parse_anchors(raw)


def _parse_anchors(data: dict) -> list[Anchor]:
    """Decode an Overpass JSON blob into [`Anchor`] rows."""
    nodes = {
        e["id"]: (e.get("lat"), e.get("lon"))
        for e in data["elements"]
        if e["type"] == "node"
    }

    def centroid(e: dict) -> tuple[float, float] | None:
        pts = [
            nodes[n]
            for n in e.get("nodes", [])
            if n in nodes and nodes[n][0] is not None
        ]
        if not pts:
            return None
        return (
            sum(p[0] for p in pts) / len(pts),
            sum(p[1] for p in pts) / len(pts),
        )

    out: list[Anchor] = []
    kind_index: dict[str, int] = {}
    for e in data["elements"]:
        tags = e.get("tags") or {}
        # Prefer English; fall back to transliterated local name;
        # final fallback is a synthetic `<kind>-<n>` name. GUIs
        # + map labels use this, so it must render in an ASCII font
        # (egui / matplotlib / staticmap all ASCII-safe).
        name_en = (
            tags.get("name:en")
            or tags.get("int_name")
            or tags.get("official_name:en")
            or tags.get("alt_name:en")
        )
        name_local = tags.get("name") or tags.get("name:ar")
        kind = _classify(tags)
        if kind is None:
            continue

        if name_en:
            name = name_en
        elif name_local:
            name = transliterate_to_latin(name_local)
            if not name:
                kind_index[kind] = kind_index.get(kind, 0) + 1
                name = f"{_kind_label(kind)} {kind_index[kind]}"
        else:
            kind_index[kind] = kind_index.get(kind, 0) + 1
            name = f"{_kind_label(kind)} {kind_index[kind]}"

        if e["type"] == "node":
            coord = (e["lat"], e["lon"])
        elif e["type"] == "way":
            coord = centroid(e)
            if coord is None:
                continue
        else:
            continue
        out.append(
            Anchor(
                kind=kind,
                name=name,
                lat=coord[0],
                lon=coord[1],
                weight=DEFAULT_WEIGHTS.get(kind, 1.0),
            )
        )
    return out


def _kind_label(kind: str) -> str:
    return {
        "railway-station": "Rail Station",
        "intermodal":      "Intermodal",
        "airport":         "Airport",
        "university":      "University",
        "hospital":        "Hospital",
        "mall":            "Mall",
        "marketplace":     "Market",
        "city":            "Centre",
        "suburb":          "Suburb",
        "neighbourhood":   "District",
    }.get(kind, "Station")


# Arabic → Latin transliteration table (simplified Buckwalter-style).
# Good enough for GUI labels; not intended as a linguistic tool.
_ARABIC_TO_LATIN: dict[str, str] = {
    "ا": "a", "أ": "a", "إ": "i", "آ": "a",
    "ب": "b", "ت": "t", "ث": "th",
    "ج": "j", "ح": "h", "خ": "kh",
    "د": "d", "ذ": "dh", "ر": "r", "ز": "z",
    "س": "s", "ش": "sh", "ص": "s", "ض": "d",
    "ط": "t", "ظ": "dh",
    "ع": "'", "غ": "gh",
    "ف": "f", "ق": "q", "ك": "k", "ل": "l",
    "م": "m", "ن": "n", "ه": "h",
    "و": "w", "ي": "y", "ى": "a", "ة": "h", "ء": "'",
    "ؤ": "w", "ئ": "y",
    "ـ": "",  # tatweel
    "ً": "", "ٌ": "", "ٍ": "", "َ": "", "ُ": "", "ِ": "", "ّ": "", "ْ": "",
}


def transliterate_to_latin(s: str) -> str:
    """Return an ASCII-only rendering of `s`. Arabic chars go through
    the _ARABIC_TO_LATIN table; anything else ASCII passes through;
    the rest is dropped."""
    out: list[str] = []
    for ch in s or "":
        if ch in _ARABIC_TO_LATIN:
            out.append(_ARABIC_TO_LATIN[ch])
        elif ord(ch) < 128:
            out.append(ch)
        # else: drop non-translatable non-ASCII.
    result = "".join(out).strip()
    # Collapse repeated spaces.
    while "  " in result:
        result = result.replace("  ", " ")
    # Title-case words for display.
    return " ".join(w.capitalize() for w in result.split()) if result else ""


# Keywords that indicate an OSM `amenity=hospital` is really a
# pharmacy / clinic / small health post — drop these from our
# hospital kind. Multilingual because OSR targets developing-nation
# cities that often have only local-language OSM tags.
_PHARMACY_HINTS = {
    "pharmacy", "clinic", "health centre", "health center", "dispensary",
    "صيدلية", "صيدلة", "عيادة",  # Arabic: pharmacy, pharmacy, clinic
    "farmacia", "farmácia",
    "clinique",
}


def _is_real_hospital(tags: dict, name: str) -> bool:
    """Filter `amenity=hospital` to exclude pharmacy / clinic mis-tags.

    Policy: require one of:
    - explicit `healthcare=hospital` tag (the newer, specific tag), OR
    - no pharmacy/clinic hint in the name.
    """
    if tags.get("healthcare") == "hospital":
        return True
    lower = (name or "").lower()
    return not any(h in lower for h in _PHARMACY_HINTS)


def _classify(tags: dict) -> str | None:
    if tags.get("railway") == "station":
        return "railway-station"
    if tags.get("aeroway") == "aerodrome":
        return "airport"
    if tags.get("amenity") == "university":
        return "university"
    if tags.get("amenity") == "hospital":
        name = (
            tags.get("name:en")
            or tags.get("name")
            or tags.get("name:ar")
            or ""
        )
        return "hospital" if _is_real_hospital(tags, name) else None
    if tags.get("shop") == "mall":
        return "mall"
    if tags.get("amenity") == "marketplace":
        return "marketplace"
    place = tags.get("place")
    if place == "city" or place == "town":
        return "city"
    if place == "suburb":
        return "suburb"
    if place == "neighbourhood":
        return "neighbourhood"
    return None


def weight_anchors(
    anchors: Iterable[Anchor],
    overrides: dict[str, float] | None = None,
) -> list[Anchor]:
    """Re-weight anchors using per-kind overrides."""
    if overrides is None:
        return list(anchors)
    return [
        Anchor(
            kind=a.kind,
            name=a.name,
            lat=a.lat,
            lon=a.lon,
            weight=overrides.get(a.kind, a.weight),
        )
        for a in anchors
    ]


def haversine_m(
    a: tuple[float, float], b: tuple[float, float]
) -> float:
    """Great-circle distance in metres."""
    la1, lo1 = math.radians(a[0]), math.radians(a[1])
    la2, lo2 = math.radians(b[0]), math.radians(b[1])
    dla, dlo = la2 - la1, lo2 - lo1
    h = math.sin(dla / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin(dlo / 2) ** 2
    return 2 * 6_371_000 * math.asin(math.sqrt(h))
