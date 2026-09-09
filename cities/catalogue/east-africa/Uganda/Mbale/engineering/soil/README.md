# Mbale civil soil screening

114 route/station sample locations; 114 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 64 |
| fine-soil-plasticity-and-shrink-swell-tests | 114 |
| granular-density-and-groundwater-tests | 21 |
| organic-content-and-compressibility-tests | 5 |
| silt-moisture-frost-and-erosion-review | 18 |

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
| 0..30cm | clay | % | 26–34 | 14–44 | 114 |
| 0..30cm | sand | % | 34–48 | 15–70 | 114 |
| 0..30cm | silt | % | 25–33 | 11–52 | 114 |
| 0..30cm | bd.core | kg/m3 | 1020–1200 | 790–1430 | 114 |
| 0..30cm | soc | g/kg | 8.7–30.2 | 4.4–53.4 | 114 |
| 0..30cm | ph.h2o | pH | 5.6–6.6 | 4.7–7.6 | 114 |
| 30..60cm | clay | % | 29–36 | 12–49 | 114 |
| 30..60cm | sand | % | 33–49 | 14–74 | 114 |
| 30..60cm | silt | % | 21–32 | 3–52 | 114 |
| 30..60cm | bd.core | kg/m3 | 1090–1230 | 850–1440 | 114 |
| 30..60cm | soc | g/kg | 5.9–12.9 | 2.6–23.2 | 114 |
| 30..60cm | ph.h2o | pH | 5.6–6.6 | 4.7–7.6 | 114 |
| 60..100cm | clay | % | 29–38 | 11–52 | 114 |
| 60..100cm | sand | % | 31–49 | 10–78 | 114 |
| 60..100cm | silt | % | 20–33 | 0–53 | 114 |
| 60..100cm | bd.core | kg/m3 | 1120–1240 | 850–1450 | 114 |
| 60..100cm | soc | g/kg | 4.8–9.9 | 1.8–32.8 | 114 |
| 60..100cm | ph.h2o | pH | 5.6–6.7 | 4.7–7.6 | 114 |
