# Beira civil soil screening

117 route/station sample locations; 117 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 116 |
| fine-soil-plasticity-and-shrink-swell-tests | 117 |
| granular-density-and-groundwater-tests | 117 |

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
| 0..30cm | clay | % | 21–33 | 3–52 | 117 |
| 0..30cm | sand | % | 46–66 | 11–95 | 117 |
| 0..30cm | silt | % | 12–22 | 0–39 | 117 |
| 0..30cm | bd.core | kg/m3 | 1220–1360 | 920–1510 | 117 |
| 0..30cm | soc | g/kg | 6–11.5 | 2.2–21.7 | 117 |
| 0..30cm | ph.h2o | pH | 5.9–6.9 | 4.9–8.1 | 117 |
| 30..60cm | clay | % | 24–36 | 4–52 | 117 |
| 30..60cm | sand | % | 47–66 | 13–95 | 117 |
| 30..60cm | silt | % | 10–19 | 0–35 | 117 |
| 30..60cm | bd.core | kg/m3 | 1240–1440 | 950–1610 | 117 |
| 30..60cm | soc | g/kg | 3.7–7.4 | 1.4–16.5 | 117 |
| 30..60cm | ph.h2o | pH | 6–7 | 4.8–8.1 | 117 |
| 60..100cm | clay | % | 26–36 | 4–55 | 117 |
| 60..100cm | sand | % | 45–65 | 8–95 | 117 |
| 60..100cm | silt | % | 9–18 | 0–36 | 117 |
| 60..100cm | bd.core | kg/m3 | 1220–1480 | 780–1720 | 117 |
| 60..100cm | soc | g/kg | 2.7–5.9 | 0.9–19.6 | 117 |
| 60..100cm | ph.h2o | pH | 5.9–7.1 | 4.7–8.3 | 117 |
