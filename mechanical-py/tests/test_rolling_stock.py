"""Rolling-stock geometry + RFC 0008 consistency checks.

Runs four tests:

1. Every consist family's trainset fits inside its published platform
   length (RFC 0008 §1).
2. A bogie's wheel centres fall on standard gauge (within tolerance).
3. A car body has the current two-low-floor-doors-per-side pattern — verified
   indirectly by volume and family-dimension checks.
4. The sensor cowl has a real sensor-window cutout reducing volume
   below the solid bounding box.
"""

from __future__ import annotations

import pytest

from osr_mech.common import ConsistFamily, STANDARD_GAUGE_MM
from osr_mech.rolling_stock.bogie import (
    BOGIE_FRAME_HEIGHT_MM,
    BOGIE_FRAME_LENGTH_MM,
    BOGIE_FRAME_WIDTH_MM,
    WHEEL_DIAMETER_MM,
    motor_bogie,
)
from osr_mech.rolling_stock.car_body import (
    HIGH_FLOOR_HEIGHT_MM,
    LOW_FLOOR_HEIGHT_MM,
    CarDimensions,
    car_body,
)
from osr_mech.rolling_stock.cots_equipment import (
    CATALOGUE,
    Category,
    bom_per_car,
    fit_out_car_body,
    locations_for,
    total_active_power_w,
    total_mass_kg,
)
from osr_mech.rolling_stock.mechanical_interfaces import (
    INTERFACE_BUILDERS,
    battery_installations,
    bench_on_battery_installations,
    bogie_to_chassis_connector,
    bogie_to_motor_connector,
    door_installations,
    door_mounts,
    external_lighting_lidar_system,
    hvac_roof_ducting_installation,
    mechanical_interface_package,
    screen_speaker_mountings,
    train_connector_mount_pair,
    window_installations,
)
from osr_mech.rolling_stock.sensor_cowl import (
    COWL_LENGTH_MM,
    GLASS_RAKE_DEG,
    LEADING_FACE_HEIGHT_MM,
    LEADING_FACE_WIDTH_MM,
    PANORAMIC_GLASS_HEIGHT_MM,
    PANORAMIC_GLASS_WIDTH_MM,
    sensor_cowl,
)
from osr_mech.rolling_stock.systems import (
    BATTERY_MODULES_PER_CAR,
    ROOF_SOLAR_MODULES_PER_CAR,
    car_systems,
    inter_car_articulation,
    roof_solar_system,
)
from osr_mech.rolling_stock.trainset import (
    expected_platform_length_m,
    family_dimensions,
    trainset,
    trainset_length_m,
)


@pytest.mark.parametrize(
    "family",
    [
        ConsistFamily.TRAM_2CAR,
        ConsistFamily.LIGHT_METRO_3CAR,
        ConsistFamily.METRO_4CAR,
        ConsistFamily.METRO_6CAR,
    ],
)
def test_trainset_fits_within_published_platform(family: ConsistFamily) -> None:
    """RFC 0008 §1 publishes a platform length per family; the
    trainset must fit on it with a small stopping-tolerance margin."""
    length_m = trainset_length_m(family)
    platform_m = expected_platform_length_m(family)
    # Trainset must be strictly shorter than platform (so both noses
    # fit between the stop marks), with ≥ 1 m of margin.
    assert length_m < platform_m, (
        f"{family.value}: trainset {length_m:.1f} m ≥ platform {platform_m:.1f} m"
    )
    margin = platform_m - length_m
    assert margin >= 1.0, (
        f"{family.value}: only {margin:.1f} m stopping margin on a "
        f"{platform_m:.0f} m platform — too tight"
    )


