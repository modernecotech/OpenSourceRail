"""Publish both full central Baghdad lines on their own map and GIS layer."""

from io import BytesIO
from math import cos, radians

COLORS = {"C1": "#106e62", "C2": "#793975"}
# Offset labels around the denser river and interchange approaches.
LABELS = {
    "Mansour": ("Al Mansour", 4, -15, "left"),
    "Zawraa": ("Al Zawraa", -3, -15, "center"),
    "Allawi": ("Allawi / Central Station", -7, 11, "right"),
    "Museum": ("Iraq Museum", 8, -12, "left"),
    "Karkh": ("Karkh / Haifa St", -9, 11, "right"),
    "Tahrir": ("Tahrir Square", 1, 12, "center"),
    "Kilani": ("Al Kilani", 5, 10, "left"),
    "East-approach": ("Al Muthanna St", -5, 12, "center"),
    "Zayouna": ("Zayouna", -3, -17, "center"),
    "Mustansiriya": ("Al Mustansiriya", 7, -13, "left"),
    "Bab": ("Bab al-Muadham", -5, 14, "left"),
    "Medical": ("Medical City", -3, 12, "right"),
    "Mutanabbi": ("Mutanabbi Street", -7, 9, "right"),
    "Shorja": ("Al-Shorja market", 2, 12, "center"),
    "Saadoun": ("Al Saadoun", 9, 7, "left"),
    "Firdos": ("Firdos Square", 10, -1, "left"),
    "Karrada": ("Central Karrada", 10, 1, "left"),
    "Jadriya": ("Jadriya", 5, -14, "left"),
    "University": ("University of Baghdad", 7, 0, "left"),
}


def geojson(record):
    """Export only the central study, with physical IDs and line memberships."""
    study = record["central_study"]
    stations = study["stations"]
    features = []
    for line_id, line in study["lines"].items():
        stops = line["station_ids"]
        if [line["geometry"][i] for i in (0, -1)] != [stations[stops[i]]["coordinates"] for i in (0, -1)]:
            raise ValueError("Central route line must extend to both terminal station markers")
        features.append({
            "type": "Feature", "id": line_id,
            "properties": {"name": line["name"], "role": "proposed line", "stations_in_order": stops,
                           "route_km": line["one_way_km"], "headway_minutes": study["headway_s"] / 60,
                           "color": COLORS[line_id]},
            "geometry": {"type": "LineString", "coordinates": line["geometry"]},
        })
    for key, station in stations.items():
        served = [line_id for line_id, line in study["lines"].items() if key in line["station_ids"]]
        if not served:
            raise ValueError("A proposed station must have an end-to-end service")
        features.append({
            "type": "Feature", "id": key,
            "properties": {"name": station["name"], "role": "proposed interchange" if len(served) > 1
                           else "proposed stop", "lines": served, "source": station["source"],
                           "site_basis": station["basis"]},
            "geometry": {"type": "Point", "coordinates": station["coordinates"]},
        })
    return {"type": "FeatureCollection", "name": "Central Baghdad two-line study", "features": features,
            "candidate_id": study["candidate_id"], "evaluation_id": record["evaluation_id"]}


def source_geometry(context):
    """Read only the major road and water geometry needed for the city map."""
    water, rivers, roads = [], [], []
    for feature in context["layers"]["water"]:
        shape = feature["geometry"]
        if shape["type"] == "Polygon":
            water.append(shape["coordinates"][0])
        elif shape["type"] == "MultiPolygon":
            water.extend(poly[0] for poly in shape["coordinates"])
        elif feature["properties"].get("name:en") == "Tigris River":
            if shape["type"] == "LineString":
                rivers.append(shape["coordinates"])
            elif shape["type"] == "MultiLineString":
                rivers.extend(shape["coordinates"])
    for feature in context["layers"]["roads"]:
        if feature["properties"]["kind"] not in {"major_road", "highway"}:
            continue
        shape = feature["geometry"]
        if shape["type"] == "LineString":
            roads.append(shape["coordinates"])
        elif shape["type"] == "MultiLineString":
            roads.extend(shape["coordinates"])
    return water, rivers, roads


