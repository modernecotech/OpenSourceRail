# Meerut civil soil screening

3,193 route/station sample locations; 3,193 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 66 |
| fine-soil-plasticity-and-shrink-swell-tests | 3193 |
| granular-density-and-groundwater-tests | 2600 |
| silt-moisture-frost-and-erosion-review | 808 |

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
| 0..30cm | clay | % | 22–29 | 7–43 | 3193 |
| 0..30cm | sand | % | 39–52 | 11–81 | 3193 |
| 0..30cm | silt | % | 26–33 | 11–52 | 3193 |
| 0..30cm | bd.core | kg/m3 | 1340–1560 | 1070–1720 | 3193 |
| 0..30cm | soc | g/kg | 2.7–6.8 | 0.6–18.1 | 3193 |
| 0..30cm | ph.h2o | pH | 6.5–7.4 | 5.3–8.1 | 3193 |
| 30..60cm | clay | % | 23–30 | 6–45 | 3193 |
| 30..60cm | sand | % | 36–49 | 9–83 | 3193 |
| 30..60cm | silt | % | 27–35 | 8–55 | 3193 |
| 30..60cm | bd.core | kg/m3 | 1420–1640 | 1090–1780 | 3193 |
| 30..60cm | soc | g/kg | 1.3–4 | 0.3–7.8 | 3193 |
| 30..60cm | ph.h2o | pH | 6.5–7.6 | 5.3–8 | 3193 |
| 60..100cm | clay | % | 24–30 | 6–46 | 3193 |
| 60..100cm | sand | % | 35–48 | 8–83 | 3193 |
| 60..100cm | silt | % | 27–35 | 5–56 | 3193 |
| 60..100cm | bd.core | kg/m3 | 1510–1700 | 1110–1850 | 3193 |
| 60..100cm | soc | g/kg | 1–2.8 | 0.2–6.5 | 3193 |
| 60..100cm | ph.h2o | pH | 6.5–7.8 | 5.3–8.3 | 3193 |
