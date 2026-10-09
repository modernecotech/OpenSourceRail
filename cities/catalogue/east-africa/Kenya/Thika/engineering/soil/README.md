# Thika civil soil screening

805 route/station sample locations; 805 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 64 |
| fine-soil-plasticity-and-shrink-swell-tests | 805 |
| granular-density-and-groundwater-tests | 86 |
| silt-moisture-frost-and-erosion-review | 5 |

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
| 0..30cm | clay | % | 29–41 | 13–53 | 805 |
| 0..30cm | sand | % | 28–48 | 7–76 | 805 |
| 0..30cm | silt | % | 22–33 | 8–46 | 805 |
| 0..30cm | bd.core | kg/m3 | 1130–1390 | 970–1530 | 805 |
| 0..30cm | soc | g/kg | 6.1–20.8 | 3.1–37.4 | 805 |
| 0..30cm | ph.h2o | pH | 5.7–7.2 | 4.7–8.1 | 805 |
| 30..60cm | clay | % | 29–42 | 10–55 | 805 |
| 30..60cm | sand | % | 28–50 | 7–79 | 805 |
| 30..60cm | silt | % | 21–33 | 5–49 | 805 |
| 30..60cm | bd.core | kg/m3 | 1120–1420 | 910–1600 | 805 |
| 30..60cm | soc | g/kg | 4.3–10.8 | 2–19.7 | 805 |
| 30..60cm | ph.h2o | pH | 5.6–7.2 | 4.8–8.2 | 805 |
| 60..100cm | clay | % | 29–42 | 8–56 | 805 |
| 60..100cm | sand | % | 28–49 | 7–79 | 805 |
| 60..100cm | silt | % | 21–34 | 5–51 | 805 |
| 60..100cm | bd.core | kg/m3 | 1090–1460 | 900–1630 | 805 |
| 60..100cm | soc | g/kg | 2.9–8.2 | 1–15.9 | 805 |
| 60..100cm | ph.h2o | pH | 5.7–7.3 | 4.6–8.3 | 805 |
