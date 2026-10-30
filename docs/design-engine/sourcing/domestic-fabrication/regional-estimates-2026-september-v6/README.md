# Iraqi domestic material + labour cost reference — September 2026

This generated packet combines official Iraqi Central Statistical Organization (CSO) September 2026 material and governorate wage observations with explicit cost sensitivities. The same-period concrete estimates and historical comparisons remain separate. The Ur Company aluminium price observations were observed on 29 October 2026; their price-effective date is unknown.

## Formula and scope

`(material quantity × dated source rate + assumed person-hours × hourly base wage) × 1.20`

The 20% is an unallocated planning uplift on direct material plus base-wage labour only. It is not verified overhead, profit, tax, contingency, or margin. The CSO wage is a statistical construction-worker base wage normalized by an explicit 8-hour day, not a shop charge-out rate. The packet contains no supplier quote, complete process price, procurement approval, installed cost, whole-life cost, or physical qualification.

## Candidate-mapped domestic aluminium stock sensitivities

The exact federated material takeoff `042b2b73f6ac0b92da886eb71949c0020c595f0bb7485c413700d40215939d41` contains 17,535.607 kg of `aluminium_reference` across 1,164 manufacturing groups / 23,286 occurrences and 1,652.057 kg of `6082-T6-proposed` across 312 groups / 312 occurrences. It does not identify the product-form split, order quantity, purchase yield, or declared labour hours. Every estimate below is therefore a separate whole-rollup alternative; profile and sheet cases must not be added together.

The official [Ur Company posted price page](https://ur.industry.gov.iq/public/prices) lists three profile categories (non-oxidized, oxidized, spray-painted) and four sheet categories (hard or annealed, each at 0.6–0.9 mm or 1 mm and above), priced per tonne in IQD. Prices were observed on 29 October 2026; the effective date and commercial terms are unstated. For each material rollup, the generator evaluates all seven source forms at 8 / 16 / 32 assumed labour hours per gross stock tonne, using the Baghdad September CSO skilled-worker base-wage proxy of IQD 9,375/hour. Gross stock mass is used as a proxy for purchased tonnes with 100% yield solely to calculate a sensitivity.

- `aluminium_reference`: **IQD 98.375–122.048 million** across its 21 alternative form/hour cases.
- `6082-T6-proposed`: **IQD 9.268–11.498 million** across its 21 alternative form/hour cases.

The Ur listings do not state structural alloy/temper, dimensional match, availability, delivery terms, taxes, or quantity conditions. In particular, they do not verify 6082-T6 compatibility or support an accepted product match. Labour hours are assumptions, not timed local fabrication routes. The calculation excludes scrap and nesting yield, machining, joining, heat treatment, additional coating, consumables, tooling, moulds, equipment depreciation, employer burden, utility, QA, packaging, transport, taxes, installation, rework, warranty, and maintenance. The 42 mass extensions are cost sensitivities, not actual body or secondary prices.

## Concrete comparison and provenance

The same packet carries six Baghdad / Al-Muthanna concrete recipe comparisons over 81 groups and 486 occurrences. Their nominal ingredient recipe is 0.35 t cement + 0.50 m³ red sand + 0.80 m³ crushed gravel; it is not a designed mix or verified yield. The CSO material/wage source is the official [monthly construction-material bulletin](https://cosit.gov.iq/ar/constr-stat/constr-pr). See the source hashes in `manifest.json` and each packet's source references.

- Candidate: `9c7d0942c9de6056e6afd051549273d0f34a72edf301fdd680ba37d12da7879f`
- Source input: `d4f1d575895a3b8609670fff66e7e53aee023a248d0233c40152f46f267c2842`
- Material takeoff: `042b2b73f6ac0b92da886eb71949c0020c595f0bb7485c413700d40215939d41`
- Source epoch: `379dd75f79c53eafe6eba8ef30aea36e0f7a78a4165b2bb655d9104b3b0c54d1`
- Regional unit-rate cases: 90
- Candidate-mapped concrete cases: 6
- Candidate-mapped aluminium raw-stock sensitivities: 42 (two rollups, seven forms, three labour-hour assumptions)
- Complete procurement and installed costs: unknown
- Supplier communication: none sent
