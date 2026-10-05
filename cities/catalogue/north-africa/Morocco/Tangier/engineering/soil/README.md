# Tangier civil soil screening

233 route/station sample locations; 216 complete profiles; 17 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 15 |
| coverage-gap | 17 |
| fine-soil-plasticity-and-shrink-swell-tests | 166 |
| granular-density-and-groundwater-tests | 203 |
| organic-content-and-compressibility-tests | 3 |

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
| 0..30cm | clay | % | 17–29 | 2–42 | 216 |
| 0..30cm | sand | % | 36–61 | 10–89 | 216 |
| 0..30cm | silt | % | 21–35 | 5–48 | 216 |
| 0..30cm | bd.core | kg/m3 | 1080–1440 | 870–1600 | 216 |
| 0..30cm | soc | g/kg | 4.7–18.4 | 1.9–50.2 | 216 |
| 0..30cm | ph.h2o | pH | 6.4–7.8 | 5.1–8.2 | 216 |
| 30..60cm | clay | % | 18–29 | 0–43 | 216 |
| 30..60cm | sand | % | 37–60 | 10–92 | 216 |
| 30..60cm | silt | % | 20–34 | 0–47 | 216 |
| 30..60cm | bd.core | kg/m3 | 1280–1600 | 1090–1750 | 216 |
| 30..60cm | soc | g/kg | 3.1–10.3 | 0.8–27.7 | 216 |
| 30..60cm | ph.h2o | pH | 6.3–7.8 | 5–8.4 | 216 |
| 60..100cm | clay | % | 18–29 | 0–43 | 216 |
| 60..100cm | sand | % | 37–60 | 13–91 | 216 |
| 60..100cm | silt | % | 19–34 | 0–47 | 216 |
| 60..100cm | bd.core | kg/m3 | 1380–1630 | 1050–1820 | 216 |
| 60..100cm | soc | g/kg | 1.8–11.5 | 0.3–56.4 | 216 |
| 60..100cm | ph.h2o | pH | 6.2–8 | 5.1–8.6 | 216 |
