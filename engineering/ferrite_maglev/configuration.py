"""Typed, revisioned provisional configuration; unknowns are not default approvals."""
from dataclasses import asdict, dataclass
from functools import lru_cache
from copy import deepcopy
from pathlib import Path
import math
import tomllib

ROOT=Path(__file__).resolve().parents[2]
INPUT=Path(__file__).with_name('reference-configuration.toml')

@dataclass(frozen=True)
class Formation:
    city: str
    cars: int
    body_length_m: float
    coupling_gap_assumption_m: float
    doors_per_side_x_m: tuple[float,...]
    cabin_width_m: float
    arm_width_m: float
    @property
    def body_sum_m(self): return self.cars*self.body_length_m
    @property
    def assumed_overall_length_m(self): return self.body_sum_m+(self.cars-1)*self.coupling_gap_assumption_m
    @property
    def devices(self): return self.cars*2*len(self.doors_per_side_x_m)

@dataclass(frozen=True)
class Civil:
    span_m: float
    width_m: float
    depth_m: float
    web_m: float
    flange_m: float
    pier_height_m: float
    ground_level_m: float
    rail_thickness_m: float
    rail_width_m: float
    rail_pitch_m: float
    rail_segment_length_m: float

@dataclass(frozen=True)
class Configuration:
    revision: str
    formation: Formation
    civil: Civil
    station: dict
    vehicle: dict
    magnetic: dict
    evacuation: dict
    operations: dict
    cost: dict
    def record(self):
        return dict(schema='osr-selected-configuration/1',architecture='ferrite-pm-maglev-study',
            publication_role='primary-provisional-design',configuration=asdict(self),
            physical_release=False,manufacturing_release=False,design_complete=False,physical_validation=False)


@lru_cache(maxsize=8)
def _parsed(text):
    return tomllib.loads(text)


def document(path):
    # Key by actual file contents, and return independent mutable values.
    # Repeated quantity screens avoid reparsing; edits invalidate immediately.
    return deepcopy(_parsed(Path(path).read_text()))


def selected(c=None,*,city='Baghdad',cars=6):
    if c is None:c=document(ROOT/'ferrite-maglev-study.toml')
    a=document(INPUT);b=c['civil']['narrow_box_screen'];v=c['vehicle']
    if a['evacuation']['walkway_removal_approved'] is not False:raise ValueError('no approved alternative evacuation evidence adapter supplied')
    if (v['nominal_car_length_m'],v['nominal_car_width_m'],a['formation']['arm_width_m'])!=(17.,2.65,2.96):raise ValueError('native interface supports 17 m bodies, 2.65 m cabin and 2.96 m arm envelope; regenerate/revalidate unsupported geometry')
    if type(cars) is not int or not 1<=cars<=12 or (city.lower()=='baghdad' and cars!=6):
        raise ValueError('Baghdad requires six cars; other formations must be integers 1–12')
    f=Formation(city,cars,v['nominal_car_length_m'],a['formation']['coupling_gap_assumption_m'],
        tuple(a['formation']['doors_per_side_x_m']),v['nominal_car_width_m'],a['formation']['arm_width_m'])
    cv=Civil(c['civil']['reference_span_m'],b['outer_width_m'],b['outer_depth_m'],b['web_thickness_m'],b['flange_thickness_m'],**a['civil'])
    for field,value in asdict(cv).items():
        if not math.isfinite(value) or (field!='ground_level_m' and value<=0):raise ValueError('invalid civil '+field)
    if cv.width_m<=2*cv.web_m or cv.depth_m<=2*cv.flange_m or cv.rail_segment_length_m>cv.rail_pitch_m:raise ValueError('invalid section or rail segmentation')
    if f.coupling_gap_assumption_m<0 or not f.doors_per_side_x_m or len(set(f.doors_per_side_x_m))!=len(f.doors_per_side_x_m) or any(abs(x)+.67>=f.body_length_m/2 for x in f.doors_per_side_x_m):raise ValueError('invalid assumed coupling or door layout')
    if a['station']['island_width_m']<=a['station']['lift_width_m']+2*a['station']['minimum_side_passage_m']:raise ValueError('lift blocks island circulation')
    from . import model
    baseline_mass=model.mass(c,c['mass']['ferrite_base'],c['power']['gross_battery_matched_kwh_per_car'])
    return Configuration(a['revision'],f,cv,a['station'],dict(
        baseline_tare_kg_per_car=baseline_mass['tare_kg'],
        payload_aw3_kg_per_car=v['aw3_passengers_per_car']*v['passenger_mass_screen_kg'],
        cg_m=None,inertia_kg_m2=None,net_chute_addition_kg=None),
        dict(modules_per_car=24,force_map=None,measured_electrical_limits=None),a['evacuation'],
        dict(charger_kw_per_car=c['power']['candidate_station_charger_kw_per_car'] if 'candidate_station_charger_kw_per_car' in c['power'] else 600.,
            gross_storage_kwh_per_car=c['power']['gross_battery_matched_kwh_per_car'],approved_reserve_kwh=None,recovery_method=None),
        dict(quantity_basis='selected native geometry; unmodelled and unpriced scope remains open',installed_programme_usd=None,origin_audited=False))


def source_paths():return [Path(__file__),INPUT,ROOT/'ferrite-maglev-study.toml']
