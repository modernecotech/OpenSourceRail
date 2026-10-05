# Khouribga civil soil screening

32 route/station sample locations; 32 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 32 |
| granular-density-and-groundwater-tests | 15 |

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
| 0..30cm | clay | % | 24–30 | 12–40 | 32 |
| 0..30cm | sand | % | 36–47 | 15–70 | 32 |
| 0..30cm | silt | % | 28–34 | 15–47 | 32 |
| 0..30cm | bd.core | kg/m3 | 1400–1480 | 1220–1620 | 32 |
| 0..30cm | soc | g/kg | 4.7–11.5 | 2.7–22.5 | 32 |
| 0..30cm | ph.h2o | pH | 7.6–7.9 | 7–8.5 | 32 |
| 30..60cm | clay | % | 26–31 | 12–45 | 32 |
| 30..60cm | sand | % | 36–47 | 11–74 | 32 |
| 30..60cm | silt | % | 27–32 | 11–47 | 32 |
| 30..60cm | bd.core | kg/m3 | 1470–1570 | 1290–1720 | 32 |
| 30..60cm | soc | g/kg | 3–5.1 | 1.2–8.3 | 32 |
| 30..60cm | ph.h2o | pH | 7.7–8.1 | 7–8.6 | 32 |
| 60..100cm | clay | % | 26–31 | 10–47 | 32 |
| 60..100cm | sand | % | 37–49 | 13–75 | 32 |
| 60..100cm | silt | % | 25–31 | 9–48 | 32 |
| 60..100cm | bd.core | kg/m3 | 1490–1580 | 1290–1750 | 32 |
| 60..100cm | soc | g/kg | 2.3–3.7 | 0.9–7.1 | 32 |
| 60..100cm | ph.h2o | pH | 7.8–8.1 | 6.8–8.8 | 32 |
