# Mbeya civil soil screening

157 route/station sample locations; 157 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 153 |
| fine-soil-plasticity-and-shrink-swell-tests | 153 |
| granular-density-and-groundwater-tests | 101 |

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
| 0..30cm | clay | % | 24–37 | 13–50 | 157 |
| 0..30cm | sand | % | 40–58 | 19–77 | 157 |
| 0..30cm | silt | % | 16–26 | 4–38 | 157 |
| 0..30cm | bd.core | kg/m3 | 1230–1350 | 1100–1520 | 157 |
| 0..30cm | soc | g/kg | 8–19.5 | 3.7–32.9 | 157 |
| 0..30cm | ph.h2o | pH | 5.7–6.5 | 5.1–7.7 | 157 |
| 30..60cm | clay | % | 24–40 | 12–53 | 157 |
| 30..60cm | sand | % | 35–59 | 15–82 | 157 |
| 30..60cm | silt | % | 15–28 | 1–42 | 157 |
| 30..60cm | bd.core | kg/m3 | 1190–1380 | 890–1560 | 157 |
| 30..60cm | soc | g/kg | 6–9.8 | 2.3–16.9 | 157 |
| 30..60cm | ph.h2o | pH | 5.7–6.6 | 5.1–7.7 | 157 |
| 60..100cm | clay | % | 24–41 | 12–54 | 157 |
| 60..100cm | sand | % | 32–59 | 10–80 | 157 |
| 60..100cm | silt | % | 16–30 | 0–46 | 157 |
| 60..100cm | bd.core | kg/m3 | 1100–1410 | 420–1610 | 157 |
| 60..100cm | soc | g/kg | 4.6–7.9 | 1.8–15.9 | 157 |
| 60..100cm | ph.h2o | pH | 5.9–6.7 | 4.9–8 | 157 |
