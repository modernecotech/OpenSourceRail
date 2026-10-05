# Nyeri civil soil screening

229 route/station sample locations; 229 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 226 |
| fine-soil-plasticity-and-shrink-swell-tests | 229 |
| granular-density-and-groundwater-tests | 5 |

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
| 0..30cm | clay | % | 30–36 | 19–47 | 229 |
| 0..30cm | sand | % | 36–49 | 15–71 | 229 |
| 0..30cm | silt | % | 21–30 | 7–41 | 229 |
| 0..30cm | bd.core | kg/m3 | 1080–1260 | 830–1430 | 229 |
| 0..30cm | soc | g/kg | 11.9–26.6 | 6.4–44.7 | 229 |
| 0..30cm | ph.h2o | pH | 5.7–6.2 | 4.8–7.5 | 229 |
| 30..60cm | clay | % | 32–39 | 19–50 | 229 |
| 30..60cm | sand | % | 36–47 | 13–69 | 229 |
| 30..60cm | silt | % | 20–30 | 6–44 | 229 |
| 30..60cm | bd.core | kg/m3 | 1140–1270 | 870–1420 | 229 |
| 30..60cm | soc | g/kg | 8.9–13.9 | 4.2–23.1 | 229 |
| 30..60cm | ph.h2o | pH | 5.7–6.4 | 4.7–7.3 | 229 |
| 60..100cm | clay | % | 31–39 | 18–52 | 229 |
| 60..100cm | sand | % | 34–46 | 12–70 | 229 |
| 60..100cm | silt | % | 20–29 | 3–43 | 229 |
| 60..100cm | bd.core | kg/m3 | 1150–1240 | 930–1480 | 229 |
| 60..100cm | soc | g/kg | 6.3–8.9 | 3.2–16.4 | 229 |
| 60..100cm | ph.h2o | pH | 5.7–6.5 | 4.7–8.1 | 229 |
