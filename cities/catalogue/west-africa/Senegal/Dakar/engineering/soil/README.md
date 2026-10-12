# Dakar civil soil screening

6,845 route/station sample locations; 6,835 complete profiles; 10 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 6765 |
| coverage-gap | 10 |
| fine-soil-plasticity-and-shrink-swell-tests | 61 |
| granular-density-and-groundwater-tests | 6835 |

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
| 0..30cm | clay | % | 6–18 | 0–34 | 6835 |
| 0..30cm | sand | % | 57–82 | 23–92 | 6835 |
| 0..30cm | silt | % | 12–27 | 3–44 | 6835 |
| 0..30cm | bd.core | kg/m3 | 1250–1500 | 970–1730 | 6835 |
| 0..30cm | soc | g/kg | 3–9.1 | 0.9–24.2 | 6835 |
| 0..30cm | ph.h2o | pH | 5.6–7.5 | 3.2–8.5 | 6835 |
| 30..60cm | clay | % | 6–18 | 0–36 | 6835 |
| 30..60cm | sand | % | 56–83 | 22–92 | 6835 |
| 30..60cm | silt | % | 11–27 | 2–43 | 6835 |
| 30..60cm | bd.core | kg/m3 | 1200–1530 | 910–1770 | 6835 |
| 30..60cm | soc | g/kg | 2.7–6.8 | 0.5–40.9 | 6835 |
| 30..60cm | ph.h2o | pH | 5.2–7.7 | 3.3–9.1 | 6835 |
| 60..100cm | clay | % | 6–19 | 0–37 | 6835 |
| 60..100cm | sand | % | 55–84 | 22–93 | 6835 |
| 60..100cm | silt | % | 10–27 | 3–44 | 6835 |
| 60..100cm | bd.core | kg/m3 | 1120–1560 | 710–1820 | 6835 |
| 60..100cm | soc | g/kg | 1.9–6.3 | 0.4–30.4 | 6835 |
| 60..100cm | ph.h2o | pH | 5.4–7.7 | 3.6–9.3 | 6835 |
