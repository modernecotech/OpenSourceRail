# Tripoli-Lb civil soil screening

129 route/station sample locations; 129 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 11 |
| fine-soil-plasticity-and-shrink-swell-tests | 128 |
| granular-density-and-groundwater-tests | 76 |
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
| 0..30cm | clay | % | 22–32 | 3–44 | 129 |
| 0..30cm | sand | % | 34–55 | 11–91 | 129 |
| 0..30cm | silt | % | 22–35 | 3–52 | 129 |
| 0..30cm | bd.core | kg/m3 | 1230–1400 | 1040–1560 | 129 |
| 0..30cm | soc | g/kg | 5.5–18.1 | 1.9–34.3 | 129 |
| 0..30cm | ph.h2o | pH | 6.4–7.7 | 5.3–8.2 | 129 |
| 30..60cm | clay | % | 23–33 | 2–46 | 129 |
| 30..60cm | sand | % | 34–59 | 12–90 | 129 |
| 30..60cm | silt | % | 18–33 | 0–49 | 129 |
| 30..60cm | bd.core | kg/m3 | 1320–1550 | 1100–1750 | 129 |
| 30..60cm | soc | g/kg | 2.7–7.8 | 0.8–15.5 | 129 |
| 30..60cm | ph.h2o | pH | 6.5–7.7 | 5.3–8.4 | 129 |
| 60..100cm | clay | % | 23–34 | 1–47 | 129 |
| 60..100cm | sand | % | 35–60 | 11–88 | 129 |
| 60..100cm | silt | % | 17–33 | 1–48 | 129 |
| 60..100cm | bd.core | kg/m3 | 1310–1590 | 1000–1830 | 129 |
| 60..100cm | soc | g/kg | 1.7–5.6 | 0.3–13 | 129 |
| 60..100cm | ph.h2o | pH | 6.6–7.6 | 5.3–8.5 | 129 |
