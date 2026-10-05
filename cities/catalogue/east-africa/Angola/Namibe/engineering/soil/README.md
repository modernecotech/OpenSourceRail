# Namibe civil soil screening

101 route/station sample locations; 40 complete profiles; 61 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 61 |
| fine-soil-plasticity-and-shrink-swell-tests | 8 |
| granular-density-and-groundwater-tests | 40 |
| organic-content-and-compressibility-tests | 1 |

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
| 0..30cm | clay | % | 12–20 | 0–34 | 40 |
| 0..30cm | sand | % | 58–74 | 31–90 | 40 |
| 0..30cm | silt | % | 14–23 | 3–37 | 40 |
| 0..30cm | bd.core | kg/m3 | 1400–1530 | 1150–1780 | 40 |
| 0..30cm | soc | g/kg | 1.8–7 | 0.7–23.1 | 40 |
| 0..30cm | ph.h2o | pH | 7.7–8.4 | 6.8–9 | 40 |
| 30..60cm | clay | % | 14–21 | 1–36 | 40 |
| 30..60cm | sand | % | 58–69 | 27–94 | 40 |
| 30..60cm | silt | % | 16–22 | 0–45 | 40 |
| 30..60cm | bd.core | kg/m3 | 1460–1530 | 1200–1820 | 40 |
| 30..60cm | soc | g/kg | 1.2–6.6 | 0.3–51.3 | 40 |
| 30..60cm | ph.h2o | pH | 7.9–8.4 | 6.9–9.5 | 40 |
| 60..100cm | clay | % | 15–20 | 0–35 | 40 |
| 60..100cm | sand | % | 58–68 | 27–94 | 40 |
| 60..100cm | silt | % | 16–22 | 0–43 | 40 |
| 60..100cm | bd.core | kg/m3 | 1400–1530 | 1090–1830 | 40 |
| 60..100cm | soc | g/kg | 1–5.3 | 0.1–39.2 | 40 |
| 60..100cm | ph.h2o | pH | 8–8.6 | 7–9.5 | 40 |
