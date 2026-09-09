# Galle civil soil screening

150 route/station sample locations; 150 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 150 |
| fine-soil-plasticity-and-shrink-swell-tests | 150 |
| granular-density-and-groundwater-tests | 128 |
| organic-content-and-compressibility-tests | 64 |
| silt-moisture-frost-and-erosion-review | 37 |

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
| 0..30cm | clay | % | 27–36 | 11–49 | 150 |
| 0..30cm | sand | % | 37–52 | 12–88 | 150 |
| 0..30cm | silt | % | 21–28 | 0–46 | 150 |
| 0..30cm | bd.core | kg/m3 | 370–1170 | 110–1510 | 150 |
| 0..30cm | soc | g/kg | 9.6–73.1 | 3.8–187.5 | 150 |
| 0..30cm | ph.h2o | pH | 5–5.9 | 4.2–7.1 | 150 |
| 30..60cm | clay | % | 29–38 | 9–51 | 150 |
| 30..60cm | sand | % | 35–49 | 6–87 | 150 |
| 30..60cm | silt | % | 22–29 | 0–50 | 150 |
| 30..60cm | bd.core | kg/m3 | 390–1250 | 100–1500 | 150 |
| 30..60cm | soc | g/kg | 4.9–57.8 | 1.6–127.3 | 150 |
| 30..60cm | ph.h2o | pH | 5.1–6 | 4.3–7.2 | 150 |
| 60..100cm | clay | % | 30–39 | 9–52 | 150 |
| 60..100cm | sand | % | 32–47 | 3–87 | 150 |
| 60..100cm | silt | % | 23–30 | 0–52 | 150 |
| 60..100cm | bd.core | kg/m3 | 400–1290 | 100–1600 | 150 |
| 60..100cm | soc | g/kg | 4.4–47.4 | 1.9–168.1 | 150 |
| 60..100cm | ph.h2o | pH | 5.2–6.2 | 4.3–7.5 | 150 |
