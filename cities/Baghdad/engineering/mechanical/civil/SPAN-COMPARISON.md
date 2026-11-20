# Baghdad viaduct span comparison

For the 148.2 km proposal, the installed-capital allowance is $7,865.67m in 2026 USD. Its repetitive single-track beam is 10 m long on separate piers. The comparisons below keep the two-track railway, seven corridors and loaded train fixed. They test what happens when a precaster lengthens the same trial box. The longer units need their own section, tendons, handling scheme and price before selection.

## Structure and handling

Each train has 24 axle planes and a crowd-loaded mass of 201.092 t. The train advances in 10 mm steps, with additional entry and exit positions. Each trial retains the 2.00 × 1.40 m cross-section, 550 mm solid ends, bearing seats 250 mm from each end, the trial pier and footing, and lifting lines one fifth of the stock length from each end. The structural screening uses the same 1.30 moving-load multiplier and 150 mm eccentricity as the 10 m study.

| Stock length | Concrete per beam | Bare equivalent mass | Dead + live positive moment¹ | Elastic displacement bound | Trial soil pressure | Load margin at 12 m radius² |
|---:|---:|---:|---:|---:|---:|---:|
| 10 m | 13.40 m³ | 34.17 t | 892.3 kNm | 1.0 mm | 207.4 kPa | +25.83 t |
| 20 m | 25.00 m³ | 63.74 t | 3,110.7 kNm | 15.4 mm | 286.1 kPa | -3.74 t |
| 25 m | 30.80 m³ | 78.53 t | 4,522.9 kNm | 35.3 mm | 333.5 kPa | -18.53 t |
| 30 m | 36.60 m³ | 93.31 t | 6,302.2 kNm | 71.3 mm | 381.6 kPa | -33.31 t |

¹ Separately peaked dead moment and sampled train moment give a positive-action screen. The uncracked gross-section displacement bound excludes camber, cracking, creep, settlement and rail continuity. Compare measured rail and conductor elevations with the collector travel and station boarding tolerance before accepting the result.

² Against the project’s illustrative 60 t chart at 12 m, before hook block, lifting beam, slings, inserts, construction tolerances or crane setup. A negative margin rules out that assumed lift. A positive margin requires a supplier chart at the surveyed radius, ground pressure and rigging take-off. Obtain trailer payload, axle-group reactions, swept path and temporary bracing design.

| Stock length | Support-pair torque | Effective prestress screen | Pick-line hogging | Pick top / bottom³ | Centre top / bottom³ |
|---:|---:|---:|---:|---:|---:|
| 10 m | 42.8 kNm | 1.28 MN | -96.9 kNm | +0.12 / +2.65 MPa | +0.41 / +2.36 MPa |
| 20 m | 55.7 kNm | 4.48 MN | -316.0 kNm | +0.47 / +9.18 MPa | +1.61 / +8.04 MPa |
| 25 m | 65.9 kNm | 6.51 MN | -469.0 kNm | +0.66 / +13.37 MPa | +2.44 / +11.59 MPa |
| 30 m | 76.5 kNm | 9.07 MN | -651.1 kNm | +0.93 / +18.62 MPa | +3.49 / +16.05 MPa |

³ Compression is positive. Assume a bonded constant-eccentricity tendon at 0.30 m and full transfer before a bare-stock lift. Divide the effective prestress screen by 0.80 to illustrate 20% total loss. Combine that force with self-weight moment at each pick and at midspan. Negative top-fibre stresses identify tension to check against measured concrete release strength. Anchorage, transfer length, end-zone bursting, shear, unequal slings, buckling, bearing seat strength, fatigue and lateral stability require individual checks.

## Price and deliver the same service

| Length | Placements | Pier and foundation positions | Yards / erection fronts | Modelled direct elevated scope | Maximum extra cost per placement to match 10 m⁴ |
|---:|---:|---:|---:|---:|---:|
| 10 m | 29,640 | 29,654 | 6 / 6 | $1,331.24m | $0 |
| 20 m | 14,820 | 14,834 | 3 / 3 | $1,213.05m | $7,975 |
| 25 m | 11,856 | 11,870 | 3 / 3 | $1,189.42m | $11,962 |
| 30 m | 9,886 | 9,900 | 2 / 2 | $1,174.05m | $15,900 |

⁴ Divide the difference in the direct elevated allowance by the longer option’s placements. The combined **net** extra cost for redesigned stock, foundations, yard, transport, rigging and erection must fit within that amount to preserve the modelled saving. Include avoided costs once. These prices use the existing length-scaled rates. All four alternatives require ground and access evidence.

The 10 m programme deploys 6 yards for 216 yard-months and 6 fronts for 210 front-months under a continuous-hire scenario, assuming all yards store beams from first casting through final erection and all fronts remain on hire between first and last lift. Peak month-end inventory is 983 beams in 2028-12 or about 33,590 t of stock systemwide. Daily peaks and yard allocations require a dispatch plan. Confirm the asset hand-back dates and demobilisation price.

For the 10 m case, each additional $10,000 per yard-month amounts to $2.16m of direct cost, and each additional $10,000 per front-month to $2.10m. Apply only the residual after deducting work already included in beam, pier, lift, transport and tooling prices. Quote mobilisation, rent, beds, moulds, shifts, utilities, working capital, route permits and crane possessions separately. Use the [matched return calculation](../compare_returns.py) once a complete elevated scope is priced.

Obtain the yard return form with `--yard-template > build/baghdad-yard-rates.json`. Enter tendered 2026 USD rates and the itemised amount already carried per unit, attach the scope review reference, then run `--yard-return build/baghdad-yard-rates.json`. The result compares direct elevated costs for the 10 m family. It covers mobilisation and continuous hire. Transport, other civil trades, financing and project-level allowances require their own reconciliations.

The pier model envelopes two adjacent peak vertical reactions on the trial 2.50 m square footing. Verify site bearing, settlement, overturning, flood/scour and lateral action. Price the river crossing and a step-free station as separate lots, with surveyed access windows and traffic management.

## Reproduce the comparison

Run `python3 cities/Baghdad/engineering/mechanical/civil/compare_spans.py --check` from the repository root. Use `--json` for every candidate identity, source fingerprint, axle envelope, pad reaction, lift demand and price threshold. [10 m parent section and assembly details](README.md) · [City capital model](../../../system-results.json)

Train candidate `f6844cd4d9f5d9320fa421b37eb074b9911d3cd695d350fdc464cc3597184a72`. Evaluation `d2f138c7af47a0ba9b954d8dc5d657c32bad8fced0bb9eb1a0239784ff4ad534`.
