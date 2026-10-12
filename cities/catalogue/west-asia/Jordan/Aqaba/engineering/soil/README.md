# Aqaba civil soil screening

930 route/station sample locations; 830 complete profiles; 100 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 100 |
| fine-soil-plasticity-and-shrink-swell-tests | 67 |
| granular-density-and-groundwater-tests | 830 |

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
| 0..30cm | clay | % | 11–20 | 0–36 | 830 |
| 0..30cm | sand | % | 55–74 | 24–92 | 830 |
| 0..30cm | silt | % | 15–25 | 5–41 | 830 |
| 0..30cm | bd.core | kg/m3 | 1470–1540 | 1300–1690 | 830 |
| 0..30cm | soc | g/kg | 2.2–7.5 | 0.5–20.9 | 830 |
| 0..30cm | ph.h2o | pH | 8–8.7 | 7.1–9.6 | 830 |
| 30..60cm | clay | % | 11–22 | 0–39 | 830 |
| 30..60cm | sand | % | 55–75 | 23–98 | 830 |
| 30..60cm | silt | % | 13–24 | 2–42 | 830 |
| 30..60cm | bd.core | kg/m3 | 1500–1570 | 1340–1750 | 830 |
| 30..60cm | soc | g/kg | 1.3–8.2 | 0–41.5 | 830 |
| 30..60cm | ph.h2o | pH | 8.2–9 | 7.3–9.7 | 830 |
| 60..100cm | clay | % | 11–21 | 0–38 | 830 |
| 60..100cm | sand | % | 55–75 | 24–98 | 830 |
| 60..100cm | silt | % | 14–24 | 2–42 | 830 |
| 60..100cm | bd.core | kg/m3 | 1510–1600 | 1280–1790 | 830 |
| 60..100cm | soc | g/kg | 1.1–6.2 | 0–31.2 | 830 |
| 60..100cm | ph.h2o | pH | 8.1–9.1 | 7.2–9.8 | 830 |
