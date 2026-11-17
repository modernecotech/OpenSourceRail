# Baghdad v0.7 evidence and reproducibility

The work was calculated on 17 November 2026 from source commit `bb9e0d7fd73f12a6c7ba4735566b7658e977a566` in an isolated source worktree. The root checkout's unrelated edits were left untouched. Numerical workers wrote private `build/v07-baghdad/` run packages; the coordinator copied immutable output and scripts into this proposal. Shared-filesystem reviewers were read-only by instruction and SHA-256 integrity checks; that is not OS isolation. No candidate was physically accepted or automatically selected. The [candidate manifest](candidate-manifest.json) binds each physical, evaluation and selection identity to exact file hashes.

| Record | Identity / purpose | Present status |
|---|---|---|
| Concept A physical planning geometry | [RFI waypoint table](rfi-waypoints.json), waypoint identity `74c7d3e4dbb4a45972e36cf48c97a5a11788d3df009880afd348eb7a894fef42` | Schematic, with 15 named places unlocated and no owner route approval |
| Concept A background access screen | `a2f7bd1fe99842aaac3afd80191dc4089fa153f30e4d23c3be705572058daf72` in [sealed run](repro/network-20261117-a/result.json) | Preliminary screen before the 57-waypoint A table; **not** native same-candidate reuse |
| Concept A cost evaluation | `cc98df4296e1e24a0e67400bfa50d311bb0dd39854f1c46c8a069ad82498a6b0` in [14-scope ledger](cost-ledger-a.json) | US$18.0bn one-point planning envelope, not a bid |
| Concept B physical planning topology | `0a8d50dc8e637c307ca45a14224a9b744531ff635abaeef7ca5972e2c1a61985` in [infill evaluation](concept-b-infill-evaluation.json) | 605.652 km schematic chords and 226 line-stop markers; no surveyed geometry |
| Concept B radial evaluation | `92abf9b4d5f87fdb0d228fc308712c320b1c31c076477afba5fd3a0aaa45010a` | WorldPop 2026 modelled proximity, not demand |
| Concept B filtered walking evaluation | `9e711b358480e1484b9c738c608a25d487e7de1625fe52d1b700210b636e9d00` in [screen](concept-b-walking-screen.json) | OSM tagged-edge sensitivity; no accessible walking certification |
| Concept B cost evaluation | `53e4fbbbe80a80107bb803779936aa4d08841ee766e72bf5d3f34ad77e063146` in [14-scope ledger](cost-ledger-b.json) | US$69.6bn one-point planning envelope, not a bid |
| Selection identity | None | Neither concept is an owner-selected physical railway |

The [Concept A run receipt](evidence/network-a-receipt.json), [Concept B walking receipt](evidence/network-b-walking-receipt.json) and [initial independent audit](evidence/independent-initial-audit.json) preserve source hashes and execution/validity status. The original two-concept cost ledger was sealed, then its arbitrary 600 km B sensitivity was superseded by the 605.652 km candidate-specific B evaluation. The [A ledger](cost-ledger-a.json) is an extracted copy of the original A row with its original SHA-256 recorded in its `extraction_note`; no A amounts were changed. The sealed [original A](repro/cost-a-original-ledger.json) and [original B](repro/cost-b-original-ledger.json) ledgers remain for audit. The presentation ledgers add candidate and evaluation identities; their original receipts therefore authenticate the original calculations, while the candidate manifest hashes the final files.

The exact byte preimages for the price evaluation IDs are [A's basis](cost-evaluation-basis-a.json) and [B's basis](cost-evaluation-basis-b.json). Each is UTF-8 JSON with lexicographically sorted keys, `,` and `:` separators without spaces, `ensure_ascii=false`, and no trailing newline. `sha256sum` of each basis file must equal the corresponding `cost_evaluation_id` in the ledger and candidate manifest. The manifest separately hashes the complete ledger file, avoiding any self-referential hash field.

## Bounded numerical methods

The [reproduction package](repro/) contains the exact numerical scripts, input/output JSON, GIS links, logs and receipts from the two route screens. To replay in a clean checkout with the same large GIS data present, copy `repro/network-20261117-a` and `repro/network-20261117-b` to `build/v07-baghdad/`, then run:

```sh
python3 build/v07-baghdad/network-20261117-a/run.py
python3 build/v07-baghdad/network-20261117-b/run.py
python3 build/v07-baghdad/network-20261117-b/filtered.py
```

These scripts reject a run if projected disk use would breach the 20 GiB free-space floor. Original A core screen took 9.922 s; B radial screen 0.898 s; B filtered OSM graph screen 3.707 s (about 346 MB peak). Inputs use WorldPop 2026 modelled 100 m population, OSM station/road geometries and tagged walking exclusions. A walking snap can still cross an unrecorded wall, unsafe road, inaccessible kerb or airport security boundary. Consequently neither screen verifies a station site, accessible walking network, line demand or 2035 population.

The cost-ledger arithmetic is `sum(quantity × rate for 14 scopes) × 1.20`; B's exact evaluated geometry is 605.652 km and 226 **line-stop markers**, not 226 approved unique station sites. Price rates, 15% underground class, fleet, depots, power, local origin and procurement status are planning hypotheses. UKEF and bank eligibility, physical safety and environmental/social acceptance require independent external decisions. The PDF is a presentation of these source records and must be regenerated after any numerical revision.

To regenerate the six-page presentation from these proposal records, run `python3 docs/proposals/baghdad-v07/render-proposal.py` from the repository root. It writes `output/pdf/Baghdad-Metro-v0.7-Proposal.pdf`; render all pages with `pdftoppm` and inspect them before distribution. The source PDF has clickable official source links and its GIS illustration is explicitly schematic.
