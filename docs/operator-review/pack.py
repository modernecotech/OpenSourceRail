"""Package the offline operator workshop without requiring the engineering toolchain."""
import argparse
import hashlib
import io
import json
import re
from urllib.parse import quote, urlsplit
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

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
<a href="docs/operator-review/screens/supervision.html"><strong>Control room</strong><small>Replay equipment trips, a stale signal and restoration.</small></a>
<a href="docs/operator-review/finance/index.html"><strong>Funding and fares</strong><small>Compare debt payments and test the public funding requirement.</small></a>
<a href="docs/operator-review/delivery/index.html"><strong>Workforce and training</strong><small>Inspect shift coverage, hiring and training provision.</small></a>
<a href="cities/Baghdad/Baghdad-Metro-Proposal.pdf"><strong>Baghdad investment proposal</strong><small>Read the routes, local delivery options and the purchasing case.</small></a>
</nav><p><a href="docs/operator-review/delivery/vehicle-works.svg">Vehicle works plan</a> · <a href="docs/operator-review/delivery/precast-yard.svg">Precast yard plan</a> · <a href="cities/Baghdad/maps/Baghdad-148km.png">Seven corridors map</a> · <a href="cities/Baghdad/maps/Baghdad-606km.png">Citywide map</a></p>
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


def build():
    files = set()
    for f in HERE.rglob('*'):
        if f.suffix in {'.md', '.html', '.css', '.js', '.png', '.json', '.ifc', '.svg', '.pdf'} and f.is_file():
            files.add(f)
    files.update(ROOT / f for f in ('LICENSE.md', 'cities/Baghdad/Baghdad-Metro-Proposal.pdf',
                 'cities/Baghdad/COST-AND-DELIVERY.md', 'cities/Baghdad/BUYER-COMPARISON.md',
                 'cities/Baghdad/maps/Baghdad-148km.png', 'cities/Baghdad/maps/Baghdad-606km.png',
                 'docs/reference-v07/cost/README.md'))
    raw = (HERE/'twins/models.js').read_text().strip()
    models = json.loads(raw.removeprefix('window.RAIL_MODELS=').removesuffix(';'))
    for m in models.values():
        files.update(ROOT / path for path in m['links'].values())
    buffer = io.BytesIO()
    with ZipFile(buffer, 'w') as archive:
        def put(name, content):
            info = ZipInfo(name, (2026, 11, 19, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, content)
        put('START.html', START.encode())
        for f in sorted(files):
            put(f.relative_to(ROOT).as_posix(), document_content(f, files))
    return buffer.getvalue()


if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--check', action='store_true')
    args = ap.parse_args()
    data = build()
    dest = HERE / 'OpenSourceRail-Operator-Kit.zip'
    if args.check:
        if hashlib.sha256(data).digest() != hashlib.sha256(dest.read_bytes()).digest():
            raise SystemExit('Rebuild the operator kit from the published files')
    else:
        dest.write_bytes(data)
