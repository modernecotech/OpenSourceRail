"""Shared station topology, geometry and access quantities (RFC 0034).

Coordinates are millimetres. Study envelopes are not structural or evacuation
approvals. Door sides assume each track's declared travel direction.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

PLATFORM_SURFACE_Z_MM = 420.0
TOP_OF_RAIL_Z_MM = 70.0


@dataclass(frozen=True)
class Platform:
    id: str
    level: str
    y_mm: float
    base_z_mm: float
    width_mm: float


@dataclass(frozen=True)
class BoardingFace:
    id: str
    platform_id: str
    level: str
    platform_face_y_mm: float
    track_centre_y_mm: float
    boarding_z_mm: float
    top_of_rail_z_mm: float
    direction: int
    door_side: str
    psd_side: str
    static_vehicle_to_platform_gap_mm: float = 75.0
    dynamic_envelope_review_margin_mm: float = 15.0


@dataclass(frozen=True)
class AccessEquipment:
    id: str
    kind: str
    served_levels: tuple[str, ...]
    x_mm: float
    y_mm: float
    width_mm: float
    length_mm: float


@dataclass(frozen=True)
class StationLayout:
    layout: str
    elevation: str
    platforms: tuple[Platform, ...]
    faces: tuple[BoardingFace, ...]
    equipment: tuple[AccessEquipment, ...]
    entrances: tuple[dict[str, Any], ...]
    transfer_connections: tuple[dict[str, Any], ...]
    minimum_clear_width_mm: float
    level_elevations_mm: dict[str,float]
    concourse_decks: tuple[dict[str,Any],...]
    qualification: str = "study-only-access-flow-egress-and-structure-unreleased"

    @property
    def quantities(self) -> dict[str, int]:
        return dict(platform_count=len(self.platforms), boarding_face_count=len(self.faces),
                    track_count=len(self.faces),
                    **{f"{kind}_count": sum(e.kind == kind for e in self.equipment)
                       for kind in ("lift", "escalator", "staircase", "shaft")})

    def payload(self) -> dict[str, Any]:
        return {**asdict(self), "quantities": self.quantities}


def station_layout(parameters: dict[str, Any]) -> StationLayout:
    layout = str(parameters.get("platform_layout", "side"))
    elevation = str(parameters.get("elevation", "elevated" if layout == "stacked" else "at-grade"))
    if elevation not in ("elevated", "at-grade"):
        raise ValueError("elevation must be elevated or at-grade")
    if elevation == "elevated" and layout == "side" and not parameters.get("layout_exception_reason"):
        raise ValueError("ordinary elevated side platforms require layout_exception_reason")
    count = int(parameters.get("platform_count", 1))
    length = float(parameters["platform_length_m"]) * 1000
    if count <= 0 or length <= 0:
        raise ValueError("platform count and length must be positive")
    island = layout in ("island", "stacked", "same-grade-transfer")
    width = float(parameters.get("platform_width_m", 8.0 if island and elevation == "elevated" else 6.0 if island else 3.0)) * 1000
    if width <= 0:
        raise ValueError("platform width must be positive")
    if layout == "stacked":
        levels = parameters.get("levels_m", [9.0, 17.0])
        centres = [(0.0, float(z)*1000, f"platform-{i+1}") for i,z in enumerate(levels)]
    elif island:
        centres = [((i-(count-1)/2)*(width+10000), float(parameters.get("elevated_height_m",9.0))*1000 if elevation == "elevated" else 0.0, "platform") for i in range(count)]
    elif layout == "side":
        if count not in (1, 2):
            raise ValueError("side layout supports one or two platforms per level")
        centres = [(y, float(parameters.get("elevated_height_m",9.0))*1000 if elevation == "elevated" else 0.0, "platform") for y in ([5000.0] if count == 1 else [-5000.0,5000.0])]
    else:
        raise ValueError(f"unknown station layout {layout}")
    if len(centres) != count:
        raise ValueError("physical platform count must match declared levels")
    levels = {"street":0.0 if elevation == "elevated" else PLATFORM_SURFACE_Z_MM}
    levels.update({level:z+PLATFORM_SURFACE_Z_MM for _,z,level in centres})
    if elevation == "elevated":
        levels["concourse"] = 4500.0
        if layout == "stacked":
            levels["concourse-upper"] = 13000.0
    platforms, faces, equipment = [], [], []
    for i,(y,z,level) in enumerate(centres,1):
        platform_id = f"platform-{i}"
        platforms.append(Platform(platform_id,level,y,z,width))
        signs = (-1,1) if island else (-1,) if y > 0 else (1,)
        for sign in signs:
            edge = y + sign*width/2
            track = edge + sign*1500
            direction = 1 if len(faces)%2 == 0 else -1
            side = "left" if (edge-track)*direction > 0 else "right"
            faces.append(BoardingFace(f"face-{len(faces)+1}",platform_id,level,edge,track,
                                      z+PLATFORM_SURFACE_Z_MM,z+TOP_OF_RAIL_Z_MM,direction,side,side))
        if elevation == "elevated":
            served = ("street","concourse",level) if layout != "stacked" or i == 1 else (centres[i-2][2],"concourse-upper",level)
            for kind, fractions, w, l in (
                ("lift",(-0.30,0.30),3500,3500),
                ("shaft",(-0.30,0.30),3500,3500),
                ("escalator",(-0.15,0.15),1800,10000),
                ("staircase",(-0.43,0.43),3000,10000)):
                for j,f in enumerate(fractions,1):
                    equipment.append(AccessEquipment(f"{platform_id}-{kind}-{j}",kind,served,length*f,y,w,l))
    if "access_equipment" in parameters:
        equipment = [AccessEquipment(**{**row,"served_levels":tuple(row["served_levels"])}) for row in parameters["access_equipment"]]
    for row in parameters.get("additional_access_equipment", []):
        equipment.append(AccessEquipment(**{**row, "served_levels": tuple(row["served_levels"])}))
    identities = [e.id for e in equipment]
    if len(identities) != len(set(identities)):
        raise ValueError("access equipment identities must be unique")
    level_ids = set(levels)
    if any(e.kind not in ("lift","escalator","staircase","shaft") or not set(e.served_levels) <= level_ids or len(e.served_levels)<2 or e.width_mm <= 0 or e.length_mm <= 0 for e in equipment):
        raise ValueError("invalid access equipment type, levels or envelope")
    clear = min((p.width_mm-max((e.width_mm for e in equipment if e.y_mm == p.y_mm),default=0))/2 for p in platforms)
    if clear < float(parameters.get("minimum_clear_width_m",1.5))*1000:
        raise ValueError("access equipment leaves insufficient platform clear width")
    # Overlapping equipment on the same level is invalid; lift and its shaft
    # intentionally occupy the same envelope.
    installed = [e for e in equipment if e.kind != "shaft"]
    for i,a in enumerate(installed):
        for b in installed[i+1:]:
            z_overlap = max(levels[a.served_levels[0]], levels[b.served_levels[0]]) < min(levels[a.served_levels[-1]],levels[b.served_levels[-1]])
            if z_overlap and abs(a.y_mm-b.y_mm) < (a.width_mm+b.width_mm)/2 and abs(a.x_mm-b.x_mm) < (a.length_mm+b.length_mm)/2:
                raise ValueError("access equipment envelopes overlap; increase platform length or revise access")
    entrances = tuple(parameters.get("entrances", [dict(id=f"entrance-{i}",x_mm=s*length/2,y_mm=0.0,level="street",connected_to="concourse" if elevation == "elevated" else "platform",surveyed=False) for i,s in enumerate((-1,1),1)]))
    transfers = tuple(dict(from_level=centres[i][2],to_level=centres[i+1][2],via="concourse-upper",qualification="unreleased") for i in range(len(centres)-1) if layout == "stacked")
    return StationLayout(layout,elevation,tuple(platforms),tuple(faces),tuple(equipment),entrances,transfers,clear,levels,tuple(dict(id=level,level=level,z_mm=z,length_mm=24000.0,width_mm=10000.0,thickness_mm=350.0) for level,z in levels.items() if level.startswith("concourse")))


def step_free_reachability(layout: StationLayout, unavailable: set[str] | None = None) -> dict:
    """Study connectivity only; passenger capacity, fire and barriers are separate."""
    unavailable = unavailable or set()
    graph = {level:set() for level in layout.level_elevations_mm}
    for e in layout.equipment:
        if e.kind == "lift" and e.id not in unavailable:
            for a,b in zip(e.served_levels,e.served_levels[1:]):
                graph[a].add(b);graph[b].add(a)
    if layout.elevation == "at-grade":
        for p in layout.platforms:
            graph["street"].add(p.level)
    reached=set();pending=["street"]
    while pending:
        level=pending.pop()
        if level in reached:
            continue
        reached.add(level);pending.extend(graph[level]-reached)
    return dict(platforms_reachable={p.id:p.level in reached for p in layout.platforms},
                unavailable_equipment=sorted(unavailable),capacity_accepted=False,evacuation_accepted=False)
