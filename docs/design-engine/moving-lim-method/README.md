# Finite moving LIM component method

Actual bounded component calculations with a translating finite aluminium secondary and voltage-coupled winding currents. **No available operating map, qualified launch, complete journey or physical release.** The selected v0.6 reference is unchanged.

The P1 research parent is `70eb0ba82c796bc3ec3c52dbdb1c64db15b0d337c64a021f5a5ed3956a28fdc5`; its exact motor geometry is `be98f644c7c5117cb0423970c02501f234c3488689db8b0d017ef34dc6718dc5`. A declared, unverified wiring hypothesis adds 30 separately solved paths, five coils per path and a floating neutral. No result is transferred to a different motor, vehicle or installed wiring arrangement.

[Immutable input/output/log and evaluator-source archive](native-runs.tar.gz) · [Assessment](assessment.json) · [Publication receipt](manifest.json)

| Case | Execution | Mesh nodes | Last force, N | Last time, s | Archived source |
|---|---|---:|---:|---:|---|
| entry-coarse | completed | 33368 | -0.01665120 | 0.0160 | source-epoch-1 |
| entry-final-coarse | completed | 33368 | -0.01665120 | 0.0160 | source-epoch-2 |
| entry-time-half | completed | 33368 | -0.01862530 | 0.0160 | source-epoch-2 |
| entry-mesh-refined | completed | 60645 | -0.01767768 | 0.0160 | source-epoch-2 |
| highspeed-domain-control | held | — | — | — | source-epoch-2 |
| low-dt-1ms | completed | 33368 | -0.01862530 | 0.0160 | source-epoch-3 |
| low-dt-half | completed | 33368 | -0.01956088 | 0.0160 | source-epoch-3 |
| low-mesh-30mm | completed | 60645 | -0.02067058 | 0.0160 | source-epoch-3 |
| low-mesh-25mm | interrupted | — | -0.02254387 | 0.0135 | source-epoch-3 |
| high-supg-dt-2ms | completed | 33368 | -0.04085596 | 0.0160 | source-epoch-3 |
| high-supg-dt-1ms | completed | 33368 | -0.04049922 | 0.0160 | source-epoch-3 |
| high-supg-mesh-30mm | completed | 60645 | -0.03828821 | 0.0160 | source-epoch-4 |
| high-supg-mesh-25mm | completed | 70929 | -0.03812261 | 0.0160 | source-epoch-4 |
| zero-medium | completed | 22545 | -0.00000000 | 0.0160 | source-epoch-5 |
| motoring-coarse | completed | 14124 | -0.00259630 | 0.0160 | source-epoch-5 |
| motoring-x-refined | completed | 16533 | -0.00257470 | 0.0160 | source-epoch-5 |
| motoring-y-refined | completed | 19260 | -0.00256501 | 0.0160 | source-epoch-5 |
| motoring-medium | completed | 22545 | -0.00253956 | 0.0160 | source-epoch-5 |
| motoring-fine | completed | 44643 | -0.00241864 | 0.0160 | source-epoch-5 |
| motoring-fine-dt-half | completed | 44643 | -0.00352017 | 0.0160 | source-epoch-5 |
| motoring-fine-dt-quarter | completed | 44643 | -0.00420732 | 0.0160 | source-epoch-5 |

The initial final-force comparison changes 11.86% when the time step is halved and 6.16% under the tested 2D mesh refinement. Convergence is **not established**. The original unstabilized 20 m/s request retains its Peclet-domain hold. The 2 V, 0.5 m/s startup samples are not operating thrust or an insufficient-thrust verdict for the reference railway.

The initial six attempts comprise five sealed worker packages and one interactive zero-field smoke. The smoke lacked an exact saved source epoch; it is retained explicitly as unqualified and does not satisfy the source-bound zero-excitation obligation. Native runs retain their original source epochs. Current validation/verifier changes are bound separately by this publication; the old runs are never resealed as executions of current code.

## Method and independent controls

The fixed mesh conforms to the exact 12.5 m primary, teeth, slots and 15 mm gaps. The 9 m aluminium rectangle translates through it. Exact degree-two triangle/polygon moments update conductor mass, transport and floating-current operators at each position; forces are integrated from current and field, without overlap multiplication.

The coupled equations are `K(A)+M(x) A_dot+C(x,v) A+b(x)u=W I`, floating secondary-current closure, and `R I+height W^T A_dot+neutral=voltage`, with `sum(I)=0`. Here `Jz=-sigma(A_dot+u+v A_x)` and `Fx=integral(Jz A_x) dV`. Terminal work balances copper loss, secondary Joule loss, mechanical work, stored magnetic energy and explicit backward-Euler numerical dissipation. Tiny residuals establish the discrete accounting only.

