# Uige civil soil screening

211 route/station sample locations; 211 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 211 |
| fine-soil-plasticity-and-shrink-swell-tests | 211 |
| granular-density-and-groundwater-tests | 12 |
| silt-moisture-frost-and-erosion-review | 1 |

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
| 0..30cm | clay | % | 33–38 | 18–50 | 211 |
| 0..30cm | sand | % | 36–46 | 18–71 | 211 |
| 0..30cm | silt | % | 20–27 | 2–43 | 211 |
| 0..30cm | bd.core | kg/m3 | 1140–1330 | 910–1490 | 211 |
| 0..30cm | soc | g/kg | 9.1–18.5 | 4.3–30.8 | 211 |
| 0..30cm | ph.h2o | pH | 5.4–5.8 | 4.8–6.3 | 211 |
| 30..60cm | clay | % | 37–41 | 21–54 | 211 |
| 30..60cm | sand | % | 34–43 | 11–68 | 211 |
| 30..60cm | silt | % | 20–25 | 1–46 | 211 |
| 30..60cm | bd.core | kg/m3 | 1130–1400 | 790–1590 | 211 |
| 30..60cm | soc | g/kg | 6.4–11.1 | 2.8–29.2 | 211 |
| 30..60cm | ph.h2o | pH | 5.4–5.8 | 4.9–6.4 | 211 |
| 60..100cm | clay | % | 39–43 | 19–58 | 211 |
| 60..100cm | sand | % | 32–41 | 8–66 | 211 |
| 60..100cm | silt | % | 20–25 | 0–50 | 211 |
| 60..100cm | bd.core | kg/m3 | 1030–1390 | 420–1600 | 211 |
| 60..100cm | soc | g/kg | 6.4–11.9 | 1.8–35.6 | 211 |
| 60..100cm | ph.h2o | pH | 5.4–5.9 | 4.9–6.5 | 211 |
