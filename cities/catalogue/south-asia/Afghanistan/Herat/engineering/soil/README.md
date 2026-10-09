# Herat civil soil screening

509 route/station sample locations; 506 complete profiles; 3 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 3 |
| fine-soil-plasticity-and-shrink-swell-tests | 506 |
| granular-density-and-groundwater-tests | 210 |
| silt-moisture-frost-and-erosion-review | 337 |

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
| 0..30cm | clay | % | 18–28 | 4–40 | 506 |
| 0..30cm | sand | % | 29–52 | 8–77 | 506 |
| 0..30cm | silt | % | 27–43 | 13–60 | 506 |
| 0..30cm | bd.core | kg/m3 | 1370–1460 | 1170–1650 | 506 |
| 0..30cm | soc | g/kg | 2.9–7.8 | 1.1–20 | 506 |
| 0..30cm | ph.h2o | pH | 7.4–7.9 | 6.8–8.4 | 506 |
| 30..60cm | clay | % | 21–30 | 5–42 | 506 |
| 30..60cm | sand | % | 32–53 | 10–82 | 506 |
| 30..60cm | silt | % | 26–38 | 9–56 | 506 |
| 30..60cm | bd.core | kg/m3 | 1390–1560 | 1180–1770 | 506 |
| 30..60cm | soc | g/kg | 2.3–4.7 | 0.6–11.6 | 506 |
| 30..60cm | ph.h2o | pH | 7.2–7.9 | 6.1–8.9 | 506 |
| 60..100cm | clay | % | 23–32 | 6–45 | 506 |
| 60..100cm | sand | % | 33–54 | 9–84 | 506 |
| 60..100cm | silt | % | 23–35 | 5–52 | 506 |
| 60..100cm | bd.core | kg/m3 | 1420–1620 | 1200–1910 | 506 |
| 60..100cm | soc | g/kg | 1.7–3 | 0.2–6.7 | 506 |
| 60..100cm | ph.h2o | pH | 7.2–7.9 | 6.1–9.1 | 506 |
