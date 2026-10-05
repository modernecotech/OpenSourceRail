# Irbid civil soil screening

64 route/station sample locations; 64 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 64 |
| granular-density-and-groundwater-tests | 48 |
| silt-moisture-frost-and-erosion-review | 9 |

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
| 0..30cm | clay | % | 23–29 | 6–41 | 64 |
| 0..30cm | sand | % | 35–47 | 10–78 | 64 |
| 0..30cm | silt | % | 30–37 | 12–52 | 64 |
| 0..30cm | bd.core | kg/m3 | 1390–1430 | 1170–1640 | 64 |
| 0..30cm | soc | g/kg | 2.5–13.6 | 1.2–26.1 | 64 |
| 0..30cm | ph.h2o | pH | 7.5–7.7 | 6.8–8.2 | 64 |
| 30..60cm | clay | % | 24–31 | 9–43 | 64 |
| 30..60cm | sand | % | 34–47 | 8–79 | 64 |
| 30..60cm | silt | % | 29–36 | 10–51 | 64 |
| 30..60cm | bd.core | kg/m3 | 1450–1590 | 1260–1770 | 64 |
| 30..60cm | soc | g/kg | 2–4.7 | 0.6–9.6 | 64 |
| 30..60cm | ph.h2o | pH | 7.5–7.8 | 6.8–8.4 | 64 |
| 60..100cm | clay | % | 25–32 | 8–46 | 64 |
| 60..100cm | sand | % | 34–47 | 7–78 | 64 |
| 60..100cm | silt | % | 28–35 | 8–53 | 64 |
| 60..100cm | bd.core | kg/m3 | 1470–1630 | 1250–1850 | 64 |
| 60..100cm | soc | g/kg | 1.8–3.8 | 0.4–8.8 | 64 |
| 60..100cm | ph.h2o | pH | 7.5–8 | 6.7–8.7 | 64 |
