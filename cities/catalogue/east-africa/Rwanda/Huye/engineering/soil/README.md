# Huye civil soil screening

457 route/station sample locations; 457 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 457 |
| fine-soil-plasticity-and-shrink-swell-tests | 457 |
| granular-density-and-groundwater-tests | 3 |
| organic-content-and-compressibility-tests | 26 |

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
| 0..30cm | clay | % | 29–38 | 17–47 | 457 |
| 0..30cm | sand | % | 32–45 | 16–72 | 457 |
| 0..30cm | silt | % | 25–31 | 10–42 | 457 |
| 0..30cm | bd.core | kg/m3 | 1160–1320 | 960–1470 | 457 |
| 0..30cm | soc | g/kg | 13–21.6 | 7.9–45.1 | 457 |
| 0..30cm | ph.h2o | pH | 5.3–5.9 | 4.7–6.6 | 457 |
| 30..60cm | clay | % | 30–40 | 18–50 | 457 |
| 30..60cm | sand | % | 32–45 | 14–70 | 457 |
| 30..60cm | silt | % | 23–30 | 5–45 | 457 |
| 30..60cm | bd.core | kg/m3 | 1230–1350 | 1000–1520 | 457 |
| 30..60cm | soc | g/kg | 7.3–13.7 | 3.4–34.7 | 457 |
| 30..60cm | ph.h2o | pH | 5.7–6.2 | 5–7.2 | 457 |
| 60..100cm | clay | % | 31–40 | 17–50 | 457 |
| 60..100cm | sand | % | 32–45 | 15–71 | 457 |
| 60..100cm | silt | % | 22–30 | 5–44 | 457 |
| 60..100cm | bd.core | kg/m3 | 1260–1350 | 1020–1590 | 457 |
| 60..100cm | soc | g/kg | 5.3–16.9 | 2.3–91.9 | 457 |
| 60..100cm | ph.h2o | pH | 6–6.6 | 5–8.1 | 457 |
