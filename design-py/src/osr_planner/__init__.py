"""`osr_planner` — auto-generate an OSR urban-rail network for any city.

Inputs: a bounding box + slug + population estimate.
Outputs: a `design.toml` with stations + lines + fleets + depots,
ready to feed into `osr_scenario` to generate the sim scenario,
and into `osr_scenario.render_map` to draw the network.

The planner optimises for three criteria:

1. **Low curvature** — stations on a line are ordered by PCA
   projection (monotonic along the line's principal axis, kills
   zigzags). Inter-station routing penalises turns in the
   weighted shortest-path.
2. **Coverage maximisation** — station count is sized from
   population. Placement is greedy on a demand-density grid
   (OSM neighbourhood anchors, weighted) with a minimum-spacing
   rule to avoid redundant stations.
3. **Transfer minimisation** — stations are clustered into lines
   with K-means, then each line's path is chosen so all lines
   route through 1–2 common hub stations (interchanges).

Every step is deterministic given the same OSM cache + seed, so
500-city batches produce the same artefacts on re-runs.
"""

from .anchors import Anchor, fetch_anchors, weight_anchors
from .emit import design_toml
from .lines import LinePlan, plan_lines, plan_straight_network
from .planner import CityInputs, NetworkPlan, plan_city
from .stations import StationCandidate, place_stations

__all__ = [
    "Anchor",
    "CityInputs",
    "LinePlan",
    "NetworkPlan",
    "StationCandidate",
    "design_toml",
    "fetch_anchors",
    "place_stations",
    "plan_city",
    "plan_lines",
    "plan_straight_network",
    "weight_anchors",
]
