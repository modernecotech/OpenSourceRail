# v0.7 digital production handoff

This is the digital quote and build plan for the [selected thirteen-strand
candidate](../selected.toml), physical ID
`osr-v07-joined-civil-518dad57a3af5046f40c8f4f`. The [compiled handoff](handoff.json)
binds the digital vehicle and civil results, 52 manufacturing BOM rows, 23
routing steps, the single cost basis and the 43-month programme. Its parent
vehicle and station assembly definitions retain their original source IDs;
the selected beam revision adds 79.96 kg counted strand per beam and is
included in the BOM, lifting load and price.

| Reconciled planning output | Value |
|---|---:|
| Installed capital, 2026 USD | $1,025.2272m |
| Direct capital | $854.356m |
| One 20% project contingency | $170.8712m |
| Modelled local work within direct capital | $411.9078m |
| Capital scopes | 14 |
| Programme to trial-operation handover | 43 months |
| Powered fleet | 51 six-car sets; 306 cars; 612 door openings |
| 10 m thirteen-strand beams | 6,000, with 24,000 provisional bearings |
| First-car direct assembly allowance | 720 hours/car |

The 52 BOM lines are mapped to one of the 14 capital scopes. The eleven control-electronics items are counted for this candidate: 51 trainsets, 306 cars, 612 door openings and bogies, twelve stations, six grid sites and 22 line sections. Their $15.56m equipment allowance is allocated within the existing vehicle, station, grid and line-control scopes. It is not added to capital a second time. An unpriced child
line remains **included within its parent scope allowance**; it is not a
zero-price procurement item. Seven scopes have a representative assembly route;
the other scopes retain their single priced cost-basis line without a fabricated
part decomposition. Station launch is an explicit zero-quantity exclusion for
this powered-wheel candidate. The 43-month schedule includes survey/design
(months 0–6), supports (6–24), beam production (8–31), erection (15–35),
rail/overhead (26–38), stations/depot/power/controls (29–40), and integration
and trials (40–43). At 16 beams per workday, factory and erection each require
375 working days within their overlapping windows.

The five controls installation routes allow **4,308 direct planning hours**:
3,060 train integration, 192 station, 176 section, 720 route detection and
160 control-room hours. These hours sit inside the parent scope rates. They are
planning inputs for workshop quotations, not measured factory productivity.

The `erpnext_dry_run` section is a candidate-specific preview of Item groups
and proposed document sequence. It makes no live call and is **not an ERPNext
import pack**: the current native adapter requires a sealed 13-hash source
proposal, per-part controlled drawings/inspections/routes, site masters and
independent authenticated review. Those inputs, supplier prices and actual QA
measurements must be supplied before native orders, receipts, installation or
repair records can be created. No synthetic inspection or supplier transaction
is inserted to complete the digital release.

From the repository root:

```bash
python3 docs/reference-v07/digital/production/generate.py --check
```

To regenerate after an intentional source revision, run the same command
without `--check`, inspect the changed cost, candidate and quantity identities,
then commit the updated result. The generator requires only Python's standard
library, executes arithmetic and text checks in under a second, and writes
about 56 KiB. The `--check` output reports the exact current
`handoff.json` SHA-256.
