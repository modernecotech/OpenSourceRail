# `standard` station — architectural drawing register (v2)

**Status:** v2 deliverable of [RFC 0010](../../rfcs/0010-station-design-standard.md).
**Purpose:** a complete list of the architectural drawings an
architect-of-record (AOR) produces for a Samawah-class
`standard` station. Every drawing is scoped, sized, and keyed
to the sections of the v1 envelope documents (envelope.md,
canopy.md, accessibility.md, services.md, compliance.md).

## Convention

- All drawings in the register are A1 size at stated scales,
  except section details which may be A3.
- Revision letters: A = first issue, B = post-coordination
  revision, C = construction issue.
- Every drawing has a title block referencing this register +
  the commit hash of the v1 envelope docs.
- Drawing numbers follow a stable scheme:

```
  OSR-STD-<discipline>-<sequence>
```

- **discipline codes:** A (architectural), S (structural),
  M (mechanical), E (electrical), F (fire), T (tactile + signage),
  L (landscape — if applicable).
- **sequence:** zero-padded 3 digits within each discipline.

A per-deployment station uses the same numbers; only the title
block's *site* field varies.

## Drawing list

### A — Architectural (13 drawings)

| No. | Title | Scale | Size | Input |
|---|---|---|---|---|
| OSR-STD-A-001 | Site plan + ROW | 1:500 | A1 | Envelope §Plan |
| OSR-STD-A-002 | Platform plan (both platforms) | 1:100 | A1 | Envelope §Plan |
| OSR-STD-A-003 | Fare/TVM plinth plan | 1:50 | A1 | Envelope §Sub-areas |
| OSR-STD-A-004 | Typical cross-section | 1:50 | A1 | Envelope §Section |
| OSR-STD-A-005 | Longitudinal section | 1:100 | A1 | Envelope §Sub-areas |
| OSR-STD-A-006 | West-end elevation (fare/TVM plinths) | 1:50 | A1 | Envelope §Sub-areas |
| OSR-STD-A-007 | East-end elevation (emergency egress) | 1:50 | A1 | Envelope §Egress |
| OSR-STD-A-008 | Canopy plan | 1:100 | A1 | Canopy §Geometry |
| OSR-STD-A-009 | Canopy section | 1:50 | A1 | Canopy §Structural system |
| OSR-STD-A-010 | Fare-zone plan (paid / unpaid) | 1:100 | A1 | Envelope §Fare paid/unpaid |
| OSR-STD-A-011 | Platform-edge detail (tactile + coping) | 1:10 | A3 | Accessibility §Tactile paving |
| OSR-STD-A-012 | Local approach grading details (if needed) | 1:20 | A3 | Envelope §Access modes |
| OSR-STD-A-013 | Equipment plinth + cabinet enclosure schedule | n/a (table) | A1 | Services §Signage |

### S — Structural (8 drawings)

| No. | Title | Scale | Size | Input |
|---|---|---|---|---|
| OSR-STD-S-001 | Foundation plan | 1:100 | A1 | Canopy §Foundation check |
| OSR-STD-S-002 | Column + footing detail | 1:20 | A1 | Canopy §Columns |
| OSR-STD-S-003 | Canopy truss elevations (typ.) | 1:50 | A1 | Canopy §Truss spans |
| OSR-STD-S-004 | Canopy truss plan | 1:100 | A1 | Canopy §Truss spans |
| OSR-STD-S-005 | Weld details + bolt tables | 1:5 | A3 | Canopy §Structural system |
| OSR-STD-S-006 | Platform slab reinforcement | 1:100 | A1 | |
| OSR-STD-S-007 | Fare/TVM plinth anchorage | 1:50 | A1 | |
| OSR-STD-S-008 | Seismic-bracing plan (when PGA > 0.2 g) | 1:100 | A1 | Canopy §Seismic load |

### M — Mechanical (5 drawings)

| No. | Title | Scale | Size | Input |
|---|---|---|---|---|
| OSR-STD-M-001 | Services-cabinet cooling layout | 1:50 | A1 | Services §HVAC |
| OSR-STD-M-002 | Platform drainage — trough + downspout | 1:100 | A1 | Services §Drainage |
| OSR-STD-M-003 | Canopy-drainage layout | 1:100 | A1 | Services §Drainage |
| OSR-STD-M-004 | Local ramp/kerb interface spec (if needed) | n/a | A3 | Envelope §Access modes |
| OSR-STD-M-005 | Accessible-toilet plumbing (if fitted per operator) | 1:20 | A3 | Services §Utilities |

### E — Electrical (8 drawings)

