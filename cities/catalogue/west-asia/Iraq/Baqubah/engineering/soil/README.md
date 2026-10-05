# Baqubah civil soil screening

134 route/station sample locations; 134 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 133 |
| granular-density-and-groundwater-tests | 19 |
| silt-moisture-frost-and-erosion-review | 113 |

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
| 0..30cm | clay | % | 18–32 | 7–41 | 134 |
| 0..30cm | sand | % | 22–50 | 4–70 | 134 |
| 0..30cm | silt | % | 32–46 | 18–61 | 134 |
| 0..30cm | bd.core | kg/m3 | 1410–1490 | 1210–1660 | 134 |
| 0..30cm | soc | g/kg | 2.5–6.5 | 0.7–16.4 | 134 |
| 0..30cm | ph.h2o | pH | 7.5–7.9 | 6.8–8.4 | 134 |
| 30..60cm | clay | % | 21–33 | 3–43 | 134 |
| 30..60cm | sand | % | 24–50 | 5–82 | 134 |
| 30..60cm | silt | % | 29–43 | 13–58 | 134 |
| 30..60cm | bd.core | kg/m3 | 1410–1550 | 1190–1730 | 134 |
| 30..60cm | soc | g/kg | 2–3.8 | 0.3–9.1 | 134 |
| 30..60cm | ph.h2o | pH | 7.7–8.3 | 6.3–9.2 | 134 |
| 60..100cm | clay | % | 22–34 | 4–44 | 134 |
| 60..100cm | sand | % | 25–51 | 7–81 | 134 |
| 60..100cm | silt | % | 27–41 | 8–54 | 134 |
| 60..100cm | bd.core | kg/m3 | 1390–1620 | 1150–1930 | 134 |
| 60..100cm | soc | g/kg | 1.8–2.7 | 0.4–6.5 | 134 |
| 60..100cm | ph.h2o | pH | 7.7–8.5 | 6.1–9.4 | 134 |
