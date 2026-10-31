# Conditional P1 journey design study

This source-bound study evaluated **28 canonical P1 bundles** from the coordinated railway campaign (two primary-iron definitions for each of 14 generated body candidates), plus one separately selection-bound P1 railway bundle. That bundle references the exact selected v0.6 vehicle candidate `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3` (body `9489e4f2666fd3b3c73232c86df3f12adf42a5531eb27373834cf3fecb1a3117`; selection `8e5905bc7c81d6177bbaafde81ab3a5f8cc54947c4923eb4493949566ac85cdc`) and has its own whole-railway identity `566f4f0e491e9968ca2beda0671d04a590c83329b27b95d86145d7ede4de6758`. The selected vehicle identity and component IDs were preserved; no result from another body was substituted. Together these inputs produced **29 bundle evaluations** and **87 low/base/high assumption cases** using each input's own accounted mass, propulsion identity, braking interface and commanded power windows.

Each generated force/current/thermal map is labelled `synthetic-method-test` inside the reduced longitudinal method and retained as an assumption-only design-study input. The selected-reference adapter is bound to the current selection, vehicle evaluation and physical component identities; its route and LIM assumptions do not change the selected vehicle's physical candidate ID. The nested result keeps `test_only=true`, `available_motor_map_id=null`, and all physical journey, engineering, acceptance and release flags false. The required campaign journey result remains `not-run`.

## Assumptions and outcomes

| Case | Assumed peak thrust per car | Train current limit | Rated efficiency | Journey outcome | Berth stops | Maximum initial acceleration |
|---|---:|---:|---:|---|---:|---:|
| low | 8.9 kN | 750 A | 85% | stopped: 29 | 29/29 | 0.316–0.316 m/s² |
| base | 11.1 kN | 1000 A | 90% | stopped: 29 | 29/29 | 0.400–0.400 m/s² |
| high | 13.3 kN | 1250 A | 95% | controller-speed-limit: 29 | 0/29 | 0.484–0.484 m/s² |

The base force assumption is 11.1 kN/car, equivalent to 222 kW/car at 20 m/s if that force were available there. The maps use a one-second stationary pre-excitation assumption, a current fraction derived from the base-case initial 0.4 m/s² force balance, and lumped route-level thermal inventory/cooling hypotheses. These are explicit model inputs, not LIM measurements or validated operating maps.

The low cases remain below the 0.4 m/s² acceleration target and take longer than the base cases. The base cases reach the declared two-metre berth tolerance using the unqualified candidate brake model. The high cases exceed the assumed controller's speed limit during the launch segment. These outcomes identify useful control and evidence work for the next design cycle.

## Service and shift context

The candidate carries 46 places per car (44 seats plus 2 wheelchair places), or 276 places per six-car train. At the declared 120 s target, arithmetic capacity is 8280 places/hour/direction. The 35 s dwell is carried separately. This calculation does not establish tail clearance, station occupation, fleet size, dwell performance or a protected headway.

The existing Class C cost model's schedule assumptions are carried forward: production uses 2 8-hour shifts/day; civil work uses 2 8-hour shifts/day; operations cost cases cover [16, 18, 24] hours/day with [2, 2, 3] shifts/day. The three-shift high case remains a cost assumption; this trajectory calculation does not validate staffing or round-the-clock operating duty.

## Exact interfaces and open limits

The study propagates each bundle's declared command windows without filling unpowered gaps. For this reference P1 case the command window is `[[0, 500]] m`; the bundle's separately defined wayside installation intervals are not treated as proof that every installed interval is energized during this trip. The point-train model also omits train-tail clearance, electrical section interaction, current protection, repeated 120-second thermal duty, charging/reserve, adverse grade/headwind, crowd loading, faults, recovery, passenger protection, and actual site geometry.

Normal mass is the candidate's accounted loaded-mass hypothesis; complete installed mass remains unknown. Braking and adhesion are unqualified hypotheses. All physical journeys, engineering validations and approvals remain open.

## Reproduction

```bash
./osr design journey-study verify --replay
./osr design journey-study publish
```

[Summary](summary.json) · [Candidate index](candidate-index.json) · [Source-bound study index](study-index.json) · [Payload manifest](manifest.json)
