# OpenSourceRail

OpenSourceRail develops simple, affordable urban transport that can be manufactured and maintained locally. **v0.6 is a station-powered freewheeling railway:** lightweight comfort cars run on passive steel-wheel bogies and conventional rails on precast concrete structures. Station linear-induction motors launch and receive the train through a passive onboard reaction element. There are no onboard traction motors, traction batteries or levitation magnets.

The aim is low whole-life cost through repeated components, repairable assemblies, compact elevated stations and open engineering. We compare the complete railway: vehicles, civil works, station power, passenger service, maintenance and energy. Cost superiority remains to be demonstrated.

## v0.6 development basis

[development-baseline.toml](engineering/development-baseline.toml) selects the new physical candidate. Its body, running gear and propulsion have separate identities. **This is a research and prototype design, with no manufacturing or operating release.**

| Design choice | Reference basis |
|---|---|
| Formation | Six 17 m cars; approximately 104.5 m including gaps |
| Comfort | 44 fixed seats + two wheelchair places/car; 276/train; no planned standing |
| Layout | Four abreast where structure permits, wall benches at doors; two passenger doors on one side |
| Body | Lightweight aluminium/GFRP architecture, sandwich floor/roof, lightweight benches and retained glazing |
| Running gear | Twelve identical unpowered two-axle bogies: 24 axles, 48 wheels |
| Propulsion | Station double-sided LIM reference; passive aluminium secondary on each car |
| Ordinary guideway | Conventional rails and fastenings on precast concrete; box, twin-beam and U-beam comparisons |
| Services | Flush solar roof and a separately sized auxiliary battery; HVAC, doors, ATP and emergency loads remain |
| Automation | Existing station-led GoA4 architecture, continuous onboard ATP and independent mechanical brakes |
| Service targets | 72 km/h, 0.4 m/s² acceleration, 0.6 m/s² service deceleration, 35 s dwell, 120 s headway |
| Capacity arithmetic | **8,280 passengers/hour/direction** at 30 departures/hour; safe headway not yet established |

Removing propulsion does not remove passenger services or braking. Loss of station power leaves the train supported on its wheels; independent brakes must stop it. A train stopped outside a powered zone needs a protected rescue/tow system. Admission, crowd loading, high-platform accessibility, one-sided doors and evacuation remain requirements.

## Current engineering

The [current dossier](docs/design-engine/current/README.md) contains the mass ledger, reference 1.5–2 km calculations, battery duty, braking bounds, civil alternatives, readiness gates and [delivery drafts](docs/design-engine/current/exports/manifest.json). The [roadmap](docs/ROADMAP.md) and [illustrated reader](OpenSourceRail-Book.pdf) explain the remaining work.

The [native follow-up campaign](docs/design-engine/v06-physical-closure/README.md) executes current-excited motor FEM, reduced Chrono braking and body-interface experiments. The tested full LIM delivers a conditional **7.17 kN/car against 11.10 kN required** and exceeds its steel-model field limit. This geometry needs redesign. Wet/downhill and failed-channel braking also require larger protection margins; these simulations do not qualify brake hardware.

Reference calculations distinguish **required force** from available motor thrust. Station-only propulsion still needs a validated LIM map, practical clearance, thermal duty and receiving/fault evidence. Complete installed mass/CG/inertia, joined-body structure, wheel dynamics, hot-weather HVAC, independent braking, rescue and same-service economics remain open.

The 266 city geographies and underlying maps are preserved as starting inputs. **City numerical regeneration is held** until the reference drive, braking, route and economic evidence is sufficient. Old fleet, station winding, CAPEX and OPEX figures are historical; they are not v0.6 results. See the [geographic catalogue and holds](docs/design-engine/current/cities.json).

## Iterative design search

**Start ongoing design work with `./osr design adaptive plan` and `./osr design adaptive run`.** This function-first workflow treats provisional targets as hypotheses, resumes pending work and advances to new definitions. It can broaden the physical family or commission missing models when local changes are ineffective.

The retained bounded v0.6 campaign connects the earlier body/motor/brake generators to restartable native execution and research-twin exports. Its original parameter bounds and screening criteria remain reproducible; [its publication](docs/design-engine/v06-optimisation/README.md) records that earlier experiment. These commands reproduce that component campaign:

```bash
./osr design campaign create campaigns/v06-wheel-lim.toml
./osr design campaign run <campaign-id>
./osr design campaign compare <campaign-id>
./osr design campaign publish <campaign-id>
```

