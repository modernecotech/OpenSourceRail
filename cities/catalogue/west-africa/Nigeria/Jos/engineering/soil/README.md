# Jos civil soil screening

1,849 route/station sample locations; 1,849 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 1849 |
| fine-soil-plasticity-and-shrink-swell-tests | 1849 |
| granular-density-and-groundwater-tests | 1823 |

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
| 0..30cm | clay | % | 20–27 | 7–42 | 1849 |
| 0..30cm | sand | % | 45–58 | 16–84 | 1849 |
| 0..30cm | silt | % | 21–29 | 6–45 | 1849 |
| 0..30cm | bd.core | kg/m3 | 1240–1430 | 1000–1590 | 1849 |
| 0..30cm | soc | g/kg | 5.6–13.4 | 2.1–24.7 | 1849 |
| 0..30cm | ph.h2o | pH | 5.5–6.1 | 4.9–6.9 | 1849 |
| 30..60cm | clay | % | 23–30 | 8–45 | 1849 |
| 30..60cm | sand | % | 41–56 | 10–88 | 1849 |
| 30..60cm | silt | % | 21–31 | 4–47 | 1849 |
| 30..60cm | bd.core | kg/m3 | 1330–1480 | 1100–1670 | 1849 |
| 30..60cm | soc | g/kg | 3.3–6.6 | 1–11.5 | 1849 |
| 30..60cm | ph.h2o | pH | 5.7–6.2 | 5–7.2 | 1849 |
| 60..100cm | clay | % | 24–31 | 7–48 | 1849 |
| 60..100cm | sand | % | 40–55 | 10–86 | 1849 |
| 60..100cm | silt | % | 20–30 | 2–47 | 1849 |
| 60..100cm | bd.core | kg/m3 | 1360–1500 | 1030–1750 | 1849 |
| 60..100cm | soc | g/kg | 2.4–4.3 | 0.9–9.3 | 1849 |
| 60..100cm | ph.h2o | pH | 5.8–6.5 | 4.8–8.2 | 1849 |
