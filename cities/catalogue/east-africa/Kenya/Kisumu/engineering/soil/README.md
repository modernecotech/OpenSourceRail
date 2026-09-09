# Kisumu civil soil screening

113 route/station sample locations; 112 complete profiles; 1 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 112 |
| coverage-gap | 1 |
| fine-soil-plasticity-and-shrink-swell-tests | 112 |
| silt-moisture-frost-and-erosion-review | 19 |

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
| 0..30cm | clay | % | 31–43 | 18–53 | 112 |
| 0..30cm | sand | % | 24–44 | 8–67 | 112 |
| 0..30cm | silt | % | 24–35 | 11–49 | 112 |
| 0..30cm | bd.core | kg/m3 | 1120–1290 | 910–1480 | 112 |
| 0..30cm | soc | g/kg | 8.6–17.7 | 3.2–29.2 | 112 |
| 0..30cm | ph.h2o | pH | 5.6–6.1 | 5.1–7.1 | 112 |
| 30..60cm | clay | % | 31–44 | 17–55 | 112 |
| 30..60cm | sand | % | 23–43 | 6–67 | 112 |
| 30..60cm | silt | % | 25–36 | 10–56 | 112 |
| 30..60cm | bd.core | kg/m3 | 1120–1340 | 860–1610 | 112 |
| 30..60cm | soc | g/kg | 5.4–11.3 | 2.3–22.8 | 112 |
| 30..60cm | ph.h2o | pH | 5.6–6.1 | 5–6.9 | 112 |
| 60..100cm | clay | % | 31–44 | 18–55 | 112 |
| 60..100cm | sand | % | 23–43 | 6–69 | 112 |
| 60..100cm | silt | % | 26–36 | 9–56 | 112 |
| 60..100cm | bd.core | kg/m3 | 1150–1350 | 890–1660 | 112 |
| 60..100cm | soc | g/kg | 4.4–10.7 | 1.6–25.9 | 112 |
| 60..100cm | ph.h2o | pH | 5.6–6.2 | 5–7.4 | 112 |
