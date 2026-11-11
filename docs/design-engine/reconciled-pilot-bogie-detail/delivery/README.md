# Pilot manufacturing and delivery planning draft

Physical candidate: `cde8e4595d365b31d169cf452d1efc1b9f0c96225ca3bbccf8bf51b5a2480c7f`

Body engineering revision: `a7a9ee09ffc7f7b5c573a1b3f5fe966625a6269bc7df6865355fe656c8ede941`

Proposal: `db8c4579461b056c8b7e339dc36c0c03eab4edfaa5f8ffa7dc9189c7270ba18d`

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

Fresh compile: 7.117 s; peak RSS 603.7 MiB. No CAD/FEM batch was executed.
