"""Native gross-section stage demand; site and resistance remain independent."""

from __future__ import annotations
import math
from pathlib import Path
import shutil
import subprocess
import json

from osr_mech.section_contract import calculix_box
from .contracts import canonical, fingerprint


def beam(contract, trace, folder, *, elements=40, stage="service"):
    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=False)
    deck = next(p for p in contract["parts"] if p["id"] == "deck")
    sec = deck["analysis"]["section"]
    length = max(p["dimensions_m"][2] for p in deck["manufacturing"]["primitives"])
    young = contract["materials"]["concrete"]["young_pa"]
    density = contract["materials"]["concrete"]["density_kg_m3"]
    mass = sum(
        p["properties"]["mass_kg"]
        for p in contract["parts"]
        if p["id"] == "deck" or p["id"].startswith(("deck-rebar-", "tendon-"))
    )
    count = elements
    nodes = {i + 1: length * i / (2 * count) for i in range(2 * count + 1)}
    forces = {tag: 0.0 for tag in nodes}
    for i in range(count):
        # Consistent quadratic B32R line-load integrals: 1/6, 2/3, 1/6.
        for tag, weight in zip(
            (2 * i + 1, 2 * i + 2, 2 * i + 3), (1 / 6, 2 / 3, 1 / 6)
        ):
            forces[tag] -= mass * 9.81 / count * weight
    if stage == "service":
        from engineering.design_consistency.analysis import civil_stages

        origin = civil_stages(contract, trace)["service"]["governing_train_origin_m"]
        for axle in trace["reference"]["axle_pattern"]:
            x = origin + axle["x_m"]
            if 0 <= x <= length:
                position = x / length * 2 * count
                left = max(1, min(2 * count, int(math.floor(position)) + 1))
                fraction = position - (left - 1)
                load = 2 * axle["static_load_kn"] * 1000
                forces[left] = forces.get(left, 0) - load * (1 - fraction)
                forces[left + 1] = forces.get(left + 1, 0) - load * fraction
        supports = [1, 2 * count + 1]
    elif stage == "lifting":
        forces = {tag: force * 1.3 for tag, force in forces.items()}
        supports = [round(0.2 * 2 * count) + 1, round(0.8 * 2 * count) + 1]
    elif stage == "bearing-replacement":
        supports = [1, 2 * count + 1]
    else:
        raise ValueError("explicit service/lifting/bearing-replacement stage required")
    rows = ["*HEADING", "OSR gross hollow deck stage demand only, SI", "*NODE"]
    rows += [f"{tag},{x},0,0" for tag, x in nodes.items()]
    rows += ["*ELEMENT,TYPE=B32R,ELSET=DECK"] + [
        f"{i+1},{2*i+1},{2*i+2},{2*i+3}" for i in range(count)
    ]
    rows += [
        "*MATERIAL,NAME=CONCRETE",
        "*ELASTIC",
        f"{young},0.2",
        "*BEAM SECTION,ELSET=DECK,MATERIAL=CONCRETE,SECTION=BOX",
        calculix_box(sec, units="m"),
        "0,1,0",
        "*NSET,NSET=ALL",
        *[
            ",".join(map(str, list(nodes)[i : i + 12]))
            for i in range(0, len(nodes), 12)
        ],
        "*NSET,NSET=SUPPORT",
        ",".join(map(str, supports)),
        "*BOUNDARY",
        f"{supports[0]},1,3",
        f"{supports[1]},2,3",
        "*STEP",
        "*STATIC",
        "*CLOAD",
    ]
    rows += [f"{tag},3,{force}" for tag, force in forces.items()]
    rows += ["*NODE PRINT,NSET=ALL", "U", "*NODE PRINT,NSET=SUPPORT", "RF", "*END STEP"]
    (folder / "stage.inp").write_text("\n".join(rows) + "\n")
    binary = shutil.which("ccx")
    if not binary:
        raise RuntimeError("native CalculiX required for structural stage confirmation")
    proc = subprocess.run(
        [binary, "-i", "stage"],
        cwd=folder,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        timeout=120,
    )
    (folder / "stage.log").write_text(proc.stdout)
    if proc.returncode or "*ERROR" in proc.stdout.upper():
        raise RuntimeError(
            "native structural-stage solve failed; raw evidence retained"
        )
    mode = None
    displacements = []
    reactions = {}
    for line in (folder / "stage.dat").read_text().splitlines():
        if "displacements" in line.lower():
            mode = "U"
        if "forces" in line.lower():
            mode = "RF"
        values = line.split()
        if len(values) == 4 and values[0].isdigit():
            if mode == "U":
                displacements.append(abs(float(values[3])))
            if mode == "RF":
                reactions[int(values[0])] = float(values[3])
    if not displacements or not reactions:
        raise ValueError("native stage displacement/reaction evidence absent")
    # CCX RF is external nodal force = reaction plus the applied nodal load,
    # per the manual's *NODE PRINT definition. Recover the support reaction.
    if set(reactions) != set(supports):
        raise ValueError("native stage must report each actual support reaction")
    support_reactions = {tag: reactions[tag] - forces[tag] for tag in supports}
    reaction_total = sum(support_reactions.values())
    balance = abs(reaction_total + sum(forces.values())) / max(
        1, abs(sum(forces.values()))
    )
    if balance > 1e-5:
        raise ValueError("native stage reactions do not balance loads")
    result = dict(
        schema="osr-native-civil-stage-demand/1",
        contract_sha256=fingerprint(contract),
        stage=stage,
        elements=elements,
        maximum_deflection_m=max(displacements),
        reaction_balance_relative_error=balance,
        applied_force_n=sum(forces.values()),
        support_reaction_n=reaction_total,
        support_demands=[
            dict(node=tag, position_m=nodes[tag], reaction_n=support_reactions[tag])
            for tag in supports
        ],
        local_support_demands=support_contact_demands(contract, stage, support_reactions),
        resistance_checks=dict(
            cracking="unknown",
            reinforcement_bond="unknown",
            prestress_loss_history="unknown",
            anchorage="unknown",
            soil_settlement_cyclic="unknown",
            lifting_insert="unknown",
            bearing_jack_local="unknown",
        ),
        gross_section_only=True,
        physical_release=False,
        source_mass_basis="same defined deck/bar/tendon quantities; no complete installed inventory",
    )
    (folder / "result.json").write_bytes(canonical(result) + b"\n")
    return result


