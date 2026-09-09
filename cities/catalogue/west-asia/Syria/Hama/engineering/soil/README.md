# Hama civil soil screening

120 route/station sample locations; 120 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 120 |
| granular-density-and-groundwater-tests | 57 |
| silt-moisture-frost-and-erosion-review | 31 |

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
| 0..30cm | clay | % | 24–31 | 11–42 | 120 |
| 0..30cm | sand | % | 33–47 | 10–75 | 120 |
| 0..30cm | silt | % | 28–37 | 10–54 | 120 |
| 0..30cm | bd.core | kg/m3 | 1360–1450 | 1170–1620 | 120 |
| 0..30cm | soc | g/kg | 3.5–11.1 | 1.7–20.6 | 120 |
| 0..30cm | ph.h2o | pH | 7.5–7.8 | 6.8–8.4 | 120 |
| 30..60cm | clay | % | 26–33 | 10–46 | 120 |
| 30..60cm | sand | % | 33–47 | 10–80 | 120 |
| 30..60cm | silt | % | 26–35 | 10–51 | 120 |
| 30..60cm | bd.core | kg/m3 | 1440–1590 | 1260–1760 | 120 |
| 30..60cm | soc | g/kg | 2.4–4.8 | 1–8.3 | 120 |
| 30..60cm | ph.h2o | pH | 7.4–7.8 | 6.3–8.6 | 120 |
| 60..100cm | clay | % | 26–34 | 8–48 | 120 |
| 60..100cm | sand | % | 34–48 | 12–80 | 120 |
| 60..100cm | silt | % | 25–33 | 2–53 | 120 |
| 60..100cm | bd.core | kg/m3 | 1420–1620 | 1250–1810 | 120 |
| 60..100cm | soc | g/kg | 1.9–3.1 | 0.5–5.9 | 120 |
| 60..100cm | ph.h2o | pH | 7.4–7.9 | 6.5–8.7 | 120 |
