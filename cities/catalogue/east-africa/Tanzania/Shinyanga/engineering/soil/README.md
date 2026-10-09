# Shinyanga civil soil screening

395 route/station sample locations; 395 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 151 |
| fine-soil-plasticity-and-shrink-swell-tests | 395 |
| granular-density-and-groundwater-tests | 395 |

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
| 0..30cm | clay | % | 20–27 | 11–38 | 395 |
| 0..30cm | sand | % | 57–71 | 34–87 | 395 |
| 0..30cm | silt | % | 9–17 | 0–31 | 395 |
| 0..30cm | bd.core | kg/m3 | 1460–1660 | 1320–1890 | 395 |
| 0..30cm | soc | g/kg | 5.9–8 | 3.9–11.3 | 395 |
| 0..30cm | ph.h2o | pH | 6.5–7.6 | 5.3–8.8 | 395 |
| 30..60cm | clay | % | 23–31 | 11–44 | 395 |
| 30..60cm | sand | % | 50–64 | 25–87 | 395 |
| 30..60cm | silt | % | 12–21 | 0–36 | 395 |
| 30..60cm | bd.core | kg/m3 | 1500–1630 | 1320–1880 | 395 |
| 30..60cm | soc | g/kg | 3.7–4.9 | 2.2–7.5 | 395 |
| 30..60cm | ph.h2o | pH | 6.6–7.5 | 5.3–8.6 | 395 |
| 60..100cm | clay | % | 25–32 | 11–48 | 395 |
| 60..100cm | sand | % | 45–61 | 22–85 | 395 |
| 60..100cm | silt | % | 14–23 | 0–38 | 395 |
| 60..100cm | bd.core | kg/m3 | 1470–1580 | 1230–1820 | 395 |
| 60..100cm | soc | g/kg | 3.5–4.3 | 1.7–7.8 | 395 |
| 60..100cm | ph.h2o | pH | 6.7–7.4 | 5.1–8.7 | 395 |
