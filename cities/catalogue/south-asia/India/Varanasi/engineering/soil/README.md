# Varanasi civil soil screening

452 route/station sample locations; 433 complete profiles; 19 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 14 |
| coverage-gap | 19 |
| fine-soil-plasticity-and-shrink-swell-tests | 152 |
| granular-density-and-groundwater-tests | 433 |

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
| 0..30cm | clay | % | 11–21 | 0–37 | 433 |
| 0..30cm | sand | % | 56–74 | 22–99 | 433 |
| 0..30cm | silt | % | 14–24 | 0–40 | 433 |
| 0..30cm | bd.core | kg/m3 | 1340–1500 | 1110–1690 | 433 |
| 0..30cm | soc | g/kg | 3.5–7.6 | 0.9–17.7 | 433 |
| 0..30cm | ph.h2o | pH | 6.4–7.1 | 5.4–8.2 | 433 |
| 30..60cm | clay | % | 12–23 | 0–40 | 433 |
| 30..60cm | sand | % | 51–74 | 21–98 | 433 |
| 30..60cm | silt | % | 14–25 | 0–44 | 433 |
| 30..60cm | bd.core | kg/m3 | 1400–1640 | 1140–1760 | 433 |
| 30..60cm | soc | g/kg | 1.9–4.1 | 0.3–11.5 | 433 |
| 30..60cm | ph.h2o | pH | 6.5–7.2 | 5.5–8.3 | 433 |
| 60..100cm | clay | % | 13–26 | 0–41 | 433 |
| 60..100cm | sand | % | 48–74 | 15–97 | 433 |
| 60..100cm | silt | % | 14–26 | 0–46 | 433 |
| 60..100cm | bd.core | kg/m3 | 1490–1680 | 1140–1860 | 433 |
| 60..100cm | soc | g/kg | 1.4–3.4 | 0.3–10.7 | 433 |
| 60..100cm | ph.h2o | pH | 6.7–7.3 | 5.4–8.4 | 433 |
