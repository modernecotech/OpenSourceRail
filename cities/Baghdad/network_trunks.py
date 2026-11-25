"""Compare whole Baghdad corridor withdrawals around retained metropolitan spines."""

from dataclasses import dataclass
from math import cos, fsum, radians
from pathlib import Path

import numpy as np

from .central_access import ROOT, digest
from .holistic_network import EXACT_CROSSING_M, LOCAL_METRES, MAX_TERMINAL_LINK_KM, Track, _physical_line, validate
from .rail_consolidation import refresh_interchange_names
from .residential_layouts import LineEdit, _clip, _rebuild_memberships


@dataclass(frozen=True)
class Skeleton:
    name: str
    purpose: str
    withdrawn: tuple[str, ...] = ()
    retained: tuple[str, ...] = ()
    branches: tuple[LineEdit, ...] = ()
    eastern_splice: bool = False


AIRPORT_APPROACH = LineEdit(
    "M05", "Use C1 for the central and Airport approaches. Run M05 east of the retained Zayouna-area "
    "interchange, with a turnback to verify.", start_station="X-C1-M05-01",
)
WESTERN_M03 = LineEdit(
    "M03", "Use M06 for the eastern reach. End the remaining M03 at its retained M04 interchange, "
    "with a turnback to verify.", end_station="X-M03-M04-01",
)
G08_CENTRAL = LineEdit(
    "G08", "Link C1 and G13 through M05 and M12.",
    start_station="X-G08-C1-6bba3a2720", end_station="X-G08-G13-2066606f1c",
)
T20_EAST = LineEdit(
    "T20", "Use C2 for the central approach and run the independent eastern T20 link "
    "between M05 and M06.", start_station="M05-infill-13500",
)
METROPOLITAN = ("C1", "C2", *(f"M{index:02d}" for index in range(1, 15)))
CONSOLIDATED_FEEDERS = ("G04", "G05", "G08", "T40")
CENTRAL_ANCHORS = ("Tahrir", "Mansour", "Karkh", "Shorja", "University")
EAST_JUNCTION = "X-M03-M06-01"

