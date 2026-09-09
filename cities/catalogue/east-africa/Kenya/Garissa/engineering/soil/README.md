# Garissa civil soil screening

70 route/station sample locations; 70 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 16 |
| granular-density-and-groundwater-tests | 60 |
| silt-moisture-frost-and-erosion-review | 5 |

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
| 0..30cm | clay | % | 17–30 | 10–42 | 70 |
| 0..30cm | sand | % | 35–62 | 11–75 | 70 |
| 0..30cm | silt | % | 20–35 | 11–51 | 70 |
| 0..30cm | bd.core | kg/m3 | 1420–1510 | 1260–1660 | 70 |
| 0..30cm | soc | g/kg | 3.7–6.7 | 1.7–13.9 | 70 |
| 0..30cm | ph.h2o | pH | 7.1–8.4 | 5.8–9 | 70 |
| 30..60cm | clay | % | 19–31 | 10–47 | 70 |
| 30..60cm | sand | % | 36–60 | 11–74 | 70 |
| 30..60cm | silt | % | 21–34 | 9–51 | 70 |
| 30..60cm | bd.core | kg/m3 | 1390–1540 | 1200–1750 | 70 |
| 30..60cm | soc | g/kg | 2.3–3.9 | 1–6.5 | 70 |
| 30..60cm | ph.h2o | pH | 7.1–8.4 | 5.7–9.3 | 70 |
| 60..100cm | clay | % | 20–30 | 10–47 | 70 |
| 60..100cm | sand | % | 37–58 | 10–75 | 70 |
| 60..100cm | silt | % | 22–33 | 8–49 | 70 |
| 60..100cm | bd.core | kg/m3 | 1330–1550 | 1100–1760 | 70 |
| 60..100cm | soc | g/kg | 2–3.3 | 0.6–6.4 | 70 |
| 60..100cm | ph.h2o | pH | 7–8.4 | 5.6–9.4 | 70 |