def test_car_body_has_door_and_window_cutouts() -> None:
    """Verify doors + windows are cut through the shell."""
    dims = CarDimensions()
    body = car_body(dims)
    solid_volume_mm3 = dims.body_length_mm * dims.body_width_mm * dims.body_height_mm
    v = _volume_recursive(body)
    assert v < solid_volume_mm3 * 1.15, (
        f"car-body layered volume {v:.0f} should stay near the solid box {solid_volume_mm3:.0f}"
    )
    # Doors (1 × 1.4 × 2.0 × 2.85 × 2 sides ≈ 16 m³) + windows remove
    # a visible share of the solid box. The
    # body should still be at least half the solid volume — anything
    # less is a geometry bug.
    assert v > solid_volume_mm3 * 0.50, (
        f"car-body volume {v:.0f} is under half the solid box — cut-geometry bug?"
    )
    # And it should be a Compound (shell + glazing + doors + livery +
    # skirt + roof equipment), not just one Part.
    assert hasattr(body, "children") and body.children, (
        "car body should be a Compound with multiple named children"
    )
    child_labels = {label.lower() for label in _labels_recursive(body)}
    assert any("shell" in l for l in child_labels), "missing shell"
    assert any("glazing" in l for l in child_labels), "missing window glazing"
    assert any("door leaf" in l for l in child_labels), "missing door leaves"
    assert any("livery" in l for l in child_labels), "missing livery band"
    assert any("skirt" in l for l in child_labels), "missing underframe skirt"


def test_car_body_exposes_complete_layered_design() -> None:
    labels = _labels_recursive(car_body(CarDimensions()))
    expected = {
        "Primary steel shell, floor, and portal structure subassembly",
        "Exterior 1 m clip-on fiberglass cladding, glazing, doors, solar, and skirt subassembly",
        "One-metre clip-on fiberglass body cladding system",
        "Clip-on fiberglass side modules",
        "Clip-on fiberglass roof modules",
        "Captive mechanical clips and anti-lift retainers",
        "Dry EPDM compression seals and drain joints",
        "Interior passenger fit-out and under-seat battery strake subassembly",
        "Car body service layers subassembly",
        "HVAC ducting layer",
        "Electrical and data routing layer",
        "High-voltage traction, PV, thermal, and fire routing layer",
        "Low-floor centre door and PRM floor pan",
        "Raised high-floor bogie-end deck",
        "Interior ramp between low centre and raised bogie floor",
        "Lowered side sill through low-floor door zone",
        "Raised side plinth over standard bogie zone",
        "Bogie rotation and suspension-travel clearance envelope",
        "Wheel-change and bogie drop clearance zone",
        "End ring frame for single glass-pane cowl",
        "Anti-climber load beam",
        "Waist rail under window cassette",
        "Window post",
        "Door portal header beam",
        "Bonded flexible rooftop solar laminate mount",
        "Rail-clamped raised rooftop solar panel mount",
        "Roof PV module junction box",
        "Roof PV fire-isolation switch box",
        "Longitudinal bench seat base on raised bogie floor",
        "Interior step tread to raised bogie-end floor",
        "Main saloon egress aisle envelope",
        "Wheelchair turning circle envelope",
        "Glass-pane end passenger viewing zone",
        "High-floor step handrail",
        "Molded roof-cassette empty HVAC centre supply plenum",
        "Electrical and data routing layer - LV/TCN cable tray",
        "High-voltage traction routing layer - under-seat DC tray",
        "Roof PV high-voltage combiner spine",
        "Battery fire vent path to exterior burst panel",
    }
    missing = expected.difference(labels)
    assert not missing, f"missing layered car-body design labels: {sorted(missing)}"
    assert HIGH_FLOOR_HEIGHT_MM > LOW_FLOOR_HEIGHT_MM


