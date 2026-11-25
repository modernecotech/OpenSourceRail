# Baghdad Airport digital project reference

The integration reference is the 17.461 km GIS-profiled Airport study with 6 provisional stops, a 30-minute service, 35 s dwell and six paired supply sites. The protected-conductor case carries six powered-wheel trainsets. This configuration is held for engineering qualification.

| Interface | What reconciles | Evidence still needed |
|---|---|---|
| Route and service | The grade profile, station order and timetable share one alignment. The nominal operating mass is 198.64 t. | Survey the alignment, stop entrances, turnbacks and depot lead. Establish observed demand and dispatch limits. |
| Traction and controls | Moving DC supplies the evaluated timetable. A source-bound Rust ATP replay exercises authority restrictions and the braking comparator. | Confirm approved protection limits, feeder duties, timing, localisation, interlocking, hardware isolation and measured braking. |
| Civil and stations | 1,746 standard placements and 1 separately priced double-track closure. 875 support positions and 6,992 bearings. | Check foundations, single-track loading, thermal effects, temporary deck loads and accessible evacuation. |
| Production and maintenance | Costed lots carry the operating train and civil row IDs. | Reconcile the installed car and complete bogie, supplier assemblies, embedded harnesses, shop routes and upkeep. |
| Finance | Base priced scope is $863.94m capital, $10.34m annual operation and $1,001.18m in priced 30-year present value. | Price the excluded site, utility, owner and funding scope before comparing complete costs. |

## Operating cases

| Case | Trip completion | Minimum live collector voltage |
|---|---:|---:|
| normal | 72 / 72 | 1,492.3 V |
| hot | 72 / 72 | 1,491.7 V |
| site out | 72 / 72 | 1,487.8 V |
| path out | 72 / 72 | 1,491.4 V |
| combined | 72 / 72 | 1,471.2 V |

**Failed functional screens.** aged battery, traction adhesion, one-driven-axle-out required force.

**Open inputs.** returned equipment, battery continuous hot power, battery brake and egress peak duty, protected stopping distance, installed door and suspension clearances.

**Electrical evidence due.** Utility connection, thermal ratings and protective coordination.

Controls, cash and construction geometry each have their own evaluation identity. The horizontal supplier enquiry, 20 m deck-fed construction study and illustrated assembly ledger provide comparison evidence. Transfer of equipment, installed weights or prices requires a matched revision and recalculation.

[GIS and cost study](GIS-SIMULATION.md) · [Candidate and evidence record](project-reference.json) · [Controls replay](../controls/AIRPORT-ATP.md) · [Engineering and release work](../../../../docs/ROADMAP.md)

Reference `8fa8a3ea32f6863600cd6036d525deeb875264f03f043d20cb8a83560313e8aa`.
