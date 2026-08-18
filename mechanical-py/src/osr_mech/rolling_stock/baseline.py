"""Promoted light-metro trainset baseline.

These values are the current v2A seed selected by the top-down design
iterator and promoted into the buildable CAD/simulation baseline.  Keep
new rolling-stock geometry, BOM, FEM, and scenario tests pointed here so
the baseline moves as one trainset instead of as scattered constants.
"""

from __future__ import annotations

PROMOTED_CANDIDATE_ID = (
    "light-metro-3car__16p5m__reference-body__reference-bogie__"
    "motor-350kw-hm47-class__battery-225kwh-lfp-800v__"
    "hvac-24kw-direct-hv-dc__pv12"
)

PROMOTED_LIGHT_METRO_CAR_LENGTH_M = 16.5
PROMOTED_LIGHT_METRO_CAR_LENGTH_MM = PROMOTED_LIGHT_METRO_CAR_LENGTH_M * 1_000.0
PROMOTED_LIGHT_METRO_CAR_WIDTH_MM = 2_850.0
# Structural body roof before mounted PV/HVAC equipment.
PROMOTED_LIGHT_METRO_CAR_HEIGHT_MM = 3_450.0
# Controlled overall running height containing the current 3,868 mm CAD
# assembly plus production tolerance. Civil clearance uses this value, while
# CarDimensions continues to use the structural body-roof height above.
PROMOTED_LIGHT_METRO_CAR_OVERALL_HEIGHT_MM = 3_900.0
# The promoted body places bogie pivots 2.1 m inboard from each car end.
PROMOTED_LIGHT_METRO_BOGIE_CENTRE_SPACING_MM = (
    PROMOTED_LIGHT_METRO_CAR_LENGTH_MM - 2.0 * 2_100.0
)
PROMOTED_LIGHT_METRO_TRAINSET_LENGTH_M = 49.5
PROMOTED_LIGHT_METRO_TRAINSET_LENGTH_MM = PROMOTED_LIGHT_METRO_TRAINSET_LENGTH_M * 1_000.0

PROMOTED_MOTOR_CONTINUOUS_KW = 250.0  # planning value pending supplier duty map
PROMOTED_MOTOR_PEAK_KW = 350.0
PROMOTED_TRACTION_CONTROLLER_COUNT = 6
PROMOTED_TRACTION_HARDWARE_PEAK_KW = 2_100.0
PROMOTED_TRACTION_CONTROL_CAP_KW = 1_800.0
PROMOTED_BATTERY_USABLE_KWH_PER_CAR = 180.0
PROMOTED_BATTERY_USABLE_KWH_PER_TRAINSET = 540.0
PROMOTED_BATTERY_GROSS_KWH_PER_CAR = 225.0
PROMOTED_BATTERY_GROSS_KWH_PER_TRAINSET = 675.0
PROMOTED_BATTERY_NOMINAL_VOLTAGE_V = 675.0
PROMOTED_BATTERY_NORMAL_MAX_VOLTAGE_V = 740.0
PROMOTED_HVAC_THERMAL_KW_PER_CAR = 24.0
PROMOTED_ROOF_SOLAR_MODULES_PER_CAR = 12
PROMOTED_ROOF_SOLAR_NAMEPLATE_KW_PER_TRAINSET = 15.12

# The design iterator currently resolves a 75,308 kg modeled subtotal.  The
# controlled planning tare retains a 3,442 kg (4.57 %) engineering reserve
# for wiring, fluids, fasteners, coatings, production tolerances, and supplier
# mass growth until the drawing-level mass-properties ledger is closed.
PROMOTED_OPTIMIZER_MASS_SUBTOTAL_KG = 75_308
PROMOTED_ENGINEERING_MASS_RESERVE_KG = 3_442
PROMOTED_LIGHT_METRO_TRAINSET_MASS_KG = (
    PROMOTED_OPTIMIZER_MASS_SUBTOTAL_KG + PROMOTED_ENGINEERING_MASS_RESERVE_KG
)
