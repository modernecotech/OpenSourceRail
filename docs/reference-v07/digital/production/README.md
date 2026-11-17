# v0.7 digital production handoff

This is the controlled digital quote/build plan for joined candidate
`osr-v07-joined-prototype-20261117`, interface evaluation
`osr-v07-interface-reconciliation-20261117`, and quotation selection
`osr-v07-prototype-quotation-20261117`. The [compiled handoff](handoff.json)
binds the exact source bytes of the candidate, 41 manufacturing BOM rows, 18
routing steps, cost basis, and programme. It is a design release record; it
does not state that physical assemblies were made or accepted.

| Reconciled planning output | Value |
|---|---:|
| Installed capital, 2026 USD | $1,023.4992m |
| Direct capital | $852.916m |
| One 20% project contingency | $170.5832m |
| Modelled local work within direct capital | $410.8278m |
| Capital scopes | 14 |
| Programme to trial-operation handover | 43 months |
| Powered fleet | 51 six-car sets; 306 cars; 612 door openings |
| 10 m running beams | 6,000, with 24,000 provisional bearings |
| First-car direct assembly allowance | 720 hours/car |

The 41 BOM lines are mapped to one of the 14 capital scopes. An unpriced child
line remains **included within its parent scope allowance**; it is not a
zero-price procurement item. Seven scopes have a representative assembly route;
the other scopes retain their single priced cost-basis line without a fabricated
part decomposition. Station launch is an explicit zero-quantity exclusion for
this powered-wheel candidate. The 43-month schedule includes survey/design
(months 0–6), supports (6–24), beam production (8–31), erection (15–35),
rail/overhead (26–38), stations/depot/power/controls (29–40), and integration
and trials (40–43). At 16 beams per workday, factory and erection each require
375 working days within their overlapping windows.

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
about 42 KiB. The current `handoff.json` SHA-256 is
`288e30e838e2ebd8b4aa987f6728d57a602d8485ff14d671080cd6246058ab89`.
