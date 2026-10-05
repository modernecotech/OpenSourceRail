# Antananarivo civil soil screening

1,240 route/station sample locations; 1,239 complete profiles; 1 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 1239 |
| coverage-gap | 1 |
| fine-soil-plasticity-and-shrink-swell-tests | 1239 |
| granular-density-and-groundwater-tests | 48 |
| silt-moisture-frost-and-erosion-review | 23 |

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
| 0..30cm | clay | % | 24–39 | 7–51 | 1239 |
| 0..30cm | sand | % | 32–59 | 15–86 | 1239 |
| 0..30cm | silt | % | 17–31 | 0–46 | 1239 |
| 0..30cm | bd.core | kg/m3 | 1020–1310 | 700–1550 | 1239 |
| 0..30cm | soc | g/kg | 6.3–21.9 | 2.6–48.5 | 1239 |
| 0..30cm | ph.h2o | pH | 5.3–6 | 4.5–6.9 | 1239 |
| 30..60cm | clay | % | 27–42 | 6–55 | 1239 |
| 30..60cm | sand | % | 29–55 | 9–89 | 1239 |
| 30..60cm | silt | % | 18–32 | 1–48 | 1239 |
| 30..60cm | bd.core | kg/m3 | 1020–1410 | 650–1640 | 1239 |
| 30..60cm | soc | g/kg | 3.4–13.7 | 1.4–33.2 | 1239 |
| 30..60cm | ph.h2o | pH | 5.3–6.1 | 4.5–7.2 | 1239 |
| 60..100cm | clay | % | 28–43 | 5–56 | 1239 |
| 60..100cm | sand | % | 26–52 | 5–89 | 1239 |
| 60..100cm | silt | % | 20–34 | 1–53 | 1239 |
| 60..100cm | bd.core | kg/m3 | 970–1450 | 120–1700 | 1239 |
| 60..100cm | soc | g/kg | 2.5–12.1 | 0.5–43.3 | 1239 |
| 60..100cm | ph.h2o | pH | 5.4–6.5 | 4.5–7.9 | 1239 |
