# Lira civil soil screening

144 route/station sample locations; 144 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 58 |
| fine-soil-plasticity-and-shrink-swell-tests | 144 |
| granular-density-and-groundwater-tests | 131 |

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
| 0..30cm | clay | % | 22–33 | 11–44 | 144 |
| 0..30cm | sand | % | 37–57 | 15–78 | 144 |
| 0..30cm | silt | % | 21–29 | 8–43 | 144 |
| 0..30cm | bd.core | kg/m3 | 1230–1330 | 980–1550 | 144 |
| 0..30cm | soc | g/kg | 9.1–16.7 | 4.4–29.5 | 144 |
| 0..30cm | ph.h2o | pH | 6.1–6.3 | 5.5–7.1 | 144 |
| 30..60cm | clay | % | 22–35 | 10–48 | 144 |
| 30..60cm | sand | % | 35–57 | 12–79 | 144 |
| 30..60cm | silt | % | 20–30 | 2–47 | 144 |
| 30..60cm | bd.core | kg/m3 | 1280–1370 | 1060–1590 | 144 |
| 30..60cm | soc | g/kg | 5.3–7.8 | 2.3–13.2 | 144 |
| 30..60cm | ph.h2o | pH | 6.1–6.4 | 5.4–7.2 | 144 |
| 60..100cm | clay | % | 23–35 | 9–48 | 144 |
| 60..100cm | sand | % | 35–55 | 12–82 | 144 |
| 60..100cm | silt | % | 20–30 | 3–48 | 144 |
| 60..100cm | bd.core | kg/m3 | 1240–1390 | 1000–1630 | 144 |
| 60..100cm | soc | g/kg | 4.4–5.6 | 1.7–13.1 | 144 |
| 60..100cm | ph.h2o | pH | 6.2–6.7 | 5.2–8.1 | 144 |