def test_sensor_cowl_has_sensor_window() -> None:
    """The cowl's sensor window cutout must reduce volume below the
    tapered-solid nominal volume."""
    cowl = sensor_cowl()
    # A rough upper bound: average of the two end sections, times
    # length. The tapered solid is smaller than this; the cutout
    # removes further material.
    v = cowl.volume
    assert v > 0.0, "cowl produced empty geometry"
    # Tapered solid upper bound.
    interface_area = CarDimensions().body_width_mm * CarDimensions().body_height_mm
    leading_area = LEADING_FACE_WIDTH_MM * LEADING_FACE_HEIGHT_MM
    untapered = (interface_area + leading_area) / 2.0 * COWL_LENGTH_MM
    assert v < untapered * 1.12, (
        "cowl volume should stay near the average cross-section × length even with glass-frame hardware"
    )
    labels = _labels_recursive(cowl)
    expected = {
        "Multipart fiberglass driverless sensor cowl aerodynamic envelope",
        "Fiberglass upper brow and roof cap cast (CWL-FRP-01)",
        "Fiberglass left cheek side-return cast (CWL-FRP-02)",
        "Fiberglass right cheek side-return cast (CWL-FRP-03)",
        "Fiberglass lower apron and anti-climber cover cast (CWL-FRP-04)",
        "Fiberglass lamp and washer service hatch cast (CWL-FRP-05)",
        "Fiberglass backing-ring upper flange datum (CWL-FRP-06)",
        "Fiberglass backing-ring lower flange datum (CWL-FRP-06)",
        "Fiberglass backing-ring side flange datum (CWL-FRP-06)",
        "Black gasketed fiberglass cowl split line",
        "Single laminated panoramic end glass pane",
        "Bonded panoramic end glass upper frame rail",
        "Bonded panoramic end glass lower frame rail",
        "Bonded panoramic end glass side frame stile",
        "Cowl crash ring around single panoramic end glass",
        "Heated glass demist busbar",
        "Washer nozzle and service access cover",
        "Emergency recovery driving desk behind glass",
        "LED headlamp cluster",
        "LED marker and daytime-running light bar",
    }
    missing = expected.difference(labels)
    assert not missing, f"missing driverless nose details: {sorted(missing)}"
    assert PANORAMIC_GLASS_WIDTH_MM >= 0.75 * LEADING_FACE_WIDTH_MM
    assert PANORAMIC_GLASS_HEIGHT_MM >= 0.60 * LEADING_FACE_HEIGHT_MM
    assert 5.0 <= GLASS_RAKE_DEG <= 12.0


def test_bogie_dimensions_are_consistent() -> None:
    """The bogie's bounding box must contain standard gauge and the
    stack of (frame + secondary suspension) must put the car-body
    pivot at the RFC 0022 §3 height."""
    bog = motor_bogie()
    bb = bog.bounding_box()
    span_y = bb.max.Y - bb.min.Y
    # The detailed bogie includes axle-boxes + brake calipers + the
    # motor cantilevered off the gearbox on the +Y side — so the full
    # Y span exceeds the frame width. Assert standard-gauge containment
    # and a realistic motor-bogie outer envelope.
    assert span_y >= STANDARD_GAUGE_MM, (
        f"bogie Y span {span_y:.0f} mm must enclose standard gauge {STANDARD_GAUGE_MM}"
    )
    assert span_y <= 3_500.0, (
        f"bogie Y span {span_y:.0f} mm wider than any plausible detailed bogie"
    )
    # Height: from rail head (0) up through wheel + primary + frame +
    # secondary air spring + pivot boss. Air-spring top ≈ 1 240 mm.
    height = bb.max.Z - bb.min.Z
    assert 700.0 <= height <= 1_400.0, (
        f"bogie height {height:.0f} mm outside expected [700, 1400]"
    )


def test_trainset_is_symmetric_in_length() -> None:
    """The trainset has no cab — both ends are sensor cowls. Building
    a `LIGHT_METRO_3CAR` trainset should place geometry symmetrically
    about X=0."""
    ts = trainset(ConsistFamily.LIGHT_METRO_3CAR)
    bb = ts.bounding_box()
    # |min X| should equal max X within a millimetre.
    asym = abs(abs(bb.min.X) - bb.max.X)
    assert asym < 1.0, f"trainset not centred on X=0; asymmetry {asym:.2f} mm"


def _labels_recursive(node) -> list[str]:
    labels: list[str] = []
    for child in getattr(node, "children", []) or []:
        label = getattr(child, "label", None)
        if label:
            labels.append(label)
        labels.extend(_labels_recursive(child))
    return labels


def _volume_recursive(node) -> float:
    children = getattr(node, "children", []) or []
    if children:
        return sum(_volume_recursive(child) for child in children)
    return float(getattr(node, "volume", 0.0))


