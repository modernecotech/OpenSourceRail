# Durban civil soil screening

3,409 route/station sample locations; 3,404 complete profiles; 5 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 3317 |
| coverage-gap | 5 |
| fine-soil-plasticity-and-shrink-swell-tests | 3346 |
| granular-density-and-groundwater-tests | 3400 |
| organic-content-and-compressibility-tests | 51 |

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
| 0..30cm | clay | % | 16–31 | 1–46 | 3404 |
| 0..30cm | sand | % | 45–74 | 6–98 | 3404 |
| 0..30cm | silt | % | 10–25 | 0–46 | 3404 |
| 0..30cm | bd.core | kg/m3 | 920–1330 | 580–1530 | 3404 |
| 0..30cm | soc | g/kg | 4.1–29.6 | 1.3–72.4 | 3404 |
| 0..30cm | ph.h2o | pH | 5.4–7.3 | 4.7–8.3 | 3404 |
| 30..60cm | clay | % | 18–36 | 1–51 | 3404 |
| 30..60cm | sand | % | 43–74 | 8–98 | 3404 |
| 30..60cm | silt | % | 7–24 | 0–45 | 3404 |
| 30..60cm | bd.core | kg/m3 | 970–1450 | 660–1670 | 3404 |
| 30..60cm | soc | g/kg | 2.4–16.8 | 0.5–43 | 3404 |
| 30..60cm | ph.h2o | pH | 5.6–7.3 | 4.8–8.5 | 3404 |
| 60..100cm | clay | % | 17–37 | 1–52 | 3404 |
| 60..100cm | sand | % | 41–75 | 6–98 | 3404 |
| 60..100cm | silt | % | 6–24 | 0–47 | 3404 |
| 60..100cm | bd.core | kg/m3 | 960–1500 | 380–1740 | 3404 |
| 60..100cm | soc | g/kg | 1.7–11.9 | 0.2–36.8 | 3404 |
| 60..100cm | ph.h2o | pH | 5.8–7.4 | 4.5–8.8 | 3404 |
