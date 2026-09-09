# Mandalay civil soil screening

645 route/station sample locations; 610 complete profiles; 35 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 128 |
| coverage-gap | 35 |
| fine-soil-plasticity-and-shrink-swell-tests | 605 |
| granular-density-and-groundwater-tests | 610 |
| silt-moisture-frost-and-erosion-review | 10 |

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
| 0..30cm | clay | % | 19–28 | 4–43 | 610 |
| 0..30cm | sand | % | 42–62 | 14–93 | 610 |
| 0..30cm | silt | % | 19–29 | 0–49 | 610 |
| 0..30cm | bd.core | kg/m3 | 1290–1500 | 950–1670 | 610 |
| 0..30cm | soc | g/kg | 4.8–14.6 | 1.9–33.3 | 610 |
| 0..30cm | ph.h2o | pH | 6.3–7.4 | 5.3–8.2 | 610 |
| 30..60cm | clay | % | 21–30 | 4–45 | 610 |
| 30..60cm | sand | % | 42–60 | 9–91 | 610 |
| 30..60cm | silt | % | 18–29 | 0–51 | 610 |
| 30..60cm | bd.core | kg/m3 | 1320–1570 | 960–1780 | 610 |
| 30..60cm | soc | g/kg | 3.1–9.6 | 0.9–29 | 610 |
| 30..60cm | ph.h2o | pH | 6.4–7.4 | 5.3–8.4 | 610 |
| 60..100cm | clay | % | 21–29 | 4–46 | 610 |
| 60..100cm | sand | % | 43–60 | 7–92 | 610 |
| 60..100cm | silt | % | 19–28 | 0–55 | 610 |
| 60..100cm | bd.core | kg/m3 | 1350–1620 | 750–1870 | 610 |
| 60..100cm | soc | g/kg | 2.4–8.6 | 0.5–31.7 | 610 |
| 60..100cm | ph.h2o | pH | 6.5–7.6 | 5.2–8.4 | 610 |