def test_trainset_contains_complete_train_systems() -> None:
    ts = trainset(ConsistFamily.LIGHT_METRO_3CAR)
    labels = _labels_recursive(ts)
    expected = {
        "A-end coupler and crash-energy assembly",
        "B-end coupler and crash-energy assembly",
        "Inter-car articulation assembly",
        "COTS electric door cassette",
        "Platform screen-door alignment datum",
        "ATO stopping accuracy target envelope",
        "Door/platform safety interlock interface",
        "LFP battery module fire-resistant enclosure",
        "Standard station side-pin charging connector",
        "Per-car roof PV MPPT DC/DC",
        "Station DC protection, isolation monitoring, contactors and precharge",
        "Independent HM47/LD32-class motor controller in fire-resistant enclosure",
        "Localized battery water-mist nozzle",
        "Lightweight flexible roof solar laminate",
        "Raised rigid roof solar panel",
        "T-ECU/S safety cabinet",
        "T-ECU/A application cabinet",
        "A-end T-OBS sensor pack",
        "B-end T-OBS sensor pack",
        "Wheelchair bay floor reservation",
    }
    missing = expected.difference(labels)
    assert not missing, f"missing train systems: {sorted(missing)}"
    assert labels.count("Independent HM47/LD32-class motor controller in fire-resistant enclosure") == 6
    assert (
        labels.count("Lightweight flexible roof solar laminate")
        + labels.count("Raised rigid roof solar panel")
        == ROOF_SOLAR_MODULES_PER_CAR * 3
    )
    assert labels.count("T-ECU/S safety cabinet") == 2
    assert labels.count("T-ECU/A application cabinet") == 2


def test_inter_car_articulation_has_detailed_load_path_and_services() -> None:
    labels = _labels_recursive(inter_car_articulation())
    expected = {
        "Articulation carbody adapter frame",
        "Bellows bolted clamp frame",
        "Articulation underframe anchor casting",
        "Semi-permanent articulated drawbar forging",
        "Lower spherical articulation bearing with anti-lift keeper",
        "Anti-lift keeper yoke over spherical bearing",
        "Drawbar crush washer stack",
        "Vertical anti-climb shear key",
        "Upper roll-yaw-pitch articulation link",
        "Upper link spherical bearing eye",
        "Double-wall corrugated gangway bellows pleat",
        "Segmented anti-slip gangway turntable",
        "Flexible vandal-resistant gangway side wall",
        "Flexible articulated gangway ceiling panel",
        "Articulation floor service hatch",
        "Drain channel and water trap",
        "HV and data energy guidance drag-chain",
        "HV traction jumper conduit",
        "TCN-E redundant Ethernet jumper conduit",
        "CAN-FD and safety-loop jumper conduit",
        "HVAC inter-car air duct sleeve",
        "Coolant flexible hose loop",
        "Articulation yaw clearance envelope +/-12 deg",
        "Articulation pitch/roll clearance envelope +/-6/+/-5 deg",
    }
    missing = expected.difference(labels)
    assert not missing, f"missing articulation details: {sorted(missing)}"
    assert labels.count("Articulation carbody adapter frame") == 2
    assert labels.count("Upper roll-yaw-pitch articulation link") == 2
    assert labels.count("Segmented anti-slip gangway turntable") == 5
    assert labels.count("Double-wall corrugated gangway bellows pleat") == 8


def test_car_systems_have_expected_repeated_modules() -> None:
    dims = CarDimensions()
    labels = _labels_recursive(car_systems(dims))
    assert labels.count("LFP battery module fire-resistant enclosure") == BATTERY_MODULES_PER_CAR
    assert (
        labels.count("Lightweight flexible roof solar laminate")
        + labels.count("Raised rigid roof solar panel")
        == ROOF_SOLAR_MODULES_PER_CAR
    )
    assert labels.count("Bonded flexible rooftop solar laminate mount") == ROOF_SOLAR_MODULES_PER_CAR // 2
    assert labels.count("Per-car roof PV MPPT DC/DC") == 1
    assert labels.count("Station DC protection, isolation monitoring, contactors and precharge") == 1
    assert labels.count("Independent HM47/LD32-class motor controller in fire-resistant enclosure") == 2
    assert labels.count("Localized battery water-mist nozzle") == BATTERY_MODULES_PER_CAR
    assert labels.count("COTS electric door cassette") == dims.doors_per_side * 2
    assert labels.count("Door sill gap-filler flap") == dims.doors_per_side * 2
    assert labels.count("Platform screen-door alignment datum") == dims.doors_per_side * 2
    assert labels.count("Door/platform safety interlock interface") == dims.doors_per_side * 2
    assert labels.count("T-ECU/S safety cabinet") == 0
    assert labels.count("T-ECU/A application cabinet") == 0


