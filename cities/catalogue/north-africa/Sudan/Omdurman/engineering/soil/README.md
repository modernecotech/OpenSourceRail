# Omdurman civil soil screening

539 route/station sample locations; 506 complete profiles; 33 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 185 |
| coverage-gap | 33 |
| fine-soil-plasticity-and-shrink-swell-tests | 496 |
| granular-density-and-groundwater-tests | 28 |

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
| 0..30cm | clay | % | 20–32 | 8–41 | 506 |
| 0..30cm | sand | % | 34–57 | 14–83 | 506 |
| 0..30cm | silt | % | 22–35 | 9–44 | 506 |
| 0..30cm | bd.core | kg/m3 | 1380–1500 | 1080–1730 | 506 |
| 0..30cm | soc | g/kg | 2.4–5.1 | 0.8–10.7 | 506 |
| 0..30cm | ph.h2o | pH | 7–7.9 | 4.9–9.1 | 506 |
| 30..60cm | clay | % | 19–34 | 8–43 | 506 |
| 30..60cm | sand | % | 29–61 | 14–88 | 506 |
| 30..60cm | silt | % | 20–37 | 6–44 | 506 |
| 30..60cm | bd.core | kg/m3 | 1420–1540 | 1210–1760 | 506 |
| 30..60cm | soc | g/kg | 1.4–2.6 | 0–7.6 | 506 |
| 30..60cm | ph.h2o | pH | 7–8.5 | 4.9–9.5 | 506 |
| 60..100cm | clay | % | 20–34 | 7–43 | 506 |
| 60..100cm | sand | % | 30–58 | 14–89 | 506 |
| 60..100cm | silt | % | 22–37 | 3–44 | 506 |
| 60..100cm | bd.core | kg/m3 | 1410–1560 | 1160–1790 | 506 |
| 60..100cm | soc | g/kg | 1.3–2.2 | 0–6.5 | 506 |
| 60..100cm | ph.h2o | pH | 7–8.5 | 4.8–9.8 | 506 |
