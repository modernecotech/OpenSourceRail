# Nablus civil soil screening

95 route/station sample locations; 95 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 95 |
| granular-density-and-groundwater-tests | 23 |
| silt-moisture-frost-and-erosion-review | 34 |

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
| 0..30cm | clay | % | 22–31 | 8–42 | 95 |
| 0..30cm | sand | % | 33–47 | 8–72 | 95 |
| 0..30cm | silt | % | 29–38 | 14–53 | 95 |
| 0..30cm | bd.core | kg/m3 | 1320–1450 | 1140–1660 | 95 |
| 0..30cm | soc | g/kg | 3.2–14 | 1.5–34.4 | 95 |
| 0..30cm | ph.h2o | pH | 7.4–7.6 | 6.5–8.3 | 95 |
| 30..60cm | clay | % | 25–33 | 9–46 | 95 |
| 30..60cm | sand | % | 34–46 | 9–77 | 95 |
| 30..60cm | silt | % | 29–35 | 10–51 | 95 |
| 30..60cm | bd.core | kg/m3 | 1440–1600 | 1230–1780 | 95 |
| 30..60cm | soc | g/kg | 2.7–6.1 | 1–14.1 | 95 |
| 30..60cm | ph.h2o | pH | 7.4–7.7 | 6.6–8.5 | 95 |
| 60..100cm | clay | % | 26–34 | 9–46 | 95 |
| 60..100cm | sand | % | 34–48 | 9–77 | 95 |
| 60..100cm | silt | % | 27–35 | 6–51 | 95 |
| 60..100cm | bd.core | kg/m3 | 1460–1670 | 1230–1880 | 95 |
| 60..100cm | soc | g/kg | 2.1–5.5 | 0.6–13.2 | 95 |
| 60..100cm | ph.h2o | pH | 7.5–7.8 | 6.4–8.4 | 95 |
