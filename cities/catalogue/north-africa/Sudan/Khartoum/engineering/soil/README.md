# Khartoum civil soil screening

11,160 route/station sample locations; 11,132 complete profiles; 28 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 2702 |
| coverage-gap | 28 |
| fine-soil-plasticity-and-shrink-swell-tests | 11102 |
| granular-density-and-groundwater-tests | 460 |

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
| 0..30cm | clay | % | 21–33 | 7–43 | 11132 |
| 0..30cm | sand | % | 31–57 | 15–82 | 11132 |
| 0..30cm | silt | % | 22–37 | 10–47 | 11132 |
| 0..30cm | bd.core | kg/m3 | 1360–1500 | 1090–1730 | 11132 |
| 0..30cm | soc | g/kg | 2.2–5.6 | 0.6–11.4 | 11132 |
| 0..30cm | ph.h2o | pH | 6.6–8.1 | 4.8–9.3 | 11132 |
| 30..60cm | clay | % | 23–35 | 8–45 | 11132 |
| 30..60cm | sand | % | 27–56 | 12–88 | 11132 |
| 30..60cm | silt | % | 21–38 | 6–47 | 11132 |
| 30..60cm | bd.core | kg/m3 | 1400–1550 | 1120–1770 | 11132 |
| 30..60cm | soc | g/kg | 1.4–2.8 | 0–8 | 11132 |
| 30..60cm | ph.h2o | pH | 6.6–8.6 | 4.8–9.8 | 11132 |
| 60..100cm | clay | % | 24–35 | 8–44 | 11132 |
| 60..100cm | sand | % | 27–53 | 12–89 | 11132 |
| 60..100cm | silt | % | 22–38 | 3–49 | 11132 |
| 60..100cm | bd.core | kg/m3 | 1360–1570 | 1120–1790 | 11132 |
| 60..100cm | soc | g/kg | 1.3–2.8 | 0–8.4 | 11132 |
| 60..100cm | ph.h2o | pH | 6.6–8.6 | 4.8–10 | 11132 |
