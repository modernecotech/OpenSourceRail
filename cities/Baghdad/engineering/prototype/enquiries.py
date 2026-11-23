"""Join the issued Airport drawings, buyer estimate and first-article schedules offline."""

from hashlib import sha256
from html import escape
from io import BytesIO
import json
from pathlib import Path
import posixpath
import re
from urllib.parse import urlsplit
from zipfile import ZipFile

from cities.Baghdad.airport_integration import same_packet, write_atomic
from cities.Baghdad.engineering.prototype import factory, review, shop_costs, shop_offers, sourcing_estimates
from cities.Baghdad.engineering.prototype.cam import build as cam
from cities.Baghdad.engineering.prototype.infrastructure import bar_stock
from engineering.outline.baghdad_system import _id
from engineering.performance import check_disk_reservation, disk_reservation

HERE = Path(__file__).resolve().parent
ROOT = sourcing_estimates.ROOT
ISSUE = HERE / "airport-enquiries.zip"

# Every supporting guide has a deliberate place in the offline issue. The
# sealed technical packet itself is included verbatim for independent readback.
GUIDES = {
    HERE / "README.md": "guides/prototype.md",
    HERE / "PRODUCTION-READINESS.md": "guides/production-readiness.md",
    HERE.parents[1] / "OPERATING-ALTERNATIVES.md": "guides/operating-options.md",
    HERE / "sourcing-verification.json": "guides/erp-verification.json",
    HERE / "PROCUREMENT-PLAN.md": "guides/buyer.md",
    HERE.parent / "controls/README.md": "guides/control-interfaces.md",
    HERE.parents[1] / "station-interface.svg": "guides/station-interface.svg",
    ROOT / "docs/operator-review/delivery/README.md": "guides/workshop.md",
    ROOT / "docs/operator-review/delivery/precast-yard.svg": "guides/precast-yard.svg",
    ROOT / "docs/operator-review/delivery/vehicle-works.svg": "guides/vehicle-works.svg",
    ROOT / "docs/operator-review/delivery/workforce.png": "guides/workforce.png",
}
DRAWING_GUIDES = {
    HERE / "mechanical.md": "drawings/workshop-guide.md",
    HERE.parent / "controls/STATION-BENCH.md": "drawings/station-bench.md",
    HERE.parent / "commissioning/COMMISSIONING.md": "drawings/commissioning.md",
    HERE.parents[1] / "CITYWIDE-SERVICE.md": "drawings/network/service-decision.md",
}
LOTS = (
    ("Representative car", "pilot-car", "vehicle-factory/README.md"),
    ("Powered bogie", "pilot-bogie", "vehicle-factory/vehicle-quote.csv"),
    ("Viaduct", "pilot-beam", "infrastructure/VIADUCT.md"),
    ("Station", "pilot-station-bay", "infrastructure/STATION.md"),
    ("Traction and control module", "pilot-traction-controls", "infrastructure/ELECTRICAL-CONTROLS.md"),
    ("Local production and repair", "tooling", factory.REPORT),
)
WORKSHOP_GUIDES = (
    "shop-rates.toml", "shop_offers.py", "SHOP-COSTS.md", "shop-costs.json", "cam/CAM.md", "cam/build.py", "cam/test_cam.py", "cam/verify_freecad.py",
    "cam/training/freecad-receipt.json",
    "training/index.html", "training/workshop.js", "training/INSTRUCTOR.md", "training/evidence-template.json",
    "infrastructure/YARD-CUTTING.md", "infrastructure/bar_stock.py", "infrastructure/WIRE-KITTING.md",
    "infrastructure/wire_kit.py", "infrastructure/wire-practice.csv",
)
SCHEDULES = (
    *WORKSHOP_GUIDES,
    factory.REPORT, factory.REGISTER, factory.ROUTES, *factory.SHOPS.values(),
    "vehicle-factory/VEHICLE-WORKCELLS.md", "infrastructure/CIVIL-WORKCELLS.md",
    "vehicle-factory/README.md", "vehicle-factory/vehicle-quote.csv", "vehicle-factory/factory-routing.md",
    "vehicle-factory/INSTALLED-GA.md", "vehicle-factory/installed-ga.svg",
    "vehicle-factory/BODY-BOGIE.md", "vehicle-factory/body-bogie-mating.svg",
    "vehicle-factory/body-bogie-limit-return.csv", "infrastructure/PLATFORM-SWEEP.md",
    "vehicle-factory/installed-ga.json", "vehicle-factory/installed-fitout-bom.csv",
    "vehicle-factory/factory-quote.csv", "infrastructure/README.md", "infrastructure/VIADUCT.md",
    "infrastructure/STATION.md", "infrastructure/ELECTRICAL-CONTROLS.md", "infrastructure/connector-return.csv",
)


