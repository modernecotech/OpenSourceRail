---
name: City design revision
about: Review an OSR City Studio network or service-plan revision
---

## City and revision

- City:
- Revision id:
- Parent approved revision:
- Proposed release tag:

## Intent

Describe why the network, station, calendar, or service change is needed.

## Semantic changes

- Stations added/moved/retired:
- Lines or geometry affected:
- Day types/time windows affected:
- Fleet/capacity/service-km change:
- CAPEX/OPEX/energy effect, where generated:

Attach or summarize the City Studio comparison against the parent revision.

## Evidence

- [ ] City Studio validation passes.
- [ ] Source locks match.
- [ ] Candidate revision JSON is committed with its input changes.
- [ ] Map and semantic diff reviewed.
- [ ] Manual station additions/retirements are present in generated simulator topology.
- [ ] Simulator or engineering checks appropriate to the change pass.
- [ ] Unresolved findings are listed below.
- [ ] No live OCC command or deployment configuration was changed directly.

## Required reviews

- [ ] Network/GIS engineering
- [ ] Operations/service planning
- [ ] Civil/station/CAD, if geometry or products changed
- [ ] Safety/assurance, if an approved deployment baseline is affected

## Unresolved findings

List each accepted open finding, owner, due point, and disposition.
