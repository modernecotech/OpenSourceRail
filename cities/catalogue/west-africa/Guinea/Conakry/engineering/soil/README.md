# Conakry civil soil screening

158 route/station sample locations; 128 complete profiles; 30 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 128 |
| coverage-gap | 30 |
| fine-soil-plasticity-and-shrink-swell-tests | 128 |
| granular-density-and-groundwater-tests | 128 |
| organic-content-and-compressibility-tests | 4 |
| silt-moisture-frost-and-erosion-review | 4 |

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
| 0..30cm | clay | % | 20–28 | 2–45 | 128 |
| 0..30cm | sand | % | 42–60 | 11–92 | 128 |
| 0..30cm | silt | % | 19–31 | 0–48 | 128 |
| 0..30cm | bd.core | kg/m3 | 820–1140 | 450–1450 | 128 |
| 0..30cm | soc | g/kg | 6.6–22.8 | 2.3–50.7 | 128 |
| 0..30cm | ph.h2o | pH | 5.4–5.9 | 4.6–7 | 128 |
| 30..60cm | clay | % | 20–29 | 0–46 | 128 |
| 30..60cm | sand | % | 40–59 | 7–92 | 128 |
| 30..60cm | silt | % | 20–31 | 1–50 | 128 |
| 30..60cm | bd.core | kg/m3 | 840–1200 | 380–1600 | 128 |
| 30..60cm | soc | g/kg | 4.6–12.9 | 1.1–40.8 | 128 |
| 30..60cm | ph.h2o | pH | 5.5–6.1 | 4.6–7.6 | 128 |
| 60..100cm | clay | % | 21–30 | 0–48 | 128 |
| 60..100cm | sand | % | 38–59 | 6–91 | 128 |
| 60..100cm | silt | % | 20–32 | 0–52 | 128 |
| 60..100cm | bd.core | kg/m3 | 870–1230 | 380–1600 | 128 |
| 60..100cm | soc | g/kg | 4.6–11.5 | 1.1–55.7 | 128 |
| 60..100cm | ph.h2o | pH | 5.5–6.2 | 4.6–7.9 | 128 |
