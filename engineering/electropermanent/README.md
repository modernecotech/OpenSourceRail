# Electropermanent next experiments

This package counts three onboard NdFeB/AlNiCo EPM coupons paired with the
retained eight-segment N35UH Halbach module. It executes DC RL and capacitor RLC
pulse calculations and explicit parallel-branch magnetic-circuit diagnostics.
The guideway remains ordinary concrete and passive steel. No guideway PM or
powered suspension is introduced.

The generated packet separates electrical execution, conditional circuit
screens, magnetic switching/retention and physical acceptance. The last two
remain unqualified. A fixed imposed AlNiCo `Br` state is not a hysteretic
switching solution; no such field model is silently substituted here.

```bash
python -m engineering.electropermanent plan --source-root /path/to/OpenSourceRail
python -m engineering.electropermanent run --source-root /path/to/OpenSourceRail --output build/epm-review
python -m engineering.electropermanent verify --source-root /path/to/OpenSourceRail --output build/epm-review
```

After review, `publish` uses the same immutable generator with an explicit fresh
destination, proposed `docs/design-engine/electropermanent/`. Existing packets
are not overwritten. Verification reconstructs results and plot bytes, so merely
resealing a changed archive does not make it valid. `--source-root` locates
retained inputs; executing implementation bytes are bound separately.

APIs:

- `catalogue.candidates(root)` returns three exact stock/material bundles;
  `catalogue.validate(value,root)` refuses even rehashed unsupported changes.
- `pulse.rl_pulse(R_ohm,L_H,V_V,duration_s)` and
  `pulse.rlc_pulse(R_ohm,L_H,C_F,V0_V,duration_s)` return exact linear states and
  independently integrated electrical/resistive energy balances.
- `pulse.coupled_loadline(...)` reports the signed common magnetic field and
  required AlNiCo branch flux for a **prescribed** gap field.
- `pulse.energized_parallel_circuit(...)` includes the two air-gap MMF demands
  and hard-NdFeB bias for **prescribed** AlNiCo/H states in either pulse direction.
- `study.study(root)` returns full candidates, pulse cases, load-line cases,
  current-demand sensitivities, counts and a bench-identification contract.
- `publication.run/verify/publish(output,root)` generate or reconstruct packets.

The common coil encloses equal-length parallel hard/soft bars. Steel endcaps and
two pole legs close through a passive facing. Every straight copper leg, PM bar,
yoke and facing-extension box has dimensions, position, material, mass, CG and
inertia. Layer/turn counts, conductor area, fill, capacitor energy and reference
24-module packing are explicit. Unknown capacitor/driver/selector/protection,
retention and insulation masses never become zero. The contact coupon is a
stationary experiment: moving clearance/retraction remains unsized, and its
reference-car multiplication is not an installation proposal.

The final rail-family recipes use 40 mm endcaps/poles and 380 turns. The original
10 mm bridge needed an implausible 4.68 T under the ideal internal-shunt hypothesis;
the wider counted bridge reduces that necessary density to 1.17 T. A bounded V/C
screen retains lower-voltage underpowered controls and Pareto alternatives.
The chosen electrical test spec is 144 V / 50 mF for rail coupons and 48 V / 50 mF for the
contact coupon. These are unqualified requirements for unknown capacitor/driver
hardware, not supplier equipment or complete installed quantities.

Pooled 24-module programming must reset the capacitor between pulses. The
reported 1 kW / 90% charger timing is a declared arithmetic scenario. The selector
cannot advance until coil current reaches zero and the clamp/recovery finishes;
that additional time is unknown. Residual inductor energy at 20 ms is reported,
and neither full-cycle heat nor permanent-state programming is inferred from
the truncated linear pulse.

The wider rail coupons still **fail the zero-current positive-AlNiCo-branch
necessary bound** in the stated no-leakage circuit. The Nd branch alone requires
gap B ≈ 0.184 T, while staying above the normal-Hc reference permits at most ≈ 0.134 T.
Reopening this optimistic interval needs pole area ≈ 0.00661 m² or magnet
length ≈ 0.0689 m, before any hysteresis or force qualification. Leakage/3D paths
can change this circuit and its useful external field; no physical
irreversibility result or retained rail-bias performance is claimed.

The reference material is **EA cast Alnico 5** (typical Br = 1.25 T, normal Hc = 51 kA/m,
table-reported Hci = 51 kA/m, density 7300 kg/m³), distinct from sintered material.
The normal coercivity is not an irreversible knee or a complete magnetizing
requirement. [Arnold's magnetization guidance](https://www.arnoldmagnetics.com/products/alnico-magnets/)
gives 240 kA/m for Alnico 5; fixturing and eddy shielding can alter pulse needs.
NdFeB retains the existing named Arnold N35UH grade/source and declared 1.05
recoil assumption; no material property is renamed or certified.

[Knaian's thesis](https://cba.mit.edu/docs/theses/10.06.knaian.pdf), figures 3-1/3-2
and equations 3.1–3.25, motivate the explicit parallel circuit and electrical
screen. Its materials and small-device force measurements are not transferred.
[Pechhacker et al.](https://doi.org/10.1016/j.ifacol.2023.10.180) identify a laboratory
EPM's hysteresis and retain separate fast Lorentz stabilization; their 19 N/s
force-tuning result is not a rail actuator rate. Primary links and inspected PDF
digests are in [data/provenance.json](data/provenance.json); full copyrighted
papers are not distributed.

The first follow-up is an instrumented protected coupon: identify R/L and
positive/negative flux minor loops at 0.2, 1 and 12 mm gaps, record actual ∫VI and∫I²R,
retained flux, hard-magnet remanence and repeated thermal duty. EPMs may offer
slow load/bias trim; active fast suspension remains necessary. A station latch,
cassette latch, mechanical parking/capture system and door lock each require
their own load, wear, release and qualification evidence.
