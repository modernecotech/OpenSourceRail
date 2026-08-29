# Rolling Stock

This folder contains the handoff documentation for train designs. The
current mid-size-city vehicle is the `light-metro-3car`: a cabless,
driverless, battery-electric trainset with roof solar, identical
multi-part fiberglass end cowls with single panoramic glass faces, LED
headlamps, repeated self-contained cars, one powered bogie and one
trailer bogie per car, high-floor bogie zones, low-floor centre
door/PRM zones, and under-seat batteries for the
300 k to 1 M population networks. Samawah is one generated instance of
this shared family, not the reason the family exists.

## Packages

| Package | Scope |
|---|---|
| [`design-system.md`](design-system.md) | Top-down / bottom-up design hierarchy and automatic candidate-iteration loop |
| [`light-metro-3car/`](light-metro-3car/) | General arrangement, fiberglass end cowl, body, bogie, traction, interfaces, BOM, fabrication plan, compliance, and drawing register |

## Related Artifacts

Use the generated buildable package as the practical handoff from this
documentation to drawing, RFQ, shop routing, QA, and first-article
planning: manifest first, definitions for drawing/RFQ, travelers for
operation routing, material/process control, and signoff templates.

| Artifact | Location |
|---|---|
| Generated CAD screenshots | [`../screenshots/`](../screenshots/) |
| Generated design iteration scorecards | [`../../mechanical-py/catalog/design-system/`](../../mechanical-py/catalog/design-system/) |
| Generated buildable trainset manifest and review | [`../../mechanical-py/catalog/buildable-trainset/`](../../mechanical-py/catalog/buildable-trainset/) |
| Product-tree definitions for drawing/RFQ/material/process specs | [`../../mechanical-py/catalog/buildable-trainset/definitions/index.md`](../../mechanical-py/catalog/buildable-trainset/definitions/index.md) |
| Unsigned shop traveler templates with process controls | [`../../mechanical-py/catalog/buildable-trainset/travelers/index.md`](../../mechanical-py/catalog/buildable-trainset/travelers/index.md) |
| Canonical parametric source | [`../../mechanical-py/src/osr_mech/rolling_stock/`](../../mechanical-py/src/osr_mech/rolling_stock/) |
| Generated FreeCAD review artifacts | [`../../mechanical-py/catalog/freecad/`](../../mechanical-py/catalog/freecad/) |
| Concept image | [`../assets/solar-metro-trainset.png`](../assets/solar-metro-trainset.png) |
| Hardware integration matrix | [`../../hardware/rolling-stock-integration.md`](../../hardware/rolling-stock-integration.md) |
| Interior COTS catalogue | [`../../hardware/trainset-interiors.md`](../../hardware/trainset-interiors.md) |