def image(record, data, context):
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import pyplot as plt
    from matplotlib.collections import LineCollection, PatchCollection
    from matplotlib.lines import Line2D
    from matplotlib.patches import Polygon

    study = record["central_study"]
    alignment = [f for f in data["features"] if f["geometry"]["type"] == "LineString"]
    stations = [f for f in data["features"] if f["geometry"]["type"] == "Point"]
    fig = plt.figure(figsize=(12.5, 10.2), facecolor="#fcfaf4")
    axes = fig.add_axes((.045, .105, .91, .755), facecolor="#f7f5ed")
    water, rivers, roads = source_geometry(context)
    axes.add_collection(PatchCollection([Polygon(poly, closed=True) for poly in water],
                                        facecolor="#c6e2e9", edgecolor="none", zorder=1))
    axes.add_collection(LineCollection(rivers, colors="#abd3df", linewidths=1.5, zorder=1.1))
    axes.add_collection(LineCollection(roads, colors="#c6baa7", linewidths=.64, alpha=.62, zorder=2))
    for feature in alignment:
        coordinates = list(zip(*feature["geometry"]["coordinates"], strict=True))
        axes.plot(*coordinates, color="#fffdf5", linewidth=7, solid_capstyle="round", zorder=3)
        axes.plot(*coordinates, color=COLORS[feature["id"]], linewidth=4.0, solid_capstyle="round", zorder=4)
    for feature in stations:
        key = feature["id"]
        here = feature["geometry"]["coordinates"]
        transfer = len(feature["properties"]["lines"]) > 1
        color = "#163a3e" if transfer else COLORS[feature["properties"]["lines"][0]]
        axes.scatter(*here, c="#fcfaf4", edgecolors=color, linewidths=2, s=119 if transfer else 46, zorder=6)
        if transfer:
            axes.scatter(*here, c=color, s=18, zorder=7)
        name, dx, dy, ha = LABELS.get(key, (feature["properties"]["name"], 5, 8, "left"))
        axes.annotate(name, here, xytext=(dx, dy), textcoords="offset points", va="center",
                      ha=ha, fontsize=10.2, color="#183638", fontweight="bold" if transfer else "normal",
                      bbox=dict(boxstyle="round,pad=.19", facecolor="#fcfaf4", edgecolor="none", alpha=.94),
                      zorder=8)
    x, y = zip(*(coord for f in alignment for coord in f["geometry"]["coordinates"]), strict=True)
    west, east, south, north = min(x) - .010, max(x) + .015, min(y) - .008, max(y) + .007
    axes.set(xlim=(west, east), ylim=(south, north), aspect=1 / cos(radians(33.3)))
    axes.set_xticks([])
    axes.set_yticks([])
    for spine in axes.spines.values():
        spine.set_color("#d5cfc1")
    fig.text(.049, .955, "Central Baghdad rail study", color="#173d40", fontsize=26, fontweight="bold", va="top")
    fig.text(.05, .906, f"{study['route_km']:.2f} km   ·   {len(stations)} stops   ·   "
                        f"{study['headway_s'] / 60:g}-minute trial timetable",
             color="#46514c", fontsize=13.5, va="top")
    fig.legend(handles=[
        Line2D([0], [0], color=COLORS["C1"], lw=3.5, label="C1   Al Mansour–Zayouna"),
        Line2D([0], [0], color=COLORS["C2"], lw=3.5, label="C2   Al Mustansiriya–University of Baghdad"),
        Line2D([0], [0], color="#173d40", marker="o", mec="#173d40", mfc="#fcfaf4",
               ls="None", ms=9, label="Tahrir Square interchange"),
    ], ncol=3, loc="lower left", bbox_to_anchor=(.055, .045), frameon=False, fontsize=10)
    fig.text(.062, .033, "Concept alignments and station locations   ·   Basemap © OpenStreetMap contributors",
             color="#58625e", fontsize=9.7)
    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=160)
    plt.close(fig)
    return buffer.getvalue()


