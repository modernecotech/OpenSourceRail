"""Sample public terrain, soil and surface-water rasters along the Airport study."""

import argparse
from bisect import bisect_right
from contextlib import ExitStack
from hashlib import file_digest
from itertools import accumulate, pairwise
import json
from math import ceil, cos, isclose, isfinite, radians
from pathlib import Path
import re
from tempfile import NamedTemporaryFile
from urllib.parse import urlencode
from urllib.request import urlopen

from cities.Baghdad.engineering.simulation import airport_alignment, corridor


HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "site-layers.json"
SCHEMA = "osr-baghdad-airport-site-layers/1"
INTERVAL_M = 20
WATER_RADIUS_M = 100
DEM_TILE = "Copernicus_DSM_COG_10_N33_00_E044_00_DEM"
DEM_URL = f"https://copernicus-dem-30m.s3.amazonaws.com/{DEM_TILE}/{DEM_TILE}.tif"
WATER_URL = (
    "https://s3.waw4-1.cloudferro.com/swift/v1/global-surface-water/"
    "download2024/Aggregated/VER1-5/occurrence/occurrence_40E_40N_v1_5_2024.tif"
)
TILE_LENGTHS = {"dem.tif": 45_589_100, "water.tif": 66_565_276}
SOIL_LAYERS = {
    "clay_pct": ("clay-deep.tif", "clay_100-200cm_mean"),
    "clay_0_5cm_pct": ("clay-shallow.tif", "clay_0-5cm_mean"),
    "clay_p05_pct": ("clay-deep-p05.tif", "clay_100-200cm_Q0.05"),
    "clay_p95_pct": ("clay-deep-p95.tif", "clay_100-200cm_Q0.95"),
}
SOIL_NATIVE = "clay-native-mask-check.tif"
SOIL_NATIVE_URL = (
    "https://files.isric.org/soilgrids/latest/data/clay/clay_100-200cm_mean/"
    "tileSG-010-054/tileSG-010-054_4-4.tif"
)
SAMPLE_FIELDS = {
    "ground_elevation_m", "water_occurrence_pct", "water_occurrence_100m_max_pct", *SOIL_LAYERS,
}
DEM_ATTRIBUTION = (
    "Produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and © Airbus Defence "
    "and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and ESA; all rights reserved"
)


def soil_url(coverage_id):
    query = [
        ("SERVICE", "WCS"), ("VERSION", "2.0.1"), ("REQUEST", "GetCoverage"),
        ("COVERAGEID", coverage_id), ("FORMAT", "image/tiff"),
        ("SUBSET", "x(4661000,4679000)"), ("SUBSET", "y(3701000,3710000)"),
    ]
    return "https://maps.isric.org/mapserv/clay?" + urlencode(query)


def route_points(alignment):
    """Return ordered coordinates at support spacing and each named operating stop."""
    vertices = []
    for segment in alignment["segments"]:
        points = segment["coordinates"]
        if vertices and vertices[-1] != points[0]:
            raise ValueError("GIS sampling requires a continuous rail alignment")
        vertices.extend(points[1:] if vertices else points)
    chainages = list(accumulate(
        (1000 * corridor.distance_km(a, b) for a, b in pairwise(vertices)), initial=0.0,
    ))
    route_m = alignment["route_km"] * 1000
    if not isclose(chainages[-1], route_m, abs_tol=1e-5):
        raise ValueError("GIS sampling route length differs from the alignment")
    sample_chainages = sorted({
        *(float(m) for m in range(0, ceil(route_m), INTERVAL_M)),
        *(km * 1000 for km in alignment["chainages_km"]), route_m,
    })
    samples = []
    for chainage in sample_chainages:
        index = min(bisect_right(chainages, chainage) - 1, len(vertices) - 2)
        start, end = vertices[index:index + 2]
        fraction = (chainage - chainages[index]) / (chainages[index + 1] - chainages[index])
        point = [a + fraction * (b - a) for a, b in zip(start, end, strict=True)]
        samples.append({"chainage_m": round(chainage, 6), "longitude_latitude": [round(x, 9) for x in point]})
    return samples


