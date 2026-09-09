# Shinyanga civil soil screening

99 route/station sample locations; 99 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 21 |
| fine-soil-plasticity-and-shrink-swell-tests | 99 |
| granular-density-and-groundwater-tests | 99 |

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
| 0..30cm | clay | % | 20–28 | 11–39 | 99 |
| 0..30cm | sand | % | 53–71 | 23–86 | 99 |
| 0..30cm | silt | % | 9–19 | 0–31 | 99 |
| 0..30cm | bd.core | kg/m3 | 1500–1670 | 1310–1870 | 99 |
| 0..30cm | soc | g/kg | 5.9–8 | 3.1–11.8 | 99 |
| 0..30cm | ph.h2o | pH | 6.5–7.6 | 5.4–8.7 | 99 |
| 30..60cm | clay | % | 24–32 | 12–43 | 99 |
| 30..60cm | sand | % | 46–64 | 23–84 | 99 |
| 30..60cm | silt | % | 12–22 | 0–38 | 99 |
| 30..60cm | bd.core | kg/m3 | 1520–1630 | 1340–1870 | 99 |
| 30..60cm | soc | g/kg | 3.5–5 | 1.6–7.9 | 99 |
| 30..60cm | ph.h2o | pH | 6.6–7.4 | 5.4–8.5 | 99 |
| 60..100cm | clay | % | 25–33 | 12–47 | 99 |
| 60..100cm | sand | % | 43–60 | 17–82 | 99 |
| 60..100cm | silt | % | 14–24 | 0–40 | 99 |
| 60..100cm | bd.core | kg/m3 | 1500–1580 | 1260–1820 | 99 |
| 60..100cm | soc | g/kg | 3.4–4.2 | 1.6–7.8 | 99 |
| 60..100cm | ph.h2o | pH | 6.7–7.4 | 5.1–8.7 | 99 |
