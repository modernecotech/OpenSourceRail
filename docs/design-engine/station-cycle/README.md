# Stateful station capture and relaunch

[Open the comparison](index.html) · [Original station-pair methods](../station-pair/README.md)

**Calculated research experiment.** Both station stores begin empty. Actual
braking work within five capture stages charges the receiving store; only a
later authorized departure from that station can use it. Capture/release losses,
leakage, finite force/power/window limits, locks, reset costs and failures are
explicit. Full or failed capture bypasses to the existing independent brakes
under an **ideal coordinated blending assumption**, without increasing their
total capability. Real spring force–stroke and hydraulic pressure–flow remain
unverified. Recovered force replaces part of the requested grid-driven launch;
it does not invent additional motor ratings or a successful journey.

## Same route, explicit hardware, retained failures

All designs use the 1.5 km two-station double-track pilot and exact 605-type body
catalogue. New vehicle-interface reserves add 300/600/1,200 kg per train, with
separate cost lines. Spring/accumulator bank mass is calculated from the declared
material/gas-work hypotheses; housing, transmissions, supports, guards, controls
and installation remain positive reserves. Hardware revisions get new candidate
IDs; faults and control hypotheses remain separate evaluations.

Eight nominal alternating movements carry the actual reversed stopping offset,
station energies and clocks. The single point-train departs every 260 s, hence
**520 s per direction**. This demonstrates only a serial storage-cycle model.
It does **not** establish the requested 200 s concurrent four-train service,
platform/crossover conflicts, real turnback or thermal duty. A restricted serial
model is not proof that the physical architecture cannot meet that service.
Complete annual energy and lifecycle NPV remain unknown; known account subtotals
are published. No city is repriced and propulsion remains unselected.

| Design / experiment | Berths | Captured kWh | Relaunched kWh | Grid traction kWh | Max moving jerk m/s³ | Expanded pilot base CAPEX |
|---|---:|---:|---:|---:|---:|---:|
| Cable / 6 motors / 350 m / nominal | 1/8 | 0.000 | 0.000 | 9.296 | 0.468 | $26.047m |
| Powered wheels / 12 driven axles / nominal | 8/8 | 0.000 | 0.000 | 53.050 | 0.318 | $28.491m |
| Cable 350 m + steel 4 MJ / nominal | 0/8 | 1.055 | 0.000 | 4.671 | 0.368 | $27.755m |
| Cable 350 m + steel 4 MJ / recovery-disabled | 0/8 | 0.000 | 0.000 | 4.671 | 0.368 | $27.755m |
| Cable 350 m + steel 8 MJ / nominal | 0/8 | 1.055 | 0.000 | 4.671 | 0.368 | $28.221m |
| Cable 350 m + steel 8 MJ / recovery-disabled | 0/8 | 0.000 | 0.000 | 4.671 | 0.368 | $28.221m |
| Cable 350 m + hydraulic 4 MJ / nominal | 0/8 | 1.055 | 0.000 | 4.671 | 0.368 | $27.632m |
| Cable 350 m + hydraulic 4 MJ / recovery-disabled | 0/8 | 0.000 | 0.000 | 4.671 | 0.368 | $27.632m |
| Cable 350 m + hydraulic 8 MJ / nominal | 0/8 | 1.055 | 0.000 | 4.671 | 0.368 | $27.674m |
| Cable 350 m + hydraulic 8 MJ / recovery-disabled | 0/8 | 0.000 | 0.000 | 4.671 | 0.368 | $27.674m |
| Powered wheel 12 axles + steel 4 MJ / nominal | 8/8 | 9.269 | 6.569 | 46.023 | 9.931 | $30.199m |
| Powered wheel 12 axles + steel 4 MJ / recovery-disabled | 8/8 | 0.000 | 0.000 | 53.225 | 2.873 | $30.199m |
| Powered wheel 12 axles + steel 8 MJ / nominal | 8/8 | 9.269 | 6.569 | 46.023 | 9.931 | $30.665m |
| Powered wheel 12 axles + steel 8 MJ / recovery-disabled | 8/8 | 0.000 | 0.000 | 53.225 | 2.873 | $30.665m |
| Powered wheel 12 axles + hydraulic 4 MJ / nominal | 8/8 | 9.271 | 5.852 | 46.809 | 10.522 | $30.076m |
| Powered wheel 12 axles + hydraulic 4 MJ / recovery-disabled | 8/8 | 0.000 | 0.000 | 53.225 | 2.873 | $30.076m |
| Powered wheel 12 axles + hydraulic 8 MJ / nominal | 8/8 | 9.271 | 5.852 | 46.809 | 10.522 | $30.118m |
| Powered wheel 12 axles + hydraulic 8 MJ / recovery-disabled | 8/8 | 0.000 | 0.000 | 53.225 | 2.873 | $30.118m |

Arrival alone is not an advisory-screen pass: the 0.5 m/s³ moving-jerk target,
journey time and uncertainty domain remain separate checks. The
[requirement context](requirement-assessments.json) retains mandatory physical
obligations as open. The summary's next-experiment Pareto set uses nominal serial
cost/energy/jerk only, never fault outcomes or an automatic baseline selection.

These energy totals cover the modeled sequence, not annual savings. Grid traction
is separate from module reset, auxiliary charging and ordinary cable return.
Retained energy at the end is not delivered propulsion. Initially-full sensitivity
cases explicitly debit their initial energy; it is never called regeneration.
All common eighteen fault/environment recipes are retained for every physical
design. Recovery designs also test failed capture/release/reset, delayed reset,
leakage, transfer-power sensitivity, initial storage and authorization refusal.

## One fourteen-scope cost ledger

Original pilot accounts are assigned once. Active/reserve fleet are partitions,
not duplicate train purchases. Extra module material/process and equipment rows
carry the same candidate ID. Land/utilities, rescue, reliability, omitted station/
depot maintenance, component renewals with parent-age resets and disposal have
explicit scenarios. Financing, taxes, customs and FX remain separate excluded
project-finance layers. Low/base/high are assumptions, not quotations or confidence
quantiles. A missing or unsupported service-energy result is unknown, not zero.

The [disabled delivery draft](delivery-draft.json.gz) identifies material reserves,
assembly steps, prototype tests and all fourteen cost scopes. It is not a controlled
drawing package, purchase order, manufacture authorization or safety approval.

## Reproduce

```bash
./osr design station-cycle plan
./osr design station-cycle run --output /path/to/private/cycle-run
./osr design station-cycle publish --run /path/to/private/cycle-run --output /path/to/fresh/publication
./osr design station-cycle verify
./osr design station-cycle verify --replay --state /path/to/private/cycle-replay
./osr design station-cycle history-verify
```

The [prior feedback packet](../../archives/station-pair-feedback-20261107/README.md)
is preserved at its exact Git/source epoch. Verification reconstructs current
requests, physical identities, costs and generated files. Native replay rebuilds
the pinned Rust protocol under CPU/address-space/wall limits, retaining failures.
Source read-only instructions are not an OS sandbox.

Study `d97736a7b649eff8a8f4e0a36946840fa8b89cc7450d8965186a9a25b21b6314`. Outline experiment and accounting records are complete
under assumptions. Installed design, concurrent service, measured mechanisms,
physical acceptance and manufacturing/operating release remain open.
