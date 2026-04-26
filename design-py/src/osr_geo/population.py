"""WorldPop population-density layer for the demand grid.

Anchor-driven demand alone systematically under-counts residential
neighbourhoods in the developing world: a suburb full of houses with
no shops or schools mapped on OSM looks empty to the planner. A
population raster fixes that — every cell with people gets demand
proportional to local population density, regardless of whether OSM
has tagged any amenities there.

We use WorldPop "constrained" 2020 rasters (CC-BY 4.0). They are
~14 MB per country, 100 m resolution, and constrain population to
detected built-up areas — a better fit for urban planning than the
unconstrained variant which spreads density across all settled land.

Source URL pattern (verified working as of 2026-04):
    https://data.worldpop.org/GIS/Population/Global_2000_2020_Constrained/
        2020/BSGM/{ISO3}/{iso3}_ppp_2020_constrained.tif

Reading: rasterio handles the GeoTIFF + EPSG:4326 → lat/lon math.
We only sample inside each city's bbox so the raster reads are tiny.
"""

from __future__ import annotations

import logging
from pathlib import Path

import numpy as np

log = logging.getLogger(__name__)


# ISO-2 → ISO-3 for the WorldPop URL path. Add countries as the
# pipeline expands — operators will hit a clear KeyError when a
# missing one is processed, which is what we want.
_ISO2_TO_ISO3 = {
    "IQ": "IRQ",
    "IR": "IRN",
    "SA": "SAU",
    "SY": "SYR",
    "JO": "JOR",
    "EG": "EGY",
    "AE": "ARE",
    "TR": "TUR",
    "PK": "PAK",
    "IN": "IND",
    "BD": "BGD",
    "ID": "IDN",
    "NG": "NGA",
    "KE": "KEN",
    "ET": "ETH",
    "TN": "TUN",
    "MA": "MAR",
    "DZ": "DZA",
    "NE": "NER",
    "ZA": "ZAF",
    "GH": "GHA",
    "FR": "FRA",
    "DE": "DEU",
    "ES": "ESP",
    "PL": "POL",
    "EC": "ECU",
    "CO": "COL",
    "MX": "MEX",
    "BR": "BRA",
    "PE": "PER",
    "BO": "BOL",
    "SV": "SLV",
    "HN": "HND",
    "GT": "GTM",
    "NI": "NIC",
    "PH": "PHL",
    "VN": "VNM",
    "TH": "THA",
    "MY": "MYS",
    "MM": "MMR",
    "KH": "KHM",
    "LA": "LAO",
    "PK": "PAK",
    "AF": "AFG",
    "LK": "LKA",
    "NP": "NPL",
    "TZ": "TZA",
    "UG": "UGA",
    "RW": "RWA",
    "BI": "BDI",
    "MZ": "MOZ",
    "MG": "MDG",
    "ML": "MLI",
    "BF": "BFA",
    "SN": "SEN",
    "CI": "CIV",
    "GH": "GHA",
    "CM": "CMR",
    "CD": "COD",
    "AO": "AGO",
    "ZW": "ZWE",
    "ZM": "ZMB",
    "SD": "SDN",
    "SS": "SSD",
    "YE": "YEM",
    "SY": "SYR",
    "JO": "JOR",
    "LB": "LBN",
    "PS": "PSE",
    "GN": "GIN",
    "SO": "SOM",
    "ZM": "ZMB",
    "BF": "BFA",
}


def iso3_for(country: str) -> str | None:
    """Return ISO-3 for a country code (ISO-2 in, ISO-3 out)."""
    if len(country) == 3:
        return country.upper()
    return _ISO2_TO_ISO3.get(country.upper())


_WORLDPOP_VARIANTS = (
    # (url-suffix relative to base, local filename suffix). The
    # constrained-2020 layer (clipped to settled pixels) has the best
    # signal quality but ~10% of countries are missing — fall back to
    # the unconstrained 2020 layer, then to the older Global_2000_2020
    # 100m mastergrid which has full ISO-3 coverage.
    (
        "Global_2000_2020_Constrained/2020/BSGM/{iso3}/"
        "{iso3l}_ppp_2020_constrained.tif",
        "_ppp_2020_constrained.tif",
    ),
    (
        "Global_2000_2020/2020/{iso3}/"
        "{iso3l}_ppp_2020.tif",
        "_ppp_2020.tif",
    ),
)


