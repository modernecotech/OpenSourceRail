# Gujranwala civil soil screening

340 route/station sample locations; 340 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 340 |
| granular-density-and-groundwater-tests | 252 |
| silt-moisture-frost-and-erosion-review | 15 |

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
| 0..30cm | clay | % | 20–29 | 5–43 | 340 |
| 0..30cm | sand | % | 43–55 | 12–81 | 340 |
| 0..30cm | silt | % | 24–32 | 8–48 | 340 |
| 0..30cm | bd.core | kg/m3 | 1290–1500 | 1030–1670 | 340 |
| 0..30cm | soc | g/kg | 3.6–8.5 | 0.7–22.4 | 340 |
| 0..30cm | ph.h2o | pH | 7.1–7.5 | 6–8.3 | 340 |
| 30..60cm | clay | % | 21–30 | 2–44 | 340 |
| 30..60cm | sand | % | 40–55 | 13–85 | 340 |
| 30..60cm | silt | % | 25–33 | 2–52 | 340 |
| 30..60cm | bd.core | kg/m3 | 1450–1610 | 1170–1780 | 340 |
| 30..60cm | soc | g/kg | 1.8–4.7 | 0.3–12.4 | 340 |
| 30..60cm | ph.h2o | pH | 7.2–7.6 | 6.2–8.3 | 340 |
| 60..100cm | clay | % | 21–31 | 3–44 | 340 |
| 60..100cm | sand | % | 37–54 | 8–84 | 340 |
| 60..100cm | silt | % | 24–34 | 3–53 | 340 |
| 60..100cm | bd.core | kg/m3 | 1530–1680 | 1240–1870 | 340 |
| 60..100cm | soc | g/kg | 1.3–3.2 | 0.2–7.8 | 340 |
| 60..100cm | ph.h2o | pH | 7.2–7.6 | 6.4–8.4 | 340 |
