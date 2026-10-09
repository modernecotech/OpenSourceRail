# Dammam civil soil screening

3,540 route/station sample locations; 3,380 complete profiles; 160 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 42 |
| coverage-gap | 160 |
| fine-soil-plasticity-and-shrink-swell-tests | 371 |
| granular-density-and-groundwater-tests | 3380 |
| organic-content-and-compressibility-tests | 13 |

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
| 0..30cm | clay | % | 9–23 | 0–36 | 3380 |
| 0..30cm | sand | % | 44–74 | 17–97 | 3380 |
| 0..30cm | silt | % | 16–33 | 1–48 | 3380 |
| 0..30cm | bd.core | kg/m3 | 1200–1540 | 780–1730 | 3380 |
| 0..30cm | soc | g/kg | 2.8–9.9 | 0.4–36.2 | 3380 |
| 0..30cm | ph.h2o | pH | 7–8.5 | 5.2–9.4 | 3380 |
| 30..60cm | clay | % | 10–25 | 0–39 | 3380 |
| 30..60cm | sand | % | 44–75 | 16–99 | 3380 |
| 30..60cm | silt | % | 14–32 | 0–46 | 3380 |
| 30..60cm | bd.core | kg/m3 | 1300–1540 | 850–1750 | 3380 |
| 30..60cm | soc | g/kg | 1.3–9.4 | 0–56.3 | 3380 |
| 30..60cm | ph.h2o | pH | 7.1–8.6 | 5.3–9.7 | 3380 |
| 60..100cm | clay | % | 10–25 | 0–40 | 3380 |
| 60..100cm | sand | % | 43–75 | 17–99 | 3380 |
| 60..100cm | silt | % | 14–32 | 0–48 | 3380 |
| 60..100cm | bd.core | kg/m3 | 1330–1570 | 1010–1820 | 3380 |
| 60..100cm | soc | g/kg | 1.1–6.8 | 0–42 | 3380 |
| 60..100cm | ph.h2o | pH | 7.2–8.7 | 5.6–9.6 | 3380 |