def fetch_population_raster(country: str, cache_dir: Path) -> Path | None:
    """Download (or reuse a cached) WorldPop raster for the country.

    Tries the constrained-2020 layer first; falls back to unconstrained
    2020 if WorldPop has no constrained-coverage tile for that country
    (KEN, NER and several other African nations are 404 on the
    constrained layer). Returns the local file path or None if every
    variant 404s.
    """
    iso3 = iso3_for(country)
    if iso3 is None:
        log.warning("no ISO-3 mapping for country %r — skipping pop raster", country)
        return None

    cache_dir.mkdir(parents=True, exist_ok=True)
    iso3l = iso3.lower()

    import urllib.request

    for path_template, suffix in _WORLDPOP_VARIANTS:
        out = cache_dir / f"{iso3l}{suffix}"
        if out.exists() and out.stat().st_size > 0:
            return out

        url = (
            "https://data.worldpop.org/GIS/Population/"
            + path_template.format(iso3=iso3, iso3l=iso3l)
        )
        log.info("downloading WorldPop %s → %s", iso3, out.name)
        tmp = out.with_suffix(out.suffix + ".part")
        try:
            urllib.request.urlretrieve(url, tmp)
            tmp.rename(out)
            return out
        except Exception as e:  # noqa: BLE001
            log.warning(
                "WorldPop fetch failed for %s (%s): %s",
                iso3, suffix.lstrip("_"), e,
            )
            if tmp.exists():
                tmp.unlink()
            continue

    log.warning(
        "no WorldPop raster available for %s after trying %d variants — "
        "falling back to anchor-only demand",
        iso3, len(_WORLDPOP_VARIANTS),
    )
    return None


def sample_population_into_grid(
    raster_path: Path,
    bbox_south: float,
    bbox_west: float,
    bbox_north: float,
    bbox_east: float,
    height: int,
    width: int,
) -> np.ndarray:
    """Read the population raster, clip to bbox, and resample onto
    the city's (height × width) cell grid.

    Returns a float32 array, units = persons per WorldPop pixel
    (~100 m × cos(lat) × 100 m). Cells outside data extent or in
    NoData regions are zero.
    """
    import rasterio
    from rasterio.windows import from_bounds
    from rasterio.warp import reproject, Resampling

    with rasterio.open(raster_path) as src:
        # WorldPop is in EPSG:4326 (lat/lon degrees). bbox is the same.
        try:
            window = from_bounds(
                bbox_west, bbox_south, bbox_east, bbox_north, src.transform
            )
            data = src.read(1, window=window, boundless=True, fill_value=0.0)
            window_transform = src.window_transform(window)
        except Exception as e:  # noqa: BLE001
            log.warning("pop raster window read failed: %s", e)
            return np.zeros((height, width), dtype=np.float32)

        # Replace NoData with 0.
        nodata = src.nodata
        if nodata is not None:
            data = np.where(data == nodata, 0.0, data)
        data = np.asarray(data, dtype=np.float32)
        data = np.where(np.isfinite(data), data, 0.0)

        # Build the destination affine: lat/lon → grid (row, col).
        # Bbox runs west→east in lon, north→south in row.
        from rasterio.transform import from_bounds as build_transform
        dst_transform = build_transform(
            bbox_west, bbox_south, bbox_east, bbox_north, width, height
        )
        dst = np.zeros((height, width), dtype=np.float32)
        reproject(
            source=data,
            destination=dst,
            src_transform=window_transform,
            src_crs=src.crs,
            dst_transform=dst_transform,
            dst_crs=src.crs,
            resampling=Resampling.average,
        )
        return dst


def population_demand_layer(
    pop: np.ndarray,
    sigma_cells: float,
) -> np.ndarray:
    """Convert raw population counts into a smoothed demand layer.

    Steps:
      1. log1p compression — a 50k-person cell shouldn't completely
         dominate a 5k-person one (real ridership grows sub-linearly
         with raw density).
      2. Gaussian smooth — a station serves passengers walking from
         within ~600 m, so demand is the *integral* over a walkshed,
         not the value at a single 100 m cell.
      3. Normalise to [0, 1] so it composes with the existing anchor
         layer in `build_demand_surface`.
    """
    if pop.size == 0 or pop.max() <= 0:
        return np.zeros_like(pop, dtype=np.float32)

    compressed = np.log1p(pop).astype(np.float32)

    # Cheap separable Gaussian via cumulative sums.
    smoothed = _gaussian_blur(compressed, sigma=max(0.5, sigma_cells))

    vmax = smoothed.max()
    if vmax > 0:
        smoothed /= vmax
    return smoothed


def _gaussian_blur(arr: np.ndarray, sigma: float) -> np.ndarray:
    """Tiny separable Gaussian blur. Avoids depending on scipy."""
    radius = max(1, int(round(3.0 * sigma)))
    xs = np.arange(-radius, radius + 1, dtype=np.float32)
    kern = np.exp(-(xs * xs) / (2.0 * sigma * sigma))
    kern /= kern.sum()

    # Pad with edge-replicated values so the city-edge demand is not
    # artificially suppressed.
    padded = np.pad(arr, ((0, 0), (radius, radius)), mode="edge")
    blurred = np.zeros_like(arr, dtype=np.float32)
    for i, k in enumerate(kern):
        blurred += k * padded[:, i : i + arr.shape[1]]

    padded = np.pad(blurred, ((radius, radius), (0, 0)), mode="edge")
    out = np.zeros_like(arr, dtype=np.float32)
    for i, k in enumerate(kern):
        out += k * padded[i : i + arr.shape[0], :]
    return out
