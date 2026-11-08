# Pilot manufacturing and delivery planning draft

Physical candidate: `f9aa3afa47a297da855b2741c9e0fde0d77ad3e3211df500f32f901cfadb1877`

Body engineering revision: `cf732ddac06d8ba607223a91bdf4658ca7eab9387c128dfc8b40a8e5da5776d5`

Proposal: `0e64e1b4ae7606fd9d1bf78d540a2334b5bd6f6f8edf12b265dca4ce8f40e32a`

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

Fresh compile: 8.015 s; peak RSS 795.2 MiB. No CAD/FEM batch was executed.
