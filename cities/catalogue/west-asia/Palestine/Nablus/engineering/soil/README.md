# Nablus civil soil screening

608 route/station sample locations; 608 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 608 |
| granular-density-and-groundwater-tests | 88 |
| silt-moisture-frost-and-erosion-review | 140 |

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
| 0..30cm | clay | % | 22–32 | 8–43 | 608 |
| 0..30cm | sand | % | 32–47 | 4–72 | 608 |
| 0..30cm | silt | % | 29–38 | 15–55 | 608 |
| 0..30cm | bd.core | kg/m3 | 1320–1450 | 1110–1670 | 608 |
| 0..30cm | soc | g/kg | 3.2–15.5 | 1.5–35.5 | 608 |
| 0..30cm | ph.h2o | pH | 7.2–7.7 | 6–8.3 | 608 |
| 30..60cm | clay | % | 23–34 | 9–46 | 608 |
| 30..60cm | sand | % | 32–53 | 6–83 | 608 |
| 30..60cm | silt | % | 24–36 | 7–53 | 608 |
| 30..60cm | bd.core | kg/m3 | 1440–1600 | 1240–1800 | 608 |
| 30..60cm | soc | g/kg | 2.7–6.3 | 0.9–14.1 | 608 |
| 30..60cm | ph.h2o | pH | 7.1–7.8 | 6.1–8.4 | 608 |
| 60..100cm | clay | % | 23–34 | 8–46 | 608 |
| 60..100cm | sand | % | 32–54 | 9–86 | 608 |
| 60..100cm | silt | % | 23–35 | 6–52 | 608 |
| 60..100cm | bd.core | kg/m3 | 1470–1670 | 1230–1890 | 608 |
| 60..100cm | soc | g/kg | 2.1–6 | 0.6–13.4 | 608 |
| 60..100cm | ph.h2o | pH | 7–7.8 | 5.8–8.5 | 608 |
