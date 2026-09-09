# San-Salvador civil soil screening

479 route/station sample locations; 479 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 436 |
| fine-soil-plasticity-and-shrink-swell-tests | 469 |
| granular-density-and-groundwater-tests | 265 |
| organic-content-and-compressibility-tests | 33 |
| silt-moisture-frost-and-erosion-review | 46 |

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
| 0..30cm | clay | % | 21–33 | 2–45 | 479 |
| 0..30cm | sand | % | 37–54 | 13–91 | 479 |
| 0..30cm | silt | % | 25–35 | 6–50 | 479 |
| 0..30cm | bd.core | kg/m3 | 1020–1420 | 810–1630 | 479 |
| 0..30cm | soc | g/kg | 7–33.6 | 2.3–84.5 | 479 |
| 0..30cm | ph.h2o | pH | 5.5–6.8 | 4.8–8 | 479 |
| 30..60cm | clay | % | 21–35 | 2–50 | 479 |
| 30..60cm | sand | % | 36–52 | 12–91 | 479 |
| 30..60cm | silt | % | 25–34 | 6–52 | 479 |
| 30..60cm | bd.core | kg/m3 | 1060–1450 | 830–1700 | 479 |
| 30..60cm | soc | g/kg | 3.7–9.8 | 0.9–22.1 | 479 |
| 30..60cm | ph.h2o | pH | 5.6–6.9 | 4.8–8.1 | 479 |
| 60..100cm | clay | % | 20–35 | 2–49 | 479 |
| 60..100cm | sand | % | 33–53 | 9–91 | 479 |
| 60..100cm | silt | % | 26–36 | 6–58 | 479 |
| 60..100cm | bd.core | kg/m3 | 1070–1470 | 850–1720 | 479 |
| 60..100cm | soc | g/kg | 2.8–8 | 0.6–26.6 | 479 |
| 60..100cm | ph.h2o | pH | 5.5–7.1 | 4.8–8.3 | 479 |
