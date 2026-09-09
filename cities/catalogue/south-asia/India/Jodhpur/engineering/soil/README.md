# Jodhpur civil soil screening

303 route/station sample locations; 303 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 1 |
| fine-soil-plasticity-and-shrink-swell-tests | 272 |
| granular-density-and-groundwater-tests | 303 |

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
| 0..30cm | clay | % | 15–27 | 4–41 | 303 |
| 0..30cm | sand | % | 45–69 | 16–90 | 303 |
| 0..30cm | silt | % | 16–28 | 4–46 | 303 |
| 0..30cm | bd.core | kg/m3 | 1440–1520 | 1240–1680 | 303 |
| 0..30cm | soc | g/kg | 3–6 | 1.1–12.6 | 303 |
| 0..30cm | ph.h2o | pH | 7.1–8.2 | 5.1–8.9 | 303 |
| 30..60cm | clay | % | 17–28 | 3–43 | 303 |
| 30..60cm | sand | % | 45–65 | 12–91 | 303 |
| 30..60cm | silt | % | 18–28 | 1–46 | 303 |
| 30..60cm | bd.core | kg/m3 | 1430–1530 | 1150–1740 | 303 |
| 30..60cm | soc | g/kg | 2–3.5 | 0.5–7 | 303 |
| 30..60cm | ph.h2o | pH | 7.2–8.5 | 5.1–9.3 | 303 |
| 60..100cm | clay | % | 18–27 | 2–44 | 303 |
| 60..100cm | sand | % | 46–64 | 13–91 | 303 |
| 60..100cm | silt | % | 18–27 | 0–48 | 303 |
| 60..100cm | bd.core | kg/m3 | 1430–1540 | 1120–1770 | 303 |
| 60..100cm | soc | g/kg | 1.5–2.8 | 0.1–7.6 | 303 |
| 60..100cm | ph.h2o | pH | 7.2–8.7 | 5.1–9.8 | 303 |
