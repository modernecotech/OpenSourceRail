# Mbarara civil soil screening

299 route/station sample locations; 299 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 126 |
| fine-soil-plasticity-and-shrink-swell-tests | 292 |
| granular-density-and-groundwater-tests | 285 |

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
| 0..30cm | clay | % | 23–33 | 9–48 | 299 |
| 0..30cm | sand | % | 42–59 | 18–86 | 299 |
| 0..30cm | silt | % | 17–25 | 4–39 | 299 |
| 0..30cm | bd.core | kg/m3 | 1140–1280 | 940–1520 | 299 |
| 0..30cm | soc | g/kg | 9.3–18.2 | 4.5–32.8 | 299 |
| 0..30cm | ph.h2o | pH | 5.8–6.9 | 4.9–8.1 | 299 |
| 30..60cm | clay | % | 23–35 | 8–49 | 299 |
| 30..60cm | sand | % | 41–60 | 14–86 | 299 |
| 30..60cm | silt | % | 16–25 | 2–40 | 299 |
| 30..60cm | bd.core | kg/m3 | 1230–1330 | 1000–1530 | 299 |
| 30..60cm | soc | g/kg | 5.9–11.7 | 2.3–20.1 | 299 |
| 30..60cm | ph.h2o | pH | 6.1–6.9 | 5.3–8.2 | 299 |
| 60..100cm | clay | % | 22–35 | 8–50 | 299 |
| 60..100cm | sand | % | 41–62 | 16–87 | 299 |
| 60..100cm | silt | % | 15–25 | 1–41 | 299 |
| 60..100cm | bd.core | kg/m3 | 1220–1360 | 990–1580 | 299 |
| 60..100cm | soc | g/kg | 4.4–9.6 | 1.3–17.5 | 299 |
| 60..100cm | ph.h2o | pH | 6.5–7.2 | 5.1–8.3 | 299 |
