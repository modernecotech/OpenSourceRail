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
- `main-heavy` only: a wheelset-lathe bay and an LM3-datum synchronized
  lifting/bogie-change bay.
- `training-wing` add-on for `main-heavy` if requested. OSR is
  driverless (RFC 0015), so the wing trains **dispatchers,
  maintenance technicians, station staff, and recovery-mode crew**
  — not revenue-service drivers. There are no driver-training
  simulators in an OSR depot.

The emitted review geometry remains a coordination model. The main-heavy
maintenance bay now includes civil foundations, pit edges, lift heads,
extraction paths, and safeguarded controls at controlled datums; certified
loads, reinforcement, supplier internals, and building services remain in the
deployment structural and equipment packages.
"""

from .bogie_change import depot_bogie_change_bay

from .layout import (
    DEFAULT_STALLS,
    DepotArchetype,
    DepotFootprint,
    depot_layout,
    depot_footprint,
    throat_turnout_count,
)

__all__ = [
    "DepotArchetype",
    "DepotFootprint",
    "DEFAULT_STALLS",
    "depot_layout",
    "depot_footprint",
    "depot_bogie_change_bay",
    "throat_turnout_count",
]
