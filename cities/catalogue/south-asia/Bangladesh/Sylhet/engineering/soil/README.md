# Sylhet civil soil screening

345 route/station sample locations; 345 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 345 |
| fine-soil-plasticity-and-shrink-swell-tests | 345 |
| granular-density-and-groundwater-tests | 268 |
| organic-content-and-compressibility-tests | 105 |

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
| 0..30cm | clay | % | 24–31 | 11–49 | 345 |
| 0..30cm | sand | % | 40–53 | 14–77 | 345 |
| 0..30cm | silt | % | 22–30 | 7–46 | 345 |
| 0..30cm | bd.core | kg/m3 | 830–1080 | 440–1340 | 345 |
| 0..30cm | soc | g/kg | 11.4–24.3 | 3.4–96.2 | 345 |
| 0..30cm | ph.h2o | pH | 5.4–5.9 | 4.5–7.2 | 345 |
| 30..60cm | clay | % | 25–32 | 8–49 | 345 |
| 30..60cm | sand | % | 38–53 | 11–81 | 345 |
| 30..60cm | silt | % | 22–31 | 4–47 | 345 |
| 30..60cm | bd.core | kg/m3 | 860–1150 | 490–1470 | 345 |
| 30..60cm | soc | g/kg | 6.3–17 | 1.9–52.9 | 345 |
| 30..60cm | ph.h2o | pH | 5.7–6.1 | 4.6–7.3 | 345 |
| 60..100cm | clay | % | 26–33 | 8–50 | 345 |
| 60..100cm | sand | % | 37–51 | 10–80 | 345 |
| 60..100cm | silt | % | 23–31 | 4–47 | 345 |
| 60..100cm | bd.core | kg/m3 | 860–1160 | 360–1490 | 345 |
| 60..100cm | soc | g/kg | 5.1–13.8 | 1.3–63.3 | 345 |
| 60..100cm | ph.h2o | pH | 5.8–6.1 | 4.6–7.3 | 345 |