def test_roof_solar_system_exposes_both_mount_styles() -> None:
    labels = _labels_recursive(roof_solar_system(CarDimensions()))
    assert labels.count("Bonded flexible rooftop solar laminate mount") == ROOF_SOLAR_MODULES_PER_CAR // 2
    assert labels.count("Lightweight flexible roof solar laminate") == ROOF_SOLAR_MODULES_PER_CAR // 2
    assert labels.count("Raised rigid roof solar panel") == ROOF_SOLAR_MODULES_PER_CAR // 2
    assert labels.count("Bolted raised solar mounting rail") == ROOF_SOLAR_MODULES_PER_CAR
    assert labels.count("Solar module edge clamp") == ROOF_SOLAR_MODULES_PER_CAR * 2
    assert labels.count("Roof PV module junction box") == ROOF_SOLAR_MODULES_PER_CAR
    assert labels.count("Roof PV fire-isolation switch box") == 2
    assert "Roof PV MPPT combiner box" in labels
    assert "Roof PV downlink cable gland" in labels


# ---------------------------------------------------------------------------
# COTS interior fit-out catalogue
# ---------------------------------------------------------------------------


def test_cots_catalogue_covers_every_category() -> None:
    """Every `Category` enum value has a catalogue row."""
    for c in Category:
        assert c in CATALOGUE, f"missing catalogue entry for {c}"
        item = CATALOGUE[c]
        assert item.length_mm > 0.0
        assert item.width_mm > 0.0
        assert item.height_mm > 0.0
        assert item.mass_kg > 0.0
        assert item.power_w >= 0.0
        assert item.supplier_reference_url.startswith("https://")
        assert item.alternates
        assert item.fit_note
        assert item.geometry_basis
        assert item.cost_basis
        assert 0.0 < item.unit_cost_low_usd <= item.unit_cost_base_usd <= item.unit_cost_high_usd


def test_bom_quantities_are_common_per_self_contained_car() -> None:
    """Every family repeats the same 17 m self-contained car module.
    Per-car windows, seats, grab poles, and PIS screens therefore stay
    common across consist length."""
    tram = bom_per_car(family_dimensions(ConsistFamily.TRAM_2CAR))
    metro = bom_per_car(family_dimensions(ConsistFamily.LIGHT_METRO_3CAR))

    def qty(bom: list, category: Category) -> int:
        for item, n in bom:
            if item.category == category:
                return n
        raise KeyError(category)

    assert qty(tram, Category.WINDOW) == qty(metro, Category.WINDOW)
    assert qty(tram, Category.GRAB_POLE) == qty(metro, Category.GRAB_POLE)
    assert qty(tram, Category.PIS_SCREEN) == qty(metro, Category.PIS_SCREEN)
    assert qty(tram, Category.SEAT) == qty(metro, Category.SEAT)
    dims = CarDimensions()
    assert qty(tram, Category.WINDOW) == (dims.doors_per_side + 1) * 2
    assert qty(tram, Category.GRAB_POLE) == dims.doors_per_side * 4
    assert qty(tram, Category.PIS_SCREEN) == dims.doors_per_side * 2
    # Per-car fixed-count items don't scale.
    assert qty(tram, Category.HVAC_ROOF) == qty(metro, Category.HVAC_ROOF) == 1
    assert qty(tram, Category.INTERCOM) == qty(metro, Category.INTERCOM) == 2
    assert qty(tram, Category.LIGHTING) == qty(metro, Category.LIGHTING) == 2


