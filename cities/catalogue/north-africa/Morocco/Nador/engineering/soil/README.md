# Nador civil soil screening

69 route/station sample locations; 69 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 69 |
| granular-density-and-groundwater-tests | 46 |

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
| 0..30cm | clay | % | 20–31 | 5–42 | 69 |
| 0..30cm | sand | % | 37–57 | 18–81 | 69 |
| 0..30cm | silt | % | 22–32 | 9–43 | 69 |
| 0..30cm | bd.core | kg/m3 | 1190–1460 | 930–1580 | 69 |
| 0..30cm | soc | g/kg | 4.6–21.3 | 2.5–37.4 | 69 |
| 0..30cm | ph.h2o | pH | 7.3–8 | 6.4–8.4 | 69 |
| 30..60cm | clay | % | 22–32 | 7–44 | 69 |
| 30..60cm | sand | % | 37–57 | 18–83 | 69 |
| 30..60cm | silt | % | 21–31 | 6–47 | 69 |
| 30..60cm | bd.core | kg/m3 | 1430–1570 | 1230–1780 | 69 |
| 30..60cm | soc | g/kg | 2.9–6.9 | 1.5–13.2 | 69 |
| 30..60cm | ph.h2o | pH | 7.4–8.2 | 6.4–8.8 | 69 |
| 60..100cm | clay | % | 23–32 | 5–45 | 69 |
| 60..100cm | sand | % | 38–55 | 17–84 | 69 |
| 60..100cm | silt | % | 22–31 | 5–46 | 69 |
| 60..100cm | bd.core | kg/m3 | 1500–1600 | 1310–1810 | 69 |
| 60..100cm | soc | g/kg | 2.1–4.6 | 1–9 | 69 |
| 60..100cm | ph.h2o | pH | 7.5–8.2 | 6.5–9 | 69 |
