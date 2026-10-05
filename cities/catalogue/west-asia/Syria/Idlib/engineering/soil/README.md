# Idlib civil soil screening

54 route/station sample locations; 54 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 54 |
| granular-density-and-groundwater-tests | 8 |
| silt-moisture-frost-and-erosion-review | 23 |

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
| 0..30cm | clay | % | 23–32 | 13–41 | 54 |
| 0..30cm | sand | % | 31–46 | 11–65 | 54 |
| 0..30cm | silt | % | 31–39 | 17–55 | 54 |
| 0..30cm | bd.core | kg/m3 | 1380–1500 | 1250–1640 | 54 |
| 0..30cm | soc | g/kg | 4.2–10.9 | 1.6–17.3 | 54 |
| 0..30cm | ph.h2o | pH | 7.2–7.7 | 6.4–8.4 | 54 |
| 30..60cm | clay | % | 25–34 | 11–46 | 54 |
| 30..60cm | sand | % | 33–48 | 12–79 | 54 |
| 30..60cm | silt | % | 27–35 | 10–48 | 54 |
| 30..60cm | bd.core | kg/m3 | 1490–1610 | 1300–1770 | 54 |
| 30..60cm | soc | g/kg | 2.5–5.2 | 0.8–8.5 | 54 |
| 30..60cm | ph.h2o | pH | 7.3–7.7 | 6.4–8.4 | 54 |
| 60..100cm | clay | % | 26–35 | 10–49 | 54 |
| 60..100cm | sand | % | 34–50 | 10–79 | 54 |
| 60..100cm | silt | % | 24–31 | 8–48 | 54 |
| 60..100cm | bd.core | kg/m3 | 1490–1630 | 1280–1810 | 54 |
| 60..100cm | soc | g/kg | 1.9–3.6 | 0.6–7.4 | 54 |
| 60..100cm | ph.h2o | pH | 7.4–7.8 | 6.4–8.7 | 54 |