def check_numeric_sample(value, minimum, maximum):
    if type(value) not in (int, float) or not minimum <= value <= maximum or not isfinite(value):
        raise ValueError("GIS raster sample is outside its declared range")


def validate(data, alignment=None):
    """Keep source identity, geometry, coverage and no-data semantics with the sample."""
    alignment = airport_alignment.evaluate() if alignment is None else alignment
    if (not isinstance(data, dict) or data.get("schema") != SCHEMA or data.get("alignment_id") != alignment["alignment_id"]
            or data.get("sample_interval_m") != INTERVAL_M or data.get("water_search_radius_m") != WATER_RADIUS_M
            or data.get("route_m") != round(alignment["route_km"] * 1000, 6)):
        raise ValueError("Site-layer inputs do not match the Airport alignment")
    supplied = data.get("samples")
    if not isinstance(supplied, list):
        raise ValueError("Site-layer inputs need a sample list")
    points = route_points(alignment)
    if len(supplied) != len(points):
        raise ValueError("Site-layer samples do not cover the complete Airport alignment")
    for actual, expected in zip(supplied, points, strict=True):
        if (not isinstance(actual, dict) or actual.keys() != expected.keys() | SAMPLE_FIELDS
                or any(actual[key] != value for key, value in expected.items())):
            raise ValueError("GIS sample chainage or coordinate differs from the Airport alignment")
        check_numeric_sample(actual["ground_elevation_m"], -500, 9000)
        for name in SAMPLE_FIELDS - {"ground_elevation_m"}:
            if actual[name] is not None:
                check_numeric_sample(actual[name], 0, 100)
        p05, p95 = actual["clay_p05_pct"], actual["clay_p95_pct"]
        if p05 is not None and p95 is not None and p05 > p95:
            raise ValueError("SoilGrids clay quantiles are reversed")
        centre, nearby = actual["water_occurrence_pct"], actual["water_occurrence_100m_max_pct"]
        if centre is not None and (nearby is None or centre > nearby):
            raise ValueError("JRC water buffer must contain the centre cell")
    sources = data.get("sources", {})
    if not isinstance(sources, dict) or sources.keys() != {"terrain", "soil", "water"}:
        raise ValueError("Site-layer input must identify terrain, soil and water sources")
    for source in sources.values():
        if not all(source.get(key) for key in ("product", "version", "reference_url", "method", "units")):
            raise ValueError("GIS source is missing its product, version, reference or units")
        if not source.get("rasters"):
            raise ValueError("GIS source must identify its sampled raster objects")
        for raster in source["rasters"]:
            if (not raster.get("url", "").startswith("https://")
                    or not re.fullmatch(r"[0-9a-f]{64}", raster.get("sha256", ""))
                    or type(raster.get("bytes")) is not int or raster["bytes"] <= 0):
                raise ValueError("GIS source needs a URL, raster hash and byte size")
    fingerprint = airport_alignment.identity({key: value for key, value in data.items() if key != "record_id"})
    if data.get("record_id") != fingerprint:
        raise ValueError("Site-layer record identity does not match its data")
    return data


def load_site_layers(path=None, alignment=None):
    """Load a published local sample without GIS libraries or internet access."""
    return validate(json.loads(Path(path or FIXTURE).read_bytes()), alignment)


