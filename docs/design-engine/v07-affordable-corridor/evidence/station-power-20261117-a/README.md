# Equal-service propulsion necessary-bound screen

**Status:** analytical demand and necessary-bound evidence only. No architecture is selected, installed, priced, or physically accepted. The selected passive-wheel v0.6 vehicle remains `756a68870162f7559b052b05c9b201728c9f448e3bb61114f287848c02f2d3a3`; it is not the cable-capstan budget anchor. Input `095f8afb0aa54de8f9bde1310d612acccd3b1365c969aa6665b0f45c7844fb93`; evaluation `13032d7e525568a94a62a9c4a97a003573f39e00c73650e40e90c44779d2a816`; no selection identity. Each row has a separate research configuration ID and model demand ID. Exact source paths and SHA-256 values are in `input.json`.

## Fixed service and scope

Thirty route-km, 12 stations, 2 tracks, six 17 m cars, 44 fixed seats plus 2 wheelchair places per car, 276 normal places/train, 8,280 offered places/hour/direction at 120 s, 72 km/h cap, 35 s dwell hypothesis, independent 0.6 m/s² stop and 160-person/car crowd control. Safety, access, parking, rescue, degraded service, and a maximum accepted journey time remain mandatory holds. The route has 11 interstation intervals averaging 2,727 m. The campaign's 1.5/2/3 km spacings are **local segment sensitivities**, not three alternative complete 30 km lines. No actual interval distribution, full-route timetable, fleet, protection headway, or city access equivalence is established.

The currently replayed 30 km cable-capstan budget packet is `build/v07-ethos/line30-current-20261117-a`: requirement `a18e0f20b6ec40e067aff40213b312ae756f7f3389ee5b43059225cf92d05ff4`, evaluation `947dd7cbcac7c260da721150912fba47531c96fd3f7a28365c394249608ee869`, manifest `b455f1f9cfa98bd41d958c736862e75578c831d287db7b5c95ca48b5a82af2c4`. Its conditional base capital remains $24.5997 million/route-km. The published `docs/design-engine/line30-benchmark` packet is retained historical and source-stale against current selected vehicle cost and braking implementation. Neither cable packet prices the station-only or powered-wheel designs screened here.

## Conditional moving-demand result

The selected vehicle's **accounted**, incomplete normal mass is 22,671.998 kg/car, with 1,770.387 kg/car rotating-equivalent inertia. Installed mass, CG, new drive mass and all associated costs remain unknown. The calculation uses the repository's event-resolved demand model: 0.4 m/s² commanded launch inside the stated window, natural coasting outside, 0.6 m/s² independent final braking target, rolling coefficient 0.0025, 50 N/car constant resistance and 1.8 N·s²/m²/car quadratic resistance, zero headwind. Receiving 350 m is reserved for installation but **not credited as traction or proved as a brake**. A reached target means only that prescribed forces and brakes could mathematically achieve it.

| Local spacing | Uphill grade | Station launch 250 m | Station launch 500 m | Sustained powered-wheel demand |
|---:|---:|---|---|---|
| 1.5 km | 0% | Reached, 146.2 s | Reached, 118.4 s | Reached, 116.7 s |
| 1.5 km | 1% | Stalled at 1,063 m | Reached, 124.2 s | Reached, 116.7 s |
| 1.5 km | 2% | Stalled at 717 m | Stalled at 1,405 m | Reached, 116.7 s |
| 2.0 km | 0% | Reached, 196.7 s | Reached, 147.4 s | Reached, 141.7 s |
| 2.0 km | 1% | Stalled at 1,063 m | Reached, 186.6 s | Reached, 141.7 s |
| 2.0 km | 2% | Stalled at 717 m | Stalled at 1,405 m | Reached, 141.7 s |
| 3.0 km | 0% | Reached, 342.9 s | Reached, 213.9 s | Reached, 191.7 s |
| 3.0 km | 1% | Stalled at 1,063 m | Stalled at 2,039 m | Reached, 191.7 s |
| 3.0 km | 2% | Stalled at 717 m | Stalled at 1,405 m | Reached, 191.7 s |

The sustained wheel case has the powered interval `[0,S]`; it is a required-force trajectory. It has no measured motor/adhesion/store force map. The 250 m station launch never reaches 20 m/s under a 0.4 m/s² command, so its slower level trip is a service penalty, not a failed speed cap. Station-only has 8 reached and 10 stalled cases; 9 stalls also have an independent optimistic coast shortfall. The remaining 1.5 km, 1%/250 m stall comes from the full declared resistance model, while the deliberately loose speed-cap bound alone does not prove it.

## Necessary bounds and physical consequence

