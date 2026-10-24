# Finite magnetic carriers and terminal curves

The [executed geometry sweep](carrier-geometry.json) compares two through five
paired-row yaw carriers under each 17 m body, at 50, 75, 100, 150 and 300 m radii.
It executes **160 geometry cases**, retaining both fixed yaw pivots and explicit
lateral slides, with 1 mm and 2 mm reserved tolerance. **No fixed-pivot yaw-only
case passes. Sixteen yaw-and-slide cases pass the declared stock-only screens.**
No installed carrier mechanism or moving dynamics is validated.

## Actual stock and proposed layout

The current 24 modules use twelve positions per side, x = −5.5…+5.5 m at 1 m
pitch, with row centres y = ±0.88 m. Their complete counted local stock box is
**0.92 × 0.90 × 0.956 m**, including the asymmetric lateral interval −0.40…+0.50 m.

The [30-support-module proposal](support-architecture.md) uses fifteen positions
per side, at **1.01 m pitch**, with centres x = −7.07…+7.07 m. The frozen wide-stock
box is **0.96 × 0.90 × 0.956 m**; 50 mm nominal gaps give a 15.1 m row and 0.95 m
nominal end clearance in a 17 m body. The model reserves at least 0.5 m body-end
clearance after carrier rotation and tolerances. These are proposed placements.
They do not adopt the heavier support candidate or qualify its magnetic model.

The proposed support study has not positioned its added coolers, fans, pumps,
hoses or separate guidance U-cores. **Their installed envelopes are excluded and
remain unresolved.** The present finite boxes cover the existing module stock,
not the complete future carrier or vehicle. New joints, crossframes, retention,
slides, wiring, capture/brake articulation and floor clearance remain undefined.

## Geometry and mechanism

Each carrier holds contiguous modules from both rows. Balanced assignments use
one or two repeated longitudinal carrier lengths. Every point in the **finite
stock box**, rather than only module centres, is conservatively screened against
the circular radial gap envelope. With 8 mm nominal and 2–30 mm allowed gaps, a
2 mm tolerance reserve leaves at most **4 mm calculated mismatch**; the 1 mm
reserve leaves 5 mm. These are declared research targets, not qualified tolerances.

For local longitudinal coordinate u, transverse coordinate v, radius R and
carrier normal recentering t, the exact radial mismatch is
`sqrt(u² + (R − v − t)²) − (R − v)`. The carrier translation balances its worst
inward and outward finite-stock errors. Actual yaw angles then follow the circle.

A rigid body can translate as a whole. Three or more yaw pivots fixed laterally
to that straight body cannot each acquire a free radial translation. The sweep
therefore retains two distinct mechanisms:

- **Yaw only:** one body lateral offset, fixed lateral pivot positions, independent
  carrier yaw. These cases retain failed gap screens.
- **Yaw plus lateral slides:** one explicitly counted slide and yaw joint per
  carrier. Required one-sided travel is calculated from the actual carrier poses.
  The whole-body offset first minimises slide travel, then shifts only as much
  as necessary to meet the declared package width, counting the extra stroke.

The body heading is tangent at its centre. This is a bounded candidate family;
the search does not prove that every possible bogie, articulated body or curved
route design fails. A conventional two-pivot arrangement still needs to fit all
finite magnetic modules on those two carriers; the tested two-carrier layouts
cannot satisfy the stated gaps at these radii.

Rotated full stock boxes are checked for module-to-module interference. Every box
is inflated by the reserved tolerance for the interference test. The study also
checks rotated stock against the available body length and a **proposed 3.0 m
centred underbody package width**, reporting the existing 2.65 m body-width screen
separately. This is a revised clearance target; it is not a qualified carbody,
guideway, station or city swept envelope. All current 2.65 m width screens fail.

## Least carrier counts in the bounded search

The following rows use the larger **2 mm tolerance reserve**. The smaller 1 mm
reserve selects the same least carrier counts.

| Stock layout | Radius | Least carriers / yaw joints per car | Lateral slides per car | Required one-sided slide travel | Centred stock width |
|---|---:|---:|---:|---:|---:|
| Current 24 modules | 150 m | 4 | 4 | 30.008 mm | 2.910494 m |
| Current 24 modules | 300 m | 3 | 3 | 13.334 mm | 2.842743 m |
| Proposed 30 modules | 150 m | 5 | 5 | 63.615 mm | 3.000000 m |
| Proposed 30 modules | 300 m | 4 | 4 | 27.957 mm | 2.879626 m |

No two-through-five-carrier layout passes all stock screens at **50, 75 or 100 m
radius**. Larger curves reduce the mechanism burden, at the cost of a larger
terminal footprint and its unpriced land/civil interfaces. A 150 m terminal
radius is therefore a concrete alternative to investigate; no city default,
station location or terminal loop has been changed.

The proposed 30-module/150 m case uses five identical three-module-per-side
carriers. Its maximum finite-stock mismatch is **3.7345 mm**; after reserving
2 mm, the lower gap is **2.2655 mm**. Peak carrier yaw is **2.3154°** and minimum
nominal adjacent-module clearance is **22.428 mm**. The minimum-slide pose would
need 3.004765 m width; moving the body another **2.3825 mm** fits the strict 3.0 m
package target, increasing required slide travel from 61.233 to 63.615 mm. No
width limit is rounded up or silently relaxed. The small remaining gap margin
must withstand real tolerances, deflection and control errors before selection.

## Next physical design work

1. Compare the 150 m terminal candidate against a larger-radius layout using
   surveyed sites, approaches, evacuation and complete civil/land costs.
2. Draw and count four/five-carrier mechanisms, yaw bearings, lateral slides,
   stops, fail-safe retention and structural hardpoints. Establish actual travel,
   stiffness, fatigue, service access, lubrication and capture/brake compatibility.
3. Install and check all coolers, separate guidance hardware, hoses and wiring;
   close the 3D floor/guideway/station swept envelopes and revised vehicle mass.
4. Recalculate support allocation, magnetic maps, electrical/control timing and
   fault states for the exact articulated revision. Independent spatial magnetic
   validation remains open; fixed-stock curvature arithmetic supplies no force.
5. Rerun coupled dynamics only after that revision has valid initial support and
   full installed fit. The canonical fourteen pre-motion failures remain intact.

All adoption, engineering, manufacturing and physical-release flags remain false.
Adding a slider or raising the permissible speed cannot resolve a static support
failure. The design objective remains useful throughput with simple, maintainable
hardware and low whole-life cost; this geometry study exposes its mechanism and
clearance costs rather than treating articulation as free.

## Reproduce

```bash
tools/automation/osr-python -m engineering.maglev_research.carrier_geometry
tools/automation/osr-python -m pytest -q \
  engineering/maglev_research/tests/test_carrier_geometry.py
```

The JSON binds the canonical source files, validated support-architecture receipt
and carrier study source. Twelve regression tests check finite versus point
geometry, constrained fixed pivots, exact radial extrema, explicit body/slide
poses, rotated-box clearance, balanced module coverage and preserved failure
states. No dynamics simulation or physical output is started.
