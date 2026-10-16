# Baghdad factory staged stressing and unloading studies

The [new native review](factory-stages/index.html) extends the common
`factory-precast` problem with individual-strand stressing and static unloading
states. It retains a fresh [93-object FreeCAD export](factory-stages/model.FCStd)
and signed ideal end-pin demands. The [previous support review](factory-support/index.html)
and all nine original factory examples remain unchanged historical evidence.
No structural, supplier, lift, concrete-transfer or production release follows.

## Connected static load path

Controlled variables now include `stressing_order` (`balanced_pairs` or
`lower_first`) and `release_order` (`reverse_stress` or `same_stress`). Each
48-strand example retains 145 states: unloaded, 48 stressing endpoints and 96
unloading increments. The latter reduce each strand through half and zero
remaining force. These are research force states; they do not specify an
operator procedure, release maturity or a dynamic envelope.

Linear transverse lever weights allocate each strand's axial force and vertical
eccentric couple to the two fixed native rail axes at y = ±1.85 m. The allocation
preserves total axial force, its transverse first moment and total vertical
couple. Unequal half-pair forces therefore produce unequal rail compression.
Actual strongback torsion/warping and three-dimensional connection stiffness
remain unresolved; this allocation cannot establish their response.

The existing Euler–Bernoulli and geometric stiffness matrices solve each rail
at its current compression. The vertical solve includes nominal RHS rail gravity
(1.892 kN/m) and opposite generalized end rotation loads from the allocated
eccentric couple. This assumes mirrored strand fields at the two bed ends.
Independent end operation is not covered. Both-plane imperfection signs combine
at matching stations, giving **9,280 support-contact cases per example**.

The same rigid plate, compression-only grout, tension-only anchor, nominal weld
and pad kernels process every case. The nominal support detail is extrapolated
to all eight stations per rail;
native CAD represents only the first pair of supports, with remaining allocations
unresolved. Each stage retains force/moment residuals,
maximum sway and signed pin reactions for both rails and vertical bow signs.
Numerical equilibrium uses absolute checks of 0.001 N and 0.01 Nm, separate from
engineering acceptance. No unstable stage can supply a complete demand envelope.
Independent controls cover uniform gravity, constant curvature from end couples,
the existing bow-only solver, resultant conservation and static unloading states.

## Actual common comparisons

The [verified four-case record](factory-stages-comparison.json) holds source and
attempt hashes, candidate variables, checks and unknown installed costs.

| Stressing hypothesis | Static unloading hypothesis | Largest anchor tension, kN | Largest ideal end-pin vertical force magnitude, kN | Largest vertical additional sway, mm |
| --- | --- | ---: | ---: | ---: |
| Balanced pairs | Reverse stressing order | 0.769 | 19.687 | 11.31 |
| Balanced pairs | Same stressing order | 0.853 | 19.687 | 11.31 |
| Lower first | Reverse stressing order | 8.212 | 127.248 | 29.60 |
| Lower first | Same stressing order | 8.212 | 127.248 | 37.15 |

All four remain elastically stable and satisfy the stated pad compression
equilibrium screen. Their structural resistance check stays unknown. The peak
total end couple is 0.133 MNm for balanced pairs and 1.363 MNm for lower first.
These are load-allocation sensitivities, not qualified connection demands.

The earlier full-force imperfection study's 2.499 kN anchor result excludes rail
gravity and staged couples. It is retained with that different load definition;
the new default's lower tension cannot be taken as an adopted reduction. New
ideal pins remain grounded at x = −0.5 and 25.5 m. Signed CSV forces act on their
foundation reservations, positive upward. Axial rail closure, actual end details
and foundation resistance still require design. Strongback/mould/service weights,
thermal effects, losses, overpull, preload and release dynamics remain absent.

## British equipment cases, checked 16 October 2026

**Hydrajaws M2000 PRO.** The manufacturer publishes a 25 kN tensile test range,
up to 50 mm stroke and included M16/M20 threaded stud adapters. Its company page
locates manufacturing at Tamworth, England. This makes it a British manufacture
candidate for anchor testing. The proposed 26.5 mm bar assembly has no confirmed
compatible thread adapter, reaction-bridge layout or engineer-specified proof
load. Calculated service tension and instrument range do not determine that load
or establish anchor/ground resistance. No installed price is adopted.
[Product](https://www.hydrajaws.co.uk/product/m2000-pro-tester-kit-anchor-tester/),
[manufacturing location](https://www.hydrajaws.co.uk/portable-pull-testing/).

**CCL matched stressing/unloading and calibration package.** CCL identifies UK
manufacture at its Yorkshire factory and lists a Digital Force Measurement System
(Load Tester Calibration Kit). The detailed product page returned 403, so no
range, accuracy, dimensions or compatibility is inferred. Request a matched
strand/grip/jack/pump/sensor configuration for the nominal 154 kN strand-force
hypothesis, with exact calibration, access, origin, interlocks, asymmetry and
release requirements. Bought-in content and every offered item need separate
origin confirmation. [Manufacturer](https://www.cclprecast.com/),
[named equipment listing](https://www.cclprecast.com/category/equipment).

These extend the existing Macalloy, Rapid and British machining cases in the
[controlled register](../../engineering/design_engine/data/factory-interface-suppliers.json).
All [enquiries remain unsent](factory-stages/interface-rfq.csv). No supplier
configuration or test programme has been accepted.

## Evidence and next gates

Native job `run-c99799f9003e4a42` executed FreeCAD and reopened FCStd and STEP.
Screen job `run-c87c744dab904be8` executed all four controlled sequence cases.
The static page projects a verified common export; its publisher executes no
additional physics. The new snapshot has an exact file seal and current-source
check. The earlier snapshot remains verifiable historically; tests now exercise
that distinction explicitly rather than requiring historical evidence to acquire
new source hashes.

```sh
.venv/bin/python tools/automation/publish-factory-review.py --check --current --output docs/design-engine/factory-stages
.venv/bin/python tools/automation/publish-factory-review.py --check --output docs/design-engine/factory-support
./osr validate run --profile factory-native --output build/validation/factory-stages-<unique-name>
```

The next structural gates are a connected three-dimensional strongback/end
connection model, full loading/stressing/transfer/release combinations, actual
soil/anchor/baseplate/weld resistance and supplier-approved operating limits.
The railway beam still needs transmission/end-zone, railway loading, compression,
reinforcement, shear, fatigue and deflection design. Measured first articles,
factory process times and installed-cost evidence remain necessary for scale-up.
