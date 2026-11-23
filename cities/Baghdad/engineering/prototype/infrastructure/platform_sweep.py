"""Screen circular platform edges against the Airport nominal car envelope."""
import argparse
from hashlib import sha256
import json
from math import hypot, sqrt
from pathlib import Path
import tomllib
from zipfile import ZipFile


HERE = Path(__file__).resolve().parent
PROTOTYPE = HERE.parent


def radial_gaps(radius, pivot, half_width, nominal_gap, x):
    """Positive gaps are separation. Radii reference the bogie pivot trajectory."""
    if radius <= pivot or radius <= half_width + nominal_gap:
        raise ValueError("Curve radius outside two-pivot concentric platform model")
    midpoint_radius = sqrt((radius - pivot) * (radius + pivot))
    inner_edge = radius - half_width - nominal_gap
    outer_edge = radius + half_width + nominal_gap
    return (hypot(midpoint_radius - half_width, x) - inner_edge,
            outer_edge - hypot(midpoint_radius + half_width, x))


def report():
    ga = json.loads((PROTOTYPE / 'vehicle-factory/installed-ga.json').read_text())
    with ZipFile(PROTOTYPE / 'airport-prototype.zip') as archive:
        civil_bytes = archive.read('civil-article.json')
        manifest = json.loads(archive.read('manifest.json'))
    civil = json.loads(civil_bytes)
    if (sha256(civil_bytes).hexdigest() != manifest['sha256']['civil-article.json']
            or ga['candidate_id'] != civil['candidate_id']
            or ga['mechanical_evaluation_id'] != civil['mechanical_evaluation_id']):
        raise ValueError("Inconsistent article identity or civil record")
    geom = ga['geometry']
    pivots = [b['body_from_bogie_translation_m'][0] for b in geom['bogies']]
    if len(pivots) != 2 or pivots[0] != -pivots[1] or pivots[1] <= 0:
        raise ValueError("Expected two symmetric bogie pivots")
    gap = civil['station_interfaces']['static_level_horizontal_gap_m']
    width = geom['car_width_m'] / 2
    radii = tomllib.loads((PROTOTYPE.parent / 'mechanical/quotation.toml').read_text())['screen']['curve_radii_m']
    openings = sorted({(abs(d['centre_x_m']), d['rough_width_m']) for d in geom['door_apertures']})
    lines = [
        '# Airport platform edge and doorway curve screen', '',
        'A straight 75 mm platform offset carried around a curve can intersect the nominal car. The table gives the minimum inside-curve and outside-curve body separation over the whole car and the minimum and maximum at each doorway. Negative values indicate geometric overlap. All gaps are radial millimetres, rounded to the nearest millimetre. Symmetric door positions share a row.', '',
        '| Illustrative radius, m | Body or door centre from car midpoint | Inside platform gap, mm | Outside platform gap, mm |',
        '|---:|---|---:|---:|',
    ]
    for radius in radii:
        def gaps(x):
            return radial_gaps(radius, pivots[1], width, gap, x)
        body = (gaps(0)[0], gaps(geom['car_length_m'] / 2)[1])
        lines.append(f'| {radius:g} | Whole body minimum | {body[0]*1000:.0f} | {body[1]*1000:.0f} |')
        for centre, rough_width in openings:
            near = gaps(max(0., centre - rough_width / 2))
            far = gaps(centre + rough_width / 2)
            lines.append(f'| {radius:g} | ±{centre:g} m door | {near[0]*1000:.0f} to {far[0]*1000:.0f} | {far[1]*1000:.0f} to {near[1]*1000:.0f} |')
    lines += ['', 'The car is a rigid 17 m rectangle on two pivots 12.8 m apart. The example uses concentric track and platform arcs, a 2.70 m wide body and a 1.36 m rough opening at each door. Each side of the rectangle follows the chord between the pivots. Its radial distance increases from the car midpoint towards the ends. The straight case gives 75 mm at every point. The three radii reproduce the existing mechanical screen and have no surveyed station assignment.', '',
              'Use the whole-body minimum to identify interference even when door gaps appear clear. Moving an edge away from the train increases both the minimum clearance and the largest boarding gap on that side. Before locating an edge, survey track curvature, transitions, cant and stopping range over the platform. Add wheel and track wear, lateral and vertical suspension travel, installed threshold projection, body deflection, construction tolerance and permitted gap and step limits. Survey all 24 boarding zones and retain accessible boarding and clearance results separately.', '',
              f"Airport physical candidate `{ga['candidate_id']}`. Vehicle arrangement evaluation `{ga['evaluation_id']}`. Civil evaluation `{civil['evaluation_id']}`.", '',
              '[Vehicle arrangement](../vehicle-factory/INSTALLED-GA.md) · [Station enquiry](STATION.md) · [Calculation](platform_sweep.py)', '']
    return '\n'.join(lines)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    generated = report()
    if args.check:
        if (HERE / 'PLATFORM-SWEEP.md').read_text() != generated:
            raise SystemExit('Stale platform sweep')
    else:
        print(generated, end='')