def raster_sources():
    return {
        "terrain": {
            "product": "Copernicus DEM GLO-30 public digital surface model",
            "version": "COG tile N33E044, AWS object last modified 2022-05-09",
            "reference_url": "https://copernicus-dem-30m.s3.amazonaws.com/readme.html",
            "attribution": DEM_ATTRIBUTION,
            "horizontal_resolution": "nominal 30 m (1 arc second)",
            "vertical_datum": "EGM2008 orthometric elevation",
            "units": "m",
            "method": "Nearest surface cell. Buildings, infrastructure and vegetation can influence elevations.",
            "rasters": [{"filename": "dem.tif", "url": DEM_URL, "sample_fields": ["ground_elevation_m"]}],
        },
        "soil": {
            "product": "ISRIC SoilGrids clay content 250 m",
            "version": "2.0 mean and prediction quantiles",
            "reference_url": "https://maps.isric.org/generated/soilgrids/clay.html",
            "licence": "CC BY 4.0",
            "horizontal_resolution": "250 m",
            "units": "percentage of dry fine-earth mass",
            "method": (
                "Native-grid WCS crop and nearest cell. Divide stored g/kg by ten. "
                "The WCS crops omit the native no-data marker. The native deep mean tile confirms "
                "the sampled values and identifies missing cells. All four crops return zero on "
                "those missing cells. Clay prediction is a texture proxy."
            ),
            "rasters": [{
                "filename": filename, "url": soil_url(coverage), "coverage_id": coverage,
                "sample_fields": [name],
            } for name, (filename, coverage) in SOIL_LAYERS.items()] + [{
                "filename": SOIL_NATIVE, "url": SOIL_NATIVE_URL,
                "purpose": "Validate deep mean samples and recover the native soil coverage mask",
                "sample_fields": ["clay_pct"],
            }],
        },
        "water": {
            "product": "JRC Global Surface Water occurrence",
            "version": "1.5, 1984–2024, tile 40E_40N",
            "reference_url": "https://global-surface-water.appspot.com/download",
            "attribution": "Source: EC JRC/Google. Pekel et al. (2016), doi:10.1038/nature20584.",
            "horizontal_resolution": "nominal 30 m (0.00025° in the delivered tile)",
            "units": "historical water occurrence percentage normalised by calendar month",
            "method": (
                "Nearest cell and maximum valid observation occurrence among pixel centres within 100 m. "
                "255 is no data. Roads and bridges can obscure underlying water in this surface layer."
            ),
            "rasters": [{"filename": "water.tif", "url": WATER_URL,
                         "sample_fields": ["water_occurrence_pct", "water_occurrence_100m_max_pct"]}],
        },
    }


def raster_sample(dataset, points, *, scale=1.0, valid_range=None):
    from numpy.ma import getmaskarray
    from rasterio.warp import transform

    longitudes, latitudes = zip(*points, strict=True)
    x_values, y_values = transform("EPSG:4326", dataset.crs, list(longitudes), list(latitudes))
    values = []
    for cell in dataset.sample(zip(x_values, y_values, strict=True), masked=True):
        if getmaskarray(cell)[0]:
            values.append(None)
            continue
        value = float(cell[0]) * scale
        values.append(round(value, 4) if valid_range is None or valid_range[0] <= value <= valid_range[1] else None)
    return values


def water_nearby(dataset, point):
    from numpy.ma import getmaskarray
    from rasterio.windows import Window

    if dataset.crs.to_epsg() != 4326:
        raise ValueError("Surface water buffer expects the native JRC WGS84 raster")
    row, col = dataset.index(*point)
    width_m = abs(dataset.transform.a) * 111000 * cos(radians(point[1]))
    height_m = abs(dataset.transform.e) * 111000
    col_pad, row_pad = ceil(WATER_RADIUS_M / width_m) + 1, ceil(WATER_RADIUS_M / height_m) + 1
    window = Window(col - col_pad, row - row_pad, 2 * col_pad + 1, 2 * row_pad + 1)
    cells = dataset.read(1, window=window, boundless=True, masked=True)
    missing = getmaskarray(cells)
    grid = dataset.window_transform(window)
    highest = None
    for i, line in enumerate(cells):
        for j, cell in enumerate(line):
            if not missing[i, j] and 0 <= cell <= 100 and (highest is None or cell > highest):
                centre = grid * (j + 0.5, i + 0.5)
                if 1000 * corridor.distance_km(point, centre) <= WATER_RADIUS_M:
                    highest = int(cell)
    return highest


