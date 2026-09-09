# Jinja civil soil screening

77 route/station sample locations; 73 complete profiles; 4 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 72 |
| coverage-gap | 4 |
| fine-soil-plasticity-and-shrink-swell-tests | 73 |
| granular-density-and-groundwater-tests | 2 |

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
| 0..30cm | clay | % | 36–47 | 17–55 | 73 |
| 0..30cm | sand | % | 22–40 | 9–78 | 73 |
| 0..30cm | silt | % | 23–32 | 7–42 | 73 |
| 0..30cm | bd.core | kg/m3 | 1100–1270 | 840–1500 | 73 |
| 0..30cm | soc | g/kg | 10.3–22.5 | 6–39.6 | 73 |
| 0..30cm | ph.h2o | pH | 5.8–6.4 | 5.2–7.5 | 73 |
| 30..60cm | clay | % | 39–49 | 19–60 | 73 |
| 30..60cm | sand | % | 20–38 | 8–80 | 73 |
| 30..60cm | silt | % | 22–31 | 4–45 | 73 |
| 30..60cm | bd.core | kg/m3 | 1150–1280 | 910–1490 | 73 |
| 30..60cm | soc | g/kg | 6.8–11.6 | 3.4–20.1 | 73 |
| 30..60cm | ph.h2o | pH | 5.7–6.4 | 5.1–7.8 | 73 |
| 60..100cm | clay | % | 39–50 | 19–60 | 73 |
| 60..100cm | sand | % | 20–38 | 6–80 | 73 |
| 60..100cm | silt | % | 22–31 | 4–45 | 73 |
| 60..100cm | bd.core | kg/m3 | 1170–1310 | 850–1520 | 73 |
| 60..100cm | soc | g/kg | 6.1–9.9 | 2.4–18.6 | 73 |
| 60..100cm | ph.h2o | pH | 5.7–6.4 | 5–7.7 | 73 |