SKELETONS = {
    "cross-city-trunks": Skeleton(
        "Metropolitan cross-city trunks with the eastern interchange link",
        "Use M08, M04 and G13 for west-bank crossings. Replace the T20 central approach with C2 "
        "and keep T20 between M05 and M06 for eastern transfers. Keep both approaches to M01 and Sadr.",
        withdrawn=("G08",),
        branches=(T20_EAST,),
    ),
    "cross-city-trunks-fewer-services": Skeleton(
        "Metropolitan cross-city trunks with fewer feeders",
        "Withdraw G08 and G05. Use M08, M04 and G13 for west-bank crossings and M04 for the "
        "former G05 catchment. Keep T20 between M05 and M06 and use C2 for its central approach.",
        withdrawn=("G05", "G08"),
        branches=(T20_EAST,),
    ),
    "corridor-first": Skeleton(
        "Metropolitan routes with fewer parallel feeders",
        "Use M01 and M05 in place of G04, M04 in place of G05, M08 and M04 in place of G08, "
        "and M14 and M09 in place of T40. Keep the remaining cross-city links for comparison.",
        withdrawn=CONSOLIDATED_FEEDERS,
    ),
    "radial-spines": Skeleton(
        "Radial spines with four cross-city links",
        "Concentrate service on the metropolitan lines, the C2 northwestern approach and three "
        "cross-city links serving the southwest, northern edge and Sadr. Test the loss of other "
        "east–west connections and of the overlapping T20 reach.",
        retained=(*METROPOLITAN, "G09", "G11", "T01", "T05"),
    ),
    "metropolitan-trunks": Skeleton(
        "Metropolitan corridors with Sadr access",
        "Build the network from the retained metropolitan corridors and C1 and C2, without the grid "
        "overlays. Preserve both Sadr routes and use T01 for the direct connection from C1.",
        retained=(*METROPOLITAN, "T01"),
    ),
    "alternate-east": Skeleton(
        "One eastern trunk with a western M03 branch",
        "Use M06 as the continuous outer east–south corridor. Keep the western half of M03 for its "
        "M08, M09, M02, M07 and M04 connections. Use C1 from the Airport and terminate the eastern "
        "M05 service where it meets C1. Retain the southeast T23 link from M04 to M09.",
        retained=(*METROPOLITAN, "G11", "T01", "T05", "T23"),
        branches=(AIRPORT_APPROACH, WESTERN_M03),
    ),
    "fewer-outer-routes": Skeleton(
        "Fewer outer cross-city routes",
        "Test M06 for the southeast–south reach and M08 for the southwest. Withdraw the entire M03 "
        "and M07 services, which tests the consequence of relying on nearer retained spines. "
        "Keep G11 across the south and T05 and T23 across the east.",
        retained=("C1", "C2", "M01", "M02", "M04", "M05", "M06", "M08", "M09", "M10",
                  "M11", "M12", "M13", "M14", "G11", "T01", "T05", "T23"),
        branches=(AIRPORT_APPROACH,),
    ),
    "compact-grid": Skeleton(
        "Central cross-city links with fewer outer corridors",
        "Keep G09 and G13 for direct approaches to C2 and G11 across the south. Withdraw the "
        "outer M03 and M13 corridors and the continuously overlapping G04, G05 and G08 feeders. "
        "Keep the C1–Sadr, Sadr cross-town and northern M14–M05 links.",
        retained=("C1", "C2", "M01", "M02", "M04", "M05", "M06", "M07", "M08", "M09", "M10",
                  "M11", "M12", "M14", "G09", "G11", "G13", "T01", "T02", "T05", "T19", "T23"),
    ),
    "eastern-junction": Skeleton(
        "One eastern approach with both outer branches",
        "Join the southwestern M06 approach to the northern M03 reach at their mapped crossing. "
        "Keep the original northeastern M06 branch from that crossing and end the separated western "
        "M03 service at M04. Withdraw G04, G05 and T40 while retaining G08 as a west-bank cross-city link.",
        withdrawn=("G04", "G05", "T40"),
        branches=(WESTERN_M03,),
        eastern_splice=True,
    ),
    "eastern-trunk-only": Skeleton(
        "One eastern approach with the west-bank network retained",
        "Join M06 to the outer M03 reach at the existing crossing and retain the northeastern M06 reach "
        "as a branch. The western M03 ends at M04, and both branches remain close beyond the crossing.",
        branches=(WESTERN_M03,),
        eastern_splice=True,
    ),
    "eastern-trunk-west-bank-link": Skeleton(
        "One eastern approach with a shorter G08",
        "Consolidate the eastern approach at the M03–M06 crossing and keep the middle G08 link "
        "between C1 and G13. Rely on M08 and M04 at the former ends of G08. Retain G04 and G05.",
        branches=(WESTERN_M03, G08_CENTRAL),
        eastern_splice=True,
    ),
    "eastern-trunk-west-bank-withdrawal": Skeleton(
        "One eastern approach and fewer west-bank routes",
        "Consolidate the eastern approach at the M03–M06 crossing. Withdraw G08 and test whether "
        "M08, M04 and G13 can cover its connections. Retain G04 and G05.",
        withdrawn=("G08",),
        branches=(WESTERN_M03,),
        eastern_splice=True,
    ),
    "west-bank-links": Skeleton(
        "West-bank links into the metropolitan trunks",
        "Retain G04 only between M05 and G09, preserving a western approach to M02, M01 and G09. "
        "Keep G08 between C1 and G13. Use M01, M04 and M14 for the rest, and remove G05 and T40 "
        "as complete services. Keep direct east-side links while the western alternatives are tested.",
        withdrawn=("G05", "T40"),
        branches=(
            LineEdit("G04", "End the independent western link at G09.", end_station="X-G04-G09-2cdd834130"),
            G08_CENTRAL,
        ),
    ),
}


