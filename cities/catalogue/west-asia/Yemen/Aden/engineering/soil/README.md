# Aden civil soil screening

73 route/station sample locations; 26 complete profiles; 47 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 47 |
| granular-density-and-groundwater-tests | 26 |

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
| 0..30cm | clay | % | 11–16 | 0–29 | 26 |
| 0..30cm | sand | % | 63–71 | 28–95 | 26 |
| 0..30cm | silt | % | 17–21 | 2–38 | 26 |
| 0..30cm | bd.core | kg/m3 | 1400–1470 | 1050–1710 | 26 |
| 0..30cm | soc | g/kg | 2.4–6.8 | 0.6–20.4 | 26 |
| 0..30cm | ph.h2o | pH | 8.4–8.8 | 7.6–9.5 | 26 |
| 30..60cm | clay | % | 12–18 | 0–34 | 26 |
| 30..60cm | sand | % | 60–70 | 26–95 | 26 |
| 30..60cm | silt | % | 16–22 | 0–41 | 26 |
| 30..60cm | bd.core | kg/m3 | 1410–1530 | 1090–1700 | 26 |
| 30..60cm | soc | g/kg | 1.6–6.9 | 0–42 | 26 |
| 30..60cm | ph.h2o | pH | 8.3–8.8 | 7.4–9.5 | 26 |
| 60..100cm | clay | % | 13–19 | 0–34 | 26 |
| 60..100cm | sand | % | 59–69 | 27–94 | 26 |
| 60..100cm | silt | % | 17–22 | 0–41 | 26 |
| 60..100cm | bd.core | kg/m3 | 1310–1550 | 750–1760 | 26 |
| 60..100cm | soc | g/kg | 1.3–5 | 0.1–34 | 26 |
| 60..100cm | ph.h2o | pH | 8.4–8.9 | 7.5–9.5 | 26 |
