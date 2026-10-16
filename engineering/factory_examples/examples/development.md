# Joint mechanical and civil development — iteration 2

The baseline four-model package remains available. These three additional CAD models develop workholding, prestress/bed restraint and crane-runway interfaces. Every physical release remains open. [Engineering comparison figure](development.svg).

## Fixture workholding

Three British-made [Brauer H350/2BLC](https://www.brauer.co.uk/product/horizontal-positive-locking-clamps/) positive-locking clamp candidates each have a published nominal holding force of 350 daN (3,500 N). The requested 500 N clamping preload is a separate unverified input. Mounting plates are OSR concepts; equipment boxes reserve operation clearance rather than reproduce the supplier's geometry.

The declared payload/CG/tool cases leave a minimum vertical locator reaction of 993.0 N. That checks contact compression in those scenarios only. The conservative shear-only crossrail weld demand is 5.48 MPa; weld resistance, local wall/plate bending and connection eccentricity remain unknown.

[Workholding CAD](fixture-workholding/model.FCStd) · [detailed numerical inputs/results](development.json)

## Prestress alternatives along both spans

The first iteration showed a Pi20 midspan tension warning. The full-force prismatic extension to the beam ends exposes a larger baseline warning. Actual pretension force develops over a transmission length that remains unknown, so the endpoint extension is diagnostic. This model includes end-diaphragm gravity patches and known strand displacement mass, while retaining gross prismatic stiffness. Conventional reinforcement and railway/track loads remain unquantified.

| Layout | Strands | Span | Minimum transfer compression | Minimum after-loss dead-load compression | Zero-tension research screen |
| --- | ---: | ---: | ---: | ---: | --- |
| low-40 | 40 | 20 m | -3.964 MPa | -3.171 MPa | outside |
| low-40 | 40 | 25 m | -3.964 MPa | -3.171 MPa | outside |
| balanced-40 | 40 | 20 m | 1.116 MPa | 0.893 MPa | within |
| balanced-40 | 40 | 25 m | 0.850 MPa | -1.842 MPa | outside |
| balanced-48 | 48 | 20 m | 0.362 MPa | 0.290 MPa | within |
| balanced-48 | 48 | 25 m | 0.362 MPa | 0.290 MPa | within |

The balanced-48 candidate increases initial bed force to 7.392 MN. Its known concrete-plus-strand Pi25 handling equivalent is at least 104.69 t including the stated rigging and multiplier; unquantified reinforcement and attachments can increase it. A zero-tension screen does not establish compression strength, transfer/bond/end-zone performance, deflection, shear, fatigue or railway capacity.

[Revised beam/bed CAD](pi25-revised-bed/model.FCStd)

## Stressing-bed restraint

Pinned beam-column finite elements check the nominal side boxes over the 26 m return path between assumed inner strongback faces x=-0.5 and +25.5 m, with ground restraints at the CAD's x=3,6,...,24 m stations. Pin-connected cross ties alone do not establish a 3 m effective length: a common sway mode remains. End rotational restraint and a real restraint path in both buckling planes must be designed, including foundations and anchorages.

| Spring per restraint | Critical force per side | Elastic load factor at candidate force | Second-order brace force maximum |
| ---: | ---: | ---: | ---: |
| 0 MN/m | 1.148 MN | 0.310 | unstable elastic tangent |
| 0.1 MN/m | 3.428 MN | 0.927 | unstable elastic tangent |
| 1 MN/m | 10.264 MN | 2.777 | 1.82 kN |
| 10 MN/m | 32.080 MN | 8.680 | 1.63 kN |

The proposed 1 MN/m spring is a requirement scenario, not measured ground stiffness. Second-order reactions use an assumed sinusoidal 10 mm stress-free bow and springs initially unstressed in that crooked shape. The revised CAD adds interface stools/pad reservations, with no demonstrated foundation stiffness or capacity. Strongback load distribution, vertical eccentricity, local plates/welds, staged release and anchorage design remain open.

The candidate adds 4.186 MNm in-plane strongback moment and a 5.667 MNm end couple from the tendon/return-box height offset. These are unresolved load-path demands; the large strongback solids remain reservations, not designed steel sections or concrete abutments.

## Dedicated crane-runway bay

A separate 6 m runway bay develops a proposed 30 m-span, 125 t rated crane interface. Assumed crab/bridge masses, lift factor, two wheels per rail and approach yield near/far wheel actions 771.5/123.4 kN. These are OSR scenarios requiring Street's actual configuration/reaction return. [Street describes wheel loads and duty as configuration-dependent](https://streetcrane.com/blog/2026/07/29/understanding-crane-duty-ratings/).

The fabricated 1.2 m-deep runway girder has gross elastic bending demand 48.9 MPa and sampled deflection envelope 1.17 mm for the stated loads. Local wheel/web bearing, stability, fatigue, torsion, clips, connections and column resistance remain open. The conservative two-adjacent-bay column scenario is 2.127 MN. A 2.5 × 2.5 m pad reservation gives 369.7 kPa average gravity pressure; ground capacity, eccentric bearing and uplift are unknown, so no footing acceptance is given.

[Runway bay CAD](runway-bay/model.FCStd). Runway supports remain separate from the vehicle hall's roof-only frame. Runway rail/clip/stiffener dead weights and final project load combinations remain unknown.

The 900 × 900 × 50 mm runway baseplate blank is about 318 kg. It exceeds both the CV5-500's published part diameter and mass limits, while the 6 m girders also need a separate fabrication route. Outsourced plate machining/long-girder fabrication or additional machinery must be selected before this pilot factory can manufacture those structures. Sheet-plan fit alone does not establish 50 mm laser-cut capacity.

## Next evidence and ownership

Mechanical engineering: clamp GA/preload trials, pin retention and mount/weld/bolt details. Prestress/civil engineering: project concrete/strand limits, transmission/end-zone and railway loading, strongbacks, both-plane restraint and geotechnical design. Crane supplier/structural engineering: exact duty/configuration, wheel actions, rails/stops, runway/column/foundation design. Procurement: technical returns, certificates, Baghdad support and itemised installed prices. No contacts have been sent and no appointments invented.
