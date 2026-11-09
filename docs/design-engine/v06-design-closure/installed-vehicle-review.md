# Installed-vehicle closure review

## Selected research body and remaining work

The closure-campaign body is `9f6d223074b3438a546d5b3d71cd9b970807387ef0542023bed79bef46dbdeba`, evaluation `dfb48ca3fac6ee9b702ae13b2e5e4e0c112d734263750deefb25ad5718fdb272`. Its installation manifest covers 668 part types, 9,804 patterns and 122,422 occurrences. It records nine tare/normal/crowd mass cases, CG coordinates and 24 static axle reactions per case.

The installation artifact still marks installed mass incomplete and supplier fit unverified. It has no inertia values in those mass cases. The 12 motor and 12 gearbox/coupling locations are envelopes; shaft/bearing fit, fastening interfaces, maintenance tool access and removal paths are not established. Its static axle results exclude dynamic civil factors. Electrical, cooling and protection quantities from the separate compact-drive child cannot be inherited into this parent candidate.

## Separate compact-drive child: bounded geometry campaign

The child `75075df9247dfff7082a78eadc273d3a99f37e5486450621536c43b1bfa2f797` / `fdac4907a6a867f0b4f27e0876a772d1b54d526ec323beb3b6d9a155e0e00b21` was evaluated in three declared gear/body-lift configurations. Its source-bound run is [retained here](compact-drive-geometry-closure/manifest.json).

| Configuration | Body candidate | Model mass low/base/high | Direct parts/process subtotal low/base/high | Nominal findings | Continuous/interface holds | Screen |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| `compact-737-h100` | `75075df…` | 111.35 / 124.62 / 145.01 t | $0.694 / 1.503 / 3.377m | 5,940 | 3,606 | HOLD |
| `compact-737-h150` | `5a3a6cd…` | 111.45 / 124.72 / 145.11 t | $0.694 / 1.504 / 3.378m | 5,790 | 3,498 | HOLD |
| `compact-980-h150` | `9af20e2…` | 111.50 / 124.77 / 145.17 t | $0.694 / 1.504 / 3.379m | 6,060 | 3,474 | HOLD |

These are model mass intervals and calculated direct part/process amounts, not verified installed masses or complete train prices. The shared 737 ratio with 150 mm body lift reduced the number of nominal findings by 150 relative to the 100 mm lift case, but every candidate retained thousands of unresolved checks. The 980 ratio case has the greatest count of nominal findings. All three report 528/528 declared ground samples passing, retained brake-component counts complete, but no braking performance. The continuous relative bounds and intended output-axle bore/tolerance interfaces remain unresolved. Removal loads/eyes are unverified.

The first report illustrates the conservative screen: a 44 mm required gap plus uncertainty against 42.22 mm signed-axis separation for a motor/guide-clevis pair, repeated across placements. It records nominal stock overlaps as well. These are envelope/analytic screening findings; exact BRep contact was not established. They are sufficient to hold the screen and guide redesign, not proof of a physical crash or proof of fit.

The run used three independent child processes, each limited to 60 CPU seconds, 1 GiB address space and 90 seconds wall time; no CAD or FEM jobs ran. Runtime was 35.4–35.7 seconds and peak RSS 428,276–428,792 KiB per trial. The complete campaign took about 107 child seconds, preserved all outputs, and reported `source_unchanged=true`. Source integrity was checked, but the source tree was not OS-sandboxed read-only. Campaign summary evaluation: `665569b22200a7e87355b203be1061a944bbff26fd7779cbb59816efce5b4573`; manifest SHA-256 `ef322685a479eb6f45b3dbba429d69c6ff7569841b152bd8309a9978584387ee`; 23 payload files totaling 32,716,748 bytes.

This campaign does not change the six-car passive-wheel development reference, select an onboard drive, close the parent candidate, or establish an integrated route/journey. The child is not promoted. Its next useful engineering work is resolving the repeated envelope overlaps and axle interface/tolerance holds, then re-running the exact changed geometry before any drivetrain or FEM claims.

## Independent review disposition

A bounded read-only review found no new contradiction in the parent candidate's recorded mass and axle loads; it found the installation gate still open for the missing interfaces, inertia, supplier-fit, service access and removal evidence above. This review used instructions only; it was not OS-enforced isolation and ran no analysis or solver.

The closure campaign's installed-vehicle gate remains **open**. A child geometry screen cannot close the parent candidate's required installed inventory, and neither screen is physical or manufacturing qualification.
