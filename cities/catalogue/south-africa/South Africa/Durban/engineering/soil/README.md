# Durban civil soil screening

1,799 route/station sample locations; 1,793 complete profiles; 6 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 1780 |
| coverage-gap | 6 |
| fine-soil-plasticity-and-shrink-swell-tests | 1789 |
| granular-density-and-groundwater-tests | 1782 |
| organic-content-and-compressibility-tests | 3 |

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
| 0..30cm | clay | % | 17–31 | 2–44 | 1793 |
| 0..30cm | sand | % | 45–74 | 10–97 | 1793 |
| 0..30cm | silt | % | 9–25 | 0–46 | 1793 |
| 0..30cm | bd.core | kg/m3 | 940–1330 | 640–1550 | 1793 |
| 0..30cm | soc | g/kg | 4.9–24.1 | 1.5–53.3 | 1793 |
| 0..30cm | ph.h2o | pH | 5.5–7.3 | 4.7–8.2 | 1793 |
| 30..60cm | clay | % | 19–36 | 2–51 | 1793 |
| 30..60cm | sand | % | 43–74 | 9–98 | 1793 |
| 30..60cm | silt | % | 7–24 | 0–46 | 1793 |
| 30..60cm | bd.core | kg/m3 | 1040–1450 | 680–1700 | 1793 |
| 30..60cm | soc | g/kg | 3.2–9 | 0.7–19.4 | 1793 |
| 30..60cm | ph.h2o | pH | 5.7–7.3 | 4.8–8.4 | 1793 |
| 60..100cm | clay | % | 19–37 | 2–51 | 1793 |
| 60..100cm | sand | % | 41–75 | 10–98 | 1793 |
| 60..100cm | silt | % | 6–24 | 0–47 | 1793 |
| 60..100cm | bd.core | kg/m3 | 1010–1490 | 380–1750 | 1793 |
| 60..100cm | soc | g/kg | 2.1–6.9 | 0.4–18.3 | 1793 |
| 60..100cm | ph.h2o | pH | 5.8–7.4 | 4.5–8.8 | 1793 |