| No. | Title | Scale | Size | Input |
|---|---|---|---|---|
| OSR-STD-E-001 | Incoming MSB + sub-board schematic | n/a | A1 | Services §Electrical |
| OSR-STD-E-002 | Platform lighting layout | 1:100 | A1 | Services §Lighting |
| OSR-STD-E-003 | Canopy PV layout + string diagram | 1:100 | A1 | Canopy §PV layout |
| OSR-STD-E-004 | Canopy PV combiner + DC cabinet | 1:20 | A1 | Canopy §PV layout |
| OSR-STD-E-005 | Emergency lighting + UPS | 1:100 | A1 | Services §Fire + life safety |
| OSR-STD-E-006 | CCTV camera positions + cable routing | 1:100 | A1 | Services §Communications |
| OSR-STD-E-007 | Help-button + PA loudspeaker layout | 1:100 | A1 | Accessibility §Audio + visual |
| OSR-STD-E-008 | Lightning-protection finial + down conductor | 1:50 | A1 | Canopy §BOM |

### F — Fire + life safety (4 drawings)

| No. | Title | Scale | Size | Input |
|---|---|---|---|---|
| OSR-STD-F-001 | Fire-detection zone plan | 1:100 | A1 | Services §Fire + life safety |
| OSR-STD-F-002 | Fire-extinguisher placement | 1:100 | A1 | Services §Fire + life safety |
| OSR-STD-F-003 | Emergency-egress plan (NFPA 130 compliance) | 1:100 | A1 | Envelope §Egress + Compliance §NFPA 130 |
| OSR-STD-F-004 | Evacuation-signage layout | 1:100 | A1 | Services §Signage |

### T — Tactile + signage (3 drawings)

| No. | Title | Scale | Size | Input |
|---|---|---|---|---|
| OSR-STD-T-001 | Tactile paving layout | 1:100 | A1 | Accessibility §Tactile paving |
| OSR-STD-T-002 | Wayfinding signage positions + typographic spec | 1:100 + swatches | A1 | Services §Signage |
| OSR-STD-T-003 | Accessible signage (Braille + raised-character) details | 1:5 | A3 | Accessibility §Compliance checklist |

## Drawing count + delivery phase

| Discipline | Drawing count |
|---|---|
| A — Architectural | 15 |
| S — Structural | 8 |
| M — Mechanical | 5 |
| E — Electrical | 8 |
| F — Fire | 4 |
| T — Tactile + signage | 3 |
| **Total per station** | **43** |

For the 12 `standard`-archetype stations in Samawah, that's
**516 drawings** — but with the archetype's repeatability,
only the site-plan (OSR-STD-A-001) varies meaningfully
between sites. The other 42 drawings are near-identical
across all 12 stations, with per-site parameters (parcel
geometry, north arrow, foundation specifics) as the only
delta.

## Interaction with per-site adaptation

The v1 envelope docs list per-deployment adaptations that the
AOR implements:

- **Site plan (A-001):** always site-specific.
- **Orientation (A-008, E-003):** rotate to face equator;
  swap if southern hemisphere.
- **Façade finish (A-015):** operator choice reflected in
  the schedule.
- **Parcel-line setbacks (A-001, A-006, A-007):** per-
  municipality.
- **Foundation depth (S-001, S-002):** per-site geotech.
- **Seismic (S-008):** applicable only if PGA > 0.2 g.

Everything else is archetype-fixed: one set of drawings
replicated 12× for Samawah.

## Delivery sequence (typical)

1. **Design Development (DD)** — all A + S drawings at rev A.
2. **Coordination** — M + E + F + T drawings at rev A +
   integrate back into A + S → rev B.
3. **Construction Documents (CD)** — everything at rev C.
4. **Tender** — operator's procurement team issues CD to
   construction-firm bidders.
5. **Shop drawings** — fabricator's own drawings (steel
   fabrication, PV module mounts) land as annexes.

## Acceptance criteria for v2

The v2 deliverable of this doc = **the architect's drawing
register for the deployment**, matching the list above
drawing-for-drawing. Per-drawing content is the architect's
scope; the register + envelope specs are the upstream input.

For a per-deployment tender, the AOR:

1. Downloads this register.
2. Fills in the title-block fields (site, project, AOR firm
   name).
3. Produces the drawings.
4. Files the commit hash of the envelope docs against which
   they drew.

## What v2 does NOT include

- Actual CAD files (AutoCAD / Revit / ArchiCAD — AOR's tool
  choice).
- Printed plot files (per-deployment plot shop).
- Renderings (optional operator deliverable).
- Cost estimates (per-deployment QS scope).
