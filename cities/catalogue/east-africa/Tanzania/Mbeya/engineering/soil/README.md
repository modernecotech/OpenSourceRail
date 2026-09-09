# Mbeya civil soil screening

104 route/station sample locations; 104 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 102 |
| fine-soil-plasticity-and-shrink-swell-tests | 102 |
| granular-density-and-groundwater-tests | 49 |

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
| 0..30cm | clay | % | 24–36 | 14–50 | 104 |
| 0..30cm | sand | % | 37–58 | 15–77 | 104 |
| 0..30cm | silt | % | 16–27 | 4–39 | 104 |
| 0..30cm | bd.core | kg/m3 | 1200–1340 | 1020–1520 | 104 |
| 0..30cm | soc | g/kg | 6.9–19.5 | 3.1–37.7 | 104 |
| 0..30cm | ph.h2o | pH | 5.6–6.5 | 5.1–7.7 | 104 |
| 30..60cm | clay | % | 24–39 | 14–53 | 104 |
| 30..60cm | sand | % | 35–59 | 12–77 | 104 |
| 30..60cm | silt | % | 15–28 | 2–45 | 104 |
| 30..60cm | bd.core | kg/m3 | 1180–1370 | 860–1560 | 104 |
| 30..60cm | soc | g/kg | 5.9–9.3 | 2.3–16.3 | 104 |
| 30..60cm | ph.h2o | pH | 5.7–6.6 | 5–7.7 | 104 |
| 60..100cm | clay | % | 24–40 | 13–54 | 104 |
| 60..100cm | sand | % | 32–59 | 10–81 | 104 |
| 60..100cm | silt | % | 16–30 | 0–46 | 104 |
| 60..100cm | bd.core | kg/m3 | 1090–1410 | 840–1610 | 104 |
| 60..100cm | soc | g/kg | 4.8–7.2 | 1.5–20.9 | 104 |
| 60..100cm | ph.h2o | pH | 5.8–6.8 | 4.9–8.2 | 104 |
