# Finite moving LIM component method

Actual bounded component calculations with a translating finite aluminium secondary and voltage-coupled winding currents. **No available operating map, qualified launch, complete journey or physical release.** The selected v0.6 reference is unchanged.

The P1 research parent is `70eb0ba82c796bc3ec3c52dbdb1c64db15b0d337c64a021f5a5ed3956a28fdc5`; its exact motor geometry is `be98f644c7c5117cb0423970c02501f234c3488689db8b0d017ef34dc6718dc5`. A declared, unverified wiring hypothesis adds 30 separately solved paths, five coils per path and a floating neutral. No result is transferred to a different motor, vehicle or installed wiring arrangement.

[Immutable input/output/log and evaluator-source archive](native-runs.tar.gz) · [Assessment](assessment.json) · [Publication receipt](manifest.json)

| Case | Execution | Mesh nodes | Final force, N | Archived source |
|---|---|---:|---:|---|
| entry-coarse | completed | 33368 | -0.01665120 | source-epoch-1 |
| entry-final-coarse | completed | 33368 | -0.01665120 | source-epoch-2 |
| entry-time-half | completed | 33368 | -0.01862530 | source-epoch-2 |
| entry-mesh-refined | completed | 60645 | -0.01767768 | source-epoch-2 |
| highspeed-domain-control | held | — | — | source-epoch-2 |

Final force changes 11.86% when the time step is halved and 6.16% under the tested 2D mesh refinement. Convergence is **not established**. The 20 m/s request retains its Peclet-domain hold. The 2 V, 0.5 m/s startup samples are not operating thrust or an insufficient-thrust verdict for the reference railway.

Six attempts comprise five sealed worker packages and one interactive zero-field smoke. The smoke lacked an exact saved source epoch; it is retained explicitly as unqualified and does not satisfy the source-bound zero-excitation obligation. Native runs retain their original source epochs. Current validation/verifier changes are bound separately by this publication; the old runs are never resealed as executions of current code.

## Method and independent controls

The fixed mesh conforms to the exact 12.5 m primary, teeth, slots and 15 mm gaps. The 9 m aluminium rectangle translates through it. Exact degree-two triangle/polygon moments update conductor mass, transport and floating-current operators at each position; forces are integrated from current and field, without overlap multiplication.

The coupled equations are `K(A)+M(x) A_dot+C(x,v) A+b(x)u=W I`, floating secondary-current closure, and `R I+height W^T A_dot+neutral=voltage`, with `sum(I)=0`. Here `Jz=-sigma(A_dot+u+v A_x)` and `Fx=integral(Jz A_x) dV`. Terminal work balances copper loss, secondary Joule loss, mechanical work, stored magnetic energy and explicit backward-Euler numerical dissipation. Tiny residuals establish the discrete accounting only.

The A/u and stranded-circuit formulation follows the class documented in the [official GetDP magnetodynamics/circuit template](https://github.com/getdp-project/getdp/blob/master/templates/Lib_Magnetodynamics2D_av_Cir.pro). The translating cut-cell integration is implemented separately. Focused tests independently integrate manufactured polynomials, check closed winding turns and compare the actual coupled Jacobian against the closed-form RL response and its energy balance. An independent same-geometry field benchmark remains open.

## Remaining obligations

The steel law is a generic reversible numerical hypothesis; hysteresis/core loss, finite-height current return, end-turn leakage, physical winding grouping, converter switching/loss, protection, hardware current control and supplier correlation remain unresolved. Temperatures, cooling, repeated duty and complete installed equipment/mass/cost remain unknown. There is no coupled train-motion model in this component packet.

Next work requires a source-qualified zero control, further mesh/time/outer-boundary refinement, independent linear field/circuit and reversal benchmarks, a validated high-speed transport discretization, supplier magnetic/loss data, actual winding/inverter/protection definitions and authenticated measurements. Physical requirements stay open.
