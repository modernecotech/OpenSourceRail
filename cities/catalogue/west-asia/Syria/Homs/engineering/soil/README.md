# Homs civil soil screening

485 route/station sample locations; 485 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 485 |
| granular-density-and-groundwater-tests | 23 |
| silt-moisture-frost-and-erosion-review | 330 |

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
| 0..30cm | clay | % | 25–32 | 11–43 | 485 |
| 0..30cm | sand | % | 29–44 | 9–73 | 485 |
| 0..30cm | silt | % | 32–40 | 15–56 | 485 |
| 0..30cm | bd.core | kg/m3 | 1370–1440 | 1160–1620 | 485 |
| 0..30cm | soc | g/kg | 3–11.6 | 1.5–23.2 | 485 |
| 0..30cm | ph.h2o | pH | 7.5–7.9 | 6.9–8.4 | 485 |
| 30..60cm | clay | % | 27–34 | 10–46 | 485 |
| 30..60cm | sand | % | 28–42 | 7–76 | 485 |
| 30..60cm | silt | % | 31–38 | 14–52 | 485 |
| 30..60cm | bd.core | kg/m3 | 1460–1590 | 1250–1740 | 485 |
| 30..60cm | soc | g/kg | 2.2–5.2 | 0.6–9.7 | 485 |
| 30..60cm | ph.h2o | pH | 7.3–7.9 | 6.2–8.5 | 485 |
| 60..100cm | clay | % | 27–35 | 10–49 | 485 |
| 60..100cm | sand | % | 29–43 | 5–76 | 485 |
| 60..100cm | silt | % | 30–36 | 11–52 | 485 |
| 60..100cm | bd.core | kg/m3 | 1470–1620 | 1240–1850 | 485 |
| 60..100cm | soc | g/kg | 1.7–3.5 | 0.4–7.1 | 485 |
| 60..100cm | ph.h2o | pH | 7.2–7.9 | 6.4–8.6 | 485 |
