"""Rebuild the inspectable Airport quotation twin and its offline article package."""

import argparse
from hashlib import sha256
from html import escape
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from cities.Baghdad import airport_integration, airport_single_line
from cities.Baghdad.engineering.commissioning import drawing, feeder, measurements, recorder
from cities.Baghdad.engineering.prototype import (
    fitout,
    degraded_service,
    car,
    civil_article,
    commercial,
    manufacturing,
    materials,
    mesh,
    weights,
)
from engineering.outline.baghdad_system import _id
from engineering.performance import check_disk_reservation, disk_reservation
from engineering.railway_completion.evidence import parse

HERE = Path(__file__).resolve().parent
CITY = HERE.parents[1]
ROOT = CITY.parents[1]
PACKET = HERE / "airport-prototype.zip"
PAGE = HERE / "review.html"
CITYWIDE_APPENDIX = HERE / "retained-citywide-appendix.zip"
# Extracted from this packet at 354522b7d7eabb57650f8d516eabf3b6df4916ba.
CITYWIDE_APPENDIX_SHA256 = "f0e84aa972554a95e34d78dfc9104ddfe5a3b12988f9e328675caa4ff85239dc"
TITLES = {
    "car": "Car and powered bogie frames",
    "track-span": "Track beam",
    "platform-bay": "Platform bay",
    "pier": "Pier and footing",
}


def encode(value):
    return (json.dumps(value, ensure_ascii=False, allow_nan=False, indent=2, sort_keys=True) + "\n").encode()


def table(headers, rows):
    return (
        '<div class="table-scroll"><table><thead><tr>'
        + "".join(f'<th scope="col">{escape(str(value))}</th>' for value in headers)
        + "</tr></thead><tbody>"
        + "".join("<tr>" + "".join(f"<td>{escape(str(v))}</td>" for v in row) + "</tr>" for row in rows)
        + "</tbody></table></div>"
    )


