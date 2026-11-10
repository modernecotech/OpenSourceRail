# Vehicle lighting, inter-car and gangway audit

## Candidate and evidence basis

This is a read-only inventory audit of the detailed six-car `9f6d2230…` body
proposal, engineering revision `dfb48ca3…`, and identity-matched delivery proposal
`7b88d05f…`. It is a research candidate, not a change to the passive-wheel
development baseline. The specialist audit ran at source commit
`6acc01115f110809ce3127c8e7aa56cdf5aa115f`; the coordinator confirmed the
following input bytes are unchanged in the current closure worktree:

| Input | SHA-256 |
|---|---|
| `campaigns/v06-design-integration-closure.toml` | `3731528a682811dc3cc98df371764682b203c186cec3a1626ed2c4c98ec9024a` |
| `docs/design-engine/reconciled-pilot-bogie-detail/delivery/proposal.json.gz` | `1b091c4875b2945cc344edcd11932d265514f193fbce2ef6d5429e76d392d90c` |
| `docs/design-engine/reconciled-pilot-bogie-detail/vehicle/bom.csv` | `4aeebf5164d7c0d840f5f9daa603ddb77cc9d2dad129e8ee8b417114d9f8d0cf` |
| `docs/design-engine/reconciled-pilot-bogie-detail/vehicle/installation.json.gz` | `111077d3fd5f4ab1008089f362f7f777bdf547cc8369b2444acf070bf5499493` |
| `docs/design-engine/v06-design-closure/vehicle-document-coverage.json` | `45749633f1a145b688f989d35a678a105971da389cb0d0b9d424c4390765198b` |
| `docs/design-engine/v06-design-closure/installed-vehicle-review.md` | `7d43f95795de5ae11073560c4d7fb0f359d9d709072ecae32a3057fc7b010a45` |

The coordinator grouped exact BOM rows by `assembly_id`, summing
`quantity_per_train`, the `mass_{low,base,high}_kg` fields and
`direct_base_usd`. These are proposal quantities, mass bounds and direct-cost
estimates, not weighed assemblies, supplier quotations or complete
installed-system prices.

| Proposal assembly | Part types | Listed occurrences/train | Listed mass low/base/high | Direct base-cost subtotal |
|---|---:|---:|---:|---:|
| Car lighting (`services/lighting`) | 14 | 2,514 | 67.900 / 91.348 / 128.836 kg | $3,667.44 |
| Gangway lighting | 9 | 220 | 2.500 / 5.060 / 9.520 kg | $460.40 |
| Inter-car electrical | 11 | 430 | 15.300 / 28.740 / 51.180 kg | $3,040.60 |
| Mechanical gangway | 44 | 6,695 | 532.273 / 635.646 / 794.317 kg | $8,703.20 |
| Mechanical coupler and air hose | 20 | 615 | 1,039.228 / 1,239.638 / 1,558.352 kg | $9,112.00 |

Together, those five distinct BOM groups list 98 types and 10,474 occurrences
per six-car train, with a 1,657.201 / 2,000.432 / 2,542.205 kg summed mass
range and a $24,983.64 base direct-cost subtotal. These totals inherit the
proposal's part definitions and do not add final assembly labour, verified
installation mass, lifecycle cost, commissioning or released QA.

## Findings

- **LED lighting:** the BOM lists car LED boards, channels, diffusers, drivers,
  vestibule and emergency LEDs, looms, fuses, clips and fixings. It also lists
  one gangway light set at each of five car interfaces. This is a component
  allowance, not a closed lighting design: circuit topology, voltage/current,
  illuminance, emergency autonomy, heat, ingress, fire performance, wiring
  routes and measured power remain open.
- **Inter-car electrical:** safety and data cables, plugs/receptacles, bonding
  braids, lugs, supports, rubber boots and fixings are counted. Cable lengths,
  ratings, connector pinout, strain relief, bend radius, flex-cycle life,
  protection and clearance through the complete articulation motion are not
  established.
- **Couplers:** the five interfaces include drawbars, ten energy absorbers,
  spherical bushes, clevises, crossplates, pins/retainers, fasteners, air hoses,
  fittings and restraints. The mass basis mixes envelope allowances with
  gross-stock geometry. Coupler load cases, joint strength/fatigue, retention,
  accepted absorber characteristics and rescue interchangeability remain open.
- **Gangway:** five interfaces include portal frames, fixed/sliding floors,
  hoops, clamps, fasteners, wear parts, stops, tethers, seals, brush and hand
  protection. Rubber/fabric properties and sections are not specified to a
  verified material grade. Articulation travel, swept clearance, pinch zones,
  floor transitions, weather sealing, fire/smoke behaviour and removal sequence
  have no verified moving-assembly evidence.
- **CAD/FEM and production documents:** the vehicle GLB is a static
  visualization. The inspected proposal has no SolidCraft parametric assembly
  or swept-motion proof for these groups and no matching FieldCraft analysis.
  All referenced subassembly/part drawing and inspection-release fields remain
  unfilled; the existing clevis stock sketch is not a controlled finished-part
  drawing.
- **Maintenance:** generic isolate/support/release/remove steps and a 0.15 m
  tool-radius hypothesis appear in the proposal. Actual tool paths, support or
  lifting points, cable disconnection access, car-separation sequence and
  replacement clearances remain unverified.

## Closure work

1. Freeze car-interface coordinate frames and define the complete angular,
   lateral and vertical motion envelope for all five connections.
2. Build SolidCraft assemblies for each coupler, gangway and flexible service
   bundle, including fixings, keep-out zones and removal paths.
3. Define connector ratings and pinouts, cable lengths/routing, protection and
   flex-cycle duty; define LED circuit loads and emergency-lighting targets.
4. Specify elastomer/fabric grades, section geometry, joining and replacement
   method, then define passenger-safety, fire/smoke, fatigue and inspection
   checks.
5. Run matched structural checks on coupler mounts and gangway frames, plus
   clearance and service-access checks over the full motion envelope. Record
   material limits and independent comparisons.
6. Reconcile the resulting solids and purchased equipment into installed mass,
   BOM quantities, centre of gravity, wiring/thermal budgets, controlled
   drawings, assembly instructions, removal steps and costs.

This audit was static and read-only. It did not run CAD, FEM, a motion solver,
or a physical inspection. The delegated read-only instruction was not an OS
sandbox; no file changes were reported, and the coordinator verified the listed
source hashes. No subassembly is promoted to engineering acceptance or
manufacturing release by this inventory review.
