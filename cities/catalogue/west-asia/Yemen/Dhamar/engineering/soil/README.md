# Dhamar civil soil screening

44 route/station sample locations; 44 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 44 |
| granular-density-and-groundwater-tests | 42 |

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
| 0..30cm | clay | % | 24–31 | 8–47 | 44 |
| 0..30cm | sand | % | 41–58 | 16–84 | 44 |
| 0..30cm | silt | % | 18–29 | 0–46 | 44 |
| 0..30cm | bd.core | kg/m3 | 1350–1440 | 1140–1650 | 44 |
| 0..30cm | soc | g/kg | 4.4–8.9 | 2.6–15.4 | 44 |
| 0..30cm | ph.h2o | pH | 7.3–8 | 6.1–9.1 | 44 |
| 30..60cm | clay | % | 25–32 | 7–53 | 44 |
| 30..60cm | sand | % | 41–57 | 10–85 | 44 |
| 30..60cm | silt | % | 18–28 | 0–47 | 44 |
| 30..60cm | bd.core | kg/m3 | 1380–1440 | 1120–1670 | 44 |
| 30..60cm | soc | g/kg | 3.7–6.2 | 1.7–14.5 | 44 |
| 30..60cm | ph.h2o | pH | 7.3–8.1 | 6.3–9.1 | 44 |
| 60..100cm | clay | % | 27–33 | 7–53 | 44 |
| 60..100cm | sand | % | 41–56 | 8–86 | 44 |
| 60..100cm | silt | % | 18–27 | 0–48 | 44 |
| 60..100cm | bd.core | kg/m3 | 1400–1460 | 1140–1730 | 44 |
| 60..100cm | soc | g/kg | 2.5–4.4 | 0.8–11 | 44 |
| 60..100cm | ph.h2o | pH | 7.4–8.1 | 6.3–9 | 44 |
