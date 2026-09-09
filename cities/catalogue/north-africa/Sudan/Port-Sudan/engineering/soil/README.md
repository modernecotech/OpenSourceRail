# Port-Sudan civil soil screening

67 route/station sample locations; 67 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| granular-density-and-groundwater-tests | 67 |

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
| 0..30cm | clay | % | 10–18 | 1–30 | 67 |
| 0..30cm | sand | % | 58–74 | 35–90 | 67 |
| 0..30cm | silt | % | 16–24 | 4–38 | 67 |
| 0..30cm | bd.core | kg/m3 | 1440–1510 | 1200–1700 | 67 |
| 0..30cm | soc | g/kg | 2–3.2 | 0.4–9.1 | 67 |
| 0..30cm | ph.h2o | pH | 7.8–8.7 | 6.7–9.4 | 67 |
| 30..60cm | clay | % | 13–19 | 0–32 | 67 |
| 30..60cm | sand | % | 57–71 | 32–91 | 67 |
| 30..60cm | silt | % | 16–24 | 4–37 | 67 |
| 30..60cm | bd.core | kg/m3 | 1430–1540 | 1220–1750 | 67 |
| 30..60cm | soc | g/kg | 1–2.1 | 0–5.8 | 67 |
| 30..60cm | ph.h2o | pH | 7.9–8.9 | 6.6–9.5 | 67 |
| 60..100cm | clay | % | 13–21 | 1–34 | 67 |
| 60..100cm | sand | % | 55–71 | 27–92 | 67 |
| 60..100cm | silt | % | 16–25 | 3–41 | 67 |
| 60..100cm | bd.core | kg/m3 | 1400–1560 | 1220–1810 | 67 |
| 60..100cm | soc | g/kg | 0.9–2 | 0–4.9 | 67 |
| 60..100cm | ph.h2o | pH | 8–9 | 6.6–9.9 | 67 |
