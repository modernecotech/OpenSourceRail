# Rolling Stock

This folder contains the handoff documentation for train designs. The
current mid-size-city vehicle is the `light-metro-3car`: a cabless,
driverless, battery-electric trainset with roof solar, identical
multi-part fiberglass end cowls with single panoramic glass faces, LED
headlamps, repeated self-contained cars, one powered bogie and one
trailer bogie per car, high-floor bogie zones, low-floor centre
door/PRM zones, and externally accessed, saloon-isolated side battery enclosures beneath the seat zone for the
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
| Generated design iteration scorecards | [`../../design/component-catalogue/catalog/design-system/`](../../design/component-catalogue/catalog/design-system/) |
| Generated buildable trainset manifest and review | [`../../design/component-catalogue/catalog/buildable-trainset/`](../../design/component-catalogue/catalog/buildable-trainset/) |
| Product-tree definitions for drawing/RFQ/material/process specs | [`../../design/component-catalogue/catalog/buildable-trainset/definitions/index.md`](../../design/component-catalogue/catalog/buildable-trainset/definitions/index.md) |
| Unsigned shop traveler templates with process controls | [`../../design/component-catalogue/catalog/buildable-trainset/travelers/index.md`](../../design/component-catalogue/catalog/buildable-trainset/travelers/index.md) |
| Canonical parametric source | [`../../design/component-catalogue/src/osr_mech/rolling_stock/`](../../design/component-catalogue/src/osr_mech/rolling_stock/) |
| Generated FreeCAD review artifacts | [`../../design/component-catalogue/models/cad/`](../../design/component-catalogue/models/cad/) |
| Concept image | [`../assets/solar-metro-trainset.png`](../assets/solar-metro-trainset.png) |
| Control-electronics integration matrix | [`../../control-electronics/rolling-stock-integration.md`](../../control-electronics/rolling-stock-integration.md) |
| Interior COTS catalogue | [`../../control-electronics/trainset-interiors.md`](../../control-electronics/trainset-interiors.md) |
