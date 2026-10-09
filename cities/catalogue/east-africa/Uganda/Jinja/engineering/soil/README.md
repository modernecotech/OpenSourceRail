# Jinja civil soil screening

956 route/station sample locations; 927 complete profiles; 29 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 927 |
| coverage-gap | 29 |
| fine-soil-plasticity-and-shrink-swell-tests | 927 |
| granular-density-and-groundwater-tests | 31 |

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
| 0..30cm | clay | % | 33–49 | 18–56 | 927 |
| 0..30cm | sand | % | 21–43 | 9–65 | 927 |
| 0..30cm | silt | % | 23–33 | 7–43 | 927 |
| 0..30cm | bd.core | kg/m3 | 950–1260 | 570–1500 | 927 |
| 0..30cm | soc | g/kg | 10.3–28 | 4.3–49 | 927 |
| 0..30cm | ph.h2o | pH | 5.4–6.4 | 4.7–7.5 | 927 |
| 30..60cm | clay | % | 37–53 | 20–61 | 927 |
| 30..60cm | sand | % | 20–43 | 6–72 | 927 |
| 30..60cm | silt | % | 20–31 | 3–45 | 927 |
| 30..60cm | bd.core | kg/m3 | 1020–1290 | 620–1490 | 927 |
| 30..60cm | soc | g/kg | 5.2–12.9 | 1.8–23.4 | 927 |
| 30..60cm | ph.h2o | pH | 5.5–6.4 | 4.7–7.7 | 927 |
| 60..100cm | clay | % | 37–53 | 18–61 | 927 |
| 60..100cm | sand | % | 19–43 | 4–74 | 927 |
| 60..100cm | silt | % | 20–31 | 3–46 | 927 |
| 60..100cm | bd.core | kg/m3 | 1040–1300 | 600–1570 | 927 |
| 60..100cm | soc | g/kg | 3.9–11.2 | 1.4–26.1 | 927 |
| 60..100cm | ph.h2o | pH | 5.5–6.4 | 4.6–7.8 | 927 |
