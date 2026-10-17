"""Primary-source equipment compatibility screens for provisional architecture.

Catalogue arithmetic is separated from accepted ratings and physical collision
proof. Prepared supplier questions remain unsent; no equipment is qualified.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import itertools
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RETRIEVED_ON = "2026-10-17"
BASIS = ROOT / "engineering/factory_examples/data/basis.json"
CONNECTIONS = ROOT / "engineering/factory_examples/data/connections.json"
TIERS = ROOT / "docs/design-engine/queued-systems/civil/report.json"
MECHANICAL = ROOT / "docs/design-engine/queued-systems/mechanical/report.json"
MECHANICAL_BASIS = ROOT / "engineering/generative_design/data/mechanical-systems.json"
EQUIPMENT = ROOT / "engineering/factory_examples/data/equipment.json"

CCL = dict(
    id="ccl-stressomatic-mkii-250kn",
    supplier="CCL Stressing Systems",
    model="Stressomatic MKII 250 kN, short/long variants",
    sources=[
        dict(
            url="https://www.cclint.com/wp-content/uploads/2024/02/CCL-Stressomatic-MKII-250-kN_Flyer.pdf",
            locator="PDF p2, product specifications and UK manufacture statement",
            retrieved_on=RETRIEVED_ON,
        ),
        dict(
            url="https://www.cclint.com/downloads/",
            locator="Current manufacturer downloads links this 250 kN flyer; publication/download path is not an offered specification date",
            retrieved_on=RETRIEVED_ON,
        ),
        dict(
            url="https://www.cclint.com/contact-us/locations/united-kingdom/",
            locator="UK operation and in-house manufacturing; exact offered unit and matched system remain unconfirmed",
            retrieved_on=RETRIEVED_ON,
        ),
    ],
    origin_state="manufacturer-stated-UK-design-and-manufacture",
    exact_offered_origin_accepted=False,
    published=dict(
        maximum_design_load_n=247000,
        strand_diameter_range_m=[0.0096, 0.015],
        short_extension_m=0.194,
        long_extension_m=0.494,
        fully_retracted_short_length_m=0.833,
        fully_retracted_long_length_m=1.433,
        short_mass_kg=28,
        long_mass_kg=45,
        minimum_strand_length_m=0.265,
        maximum_width_m=0.160,
        overall_height_m=0.234,
        main_cylinder_diameter_m=0.110,
        bottom_to_axis_m=0.070,
    ),
    accepted_design_load_n=None,
    offered_configuration=None,
    supplier_contacted=False,
    physical_release=False,
)

MECHAN = dict(
    id="mechan-30t-historical-rail-lifting-jack-lead",
    supplier="Mechan",
    model="Configured railway lifting jack; historical 30 tonne supply, no current orderable model identified",
    sources=[
        dict(
            url="https://www.mechan.co.uk/rail/lifting-jacks/",
            locator="Manufacturer lifting-jack range and configuration; not an offered 30/35t model GA",
            retrieved_on=RETRIEVED_ON,
        ),
        dict(
            url="https://www.mechan.co.uk/kiwirail-bears-fruit-for-mechan/",
            locator="Manufacturer historical project: four 30 tonne jacks supplied to KiwiRail; historical example is not a current stock offer",
            retrieved_on=RETRIEVED_ON,
        ),
        dict(
            url="https://www.mechan.co.uk/about-mechan/",
            locator="Manufacturing facility in Sheffield, England; also supplies European partner products, so source offered origin case by case",
            retrieved_on=RETRIEVED_ON,
        ),
        dict(
            url="https://www.mechan.co.uk/wp-content/uploads/2023/06/All-Mechan-Products-and-services-.pdf",
            locator="Lifting-jack section:5–40t/jack, typical anvil400–2500mm, supply380–415V3phase50Hz; actual offered configuration open",
            retrieved_on=RETRIEVED_ON,
        ),
    ],
    origin_state="manufacturer-stated-Sheffield-manufacturing-facility",
    exact_offered_origin_accepted=False,
    published=dict(
        historical_capacity_per_jack_kg=30000,
        family_capacity_range_kg=[5000, 40000],
        typical_minimum_anvil_height_m=0.4,
        typical_maximum_anvil_height_m=2.5,
        nominal_voltage_range_v=[380, 415],
        nominal_phases=3,
        nominal_frequency_hz=50,
    ),
    accepted_capacity_per_jack_kg=None,
    offered_configuration=None,
    supplier_contacted=False,
    physical_release=False,
)


def _read(path):
    return json.loads(Path(path).read_text())


def _positive(value, name):
    if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
        raise ValueError("positive finite " + name + " required")
    return value


def _criterion(name, passed, basis):
    return dict(
        id=name,
        status="passed-arithmetic-only" if passed else "failed-declared-screen",
        basis=basis,
    )


def ccl_case():
    case = deepcopy(CCL)
    a, connections = _read(BASIS)["assumptions"], _read(CONNECTIONS)
    reference = _read(TIERS)
    if reference.get("physical_release") is not False:
        raise ValueError("retained tooling research must remain unreleased")
    package = next(
        p for p in reference["packages"] if p["work_package_id"] == "FACTORY-PRECAST"
    )
    study = next(
        i for i in package["investigations"] if i["id"] == "jack-grip-access-repair"
    )
    proposal = next(
        r for r in study["candidates"] if r["id"] == "straight-tails-four-axial-tiers"
    )
    v, p = proposal["variables"], case["published"]
    strand = connections["strongback"]["strand_clearance_envelope_diameter_m"]
    F = a["strand_area_m2"] * a["strand_initial_stress_pa"]
    pitch = v["tendon_pitch_m"]
    gap = pitch - p["main_cylinder_diameter_m"] / 2 - strand / 2
    metrics = dict(
        reference_proposal_id=proposal["id"],
        reference_tool_diameter_m=v["assumed_jack_diameter_m"],
        reference_tool_length_m=v["assumed_jack_axial_length_m"],
        reference_axial_tier_pitch_m=v["axial_tier_pitch_m"],
        strand_envelope_diameter_m=strand,
        declared_initial_force_each_n=F,
        force_to_published_maximum_ratio=F / p["maximum_design_load_n"],
        same_plane_cylinder_to_adjacent_straight_strand_gap_m=gap,
        short_retracted_axial_reservation_gap_m=v["axial_tier_pitch_m"]
        - p["fully_retracted_short_length_m"],
        long_retracted_axial_reservation_gap_m=v["axial_tier_pitch_m"]
        - p["fully_retracted_long_length_m"],
        same_plane_adjacent_maximum_width_reservation_gap_m=pitch
        - p["maximum_width_m"],
        same_plane_adjacent_height_reservation_gap_m=pitch - p["overall_height_m"],
        same_tier_axis_pitch_m=proposal["metrics"]["same_tier_minimum_axis_spacing_m"],
        same_tier_width_reservation_gap_m=proposal["metrics"][
            "same_tier_minimum_axis_spacing_m"
        ]
        - p["maximum_width_m"],
        same_tier_height_reservation_gap_m=proposal["metrics"][
            "same_tier_minimum_axis_spacing_m"
        ]
        - p["overall_height_m"],
        reference_free_tail_m=v["tail_free_length_m"],
        elastic_strand_extension_reference_m=proposal["metrics"][
            "beam25_elastic_extension_m"
        ]
        + proposal["metrics"]["extra_tail_elastic_extension_m"],
        actual_tool_shape_collision_established=False,
        actual_nose_and_cylinder_axial_position_m=None,
        actual_hose_and_operator_clearance_m=None,
    )
    minimum, maximum = p["strand_diameter_range_m"]
    extension = metrics["elastic_strand_extension_reference_m"]
    case["reference_metrics"] = metrics
    case["criteria"] = [
        _criterion(
            "published_numerical_strand_range",
            minimum <= strand <= maximum,
            "15.2mm retained strand clearance envelope exceeds numeric published15.0mm maximum. Manufacturer may use a nominal size designation, but no15.2/15.7mm compatibility is inferred; exact strand/wedge/nose qualification unknown.",
        ),
        _criterion(
            "force_scalar",
            F <= p["maximum_design_load_n"],
            "154kN demand versus247kN published maximum is arithmetic only, not accepted operating pressure, calibration, strand/grip/system or tooling resistance.",
        ),
        _criterion(
            "same_plane_body_to_straight_tail_clearance",
            gap >= 0,
            "Assume main cylinder axis shares an axial plane with neighboring straight15.2mm tails at60mm spacing. Negative gap rejects this envelope hypothesis; actual nose/body axial locations and sequence are absent, so this is not a demonstrated physical shape collision.",
        ),
        _criterion(
            "short_body_within_250mm_axial_tier_reservation",
            metrics["short_retracted_axial_reservation_gap_m"] >= 0,
            "833mm fully retracted short jack exceeds250mm axial tier reservation. Overlapping aligned bounding reservations are not an actual simultaneous shape collision or a proof every possible sequential procedure fails.",
        ),
        _criterion(
            "same_tier_bounding_width_reservation",
            metrics["same_tier_width_reservation_gap_m"] >= 0,
            "160mm maximum width at120mm same-tier axis spacing: conservative bounding reservations overlap; exact handle/nose/hose surfaces and orientations are unknown.",
        ),
        _criterion(
            "same_tier_bounding_height_reservation",
            metrics["same_tier_height_reservation_gap_m"] >= 0,
            "234mm overall height at120mm same-tier vertical spacing: bounding reservations overlap; actual geometry and staggering remain unqualified.",
        ),
        _criterion(
            "short_stroke_reference_elastic_extension",
            extension <= p["short_extension_m"],
            "194mm short extension exceeds retained25m-beam+1.25m-tail elastic estimate only. Seating, full bed free length, regrips, tolerances and hydraulic working stroke must be reviewed.",
        ),
        _criterion(
            "minimum_strand_length_scalar",
            v["tail_free_length_m"] >= p["minimum_strand_length_m"],
            "The retained1.25m free-tail assumption exceeds265mm published minimum. It is not a complete axial clearance, seating or cut/restress sequence design.",
        ),
    ]
    case["hypothetical_90x200_tool_qualified_by_this_model"] = False
    case["existing_four_tier_configuration_qualified"] = False
    case["mandatory_unknown_gates"] = [
        "Exact strand metallic size/grade, barrel/wedge/nose match and manufacturer confirmation outside numeric published range",
        "Exact GA locating cylinder, nose, handles, hoses, connector/rotation and operator swept envelopes relative to every live tail and grip",
        "Written stressing, lock-off, regrip, tail cutting and detensioning procedure; no neighboring tail may be removed or force rerouted by an unqualified geometry assumption",
        "Matched jack/pump pressure-force calibration, stroke/end-stop/seating losses and full free-strand length",
        "154kN seat/standoff local and global load path, increased whole-bed force, stiffness, staged/eccentric resistance and ground/foundation acceptance",
        "Independent safe method, inspection intervals, guarding/exclusion zone, Baghdad ambient/service, exact offered origin and witnessed first article",
    ]
    return case


def mechan_case(*, loaded_car_mass_kg=None):
    case = deepcopy(MECHAN)
    reference = _read(MECHANICAL)
    basis = _read(MECHANICAL_BASIS)
    if loaded_car_mass_kg is None:
        package = next(
            p for p in reference["packages"] if p["work_package_id"] == "LM3-FRP-010"
        )
        study = next(
            i for i in package["investigations"] if i["id"] == "chassis_shared"
        )
        proposed = set(study["proposed_candidate_ids"])
        candidate = next(r for r in study["candidates"] if r["id"] in proposed)
        mass = candidate["metrics"]["conservative_loaded_car_mass_kg"]
        source = dict(
            mode="historical-provisional-chassis-loaded-mass",
            candidate_id=candidate["id"],
            description="LM3 AW2 reference plus all proposed member mass, deliberately not subtracting original member mass. This is not actual empty workshop tare or a six-car mass.",
        )
    else:
        mass = _positive(
            loaded_car_mass_kg, "caller supplied unaccepted loaded car mass"
        )
        source = dict(
            mode="caller-supplied-provisional-loaded-mass",
            candidate_id=None,
            description="Caller must bind source candidate/configuration and mass convention. This is no accepted tare, CG or whole-car lifting load.",
        )
    _positive(mass, "provisional loaded car mass")
    capacity = case["published"]["historical_capacity_per_jack_kg"]
    v = basis["variable_spaces"]["lifting"]
    rows = []
    for supports, dynamic, imbalance in itertools.product(
        v["effective_jacks"], v["dynamic_multiplier"], v["load_imbalance_multiplier"]
    ):
        demand = mass * dynamic * imbalance / supports
        rows.append(
            dict(
                effective_jacks=supports,
                dynamic_hypothesis=dynamic,
                imbalance_hypothesis=imbalance,
                demand_mass_equivalent_kg_each=demand,
                historical_case_capacity_kg_each=capacity,
                historical_capacity_arithmetic=(
                    "passed-arithmetic-only"
                    if demand <= capacity
                    else "failed-declared-screen"
                ),
                accepted_capacity_kg_each=None,
                reaction_distribution_accepted=False,
            )
        )
    vehicle_crane = next(
        e for e in _read(EQUIPMENT)["equipment"] if e["id"] == "street-zx8"
    )
    crane = vehicle_crane["published"]["capacity_kg"]
    case["mass_basis"] = source
    case["loaded_car_mass_kg_hypothesis"] = mass
    case["jack_sensitivities"] = rows
    case["existing_vehicle_crane_comparison"] = dict(
        id="street-zx8",
        published_nominal_capacity_kg=crane,
        whole_loaded_car_mass_hypothesis_kg=mass,
        status=(
            "failed-whole-loaded-car-scalar" if mass > crane else "passed-scalar-only"
        ),
        actual_empty_car_mass_kg=None,
        complete_rigging_mass_kg=None,
        accepted_whole_car_lift=False,
        boundary="The10t model is a retained component-handling candidate; no whole-car lifting role or tandem capacity is inferred. Loaded car is a conservative research load, not accepted factory tare.",
    )
    case["mandatory_unknown_gates"] = [
        "Exact current offered jack configuration, individual rating at anvil extension/height/duty and UK manufacturing origin; historical30t supply is no offer",
        "Configuration-specific actual lifted mass/tare, component removal state and3D CG, four/three-point load redistribution and anti-tip stability",
        "Lift pad/underframe strength and interface, minimum anvil height versus actual750mm-sill/floor/bogie geometry and removal sweeps",
        "Synchronized lift, mechanical locks, emergency/power-loss behavior, unequal load/height control, allowable lateral forces and platform/foundation reactions",
        "Iraqi site electrical supply, guarding/access/foundation, inspection/maintenance, proof/witness and Baghdad spares/service acceptance",
    ]
    return case


def macalloy_case():
    """Public bar-family lead, with no assumed thread/coupler design capacity."""
    return dict(
        id="macalloy-1030-post-tensioning-carbon-bar-lead",
        supplier="Macalloy",
        model="1030 carbon-steel post-tensioning bar and coupler family",
        sources=[
            dict(
                url="https://macalloy.com/products-services/post-tensioning/",
                locator="Public product page:1030N/mm2 minimum ultimate strength;26.5–75mm carbon bar and up-to11.8m pieces; couplers permit longer assemblies",
                retrieved_on=RETRIEVED_ON,
            ),
            dict(
                url="https://macalloy.com/about/history/",
                locator="Manufacturer describes current purpose-built Dinnington, Sheffield facility; exact offered bar/mill/accessory origin remains unverified",
                retrieved_on=RETRIEVED_ON,
            ),
            dict(
                url="https://macalloy.com/downloads/brochures/",
                locator="Brochure access requires login; no login-only technical data accessed or adopted",
                retrieved_on=RETRIEVED_ON,
            ),
        ],
        origin_state="manufacturer-stated-UK-factory-offered-origin-unconfirmed",
        exact_offered_origin_accepted=False,
        published=dict(
            family_minimum_ultimate_strength_pa=1030e6,
            carbon_bar_diameter_range_m=[0.0265, 0.075],
            maximum_public_piece_length_m=11.8,
            longer_assemblies_by_couplers=True,
        ),
        route_sensitivity=dict(
            reference_return_path_length_m=26,
            optimistic_minimum_piece_count=math.ceil(26 / 11.8),
            optimistic_minimum_inline_coupler_count=math.ceil(26 / 11.8) - 1,
            boundary="Piece-count lower bound only. Actual diameter-specific lengths, engagement, coupler/anchor length and end clearance alter the layout. A bar-return concept is a new force path, not a drop-in qualified replacement for the existing return rails.",
        ),
        accepted_design_tension_n=None,
        accepted_thread_or_coupler_resistance_n=None,
        selected_bar_count=None,
        mandatory_unknown_gates=[
            "1030MPa ultimate strength is not design stress, proof stress, allowable stress or fatigue resistance; no capacity/count inferred from gross area times ultimate strength",
            "Exact diameter/grade, thread stress area, certified material, coupler/end-anchor geometry, engagement, proof/fatigue and load transfer",
            "Full initial force plus eccentricity, all stressing/release stages, stiffness/elongation, thermal movement and balanced return path to the ground",
            "Layout/coupler/anchor clashes and maintainable access, complete strongback/bed/foundation redesign and independent check",
            "Exact UK manufacturing and raw-mill/component origin, Baghdad supply/support, commissioned trials and accepted offered configuration",
        ],
        supplier_contacted=False,
        offered_configuration=None,
        physical_release=False,
    )


def run(*, loaded_car_mass_kg=None):
    """Return source-evidenced leads and rejected reservations, never an offer."""
    sources = [
        Path(__file__),
        BASIS,
        CONNECTIONS,
        TIERS,
        MECHANICAL,
        MECHANICAL_BASIS,
        EQUIPMENT,
    ]
    return dict(
        schema="osr-provisional-architecture-equipment/1",
        retrieved_on=RETRIEVED_ON,
        supplier_cases=[
            ccl_case(),
            macalloy_case(),
            mechan_case(loaded_car_mass_kg=loaded_car_mass_kg),
        ],
        source_sha256={
            p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sources
        },
        procurement_authorized=False,
        supplier_contacted=False,
        accepted_equipment_configurations=0,
        engineering_design_complete=False,
        manufacturing_release=False,
        physical_release=False,
    )
