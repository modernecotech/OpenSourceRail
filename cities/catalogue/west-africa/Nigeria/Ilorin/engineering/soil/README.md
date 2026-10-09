# Ilorin civil soil screening

763 route/station sample locations; 763 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 763 |
| fine-soil-plasticity-and-shrink-swell-tests | 647 |
| granular-density-and-groundwater-tests | 763 |
| silt-moisture-frost-and-erosion-review | 2 |

- No bearing capacity, CBR, friction angle, cohesion, groundwater, contamination, sulfate/chloride or deep stratigraphy is inferred from these maps.
- Desert, water, urban fill and other nodata remain unknown; no nearest-pixel or climate-based substitution.
- Texture fractions are independent predictions; they are not renormalised or converted to a geotechnical soil class.
- Prioritisation thresholds are editable OSR screening rules, not statutory limits or evidence of a hazard.
- No excavation depths, foundation dimensions, treatment quantities or civil costs are changed from pedological predictions.

Source: [OpenLandMap soilDB](https://github.com/openlandmap/soildb), Hengl et al., DOI 10.5194/essd-2025-336, CC BY 4.0. Exact source revision, URLs and raster metadata are retained in the receipt.

## Sampled property ranges

Ranges below span the sampled locations; they are not a city-wide characteristic soil value. The uncertainty envelope spans the lowest p16 to highest p84.

| Depth | Property | Unit | Mean range | Uncertainty envelope | Available locations |
|---|---|---|---:|---:|---:|
| 0..30cm | clay | % | 18–23 | 6–38 | 763 |
| 0..30cm | sand | % | 52–62 | 22–85 | 763 |
| 0..30cm | silt | % | 18–27 | 3–44 | 763 |
| 0..30cm | bd.core | kg/m3 | 1410–1540 | 1220–1650 | 763 |
| 0..30cm | soc | g/kg | 5–10 | 2.3–16.5 | 763 |
| 0..30cm | ph.h2o | pH | 6–6.3 | 5.3–7.3 | 763 |
| 30..60cm | clay | % | 20–26 | 8–40 | 763 |
| 30..60cm | sand | % | 46–60 | 19–81 | 763 |
| 30..60cm | silt | % | 18–29 | 3–45 | 763 |
| 30..60cm | bd.core | kg/m3 | 1440–1550 | 1240–1760 | 763 |
| 30..60cm | soc | g/kg | 3.4–5.6 | 1.2–11.1 | 763 |
| 30..60cm | ph.h2o | pH | 5.8–6.1 | 5.2–7 | 763 |
| 60..100cm | clay | % | 22–28 | 8–42 | 763 |
| 60..100cm | sand | % | 42–58 | 16–85 | 763 |
| 60..100cm | silt | % | 19–29 | 2–50 | 763 |
| 60..100cm | bd.core | kg/m3 | 1480–1610 | 1250–1810 | 763 |
| 60..100cm | soc | g/kg | 2.3–4.5 | 0.4–8.8 | 763 |
| 60..100cm | ph.h2o | pH | 5.6–6.1 | 5–7.4 | 763 |
