# Pilot manufacturing and delivery planning draft

Physical candidate: `cde8e4595d365b31d169cf452d1efc1b9f0c96225ca3bbccf8bf51b5a2480c7f`

Body engineering revision: `dfb48ca3fac6ee9b702ae13b2e5e4e0c112d734263750deefb25ad5718fdb272`

Proposal: `7b88d05f9e0a16ada127d60e51d8ebfdc23b0dcb90ba0c906b2050d4e65a5775`

668 body definitions, 9804 occurrence patterns, 122422 counted occurrences per train and 4 proposed trainsets. 41 source assembly routes, 13 civil requirement types and 14 existing cost scopes are retained.

Tasks: {'held': 747, 'ready-for-planning-review': 742}. Ready means ready for planning review, never released work.

Original compressed inputs and generic engineering-evidence metadata are retained. The existing execution adapter refuses the mapping until actual review and native Item/drawing/inspection references exist. No ERPNext, FUXA or gateway writes were made. No native format was fabricated.

## Limits

- Calculated planning draft only; no manufacturing, engineering or operating acceptance.
- Stock geometry and proposed positions are not controlled finished drawings, mating fits or collision-free installed assemblies.
- No actual ERP Item mapping, released BOM, work order, purchase order, serial installation or supplier quotation is created.
- Capacity hours are declared Class A proxies; validated hours, actual crew count and calendar dates remain unknown.
- Existing direct part/process and full-system cost ledgers remain authoritative. Capacity hours and civil decomposition are non-additive.
- Civil decomposition covers the declared running beams and shared bents; terminal structure, turnouts, site services and equipment need further detail.
- No CAD, mesh or physical solver is executed by this compiler; numerical agreement does not establish qualified hardware.
- Material certificates, process qualification, release dimensions/tolerances, fatigue, electrical protection and independent safety evidence remain open.

Fresh compile: 7.359 s; peak RSS 973.0 MiB. No CAD/FEM batch was executed.
