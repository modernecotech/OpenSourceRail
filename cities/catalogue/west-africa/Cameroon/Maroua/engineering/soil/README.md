# Maroua civil soil screening

244 route/station sample locations; 244 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 10 |
| fine-soil-plasticity-and-shrink-swell-tests | 244 |
| granular-density-and-groundwater-tests | 244 |

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
| 0..30cm | clay | % | 22–32 | 7–47 | 244 |
| 0..30cm | sand | % | 42–57 | 13–86 | 244 |
| 0..30cm | silt | % | 19–26 | 2–46 | 244 |
| 0..30cm | bd.core | kg/m3 | 1450–1520 | 1230–1680 | 244 |
| 0..30cm | soc | g/kg | 4–8.2 | 2–14.5 | 244 |
| 0..30cm | ph.h2o | pH | 6–6.8 | 5.3–7.7 | 244 |
| 30..60cm | clay | % | 23–34 | 7–48 | 244 |
| 30..60cm | sand | % | 42–57 | 9–89 | 244 |
| 30..60cm | silt | % | 20–26 | 2–48 | 244 |
| 30..60cm | bd.core | kg/m3 | 1410–1500 | 1160–1700 | 244 |
| 30..60cm | soc | g/kg | 2.6–4.1 | 1.3–7.3 | 244 |
| 30..60cm | ph.h2o | pH | 6.1–7.2 | 5.5–8.3 | 244 |
| 60..100cm | clay | % | 23–34 | 8–49 | 244 |
| 60..100cm | sand | % | 41–57 | 9–88 | 244 |
| 60..100cm | silt | % | 20–27 | 2–48 | 244 |
| 60..100cm | bd.core | kg/m3 | 1380–1530 | 1040–1760 | 244 |
| 60..100cm | soc | g/kg | 2.1–3.1 | 0.9–6.4 | 244 |
| 60..100cm | ph.h2o | pH | 6.2–7.5 | 5.5–8.5 | 244 |
