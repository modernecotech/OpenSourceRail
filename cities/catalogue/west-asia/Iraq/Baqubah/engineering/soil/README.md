# Baqubah civil soil screening

122 route/station sample locations; 122 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 122 |
| granular-density-and-groundwater-tests | 26 |
| silt-moisture-frost-and-erosion-review | 84 |

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
| 0..30cm | clay | % | 17–33 | 5–40 | 122 |
| 0..30cm | sand | % | 20–52 | 5–73 | 122 |
| 0..30cm | silt | % | 31–47 | 18–61 | 122 |
| 0..30cm | bd.core | kg/m3 | 1440–1500 | 1240–1660 | 122 |
| 0..30cm | soc | g/kg | 2.4–6.6 | 0.6–13.4 | 122 |
| 0..30cm | ph.h2o | pH | 7.6–7.9 | 6.8–8.5 | 122 |
| 30..60cm | clay | % | 20–34 | 1–42 | 122 |
| 30..60cm | sand | % | 23–50 | 7–82 | 122 |
| 30..60cm | silt | % | 28–43 | 11–58 | 122 |
| 30..60cm | bd.core | kg/m3 | 1400–1530 | 1170–1770 | 122 |
| 30..60cm | soc | g/kg | 1.9–3.6 | 0.2–8.9 | 122 |
| 30..60cm | ph.h2o | pH | 7.8–8.3 | 6.5–9.1 | 122 |
| 60..100cm | clay | % | 21–34 | 2–45 | 122 |
| 60..100cm | sand | % | 25–52 | 7–87 | 122 |
| 60..100cm | silt | % | 26–41 | 5–57 | 122 |
| 60..100cm | bd.core | kg/m3 | 1390–1610 | 1150–1930 | 122 |
| 60..100cm | soc | g/kg | 1.9–2.8 | 0.4–7.6 | 122 |
| 60..100cm | ph.h2o | pH | 7.8–8.5 | 6.3–9.4 | 122 |
