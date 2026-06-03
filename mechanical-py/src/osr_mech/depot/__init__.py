"""Depot parametric CAD — three archetypes per RFC 0014.

- `main-heavy` — overhaul-capable main depot with wheelset lathe.
- `secondary-medium` — light-maintenance regional depot.
- `layup-minimal` — overnight stabling only.

Each archetype is a rectangular site with:

- A fan of stabling tracks (count from RFC 0014 §4 formula or the
  per-archetype ceiling).
- An inspection / maintenance shed with full-length pit tracks for
  `main-heavy` + `secondary-medium`.
- A single-turnout ladder at the depot throat connecting to the
  running line.
- `main-heavy` only: a wheelset-lathe bay (separate building).
- `training-wing` add-on for `main-heavy` if requested. OSR is
  driverless (RFC 0015), so the wing trains **dispatchers,
  maintenance technicians, station staff, and recovery-mode crew**
  — not revenue-service drivers. There are no driver-training
  simulators in an OSR depot.

The emitted review geometry is a massing model: the shed walls, roof,
pit lines, and track centrelines are there, but no internal MEP,
structural framing, or civil interface. Partners take the massing +
RFC 0014 into their own structural + architectural packages.
"""

from .layout import (
    DepotArchetype,
    DepotFootprint,
    depot_layout,
    depot_footprint,
)

__all__ = [
    "DepotArchetype",
    "DepotFootprint",
    "depot_layout",
    "depot_footprint",
]
