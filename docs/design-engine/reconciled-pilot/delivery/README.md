# Pilot manufacturing and delivery planning draft

Physical candidate: `f9aa3afa47a297da855b2741c9e0fde0d77ad3e3211df500f32f901cfadb1877`

Body engineering revision: `59943e9ed14b44cdd9180cccf7387c1bb09bf752b8164f4d0d49bbdca2390d29`

Proposal: `d6a1ef5505c49c6a70041fbbda9c37bb0675f0d2aabb51032dee197fcc2faacb`

650 body definitions, 9588 occurrence patterns, 121318 counted occurrences per train and 4 proposed trainsets. 40 source assembly routes, 13 civil requirement types and 14 existing cost scopes are retained.

Tasks: {'held': 712, 'ready-for-planning-review': 723}. Ready means ready for planning review, never released work.

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

Fresh compile: 7.325 s; peak RSS 638.6 MiB. No CAD/FEM batch was executed.
