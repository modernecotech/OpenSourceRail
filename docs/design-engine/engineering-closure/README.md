# Current engineering inputs and closure

This is the evidence-enabled continuation of the [research twin](../digital-twin/README.md).
It preserves the six earlier source-bound packages and selected reference. The
current configuration keeps six passive 17 m cars, five short wayside launch
banks and independent braking. No onboard traction or traction store is added.

The new executable adapters can assess supplied installed equipment, structural
results, force/time brake curves, site geometry/geotechnical inputs and complete
cost records. They calculate values and residuals instead of permanently returning
unknown for every input. Missing, unsupported, failed and authenticated evidence
remain different states. None grants manufacturing or operating release.

## Run

```bash
./osr design railway plan
./osr-complete plan
./osr-complete motor-run --state build/current-motors --max-new-runs 8
./osr-complete assess --output build/current-closure --motor-state build/current-motors
./osr-complete verify build/current-closure
./osr-complete verify build/current-closure --require-complete
./osr-complete publish build/current-closure
./osr-complete verify-publication
./osr-complete motor-publish build/current-motors
./osr-complete motor-verify-publication
./osr-complete variants-publish
./osr-complete variants-verify-publication
```

The motor campaign is bounded, locked and restartable; it preserves interrupted, failed and pending requests. Source and numerical-tool changes create new execution identities. Published motor records can be inspected with recorded-execution integrity checks on another machine; fresh native reuse/replay still requires the exact current numerical toolchain. Recorded integrity does not certify local replay or a usable force map.

The strict command returns exit code 3 while the engineering frontier is open.
`assess --input-root DIR --input-manifest FILE` imports owned, versioned record
files. A trusted calling application may supply the external authentication and
independent numerical replay callbacks plus their context identities. The CLI has
no self-approval switch, imported executable authenticator or local trust anchor.
Without the actual external verifier, signed claims remain held.

## Implemented interfaces

- **Evidence:** current T01–T10 subjects, actual referenced bytes, exact candidate/
  source/article bindings, calibrated channels and typed records/events, complete
  cases/repetitions, pre-approved procedures and guarded limits, derived reviews,
  independent witness, prerequisites, NCRs and execution times. Numerical and
  supplier records do not become measured physical tests.
- **Equipment:** net primitive geometry, source blank/cut reconciliation, complete
  replacement-account mapping, rigid placement, mass intervals, CG/inertia,
  hardware/service flexibility, lifting and conservative swept access. A changed
  physical assembly becomes an explicit revision proposal requiring canonical
  rematerialization and downstream reevaluation; parent results are not inherited.
- **Structures/brakes:** typed load cases, mesh/refinement and uncertainty margins;
  force-driven stopping, wheel-adhesion limits, energy balance and repeated lumped
  brake heat. Material/joint correlation, fade, WSP and safety floors remain open.
- **Civil works:** all counted stationary stock, including the wayside motor,
  enters beam/support reactions and bending diagnostics. Known unlocated span
  accounts have explicit placement hypotheses. Surveyed footing inputs receive
  bearing, sliding and elastic-settlement checks. Actual full substructure,
  torsion, seismic, flood, pile and erection design still require their own work.
- **Economics:** every canonical occurrence and required whole-system scope needs
  traced prices/quantities; disjoint cashflows and design-life/discount assumptions
  produce conditional present costs. Missing installed scope is not free, and no
  protected-service or economic winner is automatically selected.
- **Operating map:** sampled voltage magnitude/current, energy, Cartesian/domain
  coverage, zero-current/off-window behavior, explicit window boundaries, exact
  installed phase/gap/history context and per-component periodic RC duty. Every
  scoped support record must be externally authenticated and independently
  replayed against the exact source/tool/request/output. Four-dimensional map
  claims do not silently cover other frequencies, gaps or transient histories.
- **Journey method:** a separate current derivative preserves the retained
  point-train equations, rejects invalid voltage and reports an initial stall
  without querying negative route positions. It does not invent an initial
  brake-hold/ramp controller, safety curve or usable motor force.

## Actual 20 m motor method

The new, separately source-bound field/circuit kernel supports 40 periods, ten
parallel paths per phase and eight series coils per path. The retained 25-period
method remains unchanged. Native workers have explicit node, memory and runtime
limits; source/tool identities, exact inputs, actual mesh, traces, losses and
discrete power/current residuals are retained, including failures.

Low-voltage zero, forward/reverse phase and moving-entry controls are component
experiments. A small positive at-rest force or numerical convergence does not
establish operating thrust, converter control, finite-height returns, cooling,
section handoff or a train-level operating map. No force is scaled from overlap
or multiplied by the number of cars/banks.

Before a rated field solve, a conditional sinusoidal power screen compares one active bank with the train demand and counted copper loss. The reference 375 V peak/140 A peak envelope is insufficient for the approximately 102 t accounted normal-load GFRP train at 20 m/s and 0.4 m/s². A separate rewound hypothesis counts 45 mm² conductors, deeper slots and thicker backiron, with a 230 A peak ceiling while retaining the 4 A/mm² RMS limit. Its optimistic electrical headroom is a necessary bound only. It adds wayside material and invalidates mounting, civil, converter and cost evidence. The coarse/fine-time moving experiments do not establish a converged operating map.

`variant_design.evaluate()` propagates reference, wider-return and rewound research candidates through inventory, full stock geometry ledger, BOM, station dead loads, braking/motion contexts, civil overlays and disabled procurement/manufacturing drafts. Every changed motor remains a new physical candidate. This does not resize the piers or qualify the new winding.

The [completion campaign](../../../campaigns/engineering-completion.toml) and
[implementation](../../../engineering/railway_completion/) expose these input
contracts. The [project front door](../../../README.md) retains the wider local
manufacturing, planning, delivery, ERPNext/Frappe HR, supervision and controls remit.
[Executed validation](validation.md) records the retained experiment and current closure identities, exact checks and unresolved physical work. This remains an unreleased research/prototype design with an explicit frontier.
