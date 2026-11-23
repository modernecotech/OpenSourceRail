# Airport traction and station commissioning

The 12 km Airport service puts a demanding load on a restored feeder when one source is unavailable and two trains accelerate. The priced 30-site layout clears its 1.350 kV planning floor by 0.925 V in the published hot-circuit case. A reduction of 0.823 V in the source voltage alone would use that margin. Obtain the utility voltage envelope and hot path measurements before relying on that design. [Priced supply drawing](../../airport-traction-single-line.svg)

## Three procurement scopes

The table uses the 201.092 t planning train, three working trains, their auxiliaries and the other train’s uphill cruising allowance. The combined comparison reduces the no-load source voltage by 1%, increases the **already hot** circuit resistance by 5% and increases total collector load by 5%. These are sensitivity assumptions for the buyer. Each new mass or service evaluation needs its own report.

| Scope | Physical difference | Review decision |
|---|---|---|
| Priced radial | 30 sites, 116 outgoing breakers and 58 ties. Each affected track can receive power from an adjacent healthy source after isolation. | The two-train restored collector falls to 1.3163 kV in the combined case. Retaining the same source and conductor properties would require at least 65 uniformly spaced sites by the voltage inequality, beyond the earlier 64-site replay range. |
| Original station-sited quotation | Six regulated source groups at the stops, 20 outgoing breakers and ten ties. The original enquiry assumes reduced source droop and lower positive and return resistance. | The original hot case gives 1.3550 kV. Request hardware, losses, bids and the combined-case limits before a selection. |
| Paired station-sited quotation | Six station sources. Each outgoing breaker feeds two parallel positive branches within its existing insulated zone. Provide two return branches in the same electrical zone. Budget 48 positive and 48 return path-km, 40 positive branch disconnect points and 40 return branch test points. | The combined case gives 1.3689 kV with one site out. With one whole path pair unavailable as well it gives 1.3093 kV. Develop the degraded-service restriction and verify isolation. The installed price remains open. |

For the paired design, quote each rectifier and transformer against a 5 mΩ nominal maximum effective source droop. The original 10% hot allowance still applies to the source and each longitudinal path. Budget a further 1 mΩ for common contacts and joints. The combined study requests 9.383 kA peak and 14.075 MW DC at nominal voltage per site. The worst scheduled RMS upper bound is 3.971 kA across the service window. A one-branch thermal enquiry takes the full peak and RMS until measurements establish current sharing.

Two branches, each within the specified resistance bound, give at most half that bound in parallel. Show the taps, rail bonds, common bus and shoe contact that realise this circuit along the entire route. An unmodelled shared section consumes the common resistance allowance. Provide a site-specific, accessible arrangement for isolation, earthing, testing and preventing backfeed across both tracks. The diagram represents the electrical requirement for a quotation. Owners must review the actual switching design and access arrangements.

## Returning supplier data

Run these commands from the full repository with the opening’s exported `opening.json`. Relative filenames below refer to the reviewer's working directory. Keep each generated form’s opening, feeder, equipment scope and topology identity intact.

```sh
python3 -m cities.Baghdad.engineering.commissioning.feeder opening.json --form priced_radial > radial-return.json
python3 -m cities.Baghdad.engineering.commissioning.feeder opening.json --form six_site_parallel > paired-return.json
python3 -m cities.Baghdad.engineering.commissioning.feeder opening.json --return-file paired-return.json
python3 -m cities.Baghdad.engineering.commissioning.feeder opening.json --compare radial-return.json paired-return.json
```

Select `six_site_quotation` for the original single-path station design. Record the supplier’s document revision and exactly which sites, zones, fault types and normal/restored configurations it covers. Enter the lowest unloaded source voltage, upper hot source droop, **effective** hot positive/return resistance per kilometre for the whole circuit, additional common contact resistance, and total collector demand. Use effective equivalent values for the paired paths. The calculator keeps the two-train duty as the minimum return scope. Unknown quantities stay null.

