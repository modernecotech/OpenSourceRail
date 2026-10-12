# Fez civil soil screening

4,992 route/station sample locations; 4,992 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 4975 |
| granular-density-and-groundwater-tests | 1141 |
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
| 0..30cm | clay | % | 21–31 | 8–43 | 4992 |
| 0..30cm | sand | % | 35–53 | 12–78 | 4992 |
| 0..30cm | silt | % | 26–35 | 12–51 | 4992 |
| 0..30cm | bd.core | kg/m3 | 1320–1470 | 1100–1630 | 4992 |
| 0..30cm | soc | g/kg | 4.7–12.2 | 2–22.8 | 4992 |
| 0..30cm | ph.h2o | pH | 7.2–7.7 | 6.4–8.2 | 4992 |
| 30..60cm | clay | % | 23–33 | 8–45 | 4992 |
| 30..60cm | sand | % | 34–54 | 12–83 | 4992 |
| 30..60cm | silt | % | 23–34 | 7–49 | 4992 |
| 30..60cm | bd.core | kg/m3 | 1450–1580 | 1270–1770 | 4992 |
| 30..60cm | soc | g/kg | 2.8–5.6 | 0.7–11.1 | 4992 |
| 30..60cm | ph.h2o | pH | 7.4–7.8 | 6.2–8.5 | 4992 |
| 60..100cm | clay | % | 23–34 | 9–46 | 4992 |
| 60..100cm | sand | % | 34–56 | 10–84 | 4992 |
| 60..100cm | silt | % | 20–33 | 3–48 | 4992 |
| 60..100cm | bd.core | kg/m3 | 1490–1630 | 1260–1830 | 4992 |
| 60..100cm | soc | g/kg | 2–4.2 | 0.8–9.5 | 4992 |
| 60..100cm | ph.h2o | pH | 7.5–8 | 6.3–8.9 | 4992 |
