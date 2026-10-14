"""Installed quantity, joint, tolerance and local-process crosswalks.

Rules distinguish manufacturable research geometry from accepted production.
Unknown fits, locking, access, processes or evidence remain explicit blockers.
"""

from collections import Counter
from .contracts import fingerprint


def compile_register(definition):
    model = definition.get("contract") or definition.get("model")
    if not model:
        return dict(
            schema="osr-installed-variant-register/1",
            state="unknown",
            parts=[],
            joints=[],
            complete_installed_kit=False,
        )
    physical = model.get("parts", model.get("instances", []))
    ids = [p["id"] for p in physical]
    if len(ids) != len(set(ids)):
        raise ValueError("one physical component may be compiled only once")
    counts = Counter(p.get("part_id", p["id"]) for p in physical)
    bill = []
    inspections = []
    processes = []
    for p in physical:
        prop = p.get("properties", {})
        if "design" in prop:
            prop = prop.get("design") or {}
        bill.append(
            dict(
                physical_id=p["id"],
                part_id=p.get("part_id", p["id"]),
                quantity=1,
                unit="ea",
                material=p.get("material"),
                defined_mass_kg=prop.get("mass_kg"),
                cg_m=prop.get("cg_m"),
                inertia_tensor_kg_m2=prop.get("inertia_tensor_kg_m2"),
                manufacturing=p.get("manufacturing", p.get("geometry")),
                production_released=False,
            )
        )
        for check in p.get("inspection_characteristics", p.get("inspections", [])):
            inspections.append(
                dict(
                    physical_id=p["id"],
                    requirement=check,
                    state="not-run",
                    acceptance_limits="owner-controlled; not inferred",
                )
            )
        processes.append(
            dict(
                physical_id=p["id"],
                process="supplier purchase or controlled cut/form/bond/drill/assembly",
                qualified_local_supplier=None,
                tool_access="unknown",
                replacement_path="unknown",
                tolerance_stack="unknown",
                stock_and_thickness_limits=p.get("manufacturing_limits"),
                fixture_required=True,
                process_released=False,
            )
        )
    joints = []
    for joint in model.get("assembly_joints", model.get("joints", [])):
        joints.append(
            dict(
                id=joint["id"],
                definition=joint,
                capacity_qualified=False,
                preload_verified=False,
            )
        )
    network = model.get("support_network")
    if network:
        # Map actual clip/bolt and rail identities. Missing curved inserts are
        # an unresolved allocation, not invented mass or free connection credit.
        for rail in network["rails"]:
            for index in range(2):
                joint_id = rail["id"] + f"-clip-{index}"
                endpoints = [rail["id"], joint_id, rail["id"] + f"-clip-bolt-{index}"]
                if not set(endpoints) <= set(ids):
                    raise ValueError(
                        "attachment crosswalk refers to absent physical hardware"
                    )
                joints.append(
                    dict(
                        id=joint_id + "/connection",
                        physical_part_ids=endpoints,
                        interface="defined rail/clip/bolt geometry; panel insert/contact lands and thread locking require reviewed detail",
                        preload_n=None,
                        locking=None,
                        capacity_qualified=False,
                        preload_verified=False,
                        tool_access="unknown",
                        secondary_retention="unknown",
                    )
                )
    missing = model.get(
        "unresolved_part_allocations", definition.get("coverage", {}).get("rows", [])
    )
    return dict(
        schema="osr-installed-variant-register/1",
        physical_definition_sha256=fingerprint(model),
        parts=bill,
        catalogue_quantities=dict(sorted(counts.items())),
        joints=joints,
        processes=processes,
        inspections=inspections,
        tooling=dict(
            mould_count=None,
            fixture_count=None,
            scope="explicit tooling needed; missing counts never become zero",
        ),
        unresolved_allocations=missing,
        complete_installed_kit=False,
        production_released=False,
        physical_release=False,
    )


def reconcile(register, definition):
    model = definition.get("contract") or definition.get("model")
    if not model:
        return register
    if register["physical_definition_sha256"] != fingerprint(model):
        raise ValueError("stale geometry/joint/BOM/inspection crosswalk")
    physical = model.get("parts", model.get("instances", []))
    if {p["id"] for p in physical} != {p["physical_id"] for p in register["parts"]}:
        raise ValueError("part inventory correspondence differs")
    if any(p["quantity"] != 1 for p in register["parts"]):
        raise ValueError("physical instances must not be double counted")
    return register
