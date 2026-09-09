# Hurghada civil soil screening

96 route/station sample locations; 88 complete profiles; 8 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 18 |
| coverage-gap | 8 |
| granular-density-and-groundwater-tests | 88 |

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
| 0..30cm | clay | % | 11–18 | 0–30 | 88 |
| 0..30cm | sand | % | 58–72 | 31–94 | 88 |
| 0..30cm | silt | % | 17–24 | 4–42 | 88 |
| 0..30cm | bd.core | kg/m3 | 1380–1460 | 1050–1660 | 88 |
| 0..30cm | soc | g/kg | 2.9–6.3 | 0.8–21.5 | 88 |
| 0..30cm | ph.h2o | pH | 7.3–8.2 | 5.4–9.3 | 88 |
| 30..60cm | clay | % | 10–18 | 0–32 | 88 |
| 30..60cm | sand | % | 59–76 | 33–98 | 88 |
| 30..60cm | silt | % | 14–23 | 0–41 | 88 |
| 30..60cm | bd.core | kg/m3 | 1460–1520 | 1290–1670 | 88 |
| 30..60cm | soc | g/kg | 1.7–7.3 | 0–42 | 88 |
| 30..60cm | ph.h2o | pH | 7.3–8.5 | 4.8–9.7 | 88 |
| 60..100cm | clay | % | 10–18 | 0–34 | 88 |
| 60..100cm | sand | % | 59–76 | 33–97 | 88 |
| 60..100cm | silt | % | 14–23 | 0–38 | 88 |
| 60..100cm | bd.core | kg/m3 | 1480–1560 | 1250–1760 | 88 |
| 60..100cm | soc | g/kg | 1.8–5.5 | 0.1–33.9 | 88 |
| 60..100cm | ph.h2o | pH | 7.3–8.5 | 4.8–9.8 | 88 |
