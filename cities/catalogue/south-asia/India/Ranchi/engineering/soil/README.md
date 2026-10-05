# Ranchi civil soil screening

771 route/station sample locations; 771 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 769 |
| fine-soil-plasticity-and-shrink-swell-tests | 726 |
| granular-density-and-groundwater-tests | 304 |
| silt-moisture-frost-and-erosion-review | 565 |

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
| 0..30cm | clay | % | 21–29 | 8–41 | 771 |
| 0..30cm | sand | % | 34–49 | 11–78 | 771 |
| 0..30cm | silt | % | 29–38 | 12–52 | 771 |
| 0..30cm | bd.core | kg/m3 | 1240–1440 | 980–1640 | 771 |
| 0..30cm | soc | g/kg | 5.5–11.9 | 1.8–23.5 | 771 |
| 0..30cm | ph.h2o | pH | 5.6–6.5 | 4.9–7.7 | 771 |
| 30..60cm | clay | % | 21–29 | 8–42 | 771 |
| 30..60cm | sand | % | 33–49 | 8–78 | 771 |
| 30..60cm | silt | % | 29–39 | 12–54 | 771 |
| 30..60cm | bd.core | kg/m3 | 1350–1520 | 970–1730 | 771 |
| 30..60cm | soc | g/kg | 3.4–5.9 | 0.9–12.9 | 771 |
| 30..60cm | ph.h2o | pH | 5.8–6.6 | 5–7.8 | 771 |
| 60..100cm | clay | % | 21–29 | 5–42 | 771 |
| 60..100cm | sand | % | 31–50 | 7–80 | 771 |
| 60..100cm | silt | % | 29–40 | 12–57 | 771 |
| 60..100cm | bd.core | kg/m3 | 1380–1560 | 940–1800 | 771 |
| 60..100cm | soc | g/kg | 2.8–3.8 | 1–7.8 | 771 |
| 60..100cm | ph.h2o | pH | 5.8–6.7 | 5–8.1 | 771 |
