"""Shared planning geometry from the operational profile, never supplier release."""
from __future__ import annotations

import hashlib
import math
from pathlib import Path
import tomllib
from functools import lru_cache
from copy import deepcopy

ROOT = Path(__file__).resolve().parents[4]
PROFILE_PATH = ROOT / "lib/templates/rolling-stock.toml"
# The existing detailed bogie and all family placement consumers share this datum.
BOGIE_WHEELBASE_MM = 2_100.0


@lru_cache(maxsize=2)
def _profiles(source):
    return tomllib.loads(source.decode())["profiles"]


def family_profile(family, *, _source=None):
    """Cache parsing by actual source bytes; edits cannot reuse an old profile."""
    source=PROFILE_PATH.read_bytes() if _source is None else _source;profiles=_profiles(source)
    if family not in profiles:raise ValueError(f"unknown trainset family: {family}")
    profile=deepcopy(profiles[family]);count=profile['cars'];length=profile['length_m']
    if type(count) is not int or count<1 or type(length) not in (int,float) or not math.isfinite(length) or length<=0:
        raise ValueError('invalid family dimensions')
    return profile


def family_definition(family: str) -> dict:
    source = PROFILE_PATH.read_bytes()
    profile = family_profile(family, _source=source)
    count, length = profile["cars"], float(profile["length_m"])
    if type(count) is not int or count < 1 or not math.isfinite(length) or length <= 0:
        raise ValueError("invalid family dimensions")
    car_length = length / count
    inset = BOGIE_WHEELBASE_MM / 1000
    if car_length <= 3 * inset:
        raise ValueError("family too short for the reference bogie arrangement")
    cars, bogies, joints = [], [], []
    for i in range(count):
        car_id = f"car-{i + 1}"
        start = i * car_length
        supports = [f"{car_id}/bogie-{j + 1}" for j in range(2)]
        cars.append(dict(id=car_id, start_x_m=start, centre_x_m=start + car_length / 2,
                         length_m=car_length, supports=supports))
        for j, pivot in enumerate((start + inset, start + car_length - inset)):
            bogies.append(dict(id=supports[j], parent=car_id,
                               kind="powered" if j == 0 else "trailer", pivot_x_m=pivot,
                               axle_x_m=[pivot - inset / 2, pivot + inset / 2]))
        if i:
            joints.append(dict(id=f"articulation-{i}-{i + 1}", parents=[f"car-{i}", car_id],
                               x_m=start, permitted_motion=["yaw"], geometry_status="reference-interface"))
    return dict(schema="osr-family-definition/1", family=family, cars=cars, bogies=bogies,
                articulations=joints, length_m=length, car_length_m=car_length,
                car_count=count, profile=profile,
                source_sha256={str(PROFILE_PATH.relative_to(ROOT)): hashlib.sha256(source).hexdigest()},
                geometry_basis="equal-length planning car modules; reference inset and two bogies per car",
                supplier_geometry_verified=False, engineering_released=False)