Obtain prospective interruption and sustained remote-fault bounds from a separate DC fault study. Include the utility, transformers, rectifiers and their current limits, cable inductance, return circuits, vehicle and adjacent-source contributions, and the lowest relevant arcing fault. A traction load-regulation slope cannot establish a short-circuit current. The elementary coordination check covers an overcurrent zone for which the declared primary and backup current bands represent the same fault. Supply additional directional or differential studies for current splits, reverse feeds and high-impedance faults.

The protection return checks healthy load against minimum pickup, remote fault against maximum pickup, prospective duty against the DC interruption rating, recovery voltage, circuit time constant and consecutive current bands. In each band the upper primary clearing time plus the required margin must precede the earliest backup trip. Cable endurance must cover conservative current squared multiplied by primary or backup clearing time. Instrument-transformer uncertainty, current measurement saturation and equipment timing tolerances belong in the returned bounds. A pass refers only to the declared envelopes. Full fault isolation, touch voltage, stray current, regeneration overvoltage and accessible egress need separate evidence.

Price **both** matched scopes in constant 2026 USD. Include the grid connection and structural work per site, positive and return conductors and bonding, zone breakers and ties, controls, earthing, installation and commissioning. Enter yearly upkeep and 30 years of timed replacement costs. An explicitly empty renewal map represents a supplier assertion of no renewals in that period. The comparison reports differences in direct price, upkeep and 30-year present value at 4% real. Property acquisition, tax, financing and shared project overhead require buyer reconciliation outside the returned scopes.

## Recording a hot path

Use a passive recording from an authorised test. Keep the raw CSV, signed test method, site diagram, calibration certificates, sampling window and witness records together. Record both source current and branch current. Measure the DC bus and collector with consistent positive/return reference pairs. Identify the instrumented chainage, track and adjacent failed site. Confirm the load is steady, the measured temperature represents the critical conductors and bonds, the current distribution and topology stay as recorded, and the voltage drift allowance covers changes between windows.

```sh
python3 -m cities.Baghdad.engineering.commissioning.measurements opening.json --template six_site_parallel > hot-path.json
python3 -m cities.Baghdad.engineering.commissioning.measurements opening.json --record hot-path.json --csv logger.csv
```

The CSV header is `time_s,window,source_ka,branch_ka,bus_kv,collector_kv,conductor_c`. Record at least two ordered samples marked `low`, followed by at least two marked `high`. Supply the raw file’s SHA-256 and absolute instrument errors. The evaluator bounds the two-point source slope from the difference between bus voltages divided by the current step. It bounds bus-to-shoe loop resistance in the high window from the observed voltage difference and branch current. It reports the actual temperature, power and voltage coverage. A single recorded circuit does not establish all-site performance. Cross-check each relevant source, return path, loading configuration and temperature range.

## Station controls and hardware

