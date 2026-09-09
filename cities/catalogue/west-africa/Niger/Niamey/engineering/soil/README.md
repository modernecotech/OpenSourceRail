# Niamey civil soil screening

324 route/station sample locations; 322 complete profiles; 2 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 313 |
| coverage-gap | 2 |
| fine-soil-plasticity-and-shrink-swell-tests | 18 |
| granular-density-and-groundwater-tests | 322 |

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
| 0..30cm | clay | % | 8–28 | 3–41 | 322 |
| 0..30cm | sand | % | 40–82 | 15–92 | 322 |
| 0..30cm | silt | % | 10–31 | 2–44 | 322 |
| 0..30cm | bd.core | kg/m3 | 1400–1520 | 1200–1740 | 322 |
| 0..30cm | soc | g/kg | 2.3–6.7 | 0.9–14.9 | 322 |
| 0..30cm | ph.h2o | pH | 5.7–7.4 | 5–8.4 | 322 |
| 30..60cm | clay | % | 8–29 | 3–43 | 322 |
| 30..60cm | sand | % | 41–84 | 11–93 | 322 |
| 30..60cm | silt | % | 8–30 | 0–46 | 322 |
| 30..60cm | bd.core | kg/m3 | 1390–1500 | 1110–1740 | 322 |
| 30..60cm | soc | g/kg | 2.1–3.3 | 0.7–8 | 322 |
| 30..60cm | ph.h2o | pH | 5.5–7.9 | 4.6–8.9 | 322 |
| 60..100cm | clay | % | 8–29 | 3–43 | 322 |
| 60..100cm | sand | % | 42–84 | 10–93 | 322 |
| 60..100cm | silt | % | 8–30 | 0–47 | 322 |
| 60..100cm | bd.core | kg/m3 | 1340–1500 | 890–1760 | 322 |
| 60..100cm | soc | g/kg | 1.7–2.6 | 0.5–5.6 | 322 |
| 60..100cm | ph.h2o | pH | 5.5–8 | 4.6–9.3 | 322 |
