# Fayoum civil soil screening

695 route/station sample locations; 544 complete profiles; 151 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 96 |
| coverage-gap | 151 |
| fine-soil-plasticity-and-shrink-swell-tests | 443 |
| granular-density-and-groundwater-tests | 544 |

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
| 0..30cm | clay | % | 13–23 | 4–41 | 544 |
| 0..30cm | sand | % | 49–68 | 12–88 | 544 |
| 0..30cm | silt | % | 18–28 | 8–47 | 544 |
| 0..30cm | bd.core | kg/m3 | 1420–1540 | 1180–1750 | 544 |
| 0..30cm | soc | g/kg | 2.9–6.9 | 0.8–18.6 | 544 |
| 0..30cm | ph.h2o | pH | 7.3–8.6 | 6.1–9.4 | 544 |
| 30..60cm | clay | % | 13–24 | 3–43 | 544 |
| 30..60cm | sand | % | 49–71 | 11–94 | 544 |
| 30..60cm | silt | % | 16–27 | 4–46 | 544 |
| 30..60cm | bd.core | kg/m3 | 1470–1600 | 1260–1780 | 544 |
| 30..60cm | soc | g/kg | 1.8–4 | 0–12.9 | 544 |
| 30..60cm | ph.h2o | pH | 7.4–8.7 | 5–9.8 | 544 |
| 60..100cm | clay | % | 13–24 | 3–42 | 544 |
| 60..100cm | sand | % | 49–71 | 14–94 | 544 |
| 60..100cm | silt | % | 16–27 | 4–46 | 544 |
| 60..100cm | bd.core | kg/m3 | 1490–1660 | 1280–1910 | 544 |
| 60..100cm | soc | g/kg | 1.5–3 | 0–11.1 | 544 |
| 60..100cm | ph.h2o | pH | 7.2–8.7 | 3.3–9.8 | 544 |