def _splice_east(original, revised):
    """Use the mapped M03–M06 crossing as a planning junction."""
    branches = ("M06", "M03")
    if "B06" in revised["lines"] or set(branches) - revised["lines"].keys():
        raise ValueError("Eastern reassignment requires both M03 and M06 and an unused B06 line ID")
    source = [original["lines"][code] for code in branches]
    if any(EAST_JUNCTION not in row["station_chainage_km"] for row in source):
        raise ValueError("The mapped M03–M06 crossing is absent from the supplied lines")
    positions = [row["station_ids"].index(EAST_JUNCTION) for row in source]
    km = [row["station_chainage_km"][EAST_JUNCTION] for row in source]
    inbound, outbound = (Track(row["geometry"]) for row in source)
    a, b = km
    if a < .4 or outbound.km - b < .4:
        raise ValueError("Eastern junction lacks the mapped 400 m approach and departure chords")
    junction = original["stations"][EAST_JUNCTION]["coordinates"]
    for track, chainage in zip((inbound, outbound), km, strict=True):
        if np.linalg.norm((np.asarray(track.at(chainage)) - junction) * LOCAL_METRES) > EXACT_CROSSING_M:
            raise ValueError("Eastern junction does not coincide with both source track chainages")
    approaches = np.asarray([np.asarray(junction) - inbound.at(a - .4),
                             np.asarray(outbound.at(b + .4)) - junction]) * LOCAL_METRES
    if np.dot(*approaches) < np.prod(np.linalg.norm(approaches, axis=1)) * cos(radians(30)):
        raise ValueError("Mapped M06 to M03 departure exceeds the 30° junction chord screen")
    i, j = positions
    m06, m03 = source
    approach_stops = m06["station_ids"][:i + 1]
    former_east_stops = m06["station_ids"][i:]
    north_stops = m03["station_ids"][j + 1:]
    approach = inbound.between(0., a)
    onward = outbound.between(b, outbound.km)
    remaining = inbound.between(a, inbound.km)
    stations = original["stations"]
    basis = "Mapped junction screen. Turnout, grades, clearance, turnback and interlocking require verification."
    through = _physical_line([*approach[:-1], junction, *onward[1:]], approach_stops + north_stops,
                             stations, m06["source_sections"] + m03["source_sections"], basis)
    branch = _physical_line([junction, *remaining[1:]], former_east_stops,
                            stations, m06["source_sections"], basis)
    revised["lines"]["M06"] = through | {"name": "Al-Yusufiyah–Al-Shaoura"}
    revised["lines"]["B06"] = branch | {"name": f"{stations[EAST_JUNCTION]['name']}–Diyala"}
    return m03["one_way_km"] - b, [
        {"line_id": "M06", "action": "through_reroute", "reason": basis,
         "retained_source_chainage_km": [[0., a]], "new_terminal_ids": [approach_stops[0], north_stops[-1]],
         "transferred_source_intervals": [{"line_id": "M03", "chainage_km": [b, outbound.km]}],
         "withdrawn_calls": former_east_stops[1:], "removed_route_km": 0.},
        {"line_id": "B06", "action": "branch_from_retained_alignment", "reason": basis,
         "retained_source_chainage_km": [[a, inbound.km]],
         "new_terminal_ids": [former_east_stops[0], former_east_stops[-1]], "source_line_id": "M06",
         "withdrawn_calls": [], "removed_route_km": 0.},
    ]


