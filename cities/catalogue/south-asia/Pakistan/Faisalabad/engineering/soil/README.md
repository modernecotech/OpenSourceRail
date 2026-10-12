# Faisalabad civil soil screening

3,214 route/station sample locations; 3,214 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 2901 |
| granular-density-and-groundwater-tests | 3214 |
| silt-moisture-frost-and-erosion-review | 40 |

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
| 0..30cm | clay | % | 16–25 | 4–39 | 3214 |
| 0..30cm | sand | % | 46–63 | 18–87 | 3214 |
| 0..30cm | silt | % | 20–31 | 5–49 | 3214 |
| 0..30cm | bd.core | kg/m3 | 1400–1530 | 1200–1700 | 3214 |
| 0..30cm | soc | g/kg | 4–6.6 | 1.5–17.1 | 3214 |
| 0..30cm | ph.h2o | pH | 7.7–8.1 | 6.7–8.9 | 3214 |
| 30..60cm | clay | % | 18–27 | 5–41 | 3214 |
| 30..60cm | sand | % | 43–59 | 16–86 | 3214 |
| 30..60cm | silt | % | 21–32 | 4–52 | 3214 |
| 30..60cm | bd.core | kg/m3 | 1450–1590 | 1220–1770 | 3214 |
| 30..60cm | soc | g/kg | 2.2–4.1 | 0.4–8.5 | 3214 |
| 30..60cm | ph.h2o | pH | 7.9–8.4 | 6.8–9.4 | 3214 |
| 60..100cm | clay | % | 19–27 | 5–42 | 3214 |
| 60..100cm | sand | % | 42–60 | 15–87 | 3214 |
| 60..100cm | silt | % | 20–32 | 5–52 | 3214 |
| 60..100cm | bd.core | kg/m3 | 1500–1620 | 1220–1860 | 3214 |
| 60..100cm | soc | g/kg | 1.4–3.1 | 0.2–7.1 | 3214 |
| 60..100cm | ph.h2o | pH | 7.9–8.5 | 7–9.4 | 3214 |
