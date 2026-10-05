# Colombo civil soil screening

3,207 route/station sample locations; 3,165 complete profiles; 42 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 3165 |
| coverage-gap | 42 |
| fine-soil-plasticity-and-shrink-swell-tests | 3165 |
| granular-density-and-groundwater-tests | 2727 |
| organic-content-and-compressibility-tests | 974 |
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
| 0..30cm | clay | % | 20–38 | 3–49 | 3165 |
| 0..30cm | sand | % | 34–62 | 10–95 | 3165 |
| 0..30cm | silt | % | 18–31 | 0–46 | 3165 |
| 0..30cm | bd.core | kg/m3 | 360–1320 | 140–1570 | 3165 |
| 0..30cm | soc | g/kg | 7.6–76.5 | 1.8–273.1 | 3165 |
| 0..30cm | ph.h2o | pH | 5.1–5.9 | 4.1–7 | 3165 |
| 30..60cm | clay | % | 21–41 | 1–55 | 3165 |
| 30..60cm | sand | % | 34–63 | 6–94 | 3165 |
| 30..60cm | silt | % | 16–31 | 0–46 | 3165 |
| 30..60cm | bd.core | kg/m3 | 380–1410 | 160–1640 | 3165 |
| 30..60cm | soc | g/kg | 4.1–54.4 | 1.2–143.2 | 3165 |
| 30..60cm | ph.h2o | pH | 5.2–6 | 4.2–7.6 | 3165 |
| 60..100cm | clay | % | 22–41 | 1–55 | 3165 |
| 60..100cm | sand | % | 33–61 | 3–94 | 3165 |
| 60..100cm | silt | % | 17–32 | 0–50 | 3165 |
| 60..100cm | bd.core | kg/m3 | 410–1450 | 160–1710 | 3165 |
| 60..100cm | soc | g/kg | 3.4–37.8 | 1–376.7 | 3165 |
| 60..100cm | ph.h2o | pH | 5.3–6.2 | 4.3–8.1 | 3165 |