def _skeleton(network, concept, protected):
    if concept.retained:
        unknown = set(concept.retained) - network["lines"].keys()
        if unknown:
            raise ValueError(f"Missing retained lines: {', '.join(sorted(unknown))}")
        withdrawn = network["lines"].keys() - set(concept.retained)
    else:
        withdrawn = set(concept.withdrawn)
        unknown = withdrawn - network["lines"].keys()
        if unknown:
            raise ValueError(f"Missing lines to withdraw: {', '.join(sorted(unknown))}")

    # Reuse wholly retained line geometry and stops. Only the branch experiments
    # need to reconstruct geometry from registered chainages.
    revised = {**network, "lines": {code: row.copy() for code, row in network["lines"].items()
                                   if code not in withdrawn}}
    actions = []
    branches = {edit.line_id: edit for edit in concept.branches}
    for code in sorted(withdrawn | branches.keys()):
        original = network["lines"][code]
        edit = branches.get(code)
        if edit is None:
            reason = concept.purpose
            action, kept, terminals, intervals, remainder = "withdraw_line", [], [], [], 0.
        else:
            if code not in revised["lines"]:
                raise ValueError(f"Cannot clip a withdrawn line: {code}")
            line, intervals = _clip(original, edit, network["stations"])
            revised["lines"][code] = line
            action, reason, kept = "trim", edit.reason, line["station_ids"]
            terminals, remainder = [kept[0], kept[-1]], line["one_way_km"]
        lost = [stop for stop in original["station_ids"] if stop not in kept]
        actions.append({"line_id": code, "action": action, "reason": reason,
                        "retained_source_chainage_km": intervals, "new_terminal_ids": terminals,
                        "withdrawn_calls": lost, "removed_route_km": round(original["one_way_km"] - remainder, 3)})

    if concept.eastern_splice:
        reassigned_km, splice_actions = _splice_east(network, revised)
        m03 = next(row for row in actions if row["line_id"] == "M03")
        m03["removed_route_km"] = round(m03["removed_route_km"] - reassigned_km, 3)
        actions.extend(splice_actions)
    _rebuild_memberships(revised)
    if missing := protected - revised["stations"].keys():
        raise ValueError(f"Protected stops withdrawn: {', '.join(sorted(missing))}")
    for edit in concept.branches:
        for stop in (edit.start_station, edit.end_station):
            if stop is not None and len(revised["stations"][stop]["lines"]) < 2:
                raise ValueError(f"{edit.line_id} loses its new terminal interchange at {stop}")
        summary = revised.get("through_lines", {}).get(edit.line_id)
        if summary is not None:
            terminal_lines = [set(revised["stations"][stop]["lines"]) - {edit.line_id}
                              for stop in summary["terminal_ids"]]
            if (revised["lines"][edit.line_id]["one_way_km"] <= MAX_TERMINAL_LINK_KM
                    and all(terminal_lines) and not set.intersection(*terminal_lines)
                    and summary["transfer_count"] == 2):
                summary["terminal_link_only"] = True
    for action in actions:
        stops = action["withdrawn_calls"]
        action["closed_stations"] = [stop for stop in stops if stop not in revised["stations"]]
        action["retained_station_calls_on_other_lines"] = [stop for stop in stops if stop in revised["stations"]]

    revised["topology"] = validate(revised)
    revised["physical_accepted"] = revised["operating_timetable_validated"] = False
    revised["layout_revision"] = {"parent_candidate_id": network["candidate_id"],
                                  "parent_evaluation_id": network["evaluation_id"],
                                  "actions": actions, "terminal_turnback_validated": False}
    revised["source_sha256"] = {**network.get("source_sha256", {}),
                                Path(__file__).relative_to(ROOT).as_posix(): digest(Path(__file__))}
    return refresh_interchange_names(revised), actions


def alternatives(network, *, protected_stations=()):
    """Return graph-valid trunk skeletons or their recorded construction failures.

    All choices preserve C1's full flight-terminal route and the named central
    anchors where those anchors exist in the supplied candidate. A retained
    chainage and existing passenger interchange leave turnback feasibility open.
    Evaluate walking, journeys and overlap independently on the resulting network.
    """
    validate(network)
    if "C1" not in network["lines"] or "Airport-00" not in network["lines"]["C1"]["station_ids"]:
        raise ValueError("Trunk comparison requires the mapped C1 Airport service")
    protected = (set(protected_stations) | set(network["lines"]["C1"]["station_ids"])
                 | (set(CENTRAL_ANCHORS) & network["stations"].keys()))
    original_km = fsum(row["one_way_km"] for row in network["lines"].values())
    options = {}
    for key, concept in SKELETONS.items():
        summary = {"name": concept.name, "rationale": concept.purpose}
        try:
            revised, actions = _skeleton(network, concept, protected)
        except ValueError as error:
            options[key] = {**summary, "network": None, "actions": [], "removed_route_km": None,
                            "rejection_reason": str(error)}
            continue
        retained_km = fsum(row["one_way_km"] for row in revised["lines"].values())
        options[key] = {**summary, "network": revised, "actions": actions,
                        "removed_route_km": round(original_km - retained_km, 2)}
    return options
