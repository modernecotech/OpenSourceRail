# Conditional P1 journey design study

This source-bound study evaluated **28 canonical P1 bundles** from the current coordinated railway campaign: two separate primary-iron definitions for each of 14 body candidates. It generated **84 low/base/high assumption cases** using each bundle's own mass, propulsion identity, braking interface and commanded power windows.

Each generated force/current/thermal map is labelled `synthetic-method-test` inside the reduced longitudinal method and retained as an assumption-only design-study input. The nested result keeps `test_only=true`, `available_motor_map_id=null`, and all physical journey, engineering, acceptance and release flags false. The required campaign journey result remains `not-run`.

## Assumptions and outcomes

| Case | Assumed peak thrust per car | Train current limit | Rated efficiency | Journey outcome | Berth stops | Maximum initial acceleration |
|---|---:|---:|---:|---|---:|---:|
| low | 8.9 kN | 750 A | 85% | stopped: 28 | 28/28 | 0.316–0.316 m/s² |
| base | 11.1 kN | 1000 A | 90% | stopped: 28 | 28/28 | 0.400–0.400 m/s² |
| high | 13.3 kN | 1250 A | 95% | controller-speed-limit: 28 | 0/28 | 0.484–0.484 m/s² |

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
