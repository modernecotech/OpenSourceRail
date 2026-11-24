"""Package the offline operator workshop without requiring the engineering toolchain."""
import argparse
import hashlib
import io
import json
import posixpath
import re
import tempfile
from html.parser import HTMLParser
from urllib.parse import quote, unquote, urlsplit
from pathlib import Path
from zipfile import ZIP_DEFLATED, BadZipFile, ZipFile, ZipInfo

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
START = """<!doctype html>
<html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>OpenSourceRail | Railway operator workshop</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#f8f7ef;color:#183b3e;font:17px/1.5 system-ui,sans-serif}
header{background:#173d40;color:white;padding:18px 6vw}main{max-width:1000px;margin:auto;padding:28px 24px 48px}
h1{font-size:clamp(34px,5vw,54px);line-height:1.1;letter-spacing:-.04em;margin:12px 0}
a{color:#00675e}nav{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:15px}
nav a{background:white;border:1px solid #b8cbc3;border-radius:6px;padding:16px 19px;text-decoration:none}
a:hover,a:focus{text-decoration:underline}nav strong,small{display:block}small{color:#38585a;font-size:14px;margin-top:4px}
</style><header>OpenSourceRail &nbsp; / &nbsp; Operator workshop</header><main>
<h1>Design, build and operate the railway</h1><p>Start with the illustrated briefing, then use the models and calculators to review a core railway and the two Baghdad proposals. Extract the whole kit before opening these files.</p>
<nav>
<a href="docs/operator-review/OpenSourceRail-Operator-Brief.pdf"><strong>Operator briefing</strong><small>Fourteen illustrated pages for the meeting.</small></a>
<a href="docs/operator-review/twins/index.html"><strong>Train and station models</strong><small>Inspect the bogie, carbody, platform, viaduct and controls. Export either IFC4 model.</small></a>
<a href="cities/Baghdad/service-diagrams.html"><strong>Baghdad train diagrams</strong><small>Follow a set through its stops and terminal turn. Compare the full citywide offer and its mainline timetable.</small></a>
<a href="docs/operator-review/screens/supervision.html"><strong>Control room</strong><small>Replay equipment trips, a stale signal and restoration.</small></a>
<a href="cities/Baghdad/engineering/prototype/review.html"><strong>Airport prototype</strong><small>Inspect stock, train movements, voltages and open field trials.</small></a>
<a href="docs/operator-review/finance/index.html"><strong>Funding and fares</strong><small>Compare debt payments and test the public funding requirement.</small></a>
<a href="docs/operator-review/finance/purchasing.html"><strong>Supplier enquiries</strong><small>Download the first-article scope and compare price, documented domestic value and repair terms.</small></a>
<a href="cities/Baghdad/engineering/prototype/airport-enquiries.zip"><strong>Airport first-article enquiries</strong><small>Extract the package and open its START.html for drawings, factory records and quotation sheets.</small></a>
<a href="docs/operator-review/delivery/index.html"><strong>Workforce and training</strong><small>Inspect shift coverage, hiring and training provision.</small></a>
<a href="cities/Baghdad/engineering/simulation/AUDIT-RESULTS.md"><strong>Corridor assumption audit</strong><small>Review service delivered, electrical outages, civil quantities and the priced scope.</small></a>
<a href="cities/Baghdad/Baghdad-Metro-Proposal.pdf"><strong>Baghdad investment proposal</strong><small>Read the routes, local delivery options and the purchasing case.</small></a>
</nav><p><a href="docs/operator-review/delivery/vehicle-works.svg">Vehicle works plan</a> · <a href="docs/reference-v07/integration/TIMETABLE.md">Core train workings</a> · <a href="cities/Baghdad/airport-integration.html">Airport working plan and supplier dossier</a> · <a href="cities/Baghdad/maps/STATION-PRICING.md">Station sites and prices</a> · <a href="docs/operator-review/delivery/precast-yard.svg">Precast yard plan</a> · <a href="cities/Baghdad/maps/Baghdad-148km.png">Seven corridors map</a> · <a href="cities/Baghdad/maps/Baghdad-606km.png">Citywide map</a></p>
<p>Use the included documents for design review and indicative quotations. References to the wider engineering repository open with an internet connection. <a href="https://github.com/modernecotech/OpenSourceRail/tree/main/docs/operator-review">Full workplan, screens and sources</a></p></main></html>"""


def document_content(path, included):
    if path.suffix != '.md':
        return path.read_bytes()

    def resolve_link(match):
        label, destination = match.groups()
        parts = urlsplit(destination)
        if parts.scheme or parts.netloc or not parts.path:
            return match.group()
        target = (path.parent / parts.path).resolve()
        if target in included or not target.is_relative_to(ROOT):
            return match.group()
        route = quote(target.relative_to(ROOT).as_posix())
        suffix = '#' + parts.fragment if parts.fragment else ''
        return label + '(https://github.com/modernecotech/OpenSourceRail/blob/main/' + route + suffix + ')'
    return re.sub(r'(\[[^]\n]*\])\(([^()\s]+)\)', resolve_link, path.read_text()).encode()


class WorkshopLinks(HTMLParser):
    def __init__(self, page, members):
        super().__init__()
        self.page = page
        self.members = members

    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key not in {'href', 'src'} or not value:
                continue
            parts = urlsplit(value)
            if parts.scheme or parts.netloc or not parts.path:
                continue
            target = posixpath.normpath(posixpath.join(posixpath.dirname(self.page), unquote(parts.path)))
            if target not in self.members:
                raise ValueError(f'Offline workshop page {self.page} is missing {target}')


