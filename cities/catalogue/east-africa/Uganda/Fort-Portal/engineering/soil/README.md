# Fort-Portal civil soil screening

1,001 route/station sample locations; 1,001 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 998 |
| fine-soil-plasticity-and-shrink-swell-tests | 1001 |
| granular-density-and-groundwater-tests | 64 |
| organic-content-and-compressibility-tests | 62 |

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
| 0..30cm | clay | % | 31–39 | 18–50 | 1001 |
| 0..30cm | sand | % | 37–47 | 17–75 | 1001 |
| 0..30cm | silt | % | 22–26 | 5–40 | 1001 |
| 0..30cm | bd.core | kg/m3 | 980–1220 | 660–1460 | 1001 |
| 0..30cm | soc | g/kg | 11.8–26.1 | 7.6–49.2 | 1001 |
| 0..30cm | ph.h2o | pH | 5.6–6.4 | 4.9–7.6 | 1001 |
| 30..60cm | clay | % | 32–41 | 18–56 | 1001 |
| 30..60cm | sand | % | 37–48 | 16–74 | 1001 |
| 30..60cm | silt | % | 19–24 | 3–39 | 1001 |
| 30..60cm | bd.core | kg/m3 | 1020–1300 | 650–1570 | 1001 |
| 30..60cm | soc | g/kg | 6.3–17.9 | 1.9–43.9 | 1001 |
| 30..60cm | ph.h2o | pH | 5.8–6.5 | 4.8–7.9 | 1001 |
| 60..100cm | clay | % | 31–42 | 16–57 | 1001 |
| 60..100cm | sand | % | 36–50 | 16–78 | 1001 |
| 60..100cm | silt | % | 18–24 | 2–41 | 1001 |
| 60..100cm | bd.core | kg/m3 | 1040–1300 | 590–1620 | 1001 |
| 60..100cm | soc | g/kg | 4.6–18.8 | 1.3–119 | 1001 |
| 60..100cm | ph.h2o | pH | 5.9–6.8 | 4.8–8 | 1001 |
