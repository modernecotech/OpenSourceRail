# Segmented 20 m span: prototype planning handoff

This is a controlled **quotation and test-planning** package for civil research
candidate `abcf7e942fd1337c9872869d684ac9a8055ce94bd3e9c35de0dbcbe07f49ac82`.
It consumes the [source-bound civil experiment](../v07-affordable-corridor/evidence/civil-20261117-box20-segmented-001/README.md),
evaluation `79b896dc9517a00414245af473411b675f8eb03898788897812fa2d949458367`.
The [machine-readable plan](plan.json) has the interface schedule, erection
load paths, QA gates, quote quantities and exact source hashes. It does not
adopt the segmented span into the selected vehicle/guideway reference.

## Physical and quantity basis

| Item | Retained hypothesis | Qualification boundary |
|---|---:|---|
| Standard beam module | 20 m, two nominal 10 m pieces | Jointed structural member unverified |
| One piece | 29.592 t bare; 34.201 t provisional hook | Lifting inserts, rigging, transport and actual crane chart unverified |
| Joint | Match-cast key, epoxy and continuous post-tension; 2 mm closure proposal | Key, tendon/anchor, fatigue, torsion and shop length open |
| Support | Four bearing units/beam; 3 × 3 × 1.2 m footing and 8 m pier hypotheses | Bearing seat, tower pad and site foundation open |
| Straight 2 km, two tracks | 200 beams, 400 lifts, 202 independent supports, 800 bearings | Stations, crossovers, crossings, utilities and site access excluded |

The 3 m footing gives **167.37 kPa in the gravity-only 200 kPa soil
hypothesis**. It fails the retained 100 kPa sensitivity. This is not a ground
approval: lateral, settlement, uplift, seismic, groundwater and temporary tower
loads require site investigation. The whole-beam moving-load model reports
1.543 MN·m maximum live moment at x=10.5 m and 12.12 mm deflection upper
bound. Its nominal joint-plane x=10 m section has 1.535 MN·m live moment and
6.845 MPa maximum service compression in the source local envelope. These
figures do not qualify the segmented joint or erection stages.

## Critical mating decision

Two pieces called “10 m” plus a proposed 2 mm closure do not yet define a
finished 20 m bearing-to-bearing length. The precast shop must receive a single
controlled dimension chain linking segment cut faces, joint closure, end
bearing centres, pier seats and rail datum. The package leaves shop length and
approved tolerances null until that chain is designed and surveyed. It also
keeps lifting-insert and temporary-tower positions null because they affect
segment stress and the joint/duct layout.

The six erection stages in `plan.json` identify where the load path changes:
ground/support preparation, first segment, paired unjoined pieces, joint and
tensioning, monitored tower removal, and rail/train loading. Each stage has a
named release record. A contractor can quote the listed quantities and tests,
but must return engineered methods, dimensions, measured hours and supplier
prices before a controlled build instruction is issued.

The [cost handoff](cost-handoff.json) compares the counted straight-span
quantities without manufacturing a price from unquoted work:

| Quote or quantity | 2 km | 30 km | Pricing treatment |
|---|---:|---:|---|
| Complete segmented beam factory packages | 200 | 3,000 | Replace whole-beam factory allowance |
| Segment stocks / structural joints | 400 / 200 | 6,000 / 3,000 | Breakdowns inside the complete beam quote; do not add again |
| Certified segment lifts / tower placements | 400 / 200 | 6,000 / 3,000 | Replace old lift allowance / add new tower work |
| Independent pier and foundation supports | 202 | 3,002 | Replace gravity-minimum site proxy |
| Bearing units / direct fastener sets | 800 / 14,000 | 12,000 / 210,000 | Replace matching base allowances |
| Rail stock / welds | 8,000 m / 396 | 120,000 m / 5,996 | Replace matching base allowances |

The current USD 107.703 million (IQD 162.631 billion) civil figure belongs
to the **unsegmented 30 km Class C comparison**. It is not this candidate's
installed price. The 3 m footing adds an arithmetic material-only proxy of
IQD 1.477 billion at 30 km, or IQD 99.4 million for 2 km when scaled by the
actual support-count ratio. It is **not added** when a complete site support
quote replaces the baseline support line. All candidate unit quotes, baseline
credits, deltas and installed totals remain null until supplier and site
inputs arrive. Geotechnics, station transitions, utilities and haul permits
are separate unquantified quote rows.

## Reproduce and check

From the repository root:

```bash
python3 -m engineering.design_search.segmented_span_prototype check
python3 -m engineering.design_search.segmented_span_prototype check-cost
python3 -m pytest -q engineering/design_search/tests/test_segmented_span_prototype.py
```

To regenerate after an approved source change, run the same module with
`write` in an isolated worktree, review the changed identities and holds, then
rerun `check` and the focused tests. An updated source evaluation does not
automatically accept this physical candidate.
