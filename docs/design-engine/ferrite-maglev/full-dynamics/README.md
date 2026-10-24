# Continued six-car fault dynamics

Source-bound continued-fault digital study. Every actual terminal outcome, including failed capture, timeout and geometric/map hold, is retained. No output disappearance is classified as a safe stop.

Exact common candidate: `a79a21a0767355fcb6518471769e532a04e2e23f4bd33db90968ef4a385df5bd`. AW3 mass per car: 37,618.592 kg. Equipment-derived CG and full inertia tensor include named reserve/capture/brake allocations once.

| Case | Physical-model terminal state | Continued post-fault frames | Implemented screens |
|---|---|---:|---|
| straight-supported-stop | hold-initial-support-current-or-field-capacity | 0 | False |
| peak-current-main-power-loss | hold-initial-support-current-or-field-capacity | 0 | False |
| midspan-main-power-loss | hold-initial-support-current-or-field-capacity | 0 | False |
| handover-inverter-loss | hold-initial-support-current-or-field-capacity | 0 | False |
| receiver-braking-loss | hold-initial-support-current-or-field-capacity | 0 | False |
| sensing-disagreement | hold-initial-support-current-or-field-capacity | 0 | False |
| sensing-dropout-independent-reserve | hold-initial-support-current-or-field-capacity | 0 | False |
| watchdog-stale-map | hold-initial-support-current-or-field-capacity | 0 | False |
| nonuniform-map-errors | hold-initial-support-current-or-field-capacity | 0 | False |
| reserve-depletion-capture | hold-initial-support-current-or-field-capacity | 0 | False |
| no-capture-negative-control | hold-initial-support-current-or-field-capacity | 0 | False |
| asymmetric-load | hold-initial-support-current-or-field-capacity | 0 | False |
| urban-curve | hold-initial-curve-or-gap-geometry | 0 | False |
| terminal-loop-low-speed | hold-initial-curve-or-gap-geometry | 0 | False |

Every coil is integrated after a controller refusal: current decays in the explicitly declared freewheel path; permanent-magnet and mutual-circuit forces remain in the plant. A separate reserve controller and power/energy state are modelled. Counted unilateral shoes and friction clamps have declared, unqualified capacities, heat and travel limits. Detection alone never passes a stopping test.

The actual Rust allocation/current kernels provide bounded current demands and bridge voltages. Python integrates the nonlinear shared magnetic network and rigid-body/guideway states; there is no ideal-force substitution. The stationary1kHz/20kHz clocks and host execution observations do not establish target timing.

The six-body small-angle modes include vertical/lateral translation and roll/pitch/yaw, equipment-derived full inertia, gyroscopic terms, measured-state longitudinal spring/damper coupling, curvature chord errors, per-module asymmetry and per-span vertical/lateral/torsional modes. A rigid band does not automatically follow a tight curve. Guideway deadweight reactions include all counted stock; live modes reference dead-load-cambered geometry. Nonlinear magnetic energy, RL work, modal work, friction and reserve-energy balances are retained separately. Material hysteresis, nonlinear soil/joints and omitted shell modes remain open.

The actual Rust research allocator starts from source-bound minimax body-load preferences and enforces current-map residual-lift minimum/maximum forces, wrench and slew constraints. Static LP bounds iterate against actual six-car/guideway pole gaps. The previous zero-lift preference is not realizable merely because its force balance passes: permanent magnets still lift and cancellation can violate current/demagnetization limits. Full current inversion and actual bridge/RL dynamics execute every mechanical frame.

The receiver dq coupon is explicitly hypothetical. Its single .12Wb/4kA equivalent circuit cannot supply20kN: the actual Rust current guard refuses that demand. It must not be represented as a validated70group receiver or as the new magnetic geometry’s useful external field. Shared-core leakage/no-map and dedicated passive propulsion-band alternatives require their own geometry-derived, numerically controlled maps.

A real source-bound Rust authority producer prepares the complete four-stop fixed line and samples actual front/tail poses. Its decision is composed with the actual140group stationary-alpha-beta current kernel. The refined magnetic-material failure blocks launch: full_trip_executed is false. This is an executed refusal attempt, not completed travel, dwell, charging, terminal turnaround or240s whole-line service. Portable raw protocol records are in [authority/receipt.json](authority/receipt.json). A controller/state-machine prototype for actual-pose dwell/energy/charge holds is present; it has not completed the full-line electromechanical trip.

Protection contact revision2 counts the named capture pads, steel hanger kits, brake hangers and paired transverse ties in the same vehicle mass/CG/inertia. Two12×200mm wear strips per track add37.68kg/m to the guideway. Contact-plane, magnetic influence, weld/bolt/rail-anchor fit, actuator travel and physical qualification remain holds. In particular,8×50kN pads cannot absorb a whole-car5mm drop within8mm at the present AW3 without sufficient residual/active magnetic support; a failed-capture outcome is preserved. Conditional numerical stopping results never remove these holds.

Selected development hardware: Raspberry Pi CM5 supervisory SBC and STM32H753XI local MCU. Dual sensing, sequence/configuration/time identity, independent reserve path, watchdog and isolated gate/protection interfaces are specified in interface-spec.json; physical adapters and target deadline measurements remain unexecuted.

Open gates: nonlinear map physical correlation, power stages and shared reserve independence, receiver field/phase and distributed-group compatibility, complete equipment fit and current-density/cooling duty, nonlinear joints/bearings/soil and flexible body modes, full-line protocol/berth/charge composition, target MCU/SBC timing/EMI and protection hardware, independent engineering and physical acceptance.

- [stm32h753](https://www.st.com/resource/en/datasheet/stm32h753xi.pdf): Selected candidate MCU: Cortex-M7, ADC/PWM/watchdog resources; no measured railway execution claim.
- [stm32-independent-watchdog](https://www.st.com/content/ccc/resource/training/technical/product_training/group0/98/3f/88/10/52/e1/46/9d/STM32H7-WDG_TIMERS-Independent_Watchdog_IWDG/files/STM32H7-WDG_TIMERS-Independent_Watchdog_IWDG.pdf/_jcr_content/translations/en.STM32H7-WDG_TIMERS-Independent_Watchdog_IWDG.pdf): Independent watchdog uses separate low-speed clock; actual timeout tolerance and reset paths need target tests.
- [cm5](https://datasheets.raspberrypi.com/cm5/cm5-datasheet.pdf): Selected supervisory SBC: CM5, thermal throttling and published operating range; no fast-loop guarantee.

Reproduce explicit study: `tools/automation/osr-python -m engineering.ferrite_maglev.full_dynamics study`. Opening a retained packet never starts a simulation or hardware command.