def portable_guide(source, destination, paths):
    def target(match):
        raw = match[1]
        url = urlsplit(raw)
        if not url.path or url.scheme or url.netloc:
            return match[0]
        resolved = (source.parent / url.path).resolve()
        if resolved in paths:
            link = posixpath.relpath(paths[resolved], posixpath.dirname(destination))
        else:
            link = sourcing_estimates.REPO + resolved.relative_to(ROOT).as_posix()
        if url.query:
            link += "?" + url.query
        if url.fragment:
            link += "#" + url.fragment
        return "](" + link + ")"
    return re.sub(r"\]\(([^)\s]+)\)", target, source.read_text()).encode()


def landing(estimate):
    by_id = {r["lot_id"]: r for r in estimate["lots"]}
    rows = []
    for name, lot_id, path in LOTS:
        lot = by_id[lot_id]
        amount = f"${lot['base_usd']:,.0f}"
        if lot_id == "tooling":
            amount += " shared opening allowance"
        rows.append(f'<tr><th scope="row"><a href="{path}">{escape(name)}</a></th>'
                    f'<td>{lot_id}</td><td>{amount}</td></tr>')
    return ("""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport"
content="width=device-width, initial-scale=1"><title>Baghdad Airport first-article enquiries</title>
<style>body{font:1rem/1.55 system-ui,sans-serif;max-width:56rem;margin:2rem auto;padding:0 1rem;color:#162e34}
h1,h2{line-height:1.15}table{border-collapse:collapse}td,th{padding:.45rem .8rem;text-align:left;border-bottom:1px solid #ccd6d6}
a{color:#035d71}code{overflow-wrap:anywhere}</style><main><h1>Baghdad Airport first-article enquiries</h1>
<p>Use the same drawing and estimate edition for each supplier. Quote five individual articles and the
workshop scope for a 36-car opening. Itemise repeat production, inspection, commissioning, spares and
renewals. Identify credits where an article enters a fleet order.</p>
<table><thead><tr><th>Package and schedule</th><th>ERP lot</th><th>Central planning amount, 2026 USD</th></tr></thead>
<tbody>""" + "".join(rows) + """</tbody></table>
<h2>Drawings and returns</h2><p><a href="drawings/START.html">Open the offline prototype twin</a> ·
<a href="vehicle-factory/installed-ga.svg">Car general arrangement</a> ·
<a href="vehicle-factory/installed-fitout-bom.csv">Installed fitout register</a> · <a href="drawings/opening-bom.csv">Opening BOM</a> · <a href="drawings/draft-work-orders.json">Five draft orders</a> ·
<a href="drawings/returns/fitout.csv">Equipment fits and inspection</a></p>
<p><a href="vehicle-factory/vehicle-quote.csv">Vehicle price schedule</a> ·
<a href="FACTORY-SPECIFICATION.md">Factory sizing and production routes</a> ·
<a href="factory-equipment.csv">Return machine quantities and prices</a> ·
<a href="vehicle-factory/factory-quote.csv">Factory price schedule</a> ·
<a href="infrastructure/connector-return.csv">Electrical connector schedule</a></p>
<h2>Prepare a workshop quotation</h2>
<ul><li><a href="SHOP-COSTS.md">Check the equipment, hire and upkeep estimates</a>.
Request a <a href="machine-offer.csv">machine-level return</a> from each supplier.</li>
<li><a href="cam/CAM.md">Prepare plate nests and saw orders</a>.
Use the practice coupon to check the CAM workflow.</li>
<li><a href="infrastructure/YARD-CUTTING.md">Compare cage stock lengths</a> and issue the
<a href="infrastructure/bar-cut-tags.csv">bar cutting and traceability sheet</a>.</li>
<li><a href="infrastructure/WIRE-KITTING.md">Kit and check a wiring harness</a> from a returned wire list.</li>
<li><a href="training/index.html">Take the offline workshop exercises</a> or print the
<a href="training/INSTRUCTOR.md">instructor guide</a>.</li></ul>
<h2>Compare offers in ERPNext</h2><p>Import the <a href="sourcing-estimate.json">buyer estimate</a> using the
<a href="guides/buyer.md">buyer procedure</a>. Give each invited supplier its own account and the same lot revision.
Keep signed quotations, scope exclusions, technical review and purchase approval with the procurement record.</p>
<p>Each amount belongs to its named cost scope. The tooling amount covers the shared opening programme.
Use supplier returns and the parent-lot credits before changing the construction or annual budget.</p>
<p>Issue purpose is price and engineering review. Fabrication needs approved interface drawings and limits.
Review the <a href="guides/production-readiness.md">remaining production tasks</a>.
The <a href="manifest.json">issue manifest</a> identifies the design, estimate, source drawings and file checksums.</p>
</main></html>""").encode()


