# Polokwane civil soil screening

101 route/station sample locations; 101 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 101 |
| granular-density-and-groundwater-tests | 68 |

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
| 0..30cm | clay | % | 29–37 | 16–52 | 101 |
| 0..30cm | sand | % | 43–56 | 15–80 | 101 |
| 0..30cm | silt | % | 14–21 | 0–33 | 101 |
| 0..30cm | bd.core | kg/m3 | 1270–1430 | 1090–1600 | 101 |
| 0..30cm | soc | g/kg | 5.8–16.5 | 3–34.9 | 101 |
| 0..30cm | ph.h2o | pH | 6.6–7.8 | 5.9–8.4 | 101 |
| 30..60cm | clay | % | 32–40 | 16–56 | 101 |
| 30..60cm | sand | % | 41–54 | 14–78 | 101 |
| 30..60cm | silt | % | 12–20 | 0–34 | 101 |
| 30..60cm | bd.core | kg/m3 | 1340–1480 | 1080–1680 | 101 |
| 30..60cm | soc | g/kg | 3.7–7.4 | 1.9–13.4 | 101 |
| 30..60cm | ph.h2o | pH | 6.8–7.9 | 5.9–8.7 | 101 |
| 60..100cm | clay | % | 33–41 | 14–58 | 101 |
| 60..100cm | sand | % | 39–53 | 14–77 | 101 |
| 60..100cm | silt | % | 13–21 | 0–36 | 101 |
| 60..100cm | bd.core | kg/m3 | 1340–1530 | 870–1740 | 101 |
| 60..100cm | soc | g/kg | 2.5–6.2 | 1.1–12.3 | 101 |
| 60..100cm | ph.h2o | pH | 7–7.9 | 5.9–8.8 | 101 |
