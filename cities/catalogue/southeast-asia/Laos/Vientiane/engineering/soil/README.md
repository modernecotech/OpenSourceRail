# Vientiane civil soil screening

1,021 route/station sample locations; 1,020 complete profiles; 1 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 1020 |
| coverage-gap | 1 |
| fine-soil-plasticity-and-shrink-swell-tests | 1020 |
| granular-density-and-groundwater-tests | 756 |
| silt-moisture-frost-and-erosion-review | 418 |

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
| 0..30cm | clay | % | 19–31 | 1–45 | 1020 |
| 0..30cm | sand | % | 32–58 | 6–93 | 1020 |
| 0..30cm | silt | % | 23–37 | 2–55 | 1020 |
| 0..30cm | bd.core | kg/m3 | 1080–1400 | 830–1600 | 1020 |
| 0..30cm | soc | g/kg | 5.7–14.6 | 2.4–33.6 | 1020 |
| 0..30cm | ph.h2o | pH | 5.8–6.2 | 4.7–7.6 | 1020 |
| 30..60cm | clay | % | 21–32 | 3–44 | 1020 |
| 30..60cm | sand | % | 32–55 | 5–91 | 1020 |
| 30..60cm | silt | % | 24–37 | 1–55 | 1020 |
| 30..60cm | bd.core | kg/m3 | 1130–1450 | 760–1680 | 1020 |
| 30..60cm | soc | g/kg | 3.6–9.8 | 1.3–28.2 | 1020 |
| 30..60cm | ph.h2o | pH | 5.9–6.3 | 4.9–7.9 | 1020 |
| 60..100cm | clay | % | 21–32 | 3–45 | 1020 |
| 60..100cm | sand | % | 31–54 | 3–89 | 1020 |
| 60..100cm | silt | % | 24–37 | 1–56 | 1020 |
| 60..100cm | bd.core | kg/m3 | 1150–1440 | 730–1690 | 1020 |
| 60..100cm | soc | g/kg | 2.6–8.1 | 0.7–31.6 | 1020 |
| 60..100cm | ph.h2o | pH | 6.1–6.5 | 4.8–8.1 | 1020 |
