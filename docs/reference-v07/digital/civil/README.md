# Joined 10 m civil digital check

The [native result](result.json) is evaluation
`7c4bec060cb071880bbd3f1b87aaba2faf66bf839d097540af7d59cf555594ad`.
It binds the joined car, the selected nine-strand 10 m beam, the input decks,
CalculiX 2.23 executable and output bytes. Its parent physical candidate is
`osr-v07-joined-prototype-20261117`. The [input](input.json) contains every
source SHA-256 and the separate child identity for a changed beam.

The gross-elastic native model uses one 10 m × 2 m × 1.4 m closed box with
180 mm walls, 35 GPa concrete modulus and Poisson ratio 0.20. Twenty quadratic
beam elements have 0.25 m node spacing. One end fixes translation, the other
allows longitudinal movement, and both ends restrain torsion. Counted beam,
rail and fastening stock is spread as gravity. Prestress is screened
analytically; it is not represented as a native tendon field.

The joined [digital car](../vehicle/README.md) has a crowd-control static axle
interval reaching **155.77 kN**, while the prior equal-share civil model used
**82.46 kN**. To preserve each car's total mass, the new bound pairs one
high-reaction bogie with its complementary low-reaction bogie. The exact-event
moving-load calculation selects bogie orientations and train pose to maximise
the beam moment. The 1.3 dynamic multiplier remains a declared hypothesis.

| Case | Maximum live moment | Native midspan deflection | Gross longitudinal screen |
| --- | ---: | ---: | --- |
| Original nine strands, equal-share axle control | 0.586 MNm | 1.027 mm | Passes its original limited screen |
| Original nine strands, joined CG bound | 1.107 MNm | 1.575 mm | **Fails:** 0.977 MPa service tension against zero-tension criterion |
| Distinct 13-strand beam child, joined CG bound | 1.107 MNm | 1.576 mm | Passes declared gross longitudinal tension/compression and transfer limits |

The 13-strand option has beam ID
`34161ebcca2e35599cc5896a23b763cc35d3809107dd6b0c9f2ff98516a68160`
and *new* joined physical child
`osr-v07-joined-civil-518dad57a3af5046f40c8f4f`. It remains an option,
not an automatic selection or a silent modification of the original joined
candidate. Its modelled initial/effective prestress is 2.370/1.896 MN.
Maximum gross service tension is −0.106 MPa and compression 3.358 MPa;
transfer maximum tension is −0.760 MPa and compression 3.571 MPa. The
negative tension values mean all checked longitudinal fibers remain in
compression under these declared load and material hypotheses.

Changing nine to thirteen strands adds **79.96 kg counted steel per beam**:
31.984 t across the 400-beam demonstrator or 479.76 t across the 6,000-beam
30 km corridor. Modelled bare lifting mass becomes **29.964 t** and the 25%
hook allowance becomes **37.455 t**. The four existing civil cost items keep
their quantities, but the US$14,000/beam assembly rate and BOM steel quantity
need a revised planning estimate before this child can replace the original
in the single corridor total. No strand marginal price exists in the source
cost basis, so this artifact does not silently carry that rate across.

The revised case applies 1.118 MN total vertical load to one beam; its native
end support totals are **514.684 and 603.782 kN**, with relative vertical
force residual **1.22 × 10⁻⁸**. A severe all-on-one-rail sensitivity gives
**0.101 mm** rail-to-rail vertical difference at midspan with the assumed end
torsion restraint. These one-span reactions are not the two-adjacent-span
foundation reaction. The earlier 0.967 mm analytical equal-share deflection
is 6.2% below the native 1.027 mm value; it is not an upper bound for the
native model. The discrepancy is retained for later model reconciliation.

The joined quantity basis is 400 beams, 402 independent supports and 1,600
provisional bearings for the straight 2 km module; 6,000 beams and 6,002
supports for the 30 km corridor. At four factory beams and eight site lifts
per working day, the direct 2 km production and lift minima remain 100 and 50
days. The 60 t-at-12 m crane chart is a planning hypothesis; the revised
37.455 t hook load must be checked at the actual radius and ground condition.

Reproduce from the repository root:

```sh
python3 -m engineering.design_search.v07_joined_civil_fem build --output /tmp/osr-v07-civil-fem
python3 -m engineering.design_search.v07_joined_civil_fem check --output docs/reference-v07/digital/civil
python3 -m pytest engineering/design_search/tests/test_v07_joined_civil_fem.py -q
```

The result is a digital global beam check. It does not establish rail-seat,
diaphragm, tendon anchorage and transfer, reinforcement, cracked concrete,
fatigue, bearing, foundation, lateral/braking combination or erection
stability. Site and physical acceptance are separate from this digital result.
