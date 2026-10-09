# Bukavu — viaduct obstacle clearance

**Physical release blocked.** This is a source-bound footprint and terrain screen of the existing planning route, not an obstacle-cleared alignment.

Mapped nearby footprints: **4,262**; source heights: **0**. Building source: retained; terrain: retained.

| Screen | Status | Count |
|---|---|---:|
| Beam/building | ground-collision | 28 |
| Beam/building | ground-lateral-clearance-conflict | 12 |
| Beam/building | height-unresolved | 3,043 |
| Beam/building | product-depth-unresolved | 351 |
| Reference support/foundation | foundation-footprint-conflict | 981 |
| Reference support/foundation | foundation-setback-conflict | 208 |
| Reference support/foundation | mapped-footprints-only-clear | 2,032 |
| Terrain | beam-terrain-collision | 63 |
| Terrain | reference-gradient-exceeded | 2,063 |
| Terrain | reference-gradient-within-policy | 963 |
| Unresolved geometry/input | boundary-span-layout-unresolved | 192 |
| Unresolved geometry/input | special-product-depth-and-support-layout-unresolved | 102 |

Counts are screening events per civil segment/reference support, not unique buildings, accepted piers or procurement quantities. Reference-gradient flags are DEM height differences between provisional supports; designed rail gradients are unavailable. Roof/canopy effects, raster quantisation, noise and real ground slope remain unseparated. These flags neither prove an unbuildable rail profile nor establish clearance.

## Measures required for a buildable alignment

- **Beam overflight:** surveyed roof/plant heights plus ground datum, swept train/deck/walkway envelope, lateral clearance, fire/rescue access and property/air rights. A source height below a provisional soffit is conditional only; building floors are an uncertain height estimate.
- **Tall obstacles:** reroute, acquire/remove an approved obstacle, or raise the vertical alignment with gradient-compliant approaches and new pier/structure costs. Unknown heights never establish clearance.
- **Supports:** place the entire pier/pile-cap/foundation and construction-access footprint clear of buildings and services. A clear beam does not clear its supports. Move support lines along a tangent using verified Pi20/Pi25 spans, change foundations/cap arrangement, or design a independently checked special span; do not invent a 30 m catalogue beam.
- **Terrain:** survey a longitudinal/cross-section profile and test grades, vertical curves, terrain crests, flood levels and each erection stage. Straight beam soffits interpolate between supports; local ground peaks can still clash.
- **Release:** close every conflict and missing-height/mapping/terrain/utility finding against survey and independent engineering checks before accepting the corridor. Recalculate route, stations, supports, quantities, cost and service evidence for adopted changes.

The default screen uses a 9 m twin-track envelope plus 2 m lateral allowance, a 3 m foundation radius plus 2 m setback, 12 m reference rail height, 1.6 m conservative rail-to-soffit allowance, 2 m roof clearance and a 3.5% reference grade limit. The Pi structural depth is 1.155 m; the combined allowance leaves 0.445 m for an unverified track stack. Special products have unresolved depth and cannot pass a Pi roof-clearance check. Direct structural/foundation intersections are reported separately from clearance/setback conflicts. These are controlled screening assumptions requiring deployment-specific approval, not statutory clearances.

[Summary and source hashes](summary.json) · [Per-line beam, support and terrain events](clearance-register.json.gz).