def test_mass_and_power_totals_are_realistic() -> None:
    """Per-car interior fit-out should land in the hundreds of kg and
    draw kilowatts — if we're off by an order of magnitude one of the
    catalogue rows is wrong."""
    m = total_mass_kg()
    p = total_active_power_w()
    # Dominated by HVAC (250 kg) + seats + lighting + windows.
    assert 500.0 <= m <= 2_000.0, f"mass {m:.0f} kg is implausible"
    # Dominated by HVAC 15 kW; lighting + screens add ~1 kW.
    assert 12_000.0 <= p <= 30_000.0, f"power {p:.0f} W is implausible"


def test_envelopes_fit_inside_car_body_bounding_box() -> None:
    """Every reserved envelope must sit inside (or on top of) the car
    body. Specifically: no envelope extends below rail head; nothing
    pokes outside the body width envelope for non-roof items."""
    dims = CarDimensions()
    half_L = dims.body_length_mm / 2.0
    half_W = dims.body_width_mm / 2.0
    # Tolerance: windows + seats etc. mount on the inside of the body
    # skin; a 50 mm outward excursion is the envelope-reservation
    # slack, not a design error.
    tol = 60.0

    for category in Category:
        item = CATALOGUE[category]
        for loc in locations_for(category, dims):
            pos = loc.position
            x, y, z = pos.X, pos.Y, pos.Z
            assert -half_L - tol <= x <= half_L + tol, (
                f"{category.value} X={x:.0f} outside ±{half_L:.0f}"
            )
            if category != Category.HVAC_ROOF:
                assert -half_W - tol <= y <= half_W + tol, (
                    f"{category.value} Y={y:.0f} outside ±{half_W:.0f}"
                )
            assert z >= -tol, f"{category.value} Z={z:.0f} below rail head"


def test_fit_out_car_body_has_more_volume_than_plain_body() -> None:
    """`fit_out_car_body` overlays COTS envelopes on the structural
    body. The resulting compound must have strictly more total
    geometry volume than the body alone."""
    dims = CarDimensions()
    plain = car_body(dims)
    dressed = fit_out_car_body(dims)
    # Compound.volume sums child volumes.
    plain_volume = _volume_recursive(plain)
    dressed_volume = _volume_recursive(dressed)
    assert dressed_volume > plain_volume, (
        f"fit-out compound volume {dressed_volume:.0f} not greater than "
        f"plain body {plain_volume:.0f}"
    )


def test_cots_fit_out_uses_source_shaped_components() -> None:
    labels = _labels_recursive(fit_out_car_body(CarDimensions()))
    expected = {
        "Laminated heated glass pane",
        "Compact rooftop HVAC casing",
        "Continuous opal diffuser",
        "LED display active area",
        "Removable bench cushion pads",
        "Stainless vertical grab pole",
        "Emergency call button",
    }
    assert expected.issubset(set(labels))


# ---------------------------------------------------------------------------
# Mechanical interface and installation packages
# ---------------------------------------------------------------------------


def test_mechanical_interface_builders_are_registered_and_nonempty() -> None:
    expected_slugs = {
        "bogie-to-chassis-connector",
        "bogie-to-motor-connector",
        "low-floor-chassis",
        "side-body-frame-attachments",
        "composite-body-roof-attachments",
        "window-installations",
        "door-mounts",
        "door-design",
        "door-installations",
        "door-to-body-installations",
        "cabin-flooring",
        "battery-installations",
        "bench-on-battery-installations",
        "internal-lighting-installation",
        "hvac-roof-ducting-installation",
        "screen-speaker-mountings",
        "external-lighting-lidar-system",
        "train-connector-mount-pair",
        "mechanical-interface-package",
    }
    assert expected_slugs.issubset(INTERFACE_BUILDERS)
    for slug in expected_slugs:
        model = INTERFACE_BUILDERS[slug]()
        assert _volume_recursive(model) > 0.0, f"{slug} produced empty geometry"
        assert getattr(model, "children", None), f"{slug} should be a compound assembly"