def citywide_image(record, data, context):
    """Show the costed metropolitan concept by timetable status."""
    import matplotlib
    matplotlib.use("Agg")
    from matplotlib import pyplot as plt
    from matplotlib.collections import LineCollection, PatchCollection
    from matplotlib.lines import Line2D
    from matplotlib.patches import Polygon, Rectangle

    fig = plt.figure(figsize=(11, 9.7), facecolor="#fcfaf4")
    axes = fig.add_axes((.055, .130, .89, .724), facecolor="#f7f5ed")
    water, rivers, roads = source_geometry(context)
    axes.add_collection(PatchCollection([Polygon(poly, closed=True) for poly in water],
                                        facecolor="#c6e2e9", edgecolor="none", zorder=1))
    axes.add_collection(LineCollection(rivers, colors="#abd3df", linewidths=1.2, zorder=1.1))
    axes.add_collection(LineCollection(roads, colors="#c5bdad", linewidths=.5, alpha=.45, zorder=2))
    styles = (
        ("clockface calls", "#325d8a", "-", "Scheduled paths in the 14-route trial"),
        ("deferred access", "#a83b4a", "--", "Deferred access"),
        ("reserved guideway", "#716a5d", ":", "Reserved guideway"),
    )
    baseline = record["baseline"]
    route_points = []
    labels = []
    for status, color, style, label in styles:
        paths = [f["geometry"]["coordinates"] for f in data["features"]
                 if f["properties"]["status"] == status and f["geometry"]["type"] == "LineString"]
        axes.add_collection(LineCollection(paths, colors=color, linewidths=2.1,
                                           linestyles=style, zorder=4))
        route_points.extend(point for path in paths for point in path)
        labels.append(Line2D([0], [0], color=color, ls=style, lw=2, label=label))
    stations = [f["geometry"]["coordinates"] for f in data["features"]
                if f["properties"]["status"] == "clockface stop"]
    axes.scatter(*zip(*stations, strict=True), s=11, c="#fcfaf4", edgecolors="#325d8a",
                 linewidths=.65, zorder=5)
    west, south, east, north = record["core_bounds_wsen"]
    axes.add_patch(Rectangle((west, south), east - west, north - south, fill=False,
                              edgecolor="#7f592d", linewidth=1.2, zorder=6))
    axes.annotate("Central access review area", (west, north), xytext=(1, 6),
                  textcoords="offset points", fontsize=9, color="#6f4d26",
                  bbox=dict(facecolor="#fcfaf4", edgecolor="none", alpha=.92, pad=2), zorder=7)
    x, y = zip(*route_points, strict=True)
    axes.set(xlim=(min(x) - .020, max(x) + .020), ylim=(min(y) - .015, max(y) + .015),
             aspect=1 / cos(radians(33.3)))
    axes.set_xticks([])
    axes.set_yticks([])
    for spine in axes.spines.values():
        spine.set_color("#d5cfc1")
    fig.text(.052, .944, "Baghdad citywide service comparison", fontsize=23, fontweight="bold",
             color="#173d40", va="top")
    fig.text(.054, .891, f"{baseline['physical_route_km']:.3f} km in the earlier costed concept   ·   "
                         f"{baseline['connected_clockface_km']:.3f} km timed for passenger service",
             color="#46514c", fontsize=12, va="top")
    fig.legend(handles=labels, ncol=3, loc="lower left", bbox_to_anchor=(.055, .064), frameon=False, fontsize=10)
    fig.text(.065, .047, f"{baseline['deferred_km']:.3f} km deferred   ·   {baseline['reserved_km']:.3f} km reserved   ·   "
                         "Scheduled-stop markers from the clockface trial",
             color="#58625e", fontsize=9)
    fig.text(.065, .026, "Concept lines and stations   ·   Basemap © OpenStreetMap contributors",
             color="#58625e", fontsize=9)
    buffer = BytesIO()
    fig.savefig(buffer, format="png", dpi=150)
    plt.close(fig)
    return buffer.getvalue()
