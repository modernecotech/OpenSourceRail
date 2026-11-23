"""Build the Airport cut-stock handoff. Python 3.11+, standard library."""
import argparse
import csv
import hashlib
import io
import json
import math
import tomllib
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKET = HERE.parent / "airport-prototype.zip"
STOCK = HERE.parent.parent / "mechanical/vehicle/stock.toml"
if not STOCK.is_file():
    STOCK = HERE / "input/stock.toml"
SHEET = (3000, 1500)
MARGIN = 10
WEB = 7
KERF = 3
FRONT_TRIM = 10
TAIL_GRIP = 100


def sha(data):
    return hashlib.sha256(data).hexdigest()


def json_bytes(data):
    return (json.dumps(data, indent=2, sort_keys=True) + "\n").encode()


def table(header, rows):
    stream = io.StringIO()
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(header.split())
    writer.writerows(rows)
    return stream.getvalue().encode()


def read_source(members):
    names = ["mechanical.json", "opening.json", "car-and-bogies.obj", "revised-cuts.csv", "opening-bom.csv"]
    consumed = [*names, "manifest.json"]
    if members is None:
        with zipfile.ZipFile(PACKET) as archive:
            source = {name: archive.read(name) for name in consumed}
    else:
        source = {name: members[name] for name in consumed}
    seal = json.loads(source["manifest.json"])
    if any(sha(source[key]) != seal["sha256"][key] for key in names):
        raise ValueError("A consumed packet member differs from its manifest")
    mech = json.loads(source["mechanical.json"])
    opening = json.loads(source["opening.json"])
    bundle = opening["bundle"]
    stock_source = STOCK.read_bytes()
    if (opening["candidate_id"] != mech["candidate_id"] or seal["candidate_id"] != mech["candidate_id"]
            or seal["article"] != mech["frame_revision"] or bundle["vehicle_revision"] != seal["article"]
            or sha(stock_source) != mech["source_sha256"]["cities/Baghdad/engineering/mechanical/vehicle/stock.toml"]):
        raise ValueError("Mixed opening, frame revision or stock specification")
    counts = Counter()
    for row in csv.DictReader(io.StringIO(source["opening-bom.csv"].decode())):
        if row["scope"] == "cut material":
            counts[row["item"]] += int(row["opening_quantity"])
    rows = list(csv.DictReader(io.StringIO(source["revised-cuts.csv"].decode())))
    cars = (bundle["active_sets"] + bundle["spares"]) * bundle["formation_cars"]
    cut_counts = Counter()
    for row in rows:
        row["opening_quantity"] = cars * int(row["cuts_per_assembly"]) * (2 if row["assembly"] == "bogie" else 1)
        cut_counts[row["part"]] += row["opening_quantity"]
    if cut_counts != counts:
        raise ValueError("Opening cut schedule differs from the physical bill")
    ids = dict(candidate_id=seal["candidate_id"], frame_revision=seal["article"],
               packet_evaluation_id=seal["evaluation_id"], opening_evaluation_id=opening["evaluation_id"],
               mechanical_evaluation_id=mech["evaluation_id"], cars=cars,
               source_sha256={key: sha(value) for key, value in source.items()})
    ids["source_sha256"]["stock.toml"] = sha(stock_source)
    return rows, counts, tomllib.loads(stock_source.decode()), source["car-and-bogies.obj"].decode(), ids


def profiles(stock):
    brace = stock["braced_revision"]
    leg = round(1000 * brace["gusset_leg_m"])
    result = {"gusset": ([(0, 0), (leg, 0), (0, leg)], round(1000 * brace["gusset_thickness_m"]))}
    for name, (x, y, t) in stock["seat_plates"].items():
        result[name] = ([(0, 0), (x, 0), (x, y), (0, y)], t)
    return result


def assembly_frames(obj, shapes, expected, cars):
    """Map each extruded blank into the single-car OBJ, with a proper rotation."""
    parts = defaultdict(list)
    for line in obj.splitlines():
        if line.startswith("o "):
            name = line[2:]
        elif line.startswith("v "):
            parts[name].append(tuple(round(float(x) * 1000, 3) for x in line.split()[1:]))
    frames, found = [], Counter()
    for element, points in parts.items():
        part = element.rsplit("_", 1)[0]
        if part not in shapes:
            continue
        polygon, thickness = shapes[part]
        size = len(polygon)
        if size == 3:
            # Match the right-angle corner even when the mesh reverses the face winding.
            corner = next(i for i, a in enumerate(points[:3])
                          if sum((points[(i+1)%3][k]-a[k])*(points[(i+2)%3][k]-a[k]) for k in range(3)) == 0)
            a = points[corner]
            b, c = sorted((p for p in points[:3] if p != a), key=lambda p: abs(p[0]-a[0]), reverse=True)
        else:
            corner = 0
            a, b, c = (points[i] for i in (0, 1, size-1))
        def axis(end, start):
            delta = tuple(v-u for v, u in zip(end, start))
            return tuple(round(v / math.hypot(*delta), 9) for v in delta)
        u, v = axis(b, a), axis(c, a)
        w = (u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0])
        # Mirrored installation uses the opposite physical face for blank Z=0.
        origin = a if all(abs(a[i]+w[i]*thickness-points[size+corner][i]) < 0.001 for i in range(3)) else points[size+corner]
        matrix = [[u[i], v[i], w[i], origin[i]] for i in range(3)] + [[0, 0, 0, 1]]
        rebuilt = {tuple(round(origin[i]+u[i]*x+v[i]*y+w[i]*z, 3) for i in range(3))
                   for x, y in polygon for z in (0, thickness)}
        if rebuilt != set(points) or len(points) != 2 * size:
            raise ValueError(f"Installed vertices differ from flat blank {element}")
        frames.append(dict(object=element, part=part, car_from_blank_mm=matrix))
        found[part] += cars
    if found != {p: expected[p] for p in shapes}:
        raise ValueError("OBJ occurrences differ from calculated plate quantities")
    return frames