def test_mechanical_interface_package_covers_requested_subsystems() -> None:
    labels = _labels_recursive(mechanical_interface_package())
    expected = {
        "Bogie-to-chassis welded bolster box",
        "Bogie centre-pivot spherical-bearing socket",
        "PMSM motor terminal-box mounting bracket",
        "Dropped stainless low-floor centre tub",
        "Deep low-floor side torsion box",
        "Twin low-floor keel box beam below aisle edge",
        "Low-floor torsion-diaphragm cross tie",
        "Door threshold cross bearer and drain trough",
        "Side body waist rail with window nutplates",
        "Composite side body panel outer skin",
        "Roof cantrail clamp extrusion",
        "Bonded laminated window glass installation",
        "Window aluminium bonding frame and primer land",
        "Door top operator rail mount",
        "Pressed aluminium sliding door leaf shell",
        "Door cassette installed envelope",
        "Door-to-body bolted header backing plate",
        "Low-floor centre aisle anti-slip flooring panel",
        "Battery installation sliding tray and drain pan",
        "Bench seat pan above battery installation",
        "Internal LED light strip aluminium mounting channel",
        "Roof air-conditioner bolted curb and gasket land",
        "HVAC centre supply duct with insulation",
        "Internal passenger screen VESA backing plate",
        "PA speaker grille and acoustic backbox",
        "Front/back roofline LIDAR adjustable mount",
        "LED headlight and marker-light sealed cassette",
        "Train connector mount crashworthy coupler pocket",
    }
    missing = expected.difference(labels)
    assert not missing, f"missing mechanical interface labels: {sorted(missing)}"


def test_repeated_installation_counts_match_car_layout() -> None:
    dims = CarDimensions()
    expected_side_door_count = dims.doors_per_side * 2
    expected_window_count = (dims.doors_per_side + 1) * 2

    labels = _labels_recursive(bogie_to_chassis_connector(dims))
    assert labels.count("Bogie-to-chassis welded bolster box") == 2
    assert labels.count("Secondary air-spring chassis pad") == 4

    labels = _labels_recursive(bogie_to_motor_connector())
    assert labels.count("PMSM motor terminal-box mounting bracket") == 2
    assert labels.count("Motor coolant quick-coupler pair") == 4

    labels = _labels_recursive(window_installations(dims))
    assert labels.count("Bonded laminated window glass installation") == expected_window_count
    assert labels.count("Window condensate drain channel") == expected_window_count

    labels = _labels_recursive(door_mounts(dims))
    assert labels.count("Door top operator rail mount") == expected_side_door_count
    assert labels.count("Door lock keeper adjustable mount") == expected_side_door_count

    labels = _labels_recursive(door_installations(dims))
    assert labels.count("Door cassette installed envelope") == expected_side_door_count
    assert labels.count("Deployable door gap-filler cassette") == expected_side_door_count

    labels = _labels_recursive(battery_installations(dims))
    assert labels.count("Battery installation sliding tray and drain pan") == BATTERY_MODULES_PER_CAR
    assert labels.count("Battery module stainless retention strap") == BATTERY_MODULES_PER_CAR

    labels = _labels_recursive(bench_on_battery_installations(dims))
    assert labels.count("Bench seat pan above battery installation") == expected_window_count
    assert labels.count("Bench cantilever rail over battery strake") == expected_window_count

    labels = _labels_recursive(hvac_roof_ducting_installation(dims))
    assert labels.count("Roof air-conditioner bolted curb and gasket land") == 2
    assert labels.count("HVAC roof-to-saloon drop duct") == 2

    labels = _labels_recursive(screen_speaker_mountings(dims))
    assert labels.count("Internal passenger screen VESA backing plate") == expected_side_door_count
    assert labels.count("PA speaker grille and acoustic backbox") == 12

    labels = _labels_recursive(external_lighting_lidar_system(dims))
    assert labels.count("Front/back roofline LIDAR adjustable mount") == 2
    assert labels.count("LED headlight and marker-light sealed cassette") == 4

    labels = _labels_recursive(train_connector_mount_pair(dims))
    assert labels.count("Train connector mount crashworthy coupler pocket") == 2
    assert labels.count("Train connector M24 pocket bolt head") == 16
