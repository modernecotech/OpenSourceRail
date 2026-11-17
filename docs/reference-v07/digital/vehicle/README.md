# Joined v0.7 digital car: mass, CG and static reaction screen

This digital calculation belongs to physical candidate `osr-v07-joined-prototype-20261117` and quotation selection `osr-v07-prototype-quotation-20261117`. Its [input](input.json) has identity `7beb441511a1b237a58277fb1d8c963d1dd548905a74cce9739169b2c1eb5c61`; the reproducible [result](result.json) has evaluation identity `ebddef0c8b9c21c2d9a023b680afa372b02396a700c77be03d6983300af5a240`. The input pins the exact bytes of the selected car geometry, powered vehicle plan, prototype IFC/result, civil plan and joined candidate. A source change requires a new input and evaluation. This is a digital model, not a measured installed car.

## Model and result

The calculation reads **2,482** inherited CAD geometry occurrences, removes **52** occurrences of the retired passive station interface, and adds **10** powered-equipment occurrences at their declared nominal centres. The retained located geometry weighs **8,856.456 kg/car**: 2,965.110 kg body and fitout, 4,965.818 kg bogies and 925.528 kg underframe. The machine-readable result lists the component groups and seven powered equipment types. Two powered equipment groups and **10,090.200 kg/car** already in the inherited mass account lack CAD placement. Their mass is counted once, never set to zero. For the interval calculation only, their centroids may lie anywhere in the declared car box `x = ±8.5 m`, `y = ±1.325 m`, `z = 0–4.8 m`. Passenger mass has the same deliberately broad sensitivity box. These are calculation domains, not claimed installed locations.

| Per 17 m car | Conditional analytical mass | Longitudinal CG interval | Equal-share *static* axle reaction interval |
| --- | ---: | ---: | ---: |
| Tare | 20.292–21.617 t | −4.365 to +4.373 m | 16.13–87.25 kN |
| 46-place normal account | 23.742–25.067 t | −4.953 to +4.960 m | 13.35–106.95 kN |
| 160-person structural control | 32.292–33.617 t | −5.878 to +5.884 m | 6.47–155.77 kN |

**Sizing load handoff:** the powered service and 10 m civil packets both use **25.071998 t/car normal** (150.431989 t/train) and **33.621998 t/car crowd** (201.731989 t/train). These are **5.342775 kg/car above** the conditional interval's upper mass because the powered allowance is rounded up to 2,400 kg/car. The explicit handoff in `result.json` preserves those loads for traction, braking and civil calculations; the interval is a placement sensitivity and does not reduce them. Their equal-load static means are 61.489 kN/axle normal and 82.458 kN/axle crowd, not maximum reactions.

For each car, the two bogies are at `x = ±6.4 m`; the static calculation uses `R_left = g(M/2 − Σmx/12.8)` and `R_right = g(M/2 + Σmx/12.8)`, then divides each bogie reaction equally over its two axles. The reported interval endpoints come from different allowed mass/centroid cases and must not be combined into one load case. Actual axle maxima, dynamic factors, brake/traction transfer and lateral reactions remain **unknown**. In particular, the civil packet's equal-axle mean cannot substitute for the upper interval or a designed load combination.

The source-bound nominal screen retains **52 mm** motor-side clearance and **105.7 mm** motor-to-floor clearance *after a proposed 50 mm translation reservation*. It also computes a **75 mm straight static** car-body/platform-edge gap. These values do not cover bogie yaw, heave, roll, curves, wheel wear, tools, vehicle sway or accessible boarding tolerance. The rail brake's stowed bottom is 120 mm above the rail datum; its turnout sweep is unknown. The collector's proposed deployed top is 4.8 m above rail; conductor height and electrical clearance are unknown. The referenced [IFC](../../../design-engine/v07-prototype-bundle/packet/nominal-prototype-interface.ifc) contains 54 nominal motor, brake and collector boxes and no approved solid or station/civil assembly.

## Reproduce and next digital inputs

From the repository root:

```sh
python3 -m engineering.vehicle_parts.joined_digital_car check --output docs/reference-v07/digital/vehicle/result.json
python3 -m pytest -q engineering/vehicle_parts/tests/test_joined_digital_car.py
```

To issue a revised evaluation, record new source hashes and the centroid domain in a new input identity, then run `build` to a **fresh** result path. Place actual body, wiring, coolant, protection, brake energy, mounts, doors, HVAC, interior and passenger zones in the CAD/BOM to narrow the CG interval. Carry the resulting axle and combined traction/braking loads into the 10 m beam, bearing and foundation model. A joined Code_Aster/CalculiX stress model needs controlled beam reinforcement, prestress, seats, fixings, material law and load combinations; no joined FEM solve is represented here. The present result is reproducible digital evidence for the v0.7 design package with explicit open inputs, not fabrication fit or physical acceptance.