def dxf(contours):
    # Closed LWPOLYLINE records. Sheet stock is schedule metadata, never a cut contour.
    data = [(0,"SECTION"), (2,"HEADER"), (9,"$ACADVER"), (1,"AC1015"), (9,"$INSUNITS"), (70,4),
            (0,"ENDSEC"), (0,"SECTION"), (2,"ENTITIES")]
    for index, (layer, points) in enumerate(contours, 256):
        data += [(0,"LWPOLYLINE"), (5,format(index,"X")), (100,"AcDbEntity"), (8,layer),
                 (100,"AcDbPolyline"), (90,len(points)), (70,1)]
        for x, y in points:
            data += [(10,x), (20,y)]
    data += [(0,"ENDSEC"), (0,"EOF")]
    return "".join(f"{code}\n{value}\n" for code, value in data).encode()


def sheet_plans(shapes, counts, output):
    # QTY is realised by repeated physical sheets. 180-degree partners use a web
    # between their hypotenuses. Every contour remains individually compensated.
    layouts = defaultdict(list)
    gusset = shapes["gusset"][0]
    leg = max(x for x, _ in gusset)
    side = leg + math.ceil(WEB / math.sqrt(2))
    pair_grid = []
    for y in range(MARGIN, SHEET[1]-MARGIN-side+1, side+WEB):
        for x in range(MARGIN, SHEET[0]-MARGIN-side+1, side+WEB):
            pair_grid.extend([("gusset", x, y, 1), ("gusset", x+side, y+side, -1)])
    if not pair_grid:
        raise ValueError("Gusset pair too large for the proposed sheet")
    t = shapes["gusset"][1]
    for start in range(0, counts["gusset"], len(pair_grid)):
        layouts[t].append(tuple(pair_grid[:counts["gusset"]-start]))
    pads = defaultdict(list)
    for part, (polygon, t) in shapes.items():
        if len(polygon) == 4:
            w, h = map(max, zip(*polygon))
            pads[t].extend([(h, w, part)] * counts[part])
    for t, pieces in pads.items():
        # Decreasing height keeps parts sharing a shelf within its vertical extent.
        bins = []
        for h, w, part in sorted(pieces, reverse=True):
            if w + 2*MARGIN > SHEET[0] or h + 2*MARGIN > SHEET[1]:
                raise ValueError(f"{part} does not fit proposed sheet")
            for shelves, placements in bins:
                shelf = next((r for r in shelves if h <= r["h"] and r["x"]+w <= SHEET[0]-MARGIN), None)
                if shelf is not None:
                    break
                y = shelves[-1]["y"] + shelves[-1]["h"] + WEB
                if y+h <= SHEET[1]-MARGIN:
                    shelf = {"x":MARGIN, "y":y, "h":h}
                    shelves.append(shelf)
                    break
            else:
                shelf = {"x":MARGIN, "y":MARGIN, "h":h}
                placements = []
                bins.append(([shelf], placements))
            placements.append((part, shelf["x"], shelf["y"], 1))
            shelf["x"] += w + WEB
        layouts[t].extend(tuple(placements) for _, placements in bins)
    schedule, positions = [], []
    for t, sheets in sorted(layouts.items()):
        for index, (layout, copies) in enumerate(Counter(sheets).items(), 1):
            label = f"plate-{t}mm-{index}"
            contours = []
            for slot, (part, x, y, sign) in enumerate(layout, 1):
                outline = [(x+sign*px, y+sign*py) for px, py in shapes[part][0]]
                contours.append((part.upper(), outline))
                positions.append((label, slot, part, x, y, 0 if sign == 1 else 180))
            output[f"sheets/{label}.dxf"] = dxf(contours)
            for part, n in sorted(Counter(row[0] for row in layout).items()):
                schedule.append((label, *SHEET, t, copies, part, n, copies*n))
    output["sheet-schedule.csv"] = table("layout sheet_x_mm sheet_y_mm thickness_mm sheets part blanks_per_sheet opening_blanks", schedule)
    output["sheet-placements.csv"] = table("layout position part origin_x_mm origin_y_mm z_rotation_deg", positions)
    return sum(len(sheets) for sheets in layouts.values())

