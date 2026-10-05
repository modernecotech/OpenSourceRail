# Beni-Suef civil soil screening

61 route/station sample locations; 48 complete profiles; 13 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 12 |
| coverage-gap | 13 |
| fine-soil-plasticity-and-shrink-swell-tests | 22 |
| granular-density-and-groundwater-tests | 48 |

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
| 0..30cm | clay | % | 15–23 | 1–40 | 48 |
| 0..30cm | sand | % | 48–66 | 14–91 | 48 |
| 0..30cm | silt | % | 20–29 | 7–44 | 48 |
| 0..30cm | bd.core | kg/m3 | 1310–1490 | 1070–1670 | 48 |
| 0..30cm | soc | g/kg | 2.2–7.9 | 0.5–21.3 | 48 |
| 0..30cm | ph.h2o | pH | 7.2–8.4 | 5.6–9.4 | 48 |
| 30..60cm | clay | % | 13–25 | 2–43 | 48 |
| 30..60cm | sand | % | 48–70 | 14–94 | 48 |
| 30..60cm | silt | % | 17–27 | 4–44 | 48 |
| 30..60cm | bd.core | kg/m3 | 1430–1550 | 1170–1750 | 48 |
| 30..60cm | soc | g/kg | 1.7–6.1 | 0–18.2 | 48 |
| 30..60cm | ph.h2o | pH | 7.1–8.6 | 5–9.8 | 48 |
| 60..100cm | clay | % | 13–25 | 2–42 | 48 |
| 60..100cm | sand | % | 48–70 | 14–94 | 48 |
| 60..100cm | silt | % | 17–27 | 4–45 | 48 |
| 60..100cm | bd.core | kg/m3 | 1470–1620 | 1240–1900 | 48 |
| 60..100cm | soc | g/kg | 1.4–5 | 0.1–13.2 | 48 |
| 60..100cm | ph.h2o | pH | 6.8–8.6 | 3.5–9.8 | 48 |
