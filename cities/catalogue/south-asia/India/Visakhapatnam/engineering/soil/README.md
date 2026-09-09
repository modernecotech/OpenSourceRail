# Visakhapatnam civil soil screening

443 route/station sample locations; 441 complete profiles; 2 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 1 |
| coverage-gap | 2 |
| fine-soil-plasticity-and-shrink-swell-tests | 441 |
| granular-density-and-groundwater-tests | 435 |

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
| 0..30cm | clay | % | 21–33 | 4–48 | 441 |
| 0..30cm | sand | % | 37–59 | 9–89 | 441 |
| 0..30cm | silt | % | 18–31 | 2–49 | 441 |
| 0..30cm | bd.core | kg/m3 | 1130–1510 | 890–1700 | 441 |
| 0..30cm | soc | g/kg | 4.8–14 | 1.4–37.7 | 441 |
| 0..30cm | ph.h2o | pH | 6.5–7.3 | 5.5–8.3 | 441 |
| 30..60cm | clay | % | 22–34 | 2–52 | 441 |
| 30..60cm | sand | % | 36–61 | 6–93 | 441 |
| 30..60cm | silt | % | 17–29 | 0–49 | 441 |
| 30..60cm | bd.core | kg/m3 | 1150–1520 | 690–1770 | 441 |
| 30..60cm | soc | g/kg | 3–8.2 | 0.9–26.4 | 441 |
| 30..60cm | ph.h2o | pH | 6.8–7.5 | 5.5–8.5 | 441 |
| 60..100cm | clay | % | 22–34 | 2–51 | 441 |
| 60..100cm | sand | % | 37–61 | 6–93 | 441 |
| 60..100cm | silt | % | 17–29 | 0–49 | 441 |
| 60..100cm | bd.core | kg/m3 | 1040–1510 | 460–1820 | 441 |
| 60..100cm | soc | g/kg | 2.3–8.4 | 0.7–27.9 | 441 |
| 60..100cm | ph.h2o | pH | 6.9–7.6 | 5.3–8.7 | 441 |