def workshop_files():
    files = set()
    for f in HERE.rglob('*'):
        if f.suffix in {'.md', '.html', '.css', '.js', '.png', '.json', '.ifc', '.svg', '.pdf'} and f.is_file():
            files.add(f)
    files.update(ROOT / f for f in ('LICENSE.md', 'cities/Baghdad/Baghdad-Metro-Proposal.pdf',
                 'cities/Baghdad/IRAQ-CAPITAL.md', 'cities/Baghdad/IRAQ-ESTIMATES.md', 'cities/Baghdad/IRAQ-POWER.md',
                 'cities/Baghdad/airport-integration.html', 'cities/Baghdad/airport-integration.css',
                 'cities/Baghdad/CITYWIDE-SERVICE.md', 'cities/Baghdad/citywide-service.json',
                 'cities/Baghdad/engineering/prototype/review.html', 'cities/Baghdad/engineering/prototype/airport-prototype.zip',
                 'cities/Baghdad/engineering/prototype/airport-enquiries.zip',
                 'cities/Baghdad/engineering/prototype/sourcing-verification.json', 'cities/Baghdad/engineering/prototype/PROCUREMENT-PLAN.md', 'cities/Baghdad/engineering/prototype/sourcing-estimate.json',
                 'cities/Baghdad/engineering/prototype/README.md', 'cities/Baghdad/engineering/prototype/mechanical.md',
                 'cities/Baghdad/engineering/commissioning/COMMISSIONING.md', 'cities/Baghdad/engineering/controls/STATION-BENCH.md',
                 'cities/Baghdad/airport-dossier.zip', 'cities/Baghdad/airport-time-distance.svg',
                 'cities/Baghdad/airport-traction-single-line.svg', 'cities/Baghdad/SERVICE-DIAGRAMS.md', 'cities/Baghdad/AIRPORT-OPENING.md', 'cities/Baghdad/maps/STATION-PRICING.md',
                 'cities/Baghdad/engineering/mechanical/civil/SPAN-COMPARISON.md',
                 'cities/Baghdad/engineering/mechanical/vehicle/SECTION-POWER.md', 'cities/Baghdad/service-diagrams.html',
                 'cities/Baghdad/service-diagrams.js', 'cities/Baghdad/service-diagrams.css',
                 'cities/Baghdad/COST-AND-DELIVERY.md', 'cities/Baghdad/BUYER-COMPARISON.md',
                 'cities/Baghdad/maps/Baghdad-148km.png', 'cities/Baghdad/maps/Baghdad-606km.png',
                 'docs/reference-v07/cost/README.md', 'docs/reference-v07/integration/TIMETABLE.md'))
    files.update((ROOT / 'cities/Baghdad/engineering/prototype').glob('*-guide.md'))
    raw = (HERE/'twins/models.js').read_text().strip()
    models = json.loads(raw.removeprefix('window.RAIL_MODELS=').removesuffix(';'))
    for m in models.values():
        files.update(ROOT / path for path in m['links'].values())
    simulation = ROOT / "cities/Baghdad/engineering/simulation"
    files.update(simulation / name for name in (
        "AUDIT-RESULTS.md", "ASSUMPTION-AUDIT.md", "ALIGNMENT-DEMAND.md",
        "vehicle-audit-guide.md", "audit-production-guide.md", "audit-verification.json",
    ))
    raw = (HERE / 'finance/enquiries-data.js').read_text().strip()
    enquiries = json.loads(raw.removeprefix('const railwayEnquiries = ').removesuffix(';'))
    # Supply the exact drawing or record named in each downloadable enquiry.
    records = {}
    for railway in enquiries.values():
        for article in railway['lots']:
            for name, digest in article['records'].items():
                path = ROOT / name
                if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
                    raise ValueError(f'Refresh the supplier enquiry for {name}')
                records[path] = digest
    files.update(records)
    # Keep relative links from the original quotation records usable offline.
    for path in records:
        if path.suffix == '.md':
            for destination in re.findall(r'\[[^]\n]*\]\(([^()\s]+)\)', path.read_text()):
                parts = urlsplit(destination)
                if not parts.scheme and not parts.netloc and parts.path:
                    target = (path.parent / parts.path).resolve()
                    if target.is_relative_to(ROOT) and target.is_file():
                        files.add(target)
    members = {'START.html': START.encode()}
    for path in sorted(files):
        members[path.relative_to(ROOT).as_posix()] = (
            path.read_bytes() if path in records else document_content(path, files))
    for page, content in members.items():
        if page.endswith('.html'):
            WorkshopLinks(page, members).feed(content.decode())
    return members


def current(destination, members):
    try:
        with ZipFile(destination) as archive:
            return (archive.namelist() == list(members) and
                    all(archive.read(name) == content for name, content in members.items()))
    except (FileNotFoundError, BadZipFile):
        return False


def build(members=None):
    members = workshop_files() if members is None else members
    buffer = io.BytesIO()
    with ZipFile(buffer, 'w') as archive:
        for name, content in members.items():
            info = ZipInfo(name, (2026, 11, 19, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content)
    return buffer.getvalue()


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    dest = HERE / 'OpenSourceRail-Operator-Kit.zip'
    members = workshop_files()
    if not current(dest, members):
        if args.check:
            raise SystemExit('Rebuild the operator kit from the published files')
        with tempfile.NamedTemporaryFile(dir=dest.parent, delete=False) as temporary:
            path = Path(temporary.name)
        try:
            path.write_bytes(build(members))
            path.chmod(0o644)
            path.replace(dest)
        finally:
            path.unlink(missing_ok=True)
