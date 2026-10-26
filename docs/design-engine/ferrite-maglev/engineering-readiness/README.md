# Current engineering readiness

OpenSourceRail develops simple, locally maintainable urban transport with high normal passenger throughput. This register joins the exact magnetic component, body revision and equipped comparison before assigning an engineering gate. All permanent magnets and support/guidance coils remain onboard; ordinary guideways remain concrete with passive steel facings.

**No complete equipped train, stable multiaxis hover or physically supported 2 km journey is established.** Numerical method success and component screens do not provide physical acceptance.

[Project introduction](../../../../README.md) · [Readiness Workbench](../../../workbench/trip/readiness/index.html) · [Candidate index](index.json) · [Compressed current register](status.json.gz) · [Source receipt](manifest.json) · [Research packages](artifacts.json)

The register contains **504 exact composed comparisons** and eight gates per configuration. The two next-experiment compositions each have eight explicit hover/journey/fault preflights. Failed and unknown prerequisites refuse motion without producing a fabricated trajectory. Source bindings, rather than an old overall review date, determine the current input revisions.

## Operating magnetic experiment

The matched campaign executes 3 material/layout comparisons at a common proposed operating gap. Detailed derivatives are focused on the 12-litre differential NdFeB assembly; the retained 6-litre control and counted 6-litre NdFeB + 6-litre ferrite hybrid have fewer sampled states. This is not a complete 3D force/current/loss map.

| Configuration | Temperature °C | Nominal 2D Fz contours kN | Fixed-gap +2 t / 1.3 capacity screen |
|---|---:|---|---|
| 12L-differential-N35UH | 20 | 13.896 / 13.953 | fail |
| 12L-differential-N35UH | 80 | 11.967 / 12.016 | fail |
| 6L-retained-N35UH | 20 | 6.101 / 6.130 | unknown |
| 6L-retained-N35UH | 80 | 5.254 / 5.279 | unknown |
| 12L-mixed-N35UH-FB9B | 20 | 7.295 / 7.334 | unknown |
| 12L-mixed-N35UH-FB9B | 80 | 6.171 / 6.204 | unknown |

The coarser 3D operating attempt is **completed** at 35.338 mm, 80°C and zero coil current. Its Fz contours are **9.397 / 11.274 kN/module**.
Force-contour spread, mesh/domain refinement and finite current sources must be resolved before admission as an operating map. Lowering a proposed gap is a new evaluated state, not an automatic transfer of force.

## Finite operating refinement

| Case | Gap mm | Fz contours kN | Mean AW3 support screen | +2 t / 1.3 reserve screen |
|---|---:|---|---|---|
| medium-same-gap | 35.338 | 8.986 / 11.431 | fail sample | fail sample |
| medium-28mm | 28.000 | 12.516 / 14.550 | pass necessary sample | fail sample |

These are fixed 80°C, zero-current component states. A single mesh refinement and denser face integration are separate diagnostics, not force/moment convergence. The scalar-potential formulation contains **no coil-current source**; nonzero-current requests are refused. A mean-weight sample pass cannot establish equilibrium, reserve, multiaxis stability or a current-controlled journey.

## Equipped vehicle

| Body option | Located defined material kg | Accounted tare comparison kg | Complete installed mass / CG / inertia |
|---|---:|---:|---|
| 6082-six-cell-deep-40kn/bus-ul700-electric-five-proposal | 7165.951 | 17633.937 | unknown |
| 6082-six-cell-deep-70kn/bus-ul700-electric-five-proposal | 7278.766 | 17679.605 | unknown |

Every identified occurrence has structural-participation and fit/test/removal/repair fields. Material-region counts are not manufacturing part counts. Unlocated magnetic stock, supplier references, retained allocations and missing equipment do not acquire a uniform invented mass distribution. GFRP monocoque design variables are a separate unexecuted design space; they are not silently substituted for the selected reinforced frame.

## Hot-weather and electrical consequences

The thermal study retains **768 heat-load scenarios**, **1536 normal/N−1 nominal-capacity comparisons**, and **830 nominal-sizing failures**. Actual 50°C capacity, compressor COP/input, ventilation and complete services power remain unknown.

There are 384 conditional dark-roof/core-temperature failures in the declared passive-feature scenarios. These feature proposals require a new complete composition; they do not automatically describe the selected car. Added insulation stock is counted, while coatings, heat recovery, mounts and integration remain unknown where unweighed.

At 15 A and 80°C the selected winding dissipates **348.768 W/module**. Holding 80°C copper in 50°C ambient requires **11.626 W/K/module** in the declared steady heat balance; actual conductance is unknown. Unconstrained RL voltage responses that leave ±15 A have no validated force or controller credit.

## Service, access and economics

The retained Baghdad planning inputs have **13 lines missing their original line-specific targets** and **14 of 14 lines** below the common 14,400 normal passengers/hour/direction floor. These are different comparisons. Six cars at 120 normal passengers/car require 180-second headway arithmetically; safe headway, actual force/braking and changed fleet/station quantities remain unqualified for the new train.

The new research policy limits horizontal transfers to 300 m and walking to 300 seconds, evaluated at both 1.0 and 0.6 m/s. The retained maximum is **965.8 m** and fails this comparison. Lifts, queues, waiting, weather and actual accessible-route approval are additional. No shortcut, hub realignment or city adoption is invented.

The old city cost sensitivities and civil loads belong to their original planning configurations. They are not presented as the cost or civil design of these lighter research alternatives.

## Native numerical maintenance

| Method | Execution | Numerical screen |
|---|---|---|
| chrono | completed | pass |
| magnetic | completed | pass |
| structure | completed | pass |

The separate scheduled workflow requests a two-step 2 km ideal-force Chrono check, a manufactured nonlinear 3D GetDP mesh pair, and an actual CalculiX composite mesh pair. Native logs and failures are retained. The composite coupon checks a declared synthetic laminate; it does not establish equipped-car modes. The weekly schedule requests Tuesday 03:17 UTC on the default branch; hosted execution can be delayed. [Schedule semantics](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule).

## Next engineering programme

| Package | Required closure |
|---|---|
| Suspension/control | Converged finite operating maps, material limits, multiaxis derivatives, actuator reserve and correlated module measurements |
| Equipped vehicle | Located complete inventory, GFRP/metal joint load paths, full CG/inertia and validated equipped modes |
| Electrical/thermal | Actual hot-weather supplier data, ventilation, bus/protection ratings and repeated current/cooling duty |
| Journey/faults | Same-candidate empty/AW3 2 km travel and receiving/support-power-loss response |
| Civil | Matching facing anchors, eccentric reactions, deflection, beams, piers, foundations and construction loads |
| Service/access | Protected 180-second or explicit revised headway, dwell/fleet consequences and acceptable accessible transfers |
| Economics | Same-configuration installed scope, energy, maintenance, origin, financing and supplier evidence |
| Prototype | Weighed and instrumented magnetic/steel and structural articles with independent measurement and review |

Start `./osr workbench` and open `http://127.0.0.1:8090/docs/workbench/trip/readiness/` for the readiness page on the default port. The existing server serves this route; no hardware command or numerical job is launched by viewing it.

Reproduce with `python -m engineering.engineering_status --help`. Domain commands and all numerical inputs/logs are indexed in the retained packages. Full numerical readback requires the recorded native tool environments; a fresh campaign records the actual local solver identities. Status JSON is compressed and indexed to keep ordinary documentation concise. No research publication closes physical qualification.
