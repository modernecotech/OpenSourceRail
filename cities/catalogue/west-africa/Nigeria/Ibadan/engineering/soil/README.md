# Ibadan civil soil screening

635 route/station sample locations; 635 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 635 |
| fine-soil-plasticity-and-shrink-swell-tests | 635 |
| granular-density-and-groundwater-tests | 635 |

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
| 0..30cm | clay | % | 20–29 | 8–41 | 635 |
| 0..30cm | sand | % | 54–69 | 29–87 | 635 |
| 0..30cm | silt | % | 11–17 | 0–33 | 635 |
| 0..30cm | bd.core | kg/m3 | 1290–1450 | 1060–1600 | 635 |
| 0..30cm | soc | g/kg | 6.2–13 | 2.3–22.5 | 635 |
| 0..30cm | ph.h2o | pH | 5.9–6.8 | 4.8–7.8 | 635 |
| 30..60cm | clay | % | 24–32 | 11–45 | 635 |
| 30..60cm | sand | % | 51–65 | 29–83 | 635 |
| 30..60cm | silt | % | 10–17 | 0–37 | 635 |
| 30..60cm | bd.core | kg/m3 | 1350–1490 | 1120–1680 | 635 |
| 30..60cm | soc | g/kg | 3.3–5.4 | 1.4–11.1 | 635 |
| 30..60cm | ph.h2o | pH | 5.9–6.5 | 4.7–7.8 | 635 |
| 60..100cm | clay | % | 26–33 | 12–50 | 635 |
| 60..100cm | sand | % | 49–62 | 20–84 | 635 |
| 60..100cm | silt | % | 11–18 | 0–37 | 635 |
| 60..100cm | bd.core | kg/m3 | 1340–1500 | 1120–1750 | 635 |
| 60..100cm | soc | g/kg | 2.8–4.5 | 1.2–9.5 | 635 |
| 60..100cm | ph.h2o | pH | 5.9–6.4 | 4.8–7.8 | 635 |
