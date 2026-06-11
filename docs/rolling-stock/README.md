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
| [`light-metro-3car/`](light-metro-3car/) | General arrangement, fiberglass end cowl, body, bogie, traction, interfaces, BOM, fabrication plan, compliance, and drawing register |

## Related Artifacts

| Artifact | Location |
|---|---|
| Generated CAD screenshots | [`../screenshots/`](../screenshots/) |
| Canonical parametric source | [`../../mechanical-py/src/osr_mech/rolling_stock/`](../../mechanical-py/src/osr_mech/rolling_stock/) |
| Generated FreeCAD review artifacts | [`../../mechanical-py/catalog/freecad/`](../../mechanical-py/catalog/freecad/) |
| Concept image | [`../assets/solar-metro-trainset.png`](../assets/solar-metro-trainset.png) |
| Hardware integration matrix | [`../../hardware/rolling-stock-integration.md`](../../hardware/rolling-stock-integration.md) |
| Interior COTS catalogue | [`../../hardware/trainset-interiors/cots-catalogue.md`](../../hardware/trainset-interiors/cots-catalogue.md) |