The three-generation trial reduced the frame branch’s normal-load deflection from about 110 mm to 23 mm. Its 33.6 mm crowd-load result still fails the 25.6 mm screen, and additional mass raises the required motor thrust. All tested motors remain outside the declared linear-steel domain; no viable complete train is claimed.

Research ranking can select the next experiment while every complete design remains unqualified. The participating-panel trial remains numerically nonconverged in lateral motion; its vertical results are diagnostic, with no structural acceptance. Invalid numerical results cannot provide physical ranking values; unknown installed equipment and whole-life prices remain explicit.

The [broader design search](docs/design-engine/v06-design-space/README.md) adds aluminium, GFRP and hybrid load paths; PET/PVC foam and directional honeycomb; joints, inserts, floors and roof panels; alternative station-motor arrangements; and explicitly identified lower-speed service options. Primary supplier data guides necessary bounds and test plans. New structures require validated evaluators before full-body ranking. Run `./osr design space build` and `./osr design space verify` to reproduce the comparison.

The [whole-railway architecture campaign](docs/design-engine/v06-architecture/README.md) goes further: **509 analytical cases, 174 physical definitions and seven propulsion families** compare station-only launch, lower speeds, boosters, recovery drives, distributed wayside power and onboard wheel traction. It varies formation, powered length and guideway sections while retaining mandatory safety and accessibility. The selected v0.6 reference is preserved. Required forces, conditional fleet counts and material quantities are compared; complete installed mass, validated available thrust and whole-life prices remain unknown.

Foundation work includes six-axis joint fixtures, a counted finite-area body alternative and a nonlinear magnetic method benchmark. The former body's mesh trend is confirmed at **28.0 mm normal deflection**, above its provisional 25.6 mm comparison. That comparison is advisory in the new policy; actual functional limits require their own justification. The magnetic benchmark uses a generic material in a DC circuit; it does not establish a nonlinear moving LIM. [M1–M3 prototype plans](docs/design-engine/v06-architecture/prototype-program.json) specify the measurements still needed.

The [adaptive generator](docs/design-engine/v06-adaptive-design/README.md) opens **102 variables across 14 domains**, including materials, honeycombs, layups, structures, joints, running gear, propulsion, fitout and whole-railway arrangements. It separates real obligations, preferences, revisable assumptions and numerical validity. Failures generate different physical, model-development or measurement tasks; repeated unsuccessful local changes escalate to new load paths and architecture. Pending work survives resource budgets.

Six new native body cases demonstrate material redistribution: a deeper, thinner sill saves **48 kg/car** relative to the previous jointed body and reduces calculated normal bending from **28.018 to 19.793 mm**. Another option saves 19 kg/car with a shallower envelope. Actual mass changes feed axle, propulsion/energy and civil calculations. Thin-wall stability, strength, fatigue, clearances and physical correlation remain necessary work; no complete railway is qualified.

```bash
./osr design architecture run
./osr design architecture publish
./osr design architecture verify
./osr design adaptive plan
./osr design adaptive run --max-jobs 1
./osr design adaptive publish
./osr design adaptive verify
```

## Use the repository

```bash
./install.sh
./osr status
./osr readiness
./osr workbench
./osr build
./osr verify
./osr book --check
./osr test
./osr sim baghdad
```

`./osr sim baghdad` reports the city evaluation hold and its retained geographic inputs. Build regenerates reference analytical and delivery records. The CLI, Workbench and reader use the same selected candidate; unsupported physical jobs hold explicitly.

Rust `osr-atp`, interlocking, OCC, TCMS, door control and station SCADA remain the automation foundation. New wheel/station interface fixtures exercise readiness and independent brake demands. Historical `osr-maglev-control` healthy-gap fixtures do not qualify a wheel-supported train. Numerical or software execution alone never establishes physical acceptance.

## Historical designs and contributions

The [v0.5 maglev archive](docs/archives/v0.5-maglev/README.md) preserves the former selection and evidence at its recorded Git revision; the [earlier archive](docs/archives/pre-comfort-default/README.md) preserves preceding research. `./osr legacy verify` checks their exact source and payload bytes. Reproduce historical calculations in a separate checkout.

Start with [engineering guidance](engineering/README.md), [project instructions](AGENTS.md), [architecture](docs/ARCHITECTURE.md), [tools](tools/README.md) and the [documentation index](docs/INDEX.md). Unknown mass, performance, price and qualification stay unknown.