For no off-zone thrust, `F_floor = m g (c_roll + grade) + F_constant`; if positive, the farthest possible stop from the end of launch is at most `L + (m + m_rot) v_cap² / (2 F_floor)` per car. This omits quadratic drag and assumes the train exits launch at the full speed cap even when it does not. At +1% and 500 m launch the upper stop position is **2,228 m**; at +2% it is **1,468 m**. Thus the declared 3 km station-only uphill leg is impossible even under that optimistic bound. At 2 km, +2% is likewise excluded. A booster, longer powered section, changed spacing/alignment, or onboard traction is a new research configuration with all equipment and service consequences counted.

Grade work on a 2 km +1%/+2% leg is at least 5.448/10.896 kWh per 100 t of translated mass, or **7.411/14.822 kWh** for the inherited 136.032 t six-car normal account, before drag and losses. The opposite direction is downhill; recoverable energy cannot be credited without a receiving circuit, available sink, limits and protection. Under optimistic uniform axle loading, 0.4 m/s² acceleration and the campaign's μ=0.1 traction hypothesis, powered-wheel cases with 12/24 driven axles require μ≈0.0866/0.1066/0.1266 at 0/1/2%; thus 1% and 2% fail that hypothesis. With 24/24 driven axles the floors are 0.0433/0.0533/0.0633, which pass only this idealized arithmetic. Actual wheel loads, load transfer, wet/contaminated adhesion and equipment mass are unknown.

Independent 0.6 m/s² stopping is a separate safety hold. Even after crediting rolling and constant resistance at low speed, the inherited mass/inertia gives optimistic μ≈**0.0632 on level** and **0.0832 on a 2% downgrade**, above the campaign's μ=0.05 brake hypothesis. This is not an approved brake rejection: rail/track brakes or revised validated adhesion may be used, but an independent stop/parking system must be demonstrated, including faults and heat.

## Installed propulsion closure still required

At 120 s headway, a departure group can see 30 launches/h and 540 launches over an 18 h day. A double-track 12-station line has 22 directional interstation departures and 22 arrivals in an ordinary terminal-to-terminal layout, but actual fixed winding group count and shared installation geometry are **unknown**. Group length, train-fin overlap, phase registration and entry/exit force must be evaluated as functions of position. A scalar motor coupon or centred force sample does not satisfy this duty. For each phase, solve `L(i,x,T) di/dt = V_converter - R(T)i - e(x,v,i,T)` together with force `F(x,v,i,T)` and the converter voltage/current limits. Integrate copper, core, secondary, converter and feeder losses over the actual current history, then solve repeated `C dT/dt = P_loss - Q_cooling` to hot equilibrium and fault states. Receiving braking needs an independently controlled energy sink or dissipative path; assumed regenerative credit is zero until measured.

Station-only installation must count every stator group/core/winding, fastening, rail/fin clearance, supports, encasement, feeders/return, switchgear, converter, DC link, grounding, isolation, sensors, control, cooling, fire protection, independent brakes, station charger, spare parts, access and protected tow provision. Powered-wheel installation must count motors, gears, powered bogies/axles, bearings, inverter channels, DC supply or conductor, charge contacts/stores, busbars, protection, cooling, mounts, wiring, independent brakes and rescue after drive loss. All added masses, thermal ratings, prices, origins, local fabrication/repair hours and renewal intervals remain **unknown**, not zero. The conditional cable budget and preliminary motor catalogue prices cannot close this ledger.

## Next bounded physical test

Instrument one full-scale fixed station group and representative passive fin on loaded carriage/bogie ballast. Measure moving entry, centre and exit thrust with registered phase position, winding R/L/flux, DC/phase current and voltage, converter limits, 0/1/2% equivalent grade load and force ripple. Couple an independently controlled receiving stop/parking system and verified energy sink/dissipator. Repeat 120 s launches to hot equilibrium, test loss of one group, cooling and power faults, then demonstrate protected tow. Retain calibrated raw data, uncertainty, specimen IDs and independent review. Use those M1 results to decide whether a 1.5–2 km station-to-station M2 demonstrator can proceed.

## Reproduction and limits

`PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 python3 build/v07-ethos/station-power-20261117-a/run.py` from the worktree root. The actual execution used `timeout 120s`, a 512 MiB virtual-memory cap and `/usr/bin/time`; `log-final.txt` records 3.12 s and 264,404 KiB peak RSS. The first attempt failed because `engineering` was not on `PYTHONPATH` (`log.txt`); the first completed evaluation is retained as `input-v1.json`, `output-v1.json`, `log-v1.txt`. This final evaluation adds research configuration identities and the fresh current-source line30 packet. Source hashes, input/evaluation IDs, failed terminal states, numerical residuals, and resource limits are retained. No native solve, CAD, publication, selection or source edit was performed.