1. Extract the opening JSON, run the candidate-bound Rust station replay, and trace the door, independent brake, inverter and position signals to real logger inputs. Record equipment serials, wiring revision, timestamps, approved limits, firmware digest, clock accuracy and which of the 48 door slots are simulated. Use both travel directions. [Bench procedure and six physical trial descriptions](../controls/STATION-BENCH.md)
2. Generate the capture form for the chosen test. Map each named measurement to an independent recorder pin. Supply a synchronous wide CSV with `time_ms` and exactly one column per mapped pin. Use the declared bits, kN, mm and ms. The converter preserves raw-file and mapping identities and rejects repeated pins, reversed timestamps or invalid discrete states.
3. For the ordinary handover, place the converted output in `raw.json`. Use the existing bench intake for the matching calibration, limits, witness files and independently verified attestations. Fault captures instead report the observed stimulus, protection timing, lost holds, motion and unexpected opening under the supplied limits. Keep them beside the signed witness and stimulus files for the same visit. [Handover validation and provenance](../controls/README.md#review-a-recorded-brake-handover)

```sh
python3 -m cities.Baghdad.engineering.commissioning.recorder opening.json --template handover > capture-form.json
python3 -m cities.Baghdad.engineering.commissioning.recorder opening.json --form capture-form.json --csv visit.csv > raw.json
python3 -m cities.Baghdad.engineering.commissioning.recorder opening.json --form capture-form.json --csv visit.csv --bench-manifest manifest.json
```

The fault modes are `brake_feedback_loss`, `wrong_side_request`, `stale_command`, `power_restart`, `evacuation_blocked` and `evacuation_authorised`. For these specific trials, start at a securely held berth with the test exits closed. Use a separate stimulus indication and record the physical condition on its dedicated channel. Observe the selected and opposite door, effort, brake request, actual holding force, displacement and dispatch throughout the hold period. The restart trial covers a held reset key through restoration and a changed boot epoch. The egress trial distinguishes an authorised nominated exit from the opposite or blocked exit. Brake-loss trials with doors already open, in-motion interventions, manual evacuation and the complete post-fault return to service require the additional physical trials in the bench procedure.

The software can screen synthetic recordings and instrument files. A physical readiness decision requires independent correlation of the retained bytes, identities, approved limits, environmental coverage and witness signatures. Equipment release and operating authorisation belong to the qualification workflow.

### Trace a station visit from software to the rig

Run the Rust program against the exact opening export used by the logger. It checks the six-car opening and its controller inventory against the parent configuration. Its supervisor calls the ATP, TCMS and door crates. It exercises approach, two lock observations, load take-up, departure and fault latching in both directions. The program supplies feedback in memory. The importer separately reads recorder bytes. Neither program streams commands to a physical controller.

| Rig question | What to record and cross-check |
|---|---|
| Which vehicle and opening responded? | Fill the version 2 capture form with station, train, arrival, controller boot ID, recorder serial, direction sign, platform side and physical door slot. Use zero-based slots. Within each car slots 0–3 face left and 4–7 face right in the installed orientation. Add eight for each successive car. Map each pin to its source device serial and terminal or decoded bus field. Identify simulated openings and their feedback source in the wiring record. The signed wiring and witness record must confirm the physical orientation and addresses. |
| Did a stale packet actually arrive? | Capture the last fresh packet and the injected stale packet in consecutive samples around the stimulus. Record each packet-receipt strobe, reported age and sender timestamp aligned to the recorder clock. The checker recomputes the age and requires the timing error bounds to resolve both sides of the approved threshold. Use a separate silence trial for the local watchdog. The Rust replay's 250 ms message age and 500 ms load-transfer budget are laboratory inputs. |
| Did the equipment latch an emergency? | Measure the separate emergency-brake output on every powered fault test, in addition to drive inhibition, independent brake demand, actual force, torque and position. In evacuation trials record the local handle contact, path proof for the nominated opening and whether any other same-side exit opened. Prove the coverage of each aggregate exit channel against the installed lock circuits. For a blocked exit, keep its motor and contact under observation. |
| Did the train stay secure through restart? | Retain independent force, torque and position instrumentation through the blackout. Enter the pre-interruption counter as a decimal string in the visit’s controller boot ID. On restoration, verify the changed boot ID stays stable, the held reset key cannot dispatch, the emergency demand remains and the supply stays up throughout the required post-restoration window. |
| What evidence remains? | Use a packet trace and authenticated device inventory to establish address, boot and sequence authenticity, old-boot replay rejection, watchdog silence, reset-key release and fresh rearming. Measure arrival deceleration, feedback loss during open-door boarding, evacuation during loss of power and recovery to a fresh station cycle separately. The elementary CSV screens cover only the named stimuli and recorded time windows. |

The version 2 handover form binds direction to the bench manifest. The raw measurement record carries the capture-form digest. Retain the filled form and original CSV with the witness, calibration and limit documents so a reviewer can reproduce the mapping. Earlier version 1 fault captures can still be replayed. Their reports flag missing visit, terminal and emergency-output evidence.
