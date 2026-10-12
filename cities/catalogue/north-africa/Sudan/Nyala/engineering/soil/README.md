# Nyala civil soil screening

745 route/station sample locations; 745 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 745 |
| fine-soil-plasticity-and-shrink-swell-tests | 745 |
| granular-density-and-groundwater-tests | 745 |

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
| 0..30cm | clay | % | 21–30 | 8–41 | 745 |
| 0..30cm | sand | % | 42–59 | 22–83 | 745 |
| 0..30cm | silt | % | 20–28 | 6–40 | 745 |
| 0..30cm | bd.core | kg/m3 | 1440–1520 | 1230–1720 | 745 |
| 0..30cm | soc | g/kg | 2.4–5.2 | 1–9.4 | 745 |
| 0..30cm | ph.h2o | pH | 5.9–6.8 | 4.8–8.2 | 745 |
| 30..60cm | clay | % | 23–29 | 7–45 | 745 |
| 30..60cm | sand | % | 47–57 | 16–88 | 745 |
| 30..60cm | silt | % | 19–25 | 4–42 | 745 |
| 30..60cm | bd.core | kg/m3 | 1370–1490 | 1110–1690 | 745 |
| 30..60cm | soc | g/kg | 1.6–3.5 | 0.4–6.1 | 745 |
| 30..60cm | ph.h2o | pH | 5.7–6.7 | 4.4–8.3 | 745 |
| 60..100cm | clay | % | 22–28 | 6–45 | 745 |
| 60..100cm | sand | % | 47–59 | 14–90 | 745 |
| 60..100cm | silt | % | 18–25 | 0–41 | 745 |
| 60..100cm | bd.core | kg/m3 | 1310–1480 | 760–1710 | 745 |
| 60..100cm | soc | g/kg | 1.8–2.8 | 0.3–6.5 | 745 |
| 60..100cm | ph.h2o | pH | 5.8–6.8 | 4.4–8.4 | 745 |