def pack_bars(pieces, normal_raw_mm):
    bars, remaining, raw_lengths = [], [], []
    for length, part in sorted(pieces, reverse=True):
        needed = length + KERF*1000
        pos = next((i for i, room in enumerate(remaining) if room >= needed), len(bars))
        if pos == len(bars):
            raw = 12_500 if needed > (normal_raw_mm-FRONT_TRIM-TAIL_GRIP)*1000 else normal_raw_mm
            if needed > (raw-FRONT_TRIM-TAIL_GRIP)*1000:
                raise ValueError(f"Cut too long for proposed stock: {part}")
            raw_lengths.append(raw)
            bars.append([])
            remaining.append((raw-FRONT_TRIM-TAIL_GRIP)*1000)
        bars[pos].append((length, part))
        remaining[pos] -= needed
    return raw_lengths, bars


def saw_program(rows, shapes, output):
    by_section = defaultdict(list)
    for row in rows:
        part = row["part"]
        if part not in shapes:
            length_um = round(float(row["cut_length_m"]) * 1_000_000)
            by_section[row["nominal_stock_mm"]].extend([(length_um, part)] * row["opening_quantity"])
    cuts, purchases = [], []
    bars_total = 0
    for section, pieces in sorted(by_section.items()):
        # Compare ordinary and mill-length supply where the long chord already
        # requires a special order. Select least purchased length within a section.
        choices = [pack_bars(pieces, 12_000)]
        if any(length >= 12_000_000 for length, _ in pieces):
            choices.append(pack_bars(pieces, 12_500))
        raw_lengths, bars = min(choices, key=lambda c: (sum(c[0]), c[0].count(12_500)))
        patterns = Counter(zip(raw_lengths, map(tuple, bars), strict=True))
        for (raw, pattern), copies in patterns.items():
            label = f"BAR-{len(purchases)+1:03d}"
            start = FRONT_TRIM * 1000
            for index, (length, part) in enumerate(pattern, 1):
                end = start + length
                cuts.append((label, index, part, start/1000, end/1000, length/1000, KERF, copies,
                             "nominal axis; end prep pending" if part == "brace" else "nominal blank"))
                start = end + KERF * 1000
            purchases.append((label, section, raw, copies, len(pattern), FRONT_TRIM, TAIL_GRIP,
                              round(raw-start/1000, 3)))
            bars_total += copies
    output["saw-cuts.csv"] = table("pattern sequence part start_mm near_blade_face_mm length_mm blade_kerf_mm pattern_copies scope", cuts)
    output["saw-stock.csv"] = table("pattern stock_section raw_length_mm bars cuts_per_bar front_trim_including_kerf_mm min_tail_grip_mm remaining_tail_mm", purchases)
    return bars_total, sum(len(v) for v in by_section.values())


def practice_moves():
    """Feed rates in mm/min. Stock frame G54 is the bottom-left corner of the top."""
    moves = ["G94", "G54", "G0 Z5", "G0 X15 Y12", "M3 S6000"]
    for depth in (-0.5, -1):
        moves += [f"G1 Z{depth} F60", "G1 X43 F180", "G1 Y28",
                  "G0 Z5"]
        if depth != -1:
            moves.append("G0 X15 Y12")
    return moves


def practice_post(moves):
    def format_line(line):
        return " ".join(f"{word[0]}{float(word[1:]):.3f}" if word[0] in "XYZF" else word for word in line.split())
    return ("\n".join(["G17 G90", "G21", *map(format_line, moves), "M5", "G17 G90", "M2"])+"\n").encode()


def artifacts(members=None):
    rows, counts, stock, obj, ids = read_source(members)
    shapes = profiles(stock)
    out = {f"parts/{name}.dxf": dxf([(name.upper(), polygon)]) for name, (polygon, _) in shapes.items()}
    frames = assembly_frames(obj, shapes, counts, ids["cars"])
    out["plate-frames.json"] = json_bytes({"length_unit":"mm", "convention":"column vectors, local part XY and +Z through stock; car x forward, y left, z up at railhead", "occurrences_per_car":frames})
    sheets = sheet_plans(shapes, counts, out)
    bars, saw_count = saw_program(rows, shapes, out)
    moves = practice_moves()
    out["training/practice-path.txt"] = ("\n".join(moves)+"\n").encode()
    out["training/practice.nc"] = practice_post(moves)
    ids.update(blank_quantities={p:counts[p] for p in shapes}, plate_sheets=sheets, saw_bars=bars,
               saw_blanks=saw_count, toolpath_release="Practice coupon only; steel files describe nominal blanks for quotation",
               generator_sha256=sha(Path(__file__).read_bytes()), artifact_sha256={p:sha(v) for p,v in sorted(out.items())})
    ids["evaluation_id"] = sha(json_bytes(ids))
    out["cam-manifest.json"] = json_bytes(ids)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--out", type=Path, default=HERE)
    args = parser.parse_args()
    for name, data in artifacts().items():
        dest = args.out / name
        if args.check:
            if not dest.is_file() or dest.read_bytes() != data:
                parser.exit(1, f"Missing or stale {dest}\n")
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
    print("CAM members match" if args.check else "CAM members generated")


if __name__ == "__main__":
    main()
