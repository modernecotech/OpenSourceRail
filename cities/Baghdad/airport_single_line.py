"""Quotation drawing of the restored-feed topology in the priced Airport opening."""
from html import escape
from itertools import pairwise
from math import ceil, isclose

from engineering.outline.baghdad_system import _id


def single_line_svg(opening):
    feeder = opening.get("section_power") or {}
    selected = feeder.get("selected") or {}
    bundle, power = opening["bundle"], opening["power"]
    physical = {key: selected.get(key) for key in (
        "feed_system", "grid_sites", "site_chainage_km", "route_km", "source_kv", "droop_ohm",
        "outward_ohm_per_km", "return_ohm_per_km")}
    design = _id(physical)
    if (selected.get("feed_system") != "sectioned radial with midpoint ties"
            or power["option"] != "protected_conductor" or bundle["service_group"] != "Airport"
            or opening["candidate_id"] != _id(bundle) or power["parent_candidate_id"] != opening["candidate_id"]
            or feeder.get("evaluation_id") != _id({k: v for k, v in feeder.items() if k != "evaluation_id"})
            or feeder["power_evaluation_id"] != power["evaluation_id"]
            or feeder["power_candidate_id"] != power["physical_candidate_id"]
            or any(identity != design for identity in (bundle.get("feeder_design_id"), power.get("feeder_design_id"),
                                                       feeder["design_id"], selected["design_id"]))):
        raise ValueError("Single-line drawing requires the priced Airport radial feeder and matching identities")
    sites, n, route = selected["site_chainage_km"], selected["grid_sites"], bundle["route_km"]
    q = feeder["procurement"]
    if (not 3 <= n <= 64 or len(sites) != n or sites[0] != 0 or not isclose(sites[-1], route)
            or not isclose(selected["route_km"], route) or any(b <= a for a, b in pairwise(sites))
            or any(count != n for count in (bundle["grid_sites"], power["supply"]["grid_sites"], q["dc_source_groups"]))
            or any(count != 4*(n-1) for count in (q["dc_outgoing_breaker_circuits"], q["feed_half_bays"],
                                                   power["supply"]["powered_section_count"]))
            or q["normally_open_track_ties"] != 2*(n-1)):
        raise ValueError("Drawing quantities differ from the priced radial circuits")
    groups = ceil((n-1) / 6)
    detail = 208 + groups * 120
    height = detail + 476
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1060 {height}" role="img" aria-labelledby="title desc">',
             '<title id="title">Baghdad Airport traction supply single-line drawing</title>',
             '<desc id="desc">Planning layout of both positive conductor tracks and normally open ties, '
             'followed by a vehicle and rail-return circuit detail.</desc>',
             '<style>text{font:15px sans-serif;fill:#192e3e}.heading{font:bold 24px sans-serif}.sub{font:bold 18px sans-serif}'
             '.small{font:13px sans-serif}.id{font:13px monospace}.pos,.ac,.neg{fill:none;stroke:#126477;stroke-width:2.5}'
             '.ac{stroke:#293e50}.neg{stroke:#774526;stroke-dasharray:7 3}.breaker{fill:white;stroke:#0c5567;stroke-width:2}'
             '.tie{fill:none;stroke:#0c5567;stroke-width:2}.src{fill:#eaf5f7;stroke:#286576;stroke-width:1.6}</style>',
             '<rect width="100%" height="100%" fill="white"/>']

    def label(x, y, value, css="", anchor="start"):
        parts.append(f'<text x="{x}" y="{y}" class="{css}" text-anchor="{anchor}">{escape(str(value))}</text>')

    def path(d, css, attrs=""):
        parts.append(f'<path d="{d}" class="{css}" {attrs}/>')

    label(30, 37, "Baghdad Airport  |  Traction power single line", "heading")
    label(30, 67, f'{route:g} km  •  {n} rectifier sites  •  {q["dc_outgoing_breaker_circuits"]} outgoing DC breakers  •  {q["normally_open_track_ties"]} normally open ties')
    label(30, 94, f'Opening candidate  {opening["candidate_id"]}', "id")
    label(30, 116, f'Feeder design      {design}', "id")
    label(30, 150, "Normal supply by chainage", "sub")
    label(30, 174, "Squares are closed outgoing breakers. Open blades are track ties. Repeated site labels continue the preceding row.")
    for row in range(groups):
        first, last = row * 6, min(n-1, (row+1)*6)
        y = 211 + row * 120
        for offset, index in enumerate(range(first, last+1)):
            x = 148 + offset * 139
            parts.append(f'<rect x="{x-27}" y="{y-16}" width="54" height="22" rx="3" class="src"/>')
            label(x, y, f"S{index+1:02d}", "small", "middle")
            label(x, y+83, f"{sites[index]:.3f} km", "small", "middle")
            path(f"M{x} {y+6}V{y+58}", "pos")
        for track in range(2):
            level = y + 30 + track*28
            label(30, level+5, f"Track {track+1} +")
            for index in range(first, last):
                left = 148+(index-first)*139
                mid, right = left+69.5, left+139
                path(f"M{left} {level}H{mid-6} M{mid+6} {level}H{right}", "pos")
                for bx, side in ((left+19, "left"), (right-19, "right")):
                    parts.append(f'<rect x="{bx-4}" y="{level-4}" width="8" height="8" class="breaker" '
                                 f'data-device="breaker" data-bay="{index+1}" data-track="{track+1}" data-side="{side}"/>')
                path(f"M{mid-6} {level}l10 -8", "tie",
                     f'data-device="tie" data-bay="{index+1}" data-track="{track+1}"')

    label(30, detail, "Local supply and return  |  S01 to the first track tie", "sub")
    label(30, detail+24, "One end-site circuit is expanded below. Each terminal feeds two outgoing circuits. Each interior site feeds four.")
    y = detail+76
    label(34, y-10, "Utility AC", "small")
    path(f"M33 {y}H146", "ac")
    parts.append(f'<rect x="146" y="{y-22}" width="192" height="50" class="src"/>')
    label(242, y, "Transformer + rectifier", "small", "middle")
    label(242, y+18, "S01", "small", "middle")
    path(f"M338 {y-7}H448V{y+30}H775 M775 {y+30}H820 M836 {y+30}H997", "pos")
    path(f"M820 {y+30}l13 -10", "tie")
    parts.append(f'<rect x="490" y="{y+24}" width="12" height="12" class="breaker"/>')
    label(352, y-18, f'{selected["source_kv"]:.2f} kV DC + bus', "small")
    label(480, y+12, "Feeder breaker", "small")
    label(712, y+12, "Protected conductor", "small")
    label(847, y+52, "Toward S02", "small")
    path(f"M615 {y+30}v19 m0 28v22", "pos")
    parts.append(f'<rect x="559" y="{y+49}" width="112" height="28" class="src"/>')
    label(615, y+68, "Train / shoes", "small", "middle")
    path(f"M997 {y+99}H381V{y+16}H338", "neg")
    label(680, y+89, "Running rails / negative return", "small")
    label(389, y+121, "Negative return bonds and fault-current path require supplier design.", "small")

    label(30, detail+232, "Outage operation, access and quotation holds", "sub")
    label(30, detail+260, "A failed source divides the restored sections at its chainage. Adjacent healthy sites may feed toward the isolated bus.")
    label(30, detail+283, "Require selective trips, proof of isolation and a route-specific switching interlock to prevent backfeed through ties or shoes.")
    label(30, detail+306, "Before access or evacuation, inhibit traction, prove the work zone dead and establish its approved bonding and earthing state.")
    label(30, detail+329, "Emergency lighting, accessible walkways, rescue and re-energisation authority require witnessed procedures.")
    label(30, detail+364, f'Quote against {q["minimum_site_peak_dc_mw"]:.2f} MW peak DC per site and a {feeder["floor_kv"]:.2f} kV collector floor.')
    label(30, detail+387, "Return utility fault levels, transformer and rectifier duty, breaker ratings and settings, switching times and tie ratings.")
    label(30, detail+410, "Provide hot conductor and rail impedance, bond and earth layout, touch-voltage limits, cooling and cable schedules.")
    label(30, detail+448, "Preliminary supplier enquiry  •  Installation, protection coordination and operating authority require engineering review.", "small")
    return '\n'.join([*parts, '</svg>'])
