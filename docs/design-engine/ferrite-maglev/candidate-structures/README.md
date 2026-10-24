# Candidate-specific structural design study

Exact candidate `a79a21a0767355fcb6518471769e532a04e2e23f4bd33db90968ef4a385df5bd`; 37618.592 kg AW3 per car. All physical, engineering and manufacturing release flags remain false.

This package recalculates full force/moment equilibrium from the counted installed-mass placements. It does not scale the earlier26.4t interface result or adopt historic94ad dynamics.

Implemented results: hardpoint utilisation 0.568; retained M8 segment-splice utilisation 14.251; two-spine-only dynamic bending stress 589.5 MPa. Failed controls remain recorded; deeper collector/spine alternatives require a new shared candidate identity and repeated mass/fit/dynamic checks.

Reference25m span: 18.056 m³ concrete, 14946.1 kg new L-return/support steel, 1202.7 kg reinforcement, 604.5 kg strand, 61893.3 kg gross. This includes counted actual reaction rails, not the old7.51t allowance.

The original hypothetical60t@25m crane remains rejected. A separately identifiedLTM1750 manufacturer chart is evaluated at its26m row,32.7m boom and204t ballast;2.6t hook and3t slings/spreader are counted. Actual crane configuration, wind, access, ground reactions/mats and lift plan remain unapproved.

Material interference witnesses: 0. Zero witnesses alone does not qualify swept clearance or tolerances. New collector drilling is explicit machining with zero mass-removal credit. Concrete around fixed support embeds/blockouts is gross conservative stock, not completed net manufactured solids.

Soil cases50/100/150kPa and pile shaft/toe values are analyst sensitivities. No bearing resistance, groundwater, settlement or seismic acceptance is inferred from SoilGrids/open maps. Foundations and pier alternatives are separate, not additive.

[Section drawing](beam-section.svg) · [Geometry image](section.png) · [Candidate load plan](candidate-load-plan.svg) · [BOM](bom.json) · [Full study](study.json.gz) · [Applied-load export](load-envelope.json.gz) · [Counted geometry](geometry.json.gz)

Publication verification recomputes the structural study and independently checks retained payloads, exact source hashes, geometry-driven SVG and decoded section-image pixels. Image container bytes/fonts are not an engineering oracle.

QA and sequence records are unexecuted plans. No manufacturer quotation, concrete design code compliance, physical trial or site-specific design acceptance is claimed.

Primary references:
- [JRC68415](https://publications.jrc.ec.europa.eu/repository/handle/JRC68415) — European Commission2012 bridge worked examples: separate permanent/live/wind/fatigue/construction actions, concrete, foundations and seismic. Road-bridge examples; not a maglev or Iraq compliance route.
- [FHWA-PSC](https://www.fhwa.dot.gov/bridge/lrfd/pscustoc.cfm) — Primary worked-example structure: transfer/service stresses, losses, flexure/shear, bearings, pier and footing. Our SI material limits/factors are explicitly unqualified inputs, not imported AASHTO acceptance.
- [WSDOT-handling-2017](https://www.wsdot.wa.gov/publications/fulltext/Bridge/designmemos/03-2017.pdf) — Handling/shipping stages, transverse sweep/tilt, transport support parameters and strength at release must be stated; our simple roll/bending screens do not implement full PCI lateral-stability design.
- [BCSA51-10](https://www.steelconstruction.info/images/1/1c/BCSA_51-10.pdf) — UK steelwork fabrication, bolting/tool access, preloaded/slip-resistant bridge joints, weld procedures and fatigue. Historical2010 guide, no current code compliance claim.
- [RSSB-GMRT2100](https://www.rssb.co.uk/standards-catalogue/CatalogueItem/gmrt2100-iss-6-2) — Primary/secondary rail vehicle structure and passive-safety scope. No GB category or EN12663 load case is claimed; full standard and Iraqi applicability need independent review.
- [ISRIC-SoilGrids](https://docs.isric.org/globaldata/soilgrids/SoilGrids_faqs.html) — Global pedological prediction maps with uncertainty; no bearing, pile resistance, groundwater, liquefaction or settlement values inferred. All50/100/150kPa scenarios are analyst hypotheses.
- [Liebherr-crane-scope](https://www.liebherr.com/en-ie/mobile-and-crawler-cranes/mobile-cranes/ltm-mobile-cranes/ltm-1300-6-3-5332106) — Manufacturer300t maximum is at3m radius and configurations vary. This package uses explicitly hypothetical radius-specific capacities and retains signed lift-chart/ground approval as a hold.

- [LTM1750-9.1 manufacturer technical data](https://assets-cdn.liebherr.com/versions/019fb335-8d70-7247-8b5b-1a6146c33a97/original/), printed pages8/26, accessed2026-10-23.