def support_contact_demands(contract, stage, support_reactions):
    """Map native support force to defined contacts, retaining local unknowns.

    The gross beam has one vertical support per end; equal sharing between the
    two bearings is an explicit sensitivity assumption, not a bearing solution.
    Replacement jacks and lifting inserts have no defined footprints and cannot
    borrow the operating bearing's area or resistance.
    """
    if stage not in {"service", "lifting", "bearing-replacement"}:
        raise ValueError("explicit supported construction stage required")
    if len(support_reactions) != 2:
        raise ValueError("two actual gross beam supports required")
    rows = []
    for end, (tag, reaction) in enumerate(sorted(support_reactions.items())):
        if not math.isfinite(reaction):
            raise ValueError("finite support force required")
        if stage != "service":
            rows.append(dict(support_node=tag, reaction_n=reaction, physical_part_ids=[],
                             contact_area_m2=None, average_contact_pressure_pa=None,
                             force_share_basis="jack/insert geometry and sharing are not defined",
                             local_resistance="unknown", stage=stage))
            continue
        contacts = [p for p in contract["parts"] if p["id"].startswith(f"bearing-core-{end}-")]
        if not contacts:
            raise ValueError("service support lacks its physical bearing contacts")
        for contact in contacts:
            primitives = contact["manufacturing"]["primitives"]
            if len(primitives) != 1 or primitives[0]["kind"] != "box":
                raise ValueError("defined rectangular bearing contact required")
            footprint = primitives[0]["dimensions_m"][0] * primitives[0]["dimensions_m"][1]
            if footprint <= 0:
                raise ValueError("positive bearing footprint required")
            rows.append(dict(support_node=tag, reaction_n=reaction / len(contacts),
                             physical_part_ids=[contact["id"]], contact_area_m2=footprint,
                             average_contact_pressure_pa=reaction / len(contacts) / footprint,
                             force_share_basis="equal bearing sharing assumed; rotations/eccentricity/stiffness excluded",
                             local_resistance="unknown", stage=stage))
    return rows
