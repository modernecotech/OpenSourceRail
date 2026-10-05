# Bamenda civil soil screening

154 route/station sample locations; 154 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 154 |
| fine-soil-plasticity-and-shrink-swell-tests | 152 |
| granular-density-and-groundwater-tests | 101 |
| organic-content-and-compressibility-tests | 24 |

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
| 0..30cm | clay | % | 23–35 | 13–45 | 154 |
| 0..30cm | sand | % | 38–60 | 14–78 | 154 |
| 0..30cm | silt | % | 17–27 | 6–41 | 154 |
| 0..30cm | bd.core | kg/m3 | 910–1230 | 690–1400 | 154 |
| 0..30cm | soc | g/kg | 14.1–36.9 | 5.9–75.4 | 154 |
| 0..30cm | ph.h2o | pH | 5–5.5 | 4.5–6 | 154 |
| 30..60cm | clay | % | 25–37 | 14–49 | 154 |
| 30..60cm | sand | % | 34–57 | 13–79 | 154 |
| 30..60cm | silt | % | 16–28 | 1–42 | 154 |
| 30..60cm | bd.core | kg/m3 | 1080–1330 | 780–1540 | 154 |
| 30..60cm | soc | g/kg | 7.3–16.4 | 3.5–26.5 | 154 |
| 30..60cm | ph.h2o | pH | 5.1–5.6 | 4.5–6 | 154 |
| 60..100cm | clay | % | 26–39 | 14–50 | 154 |
| 60..100cm | sand | % | 32–56 | 11–79 | 154 |
| 60..100cm | silt | % | 16–29 | 0–43 | 154 |
| 60..100cm | bd.core | kg/m3 | 1220–1420 | 840–1640 | 154 |
| 60..100cm | soc | g/kg | 8–10.9 | 4.1–19.5 | 154 |
| 60..100cm | ph.h2o | pH | 5.1–5.6 | 4.5–6.1 | 154 |
