# Garoua civil soil screening

149 route/station sample locations; 149 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 60 |
| fine-soil-plasticity-and-shrink-swell-tests | 149 |
| granular-density-and-groundwater-tests | 149 |

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
| 0..30cm | clay | % | 22–32 | 12–46 | 149 |
| 0..30cm | sand | % | 42–57 | 16–81 | 149 |
| 0..30cm | silt | % | 20–27 | 5–43 | 149 |
| 0..30cm | bd.core | kg/m3 | 1370–1500 | 1140–1690 | 149 |
| 0..30cm | soc | g/kg | 4.5–8 | 2.2–13.2 | 149 |
| 0..30cm | ph.h2o | pH | 6.1–6.6 | 5.5–7.3 | 149 |
| 30..60cm | clay | % | 24–33 | 11–47 | 149 |
| 30..60cm | sand | % | 42–56 | 12–86 | 149 |
| 30..60cm | silt | % | 20–26 | 4–43 | 149 |
| 30..60cm | bd.core | kg/m3 | 1380–1510 | 1140–1720 | 149 |
| 30..60cm | soc | g/kg | 2.6–4.5 | 1–8.7 | 149 |
| 30..60cm | ph.h2o | pH | 6.1–6.5 | 5.6–7.2 | 149 |
| 60..100cm | clay | % | 24–33 | 8–48 | 149 |
| 60..100cm | sand | % | 42–56 | 10–87 | 149 |
| 60..100cm | silt | % | 20–26 | 3–45 | 149 |
| 60..100cm | bd.core | kg/m3 | 1390–1490 | 1100–1760 | 149 |
| 60..100cm | soc | g/kg | 1.9–3.5 | 0.7–7.8 | 149 |
| 60..100cm | ph.h2o | pH | 6.3–6.5 | 5.3–7.6 | 149 |
