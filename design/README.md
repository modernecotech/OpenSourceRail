# Design Sources

The active v0.5 physical design sources are in [engineering/ferrite_maglev](../engineering/ferrite_maglev/README.md). The component catalogue and wheel/rail synthesis interfaces below are retained references. Maglev support, linear propulsion, capture, braking, evacuation and civil interfaces require their own geometry and verification; an old component is not adopted by renaming it.

This domain contains reusable design logic, not individual city revisions or
site-approved engineering.

| Area | Authority | Main outputs |
|---|---|---|
| [`city-generation/`](city-generation/README.md) | GIS ingestion, demand/buildability rasters, route and station synthesis, scenario generation | Candidate city networks and simulator inputs |
| [`component-catalogue/`](component-catalogue/README.md) | Parametric rolling-stock, track, station, depot and reusable civil components | CAD review models, product trees, BOMs and manufacturing templates |

Editable projects are under [`../cities/workspaces/`](../cities/workspaces/README.md).
Published city results are under [`../cities/catalogue/`](../cities/catalogue/README.md).
Federated BIM and engineering validation are under
[`../engineering/`](../engineering/README.md).