def generate(directory, alignment=None):
    """Make a compact candidate-bound sample from original provider raster objects."""
    import rasterio

    alignment = airport_alignment.evaluate() if alignment is None else alignment
    samples = route_points(alignment)
    points = [row["longitude_latitude"] for row in samples]
    sources = raster_sources()
    with ExitStack() as resources:
        for kind, group in sources.items():
            for raster in group["rasters"]:
                path = directory / raster["filename"]
                with path.open("rb") as stream:
                    raster["sha256"] = file_digest(stream, "sha256").hexdigest()
                raster["bytes"] = path.stat().st_size
                if path.name in TILE_LENGTHS and raster["bytes"] != TILE_LENGTHS[path.name]:
                    raise ValueError(f"Unexpected file size for the bound source raster: {path}")
                dataset = resources.enter_context(rasterio.open(path))
                if not dataset.crs or dataset.count != 1:
                    raise ValueError(f"Expected one georeferenced band in {path}")
                name = raster["sample_fields"][0]
                values = raster_sample(dataset, points, scale=0.1 if kind == "soil" else 1.0,
                                       valid_range=(0, 100) if kind != "terrain" else None)
                for row, value in zip(samples, values, strict=True):
                    if path.name == SOIL_NATIVE:
                        if value is None and all(row[field] == 0 for field in SOIL_LAYERS):
                            row.update({field: None for field in SOIL_LAYERS})
                        elif value != row["clay_pct"]:
                            raise ValueError("SoilGrids WCS deep mean differs from the native tile")
                        continue
                    row[name] = value
                    if kind == "water":
                        row["water_occurrence_100m_max_pct"] = water_nearby(dataset, row["longitude_latitude"])
    record = {
        "schema": SCHEMA, "alignment_id": alignment["alignment_id"],
        "route_m": round(alignment["route_km"] * 1000, 6),
        "sample_interval_m": INTERVAL_M, "water_search_radius_m": WATER_RADIUS_M,
        "sources": sources, "samples": samples,
    }
    record["record_id"] = airport_alignment.identity(record)
    return validate(record, alignment)


def acquire(directory):
    """Fetch raster objects into an ignored cache before sampling."""
    directory.mkdir(parents=True, exist_ok=True)
    for group in raster_sources().values():
        for raster in group["rasters"]:
            target = directory / raster["filename"]
            expected = TILE_LENGTHS.get(target.name)
            if target.is_file() and (expected is None or target.stat().st_size == expected):
                continue
            maximum = {"dem.tif": 60_000_000, "water.tif": 75_000_000}.get(target.name, 1_000_000)
            with NamedTemporaryFile(dir=directory, delete=False) as temporary:
                staging = Path(temporary.name)
                try:
                    with urlopen(raster["url"], timeout=45) as response:
                        written = 0
                        while chunk := response.read(256 * 1024):
                            written += len(chunk)
                            if written > maximum:
                                raise ValueError(f"Raster exceeds the download limit: {target.name}")
                            temporary.write(chunk)
                    if expected is not None and written != expected:
                        raise ValueError(f"Download differs from the bound raster size: {target.name}")
                    temporary.close()
                    staging.replace(target)
                finally:
                    staging.unlink(missing_ok=True)


def encode(record):
    header = {key: value for key, value in record.items() if key != "samples"}
    samples = ",\n".join("    " + json.dumps(row, allow_nan=False) for row in record["samples"])
    return json.dumps(header, indent=2, ensure_ascii=False)[:-2] + ',\n  "samples": [\n' + samples + "\n  ]\n}\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cache", type=Path, default=Path("build/airport-site-layers"))
    parser.add_argument("--output", type=Path, default=FIXTURE)
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--check", action="store_true")
    options = parser.parse_args()
    if options.download:
        from engineering.performance import disk_reservation

        with disk_reservation(airport_alignment.ROOT, airport_alignment.ROOT, "sample Airport public GIS",
                              145_000_000):
            acquire(options.cache)
    result = generate(options.cache)
    if options.check:
        if load_site_layers(options.output) != result:
            raise SystemExit("Site-layer publication differs from the bound rasters")
    else:
        with NamedTemporaryFile(dir=options.output.parent, delete=False) as temporary:
            staging = Path(temporary.name)
            try:
                temporary.write(encode(result).encode())
                temporary.close()
                staging.chmod(0o644)
                staging.replace(options.output)
            finally:
                staging.unlink(missing_ok=True)
    print(f"{options.output}: {len(result['samples'])} samples, {result['record_id']}")


if __name__ == "__main__":
    main()
