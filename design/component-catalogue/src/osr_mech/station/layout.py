"""Shared station topology, geometry and access quantities (RFC 0034).

Coordinates are millimetres. Study envelopes are not structural or evacuation
approvals. Door sides assume each track's declared travel direction.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import math
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
        return {**asdict(self), "quantities": self.quantities,
                "equipment_geometry_contained": True, "street_access_accepted": False}


def station_layout(parameters: dict[str, Any]) -> StationLayout:
    layout = str(parameters.get("platform_layout", "side"))
    elevation = str(parameters.get("elevation", "elevated" if layout == "stacked" else "at-grade"))
    if elevation not in ("elevated", "at-grade"):
        raise ValueError("elevation must be elevated or at-grade")
    if elevation == "elevated" and layout == "side" and not parameters.get("layout_exception_reason"):
        raise ValueError("ordinary elevated side platforms require layout_exception_reason")
    count = int(parameters.get("platform_count", 1))
    length = float(parameters["platform_length_m"]) * 1000
    if count <= 0 or not math.isfinite(length) or length <= 0:
        raise ValueError("platform count and length must be positive")
    island = layout in ("island", "stacked", "same-grade-transfer")
    width = float(parameters.get("platform_width_m", 8.0 if island and elevation == "elevated" else 6.0 if island else 3.0)) * 1000
    if not math.isfinite(width) or width <= 0:
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
            if "access_equipment" not in parameters:
                # Pack from the platform ends inwards with 500 mm separation;
                # fractional chainages let stairs overhang shorter platforms.
                stair_x=length/2-5500.0
                lift_x=stair_x-7250.0
                escalator_x=lift_x-7250.0
                if escalator_x<5500:
                    raise ValueError("short elevated platform requires an explicit contained access layout")
                for kind,x,w,l in (("lift",lift_x,3500,3500),("shaft",lift_x,3500,3500),
                                   ("escalator",escalator_x,1800,10000),("staircase",stair_x,3000,10000)):
                    for j,sign in enumerate((-1,1),1):
                        equipment.append(AccessEquipment(f"{platform_id}-{kind}-{j}",kind,served,sign*x,y,w,l))
    if "access_equipment" in parameters:
        equipment = [AccessEquipment(**{**row,"served_levels":tuple(row["served_levels"])}) for row in parameters["access_equipment"]]
    for row in parameters.get("additional_access_equipment", []):
        equipment.append(AccessEquipment(**{**row, "served_levels": tuple(row["served_levels"])}))
    identities = [e.id for e in equipment]
    if len(identities) != len(set(identities)):
        raise ValueError("access equipment identities must be unique")
    level_ids = set(levels)
    if any(e.kind not in ("lift","escalator","staircase","shaft") or not set(e.served_levels) <= level_ids or len(e.served_levels)<2
           or len(set(e.served_levels))!=len(e.served_levels)
           or any(not math.isfinite(v) for v in (e.x_mm,e.y_mm,e.width_mm,e.length_mm))
           or e.width_mm <= 0 or e.length_mm <= 0
           or any(levels[a]>=levels[b] for a,b in zip(e.served_levels,e.served_levels[1:])) for e in equipment):
        raise ValueError("invalid access equipment type, levels or envelope")
    concourses=[]
    if "concourse_decks" in parameters:
        concourses=[{'x_mm':0.,'y_mm':0.,'thickness_mm':350.,**row} for row in parameters["concourse_decks"]]
    else:
        for level,z in levels.items():
            if not level.startswith("concourse"):continue
            serving=[e for e in equipment if level in e.served_levels]
            # This is a required structural envelope, with no site/strength
            # acceptance. It must contain the complete access footprint.
            x=max((abs(e.x_mm)+e.length_mm/2+500 for e in serving),default=12000.)
            y=max((abs(e.y_mm)+e.width_mm/2+500 for e in serving),default=5000.)
            concourses.append(dict(id=level,level=level,z_mm=z,x_mm=0.,y_mm=0.,
                length_mm=max(24000.,2*x),width_mm=max(10000.,2*y),thickness_mm=350.))
    if len({d['id'] for d in concourses})!=len(concourses):
        raise ValueError("concourse deck identities must be unique")
    for d in concourses:
        if d['level'] not in levels or not d['level'].startswith('concourse') or d['z_mm']!=levels[d['level']] or any(
            not math.isfinite(d[k]) for k in ('x_mm','y_mm','length_mm','width_mm','thickness_mm')) or min(d['length_mm'],d['width_mm'],d['thickness_mm'])<=0:
            raise ValueError("invalid concourse support envelope")
    def contained(e,x,y,l,w):
        return abs(e.x_mm-x)+e.length_mm/2<=l/2+1e-6 and abs(e.y_mm-y)+e.width_mm/2<=w/2+1e-6
    for e in equipment:
        for level in e.served_levels:
            if level=='street':continue  # Land, crossings and street access need survey.
            envelopes=[(0.,p.y_mm,length,p.width_mm) for p in platforms if p.level==level]
            envelopes += [(d['x_mm'],d['y_mm'],d['length_mm'],d['width_mm']) for d in concourses if d['level']==level]
            if not any(contained(e,*bounds) for bounds in envelopes):
                raise ValueError(f"access equipment {e.id} extends outside its {level} support envelope")
    clear=min((p.width_mm/2-abs(e.y_mm-p.y_mm)-e.width_mm/2
               for p in platforms for e in equipment if p.level in e.served_levels
               and contained(e,0.,p.y_mm,length,p.width_mm)),default=width/2)
    required_clear=float(parameters.get("minimum_clear_width_m",1.5))*1000
    if not math.isfinite(required_clear) or required_clear<=0:
        raise ValueError("positive finite platform clear width required")
    if clear < required_clear:
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
    return StationLayout(layout,elevation,tuple(platforms),tuple(faces),tuple(equipment),entrances,transfers,clear,levels,tuple(concourses))


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