def page(data, offline):
    a, e, f, network = (data[k] for k in ("article", "electrical", "commercial", "citywide"))
    case, door, mass = a["opening"], a["doorway"], a["mass"]
    p = e["parallel_quotation"]
    models = "".join(f'<option value="{k}">{v}</option>' for k, v in TITLES.items())
    budget = "".join(
        f"<div><strong>{value}</strong>{caption}</div>"
        for value, caption in [
            (f'{len(a["pieces"])}', "stock pieces per car"),
            (f'{1000*door["minimum_fitted_under_allocations_m"]:.0f} mm', "allocated fitted doorway"),
            (f'{case["power"]["vehicle"]["mass_t"]:.2f} t', "planning gross train load"),
            (f'${f["priced_capital_usd_m"]:,.1f}m', "priced 30-site opening"),
        ]
    )
    paths = (
        [
            ("Workshop instructions", "workshop-guide.md"),
            ("Car IFC4", "car-and-bogies.ifc"),
            ("Beam cage drawing", "beam-cage-section.svg"),
            ("Civil guide", "civil-guide.md"),
            ("Manufacturing quantities", "opening-bom.csv"),
            ("Power and controls trials", "commissioning.md"),
            ("Paired feeder drawing", "electrical/paired-paths.svg"),
            ("Service after two faults", "degraded-service.md"),
            ("Buyer’s guide", "commercial-guide.md"),
            ("Weight returns", "weight-guide.md"),
            ("Workshop orders", "manufacturing-guide.md"),
            ("Bogie and equipment interfaces", "fitout-guide.md"),
            ("Feeder bid comparison", "feeder-cash-guide.md"),
            ("Citywide service decision", "network/service-decision.md"),
        ]
        if offline
        else [
            ("Download quotation package", "airport-prototype.zip"),
            ("Workshop instructions", "mechanical.md"),
            ("Civil guide", "civil-guide.md"),
            ("Power and controls trials", "../commissioning/COMMISSIONING.md"),
            ("Buyer’s guide", "commercial-guide.md"),
            ("Weight returns", "weight-guide.md"),
            ("Workshop orders", "manufacturing-guide.md"),
            ("Bogie and equipment interfaces", "fitout-guide.md"),
            ("Feeder bid comparison", "feeder-cash-guide.md"),
            ("Citywide service decision", "../../CITYWIDE-SERVICE.md"),
        ]
    )
    links = " ".join(f'<a href="{path}">{label}</a>' for label, path in paths)
    service = data["service"]
    trips = sorted(
        [
            list(r) + [empty]
            for empty, rows in ((False, service["trips"]), (True, service["positioning_trips"]))
            for r in rows
        ],
        key=lambda r: r[2],
    )
    replay = {
        "km": case["bundle"]["route_km"],
        "first_departure": service["trips"][0][2],
        "stops": service["patterns"][0],
        "yard_moves": service["terminal"]["yard_moves"],
        "trips": trips,
        "legs": service["leg_profiles"],
    }
    option = case["section_power"]
    jsdata = json.dumps(
        {
            "power": {"radial": option["selected"], "paired": p},
            "geometry": data["geometry"],
            "datums": data["datums"],
            "service": replay,
        },
        ensure_ascii=False,
        separators=(",", ":"),
        allow_nan=False,
    ).replace("<", "\\u003c")
    power_rows = []
    for name, branch in (
        ("Priced radial", e["priced_radial"]),
        ("Six stations, single paths", e["six_site_quotation"]),
        ("Six stations, paired paths", p["operating_envelopes"]),
    ):
        cases = branch["cases"]
        power_rows.append(
            (
                name,
                f'{cases["published hot circuit"]["collector_kv"]:.4f} kV',
                f'{cases["combined sensitivity"]["collector_kv"]:.4f} kV',
                f'{cases["combined sensitivity"]["margin_v"]:+.1f} V',
            )
        )
    material = data["material"]
    stress = a["body_vertical_screens"]["1.3"]
    t = network["timetable"]
    year_rows = [
        (
            r["year"],
            *(
                f"{r[k]:,.2f}"
                for k in (
                    "capital",
                    "operations",
                    "renewals",
                    "interest",
                    "principal",
                    "net_fares",
                    "public_cash_after_fares",
                )
            ),
        )
        for r in f["annual_cash"]
    ]
    stops = " · ".join(f'{i}. {escape(s["label"])}' for i, s in enumerate(replay["stops"], 1))
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Baghdad Airport · Prototype design review</title><style>{(HERE/'twin.css').read_text()}</style></head>
<body><main><header><p>OpenSourceRail / Baghdad Airport</p><h1>Prototype design review</h1>
<p>Inspect the revised car, station bay and beam, follow the three working trains, and compare feeder options on the same 12 km railway. The drawings are available for first-article quotation. Fabrication and passenger operation require separate approvals.</p>
<nav>{links}</nav></header><div class="metric">{budget}</div>
<nav aria-label="On this page"><a href="#article">Car and structures</a><a href="#service">Train workings</a><a href="#power">Power and controls</a><a href="#accounts">Buyer’s budget</a><a href="#decisions">Outstanding decisions</a></nav>
<section id="article"><h2>Car and structures</h2><p>The revised body widens all eight steel door openings. The counted stock for one car and both bogie frames is <strong>{mass['cut_kg_per_car']:,.1f} kg</strong>, including the new liners. Wheelsets, brakes, HVAC, finishes, wiring and passengers are outside that subtotal.</p>
<div class="panel"><div><canvas id="car" tabindex="0" aria-label="Article mesh. Drag to rotate, or use the arrow keys."></canvas><div class="tools"><button id="left">Rotate left</button><button id="right">Rotate right</button><button id="reset">Reset view</button></div></div>
<div><label>Article<select id="model">{models}</select></label><label>Assembly<select id="group"></select></label><label>Piece<select id="piece"></select></label>
<label><input type="checkbox" id="detail"> Fit view to piece</label><dl><dt>Piece ID</dt><dd id="selection"></dd><dt>Extent along x × y × z</dt><dd id="dimensions"></dd></dl><p class="muted" id="datum"></p></div></div>
<details><summary>Doorway allowance and structural check</summary>
{table(("Per edge","Allowance"),[(k.replace("_"," ").removesuffix(" m"),f"{v*1000:.0f} mm") for k,v in door["per_edge_allowances_m"].items()])}
<p>The {1000*min(door["rough_widths_m"]):.0f} mm steel aperture provides {1000*door["residual_m"]:.0f} mm combined residual above the {1000*door["required_fitted_m"]:.0f} mm requirement after both edge budgets. The 1.3× vertical load model gives {stress['door_width']['worst_width_loss_mm']:.3f} mm maximum narrowing. Measure the complete fitted and loaded doorway, including three-dimensional body twist.</p></details>
<details><summary>Welded steel and aluminium/GFRP comparison</summary><p>If a hybrid supplier can remove 500 kg per car after accounting for inserts, fasteners, fire protection and finishes, the six-car train would weigh {material['illustrative_hybrid']['mass_t']:.2f} t at the same passenger load. The model then requests {material['illustrative_hybrid']['traction_mw']:.3f} MW and draws {material['illustrative_hybrid']['grid_gwh_per_year']:.3f} GWh/year on the same timetable. The central 30-year calculation leaves a whole-fleet allowance of ${material['additional_whole_life_cost_at_break_even_usd_m']*1e6:,.0f} in present-value terms for any additional tooling, purchase, inspection, maintenance and repair costs before reaching the steel case’s cost. This result includes a change from {material['steel']['supply_sites']} to {material['illustrative_hybrid']['supply_sites']} priced supply sites when the model resizes the radial layout. The saving from electricity alone is ${material['electricity_only_30y_difference_usd_m']*1e6:,.0f} at the same tariff. The mass saving is an enquiry assumption. Both installed weights and comparable prices need supplier returns.</p></details>
<details><summary>Beam cage, bearings and platform</summary><p>The 10 m beam enquiry includes {data['civil']['bar_and_strand_kg_per_beam']:,.1f} kg of scheduled bar and strand. The drawing locates twelve strands and shows the bar marks used by the bending schedule. The civil guide gives the bearing and lifting loads, platform drainage and boarding datums. The concrete price already allows for reinforced stock. Addition of the cage detail requires a replacement quotation.</p></details></section>
<section id="service"><h2>Airport train workings</h2><p>Three six-car sets run every 15 minutes per direction. The service includes {len(service["trips"])} passenger workings, {len(service["positioning_trips"])} empty mainline workings and {len(service["terminal"]["yard_moves"])} depot moves. Move the clock to inspect the mainline service. Positions follow each leg’s acceleration, cruise, braking and dwell.</p>
<label>Local time <output id="when" for="clock"></output><input id="clock" type="range" step="1"></label>
<svg id="route" viewBox="0 0 720 90" role="img" aria-label="Train positions by route distance"></svg><p class="muted">{stops}</p>
<table><thead><tr><th>Set</th><th>Working</th><th>km from Airport</th></tr></thead><tbody id="trains"></tbody></table>
<details><summary>Independent citywide planning option</summary><p>The separate citywide plan assigns {network['in_service_route_km']:.3f} km to fourteen connected services. Its {t['headway_s']/60:g}-minute clockface option passes the checked interstation, terminal and shared crossing screens. Five access sections remain deferred. The 150-second peak service and its larger capacity require further signalling and terminal design.</p></details></section>
<section id="power"><h2>Power and controls</h2><p>The revised planning load requests {case["power"]["traction"]["dc_input_rating_request_mw"]:.3f} MW per accelerating train. The combined sensitivity reduces source voltage 1%, increases peak demand 5% and increases hot loop resistance a further 5%. The planning floor is {e["floor_kv"]:.2f} kV.</p>
{table(("Restored feed with one site out","Published hot case","Combined sensitivity","Margin"),power_rows)}
<div id="power-replay"></div>
<p>The paired-path option requests {p["site_peak_current_ka"]:.2f} kA peak per branch while current sharing is unproved. Loss of one path as well as one site gives {p["single_path_lost_with_site_out_combined"]["collector_kv"]:.4f} kV. Under that double outage the collector load limit at the voltage floor is {data['outage']['sensitivity_cases']['combined sensitivity']['floor_load_bound_mw']:.2f} MW. The package identifies the movements exposed in each affected section, including train acceleration and depot movements. Restoring passenger service or permitting evacuation requires verified isolation and an approved operating plan. The six-site options need their own installed price, hot measurements, protective grading and independent utility review.</p>
<p>Use the bench procedure for stopped boarding, effort take-up against the parking hold and departure. Record door side, torque, brake force, position, emergency egress and behaviour through a power interruption. Each trial must identify the article and controller build.</p></section>
<section id="accounts"><h2>Buyer’s budget</h2><p>The 30-site radial layout is the priced configuration. At constant 2026 prices, the annual operating estimate is ${f["annual_operating_cost_usd_m"]:.2f}m. Net fares of ${f["annual_net_fares_usd_m"]:.2f}m leave ${f["annual_operating_support_usd_m"]:.2f}m of operating support before financing and renewals. The paired-path design has no installed offer in the baseline.</p>
<details><summary>Annual cash in millions of 2026 USD</summary>{table(("Year","Capital","Operations","Renewals","Interest","Principal","Net fares","Public cash"),year_rows)}</details></section>
<section id="decisions"><h2>Outstanding decisions</h2>
{table(("Decision","Digital result","Record still needed"),data["decisions"])}
<p>Use the return forms in the download for train weights, local works, demand, supplier prices, circuit measurements, bench records and annual public allocations. Attach the original supporting records. A completed form enters engineering review.</p></section>
<footer>Airport physical design <code>{case["candidate_id"]}</code><br>Car frame revision <code>{a["frame_revision"]}</code></footer>
</main><script id="model-data" type="application/json">{jsdata}</script><script>{(HERE/"twin.js").read_text()}</script></body></html>"""


def retained_citywide_appendix():
    """Read the independent network comparison supplied with this drawing edition."""
    raw = CITYWIDE_APPENDIX.read_bytes()
    if sha256(raw).hexdigest() != CITYWIDE_APPENDIX_SHA256:
        raise ValueError("The retained citywide appendix differs from the prototype drawing edition")
    with ZipFile(io.BytesIO(raw)) as appendix:
        members = {name: appendix.read(name) for name in appendix.namelist()}
    network = json.loads(members["network/citywide-service.json"])
    if network["evaluation_id"] != _id({k: v for k, v in network.items() if k != "evaluation_id"}):
        raise ValueError("Retained citywide appendix has an inconsistent evaluation identity")
    if not network["timetable"]["resource_screen_passed"]:
        raise ValueError("Citywide planning selection requires a passing resource screen")
    return network, members


def construct(financial_return=None, document_directory=None, feeder_return=None):
    parent = airport_integration.build()
    article, files = car.artifacts(parent)
    case, service = article["opening"], parent["service"]
    inputs = airport_integration.airport_opening.opening_inputs()
    cfg = inputs[0]
    material = materials.compare(article, service, inputs)
    if (
        case["candidate_id"] != article["candidate_id"]
        or case["bundle"]["vehicle_revision"] != article["frame_revision"]
    ):
        raise ValueError("Article identity differs from opening configuration")
    power = feeder.evaluate(case, feeder_return, service=service)
    accounts = commercial.assess(case, service, cfg, financial_return, document_directory)
    network, citywide_files = retained_citywide_appendix()
    files.update(citywide_files)
    civil, civil_files = civil_article.artifacts(article)
    files.update(civil_files)
    files.update(fitout.artifacts(article))
    files.update(degraded_service.artifacts(case, power, service))
    outage = json.loads(files["degraded-service.json"])
    geoms = {"car": mesh.read_obj(files["car-and-bogies.obj"], article["pieces"])}
    datums = {"car": "Metres from car centre at rail head. x forward, y left, z up."}
    files["car-and-bogies.ifc"] = mesh.ifc4(geoms["car"], article["frame_revision"], case["candidate_id"])
    for key, info in article["civil"]["meshes"].items():
        geoms[key] = mesh.read_obj(files[key + ".obj"], assembly=key)
        if len(geoms[key]) != info["objects"]:
            raise ValueError("Civil stock count differs from the structural record")
        datums[key] = info["datum"]
        files[key + ".ifc"] = mesh.ifc4(
            geoms[key],
            _id([article["civil"]["parent_physical_id"], key, info]),
            case["candidate_id"],
            TITLES[key],
            datums[key],
        )
    decisions = [
        (
            "Network service",
            "Fourteen connected citywide groups with five deferred access sections.",
            "Operator adoption, surveyed junctions, counted directional demand.",
        ),
        (
            "Vehicle and bogie",
            "Revised doorway, cut stock, service access and moving span loads.",
            "Signed installed weights by axle, joint fatigue evidence, fitted door and brake tests.",
        ),
        (
            "Viaduct and station",
            "Stock geometry, support reactions, platform panels and bearing interfaces.",
            "Ground investigation, staged lift design, verified reinforcement and prestress, survey and accessible egress.",
        ),
        (
            "Traction supply",
            "Three circuit options with single-site outage, voltage and equipment duty screens.",
            "Utility supply limits, hot circuit tests, breaker settings, discrimination and isolation evidence.",
        ),
        (
            "Automatic train control",
            "Software station-visit replay and timestamped logger intake.",
            "Witnessed door, brake, drive, position and power-loss trials on the installed equipment.",
        ),
        (
            "Investment",
            "Site/quote replacement arithmetic, reported demand and phased cash.",
            "Accepted contracts, observed demand, all-in budget, signed funding and opening decision.",
        ),
    ]
    data = dict(
        article=article,
        outage=outage,
        material=material,
        civil=civil,
        electrical=power,
        commercial=accounts,
        citywide=network,
        geometry=geoms,
        datums=datums,
        decisions=decisions,
        service=service,
    )
    orders, bom = manufacturing.routing(parent, article, files["revised-cuts.csv"])
    files.update(
        {
            "START.html": page(data, True).encode(),
            "opening.json": encode(case),
            "mechanical.json": encode({k: v for k, v in article.items() if k not in ("opening", "finance")}),
            "service.json": encode(service),
            "cash.json": encode(accounts),
            "feeder-options.json": encode(power),
            "electrical/priced-single-line.svg": airport_single_line.single_line_svg(case).encode(),
            "electrical/paired-paths.svg": drawing.parallel_svg(power).encode(),
            "returns/finance.json": encode(commercial.form(case)),
            "returns/weights.json": encode(weights.form(article)),
            "material-comparison.json": encode(material),
            **{
                name: (HERE / name).read_bytes()
                for name in (
                    "commercial-guide.md",
                    "weight-guide.md",
                    "manufacturing-guide.md",
                    "feeder-cash-guide.md",
                )
            },
            "draft-work-orders.json": encode(orders),
            "opening-bom.csv": bom,
            "station-bench.md": (CITY / "engineering/controls/STATION-BENCH.md")
            .read_text()
            .replace(
                "(README.md#",
                "(https://github.com/modernecotech/OpenSourceRail/blob/main/cities/Baghdad/engineering/controls/README.md#",
            )
            .encode(),
            "commissioning.md": (CITY / "engineering/commissioning/COMMISSIONING.md")
            .read_text()
            .replace("(../../airport-traction-single-line.svg)", "(electrical/priced-single-line.svg)")
            .replace("(../controls/STATION-BENCH.md)", "(station-bench.md)")
            .replace(
                "(../controls/README.md#",
                "(https://github.com/modernecotech/OpenSourceRail/blob/main/cities/Baghdad/engineering/controls/README.md#",
            )
            .encode(),
            "LICENSE.md": (ROOT / "LICENSE.md").read_bytes(),
        }
    )
    for name in feeder.OPTIONS:
        files[f"returns/{name}-feeder.json"] = encode(feeder.return_form(case, name))
        files[f"returns/{name}-hot-test.json"] = encode(measurements.template(case, name))
    with TemporaryDirectory() as tmp:
        opening = Path(tmp) / "opening.json"
        opening.write_bytes(files["opening.json"])
        for mode in ("handover", *recorder.FAULTS):
            files[f"returns/{mode}-logger.json"] = encode(recorder.template(opening, mode))
    files["decision-register.json"] = encode(
        {
            "airport_candidate_id": case["candidate_id"],
            "airport_parent": article["parent_candidate_id"],
            "combined_outage_evaluation": outage["evaluation_id"],
            "civil_cage_id": civil["physical_id"],
            "civil_evaluation_id": civil["evaluation_id"],
            "network_selection_id": network["selection_id"],
            "electrical_evaluation": power["evaluation_id"],
            "commercial_evaluation": accounts["evaluation_id"],
            "fabrication_released": False,
            "operating_authorisation": False,
            "decisions": decisions,
        }
    )
    digests = {k: sha256(v).hexdigest() for k, v in sorted(files.items())}
    files["manifest.json"] = encode(
        {
            "evaluation_id": _id(digests),
            "sha256": digests,
            "candidate_id": case["candidate_id"],
            "article": article["frame_revision"],
        }
    )
    return files, page(data, False).encode()


def archive(members):
    buf = io.BytesIO()
    with ZipFile(buf, "w") as z:
        for name, value in sorted(members.items()):
            info = ZipInfo(name)
            info.compress_type = ZIP_DEFLATED
            z.writestr(info, value)
    return buf.getvalue()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--publish", action="store_true")
    mode.add_argument("--packet", type=Path)
    mode.add_argument(
        "--assess-weights",
        type=Path,
        metavar="FILE",
        help="Evaluate a documented return and its dependent costs and power",
    )
    ap.add_argument("--financial-return", type=Path)
    ap.add_argument("--feeder-return", type=Path)
    args = ap.parse_args()
    if not (args.packet or args.assess_weights) and (args.financial_return or args.feeder_return):
        ap.error("Use --packet or --assess-weights for a revised return")
    financial = parse(args.financial_return.read_bytes()) if args.financial_return else None
    directory = args.financial_return.parent if args.financial_return else None
    feeder_data = parse(args.feeder_return.read_bytes()) if args.feeder_return else None
    if args.assess_weights:
        from cities.Baghdad.engineering.prototype import returned_weights

        parent = airport_integration.build()
        article, _ = car.artifacts(parent)
        result = returned_weights.assess(
            article,
            parse(args.assess_weights.read_bytes()),
            directory=args.assess_weights.parent,
            service=parent["service"],
            financial_return=financial,
            financial_directory=directory,
            feeder_return=feeder_data,
        )
        print(encode(result).decode(), end="")
        return
    files, html = construct(financial, directory, feeder_data)
    raw = archive(files)
    if args.check:
        if html != PAGE.read_bytes() or not airport_integration.same_packet(PACKET, io.BytesIO(raw)):
            raise SystemExit("Regenerate the prototype twin and quotation package")
    else:
        target = PACKET if args.publish else args.packet
        if not args.publish and target.resolve() in (PAGE.resolve(), PACKET.resolve()):
            ap.error("Publish the registered baseline with --publish")
        with disk_reservation(ROOT, target.parent, "Baghdad prototype twin", 16 * 1024**2) as lease:
            check_disk_reservation(lease)
            airport_integration.write_atomic(target, raw)
            if args.publish:
                airport_integration.write_atomic(PAGE, html)
    print(json.loads(files["manifest.json"])["evaluation_id"])


if __name__ == "__main__":
    main()
