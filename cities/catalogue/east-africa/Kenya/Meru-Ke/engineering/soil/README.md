# Meru-Ke civil soil screening

65 route/station sample locations; 65 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 33 |
| fine-soil-plasticity-and-shrink-swell-tests | 65 |
| granular-density-and-groundwater-tests | 5 |
| organic-content-and-compressibility-tests | 4 |
| silt-moisture-frost-and-erosion-review | 3 |

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
| 0..30cm | clay | % | 24–40 | 15–52 | 65 |
| 0..30cm | sand | % | 27–56 | 8–76 | 65 |
| 0..30cm | silt | % | 20–33 | 10–48 | 65 |
| 0..30cm | bd.core | kg/m3 | 1070–1220 | 860–1430 | 65 |
| 0..30cm | soc | g/kg | 8.8–28.9 | 3.8–67 | 65 |
| 0..30cm | ph.h2o | pH | 5.4–6.8 | 4.7–8 | 65 |
| 30..60cm | clay | % | 25–41 | 14–54 | 65 |
| 30..60cm | sand | % | 25–49 | 6–69 | 65 |
| 30..60cm | silt | % | 24–35 | 10–49 | 65 |
| 30..60cm | bd.core | kg/m3 | 1090–1230 | 780–1460 | 65 |
| 30..60cm | soc | g/kg | 6.7–14.3 | 2.6–25.8 | 65 |
| 30..60cm | ph.h2o | pH | 5.3–6.9 | 4.7–7.9 | 65 |
| 60..100cm | clay | % | 27–41 | 14–54 | 65 |
| 60..100cm | sand | % | 25–44 | 5–70 | 65 |
| 60..100cm | silt | % | 27–35 | 7–51 | 65 |
| 60..100cm | bd.core | kg/m3 | 1110–1210 | 800–1510 | 65 |
| 60..100cm | soc | g/kg | 5.6–8.9 | 1.8–17.5 | 65 |
| 60..100cm | ph.h2o | pH | 5.4–6.9 | 4.5–8 | 65 |
