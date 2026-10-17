"""Explicit finite test designs. These are seeds, not an LLM provider."""
def seeds(baseline):
    values = [
        ("cleat-baseline", "mechanical-cleat", dict(thickness_m=.012, topology="solid-web"), "Reference geometry before lightening"),
        ("cleat-lightened", "mechanical-cleat", dict(thickness_m=.016, topology="lightened-web"), "Compare added thickness and a lightening hole under unchanged load"),
        ("beam-rhs", "civil-steel-beam", dict(wall_m=.006, topology="rhs"), "Reference closed section"),
        ("beam-open-section", "civil-steel-beam", dict(wall_m=.006, topology="i-section"), "Compare section topology with unchanged envelope and load"),
        ("vehicle-interface", "vehicle-interface", {}, "Native part and fastener correspondence for a 14-part research interface"),
        ("civil-20m", "civil-bay", dict(length=20., pier_height=8., pile_length=15., pile_spacing=2.), "Native and IFC comparison of one research viaduct bay"),
        ("weak-control", "software-precharge", dict(policy="ratio-only"), "Deliberate negative control; unsafe policies must fail the fixed fault suite"),
        ("guarded-control", "software-precharge", dict(policy="guarded"), "Compare guarded policy against the same 19 fault cases"),
    ]
    from engineering.design_consistency import demonstrators as d
    from engineering.design_consistency.contracts import member
    contract = d.interface()
    # A model authored by changing a leaf recipe and rebuilding all correspondence
    # properties, not by editing an arbitrary FreeCAD macro or test definition.
    for i, part in enumerate(contract["parts"]):
        if part["id"].startswith("battery-carrier-"):
            y = -.22 if part["id"].endswith("0") else .22
            contract["parts"][i] = member(part["id"], 1.2, .08, .05, .004, "steel",
                contract["materials"], (0, y, -.19))
    contract["revision"] = "AI-CARRIER-RESEARCH-2"
    values.append(("carrier-revised-assembly", "controlled-assembly", dict(contract=contract),
                   "Increase carrier RHS wall 3 to 4 mm; regenerate exact part mass/inertia and inspect assembly collisions. Contact/strength qualification remains open."))
    return [dict(schema="osr-twin-proposal/1", id=name, baseline_sha256=baseline,
                 kind=kind, parameters=params, rationale=reason, sources=[],
                 expected_tests=["controller-owned geometry or fault checks", "preserve open evidence gates"])
            for name, kind, params, reason in values]
