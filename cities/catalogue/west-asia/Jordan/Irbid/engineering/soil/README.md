# Irbid civil soil screening

107 route/station sample locations; 107 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 107 |
| granular-density-and-groundwater-tests | 94 |
| silt-moisture-frost-and-erosion-review | 8 |

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
| 0..30cm | clay | % | 21–29 | 6–41 | 107 |
| 0..30cm | sand | % | 35–53 | 10–81 | 107 |
| 0..30cm | silt | % | 26–37 | 11–49 | 107 |
| 0..30cm | bd.core | kg/m3 | 1380–1440 | 1160–1640 | 107 |
| 0..30cm | soc | g/kg | 2.7–12 | 1.2–27.3 | 107 |
| 0..30cm | ph.h2o | pH | 7.5–7.8 | 6.8–8.2 | 107 |
| 30..60cm | clay | % | 22–31 | 6–43 | 107 |
| 30..60cm | sand | % | 34–51 | 8–83 | 107 |
| 30..60cm | silt | % | 27–35 | 10–52 | 107 |
| 30..60cm | bd.core | kg/m3 | 1450–1570 | 1270–1750 | 107 |
| 30..60cm | soc | g/kg | 2.3–5 | 1–10.1 | 107 |
| 30..60cm | ph.h2o | pH | 7.5–8 | 6.8–8.6 | 107 |
| 60..100cm | clay | % | 22–32 | 5–45 | 107 |
| 60..100cm | sand | % | 34–51 | 6–83 | 107 |
| 60..100cm | silt | % | 27–35 | 8–53 | 107 |
| 60..100cm | bd.core | kg/m3 | 1460–1630 | 1230–1850 | 107 |
| 60..100cm | soc | g/kg | 1.9–3.8 | 0.6–8.8 | 107 |
| 60..100cm | ph.h2o | pH | 7.6–8 | 6.7–8.7 | 107 |
