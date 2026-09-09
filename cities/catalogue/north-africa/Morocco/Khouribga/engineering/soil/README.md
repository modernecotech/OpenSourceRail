# Khouribga civil soil screening

42 route/station sample locations; 42 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 42 |
| granular-density-and-groundwater-tests | 14 |

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
| 0..30cm | clay | % | 24–29 | 12–39 | 42 |
| 0..30cm | sand | % | 40–46 | 15–72 | 42 |
| 0..30cm | silt | % | 28–32 | 14–47 | 42 |
| 0..30cm | bd.core | kg/m3 | 1400–1440 | 1250–1580 | 42 |
| 0..30cm | soc | g/kg | 5.8–11.1 | 2.8–21.3 | 42 |
| 0..30cm | ph.h2o | pH | 7.6–7.9 | 6.9–8.4 | 42 |
| 30..60cm | clay | % | 26–30 | 12–43 | 42 |
| 30..60cm | sand | % | 40–46 | 14–74 | 42 |
| 30..60cm | silt | % | 27–30 | 11–45 | 42 |
| 30..60cm | bd.core | kg/m3 | 1480–1570 | 1260–1700 | 42 |
| 30..60cm | soc | g/kg | 3.1–5.3 | 1.2–8.4 | 42 |
| 30..60cm | ph.h2o | pH | 7.7–8.1 | 7–8.6 | 42 |
| 60..100cm | clay | % | 26–31 | 12–46 | 42 |
| 60..100cm | sand | % | 40–47 | 15–75 | 42 |
| 60..100cm | silt | % | 25–30 | 9–45 | 42 |
| 60..100cm | bd.core | kg/m3 | 1480–1580 | 1290–1740 | 42 |
| 60..100cm | soc | g/kg | 2.3–3.7 | 0.9–8.1 | 42 |
| 60..100cm | ph.h2o | pH | 7.8–8.1 | 6.8–8.8 | 42 |