def contents():
    estimate = sourcing_estimates.estimate_lots()
    estimate_path = HERE / "sourcing-estimate.json"
    raw_estimate = estimate_path.read_bytes()
    if json.loads(raw_estimate) != estimate:
        raise ValueError("Rebuild the buyer estimate for this Airport drawing edition")
    drawings_path = sourcing_estimates.PACKET
    drawings = drawings_path.read_bytes()
    with ZipFile(BytesIO(drawings)) as package:
        manifest = json.loads(package.read("manifest.json"))
        members = {name: package.read(name) for name in package.namelist()}
    if (manifest["candidate_id"] != estimate["candidate_id"]
            or manifest["evaluation_id"] != estimate["opening_packet_evaluation_id"]
            or any(sha256(members[path]).hexdigest() != digest for path, digest in manifest["sha256"].items())):
        raise ValueError("Prototype drawing contents differ from the buyer estimate")
    files = {"drawings/" + k: v for k, v in members.items()}
    files.update({"airport-prototype.zip": drawings, "sourcing-estimate.json": raw_estimate,
                  "START.html": landing(estimate)})
    cam_files = cam.artifacts(members)
    paths = {HERE / name: name for name in SCHEDULES}
    paths.update({HERE / "cam" / name: "cam/" + name for name in cam_files})
    paths[ROOT / "cities/Baghdad/engineering/mechanical/vehicle/stock.toml"] = "cam/input/stock.toml"
    paths.update(GUIDES)
    paths.update(DRAWING_GUIDES)
    paths.update({HERE / name: "drawings/" + name for name in members if (HERE / name).is_file()})
    paths.update({drawings_path: "airport-prototype.zip", estimate_path: "sourcing-estimate.json", ISSUE: "START.html"})
    for source, name in paths.items():
        if name not in files:
            files[name] = portable_guide(source, name, paths) if source.suffix == ".md" else source.read_bytes()
    # Reuse the same loaded drawings and estimate to check the published shop counts.
    # Markdown links may have been adapted for offline use, so check its source edition.
    factory_files = factory.artifacts(estimate, members)
    if any((HERE / name).read_bytes() != raw for name, raw in factory_files.items()):
        raise ValueError("Rebuild the factory schedules before issuing the drawing or price revision")
    factory_record = json.loads(factory_files[factory.ROUTES])
    factory_id = factory_record["evaluation_id"]
    priced = shop_costs.artifacts(factory_record, estimate)
    if any((HERE / name).read_bytes() != raw for name, raw in priced.items()):
        raise ValueError("Rebuild the workshop costs for the issued factory and estimate")
    costs = json.loads(priced["shop-costs.json"])
    files["machine-offer.csv"] = shop_offers.template(costs)
    for name, raw in cam_files.items():
        if (HERE / "cam" / name).read_bytes() != raw:
            raise ValueError(f"Rebuild the CAM handoff for this drawing edition: {name}")
        files["cam/" + name] = raw
    cam_id = json.loads(files["cam/cam-manifest.json"])["evaluation_id"]
    readback = json.loads(files["cam/training/freecad-receipt.json"])
    if (readback["input_cam_evaluation_id"] != cam_id
            or readback["verifier_sha256"] != sha256(files["cam/verify_freecad.py"]).hexdigest()
            or readback["practice"]["posted_nc_sha256"] != sha256(files["cam/training/practice.nc"]).hexdigest()):
        raise ValueError("FreeCAD readback references a different CAM issue or verifier")
    files.update(bar_stock.artifacts(members["civil-article.json"]))
    training = json.loads(files["training/evidence-template.json"])
    if (training["factory_evaluation_id"] != factory_id or training["estimate_evaluation_id"] != estimate["evaluation_id"]
            or any(training[key] != estimate[key] for key in ("candidate_id", "frame_revision", "opening_evaluation_id"))):
        raise ValueError("Training exercises reference a different workshop issue")
    layout = json.loads(files["vehicle-factory/installed-ga.json"])
    if (layout["candidate_id"] != estimate["candidate_id"] or layout["frame_revision"] != estimate["frame_revision"]
            or layout["opening_evaluation_id"] != estimate["opening_evaluation_id"]
            or layout["mechanical_evaluation_id"] != estimate["mechanical_evaluation_id"]
            or _id({k: v for k, v in layout.items() if k != "evaluation_id"}) != layout["evaluation_id"]
            or any(manifest["sha256"][k] != digest for k, digest in layout["packet_member_sha256"].items())
            or any(sha256(files["vehicle-factory/" + k]).hexdigest() != digest
                   for k, digest in layout["outputs_sha256"].items())):
        raise ValueError("Installed-car arrangement differs from its drawing or material register")
    for directory in ("vehicle-factory", "infrastructure"):
        guide = files[directory + "/README.md"].decode()
        if not all(estimate[key] in guide for key in ("candidate_id", "opening_evaluation_id", "evaluation_id")):
            raise ValueError(f"{directory} schedules reference a different opening or ERP estimate")
    bindings = dict(shop_cost_evaluation_id=costs["evaluation_id"],
                    cam_evaluation_id=cam_id,
                    training_edition=training["edition"], factory_evaluation_id=factory_id, layout_evaluation_id=layout["evaluation_id"], candidate_id=estimate["candidate_id"], frame_revision=estimate["frame_revision"],
                    drawing_evaluation_id=manifest["evaluation_id"], estimate_evaluation_id=estimate["evaluation_id"],
                    purpose="first-article enquiry", fabrication_released=False, operating_authorisation=False,
                    package_lots=[{"package": name, "lot_id": lot, "schedule": path} for name, lot, path in LOTS],
                    sha256={k: sha256(v).hexdigest() for k, v in sorted(files.items())})
    files["manifest.json"] = review.encode({**bindings, "issue_id": _id(bindings)})
    return files


def issue(output):
    if output.suffix != ".zip":
        raise ValueError("Use a .zip filename for the buyer issue")
    output.parent.mkdir(parents=True, exist_ok=True)
    with disk_reservation(ROOT, output.parent, "Airport first-article enquiry issue", 16 << 20) as lease:
        files = contents()
        content = review.archive(files)
        if output.exists() and output.resolve() != ISSUE:
            if not same_packet(output, BytesIO(content)):
                raise ValueError("Output contains another edition. Choose a fresh .zip filename.")
        else:
            check_disk_reservation(lease)
            write_atomic(output, content)
    print(json.loads(files["manifest.json"])["issue_id"])