The A/u and stranded-circuit formulation follows the class documented in the [official GetDP magnetodynamics/circuit template](https://github.com/getdp-project/getdp/blob/master/templates/Lib_Magnetodynamics2D_av_Cir.pro). The translating cut-cell integration is implemented separately. Focused tests independently integrate manufactured polynomials, check closed winding turns and compare the actual coupled Jacobian against the closed-form RL response and its energy balance. An independent same-geometry field benchmark remains open.

## Remaining obligations

The steel law is a generic reversible numerical hypothesis; hysteresis/core loss, finite-height current return, end-turn leakage, physical winding grouping, converter switching/loss, protection, hardware current control and supplier correlation remain unresolved. Temperatures, cooling, repeated duty and complete installed equipment/mass/cost remain unknown. There is no coupled train-motion model in this component packet.

Remaining work includes further mesh/time/outer-boundary refinement, independent linear field/circuit and reversal benchmarks, a validated high-speed transport discretization, supplier magnetic/loss data, actual winding/inverter/protection definitions and authenticated measurements. Any source-qualified zero control is identified by its own component execution below. Physical requirements stay open.

## Continued numerical transport experiment

Six additional source-qualified component executions retain a separate 75,000-node, 2 GiB, 90 s request budget. Galerkin keeps its original Peclet domain gate. A distinct residual-SUPG evaluation weights time, transport and floating-potential terms; its **signed numerical work is separate from physical Joule heat**. Closed-form scalar layers and manufactured transient/energy controls check the discretization; full motor and physical validation remain open.

Further low-speed timestep change: 5.02%. Mesh changes 40→30 mm: 5.67%; 30→25 mm: held. High-speed SUPG timestep change: 0.87%. These target sizes do not imply uniform or asymptotic refinement; actual nodes and cells are indexed above. There is no converged operating force map.

The 30 Hz/0.5 m wavelength hypothesis gives a 15 m/s travelling wave. Its 20 m/s samples are negative-slip startup method cases, not a positive-thrust operating point. Partial interrupted traces retain their own times and are never compared with a completed final-time force.

The original five packages and both source epochs are unchanged. The new cross-sectional secondary-current diagnostic uses amperes; the historical trace multiplied it by active height and therefore had A·m units. That diagnostic defect does not alter its stored force/loss solution. The continuation retains the original orchestration plan plus an explicit correction of its mistyped base revision; exact numerical producer snapshots and worker inputs remain authoritative.

SUPG reference: [Brooks, 1981, §§2.4 and3.2–3.3](https://thesis.caltech.edu/430/4/brooks_an_1981.pdf). Signed stabilization work is indexed against physical secondary Joule energy; its magnitude is approximately9–16% of that energy in these high-speed startup cases. Small accounting residuals do not remove this numerical contribution. The stabilized component evaluations do not establish high-speed spatial convergence, finite-height return currents, supplier properties, thermal duty or protected service.

A separate two-job spatial request retains its own source epoch and resource budget. High-speed mesh changes 40→30 mm: 5.46%; 30→25 mm: 0.43%. These comparisons do not qualify the field model or operating motor.

The 30 mm and25 mm target meshes have the same engaged-primary longitudinal cuts and secondary transverse layers. Their small force difference tests other steel/air/exterior refinement; it does not demonstrate convergence of the engaged force grid. Exact mesh diagnostics are retained in the continuation context.

## Independent active-region refinement

Six further source-qualified 20 m/s, 50 Hz component cases use an explicit entry-window mesh family. Actual engaged streamwise cells refine20→10→5 mm, independently of secondary transverse layers4→8→16. Far-region construction rules remain fixed; global inner-fin/gap y refinement also changes remote elements. The physical motor and vehicle identity are unchanged.

The zero-voltage control returned exact zero currents, forces and energies: **True**. Coarse→x-only final-force/impulse changes are 0.83%/7.93%; coarse→y-only 1.21%/0.95%; medium→fine 4.76%/3.23%.

**Every nonzero startup trace still has negative thrust despite nominal positive10Hz slip. This remains unresolved and cannot be relabelled propulsive.** The 16 ms zero-initial-state, finite-entry sample is not a settled full-overlap operating map. Matched independent field/circuit, measured branch phase, reversal, blocked/full-overlap, warm-start and actual current-controller checks are required. Fine-grid motion crosses about four to five active cells per timestep, so temporal and whole-domain refinement also remain open.

The archive also retains independent imposed travelling-wave sign/unit/energy controls and a separately labelled scalar cold-start example. The periodic controls validate the algebraic sign convention; the scalar example shows that nominal positive slip alone does not guarantee positive transient force. Neither diagnoses the actual finite-element negatives nor supplies a motor map. Analytical synchronous/oversynchronous controls beyond20m/s are not actual candidate solver executions.

## Fixed-fine-mesh timestep controls

Two additional bounded runs keep the exact 44,643-node assembled mesh, physical component, source and recorded tool identities. Only timestep and step count change: 1 ms/16 steps, 0.5 ms/32 steps and 0.25 ms/64 steps all end at 16 ms. Recorded Python, NumPy-core and SuperLU hashes and versions match; the earlier archive did not record a complete dynamic-library closure.

Final-force/impulse changes are 45.54%/27.33% for 1→0.5 ms and 19.52%/14.59% for 0.5→0.25 ms. **Time convergence remains open.** All completed startup-force samples remain negative: True.

Backward-Euler numerical dissipation remains separate from physical secondary Joule heat. Signed SUPG work can change sign under refinement and is also retained separately. Accounting residuals do not bound discretization error. Further time, remote-field and independent matched field/circuit controls are required before any operating map can be admitted.
