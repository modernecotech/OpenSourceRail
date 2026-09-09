# Asyut civil soil screening

99 route/station sample locations; 94 complete profiles; 5 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 15 |
| coverage-gap | 5 |
| fine-soil-plasticity-and-shrink-swell-tests | 93 |
| granular-density-and-groundwater-tests | 94 |

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
| 0..30cm | clay | % | 16–27 | 2–41 | 94 |
| 0..30cm | sand | % | 40–63 | 12–90 | 94 |
| 0..30cm | silt | % | 21–33 | 7–49 | 94 |
| 0..30cm | bd.core | kg/m3 | 1410–1520 | 1160–1710 | 94 |
| 0..30cm | soc | g/kg | 3.3–7.8 | 0.7–21.4 | 94 |
| 0..30cm | ph.h2o | pH | 7.1–8.4 | 5.7–9.4 | 94 |
| 30..60cm | clay | % | 19–29 | 2–43 | 94 |
| 30..60cm | sand | % | 39–60 | 12–92 | 94 |
| 30..60cm | silt | % | 21–31 | 5–46 | 94 |
| 30..60cm | bd.core | kg/m3 | 1440–1580 | 1170–1750 | 94 |
| 30..60cm | soc | g/kg | 2.2–6.5 | 0–38.3 | 94 |
| 30..60cm | ph.h2o | pH | 7.2–8.7 | 5.2–9.8 | 94 |
| 60..100cm | clay | % | 18–29 | 1–43 | 94 |
| 60..100cm | sand | % | 39–59 | 12–92 | 94 |
| 60..100cm | silt | % | 22–31 | 5–47 | 94 |
| 60..100cm | bd.core | kg/m3 | 1480–1640 | 1210–1910 | 94 |
| 60..100cm | soc | g/kg | 1.9–4.8 | 0.2–38.3 | 94 |
| 60..100cm | ph.h2o | pH | 7–8.7 | 3.6–9.9 | 94 |
