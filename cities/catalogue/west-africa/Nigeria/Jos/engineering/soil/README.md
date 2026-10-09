# Jos civil soil screening

682 route/station sample locations; 682 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 682 |
| fine-soil-plasticity-and-shrink-swell-tests | 682 |
| granular-density-and-groundwater-tests | 668 |
| silt-moisture-frost-and-erosion-review | 2 |

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
| 0..30cm | clay | % | 20–27 | 7–41 | 682 |
| 0..30cm | sand | % | 45–58 | 16–83 | 682 |
| 0..30cm | silt | % | 21–29 | 7–45 | 682 |
| 0..30cm | bd.core | kg/m3 | 1220–1450 | 1000–1590 | 682 |
| 0..30cm | soc | g/kg | 5.8–13.4 | 2.2–24.7 | 682 |
| 0..30cm | ph.h2o | pH | 5.5–6 | 4.9–6.8 | 682 |
| 30..60cm | clay | % | 23–30 | 8–45 | 682 |
| 30..60cm | sand | % | 41–56 | 9–86 | 682 |
| 30..60cm | silt | % | 21–31 | 4–50 | 682 |
| 30..60cm | bd.core | kg/m3 | 1320–1480 | 1100–1670 | 682 |
| 30..60cm | soc | g/kg | 3.4–6.6 | 1.2–11.5 | 682 |
| 30..60cm | ph.h2o | pH | 5.7–6.2 | 4.9–7.2 | 682 |
| 60..100cm | clay | % | 24–30 | 7–48 | 682 |
| 60..100cm | sand | % | 41–55 | 10–86 | 682 |
| 60..100cm | silt | % | 20–30 | 2–49 | 682 |
| 60..100cm | bd.core | kg/m3 | 1360–1510 | 1060–1760 | 682 |
| 60..100cm | soc | g/kg | 2.4–5.1 | 1–9.6 | 682 |
| 60..100cm | ph.h2o | pH | 5.8–6.5 | 4.8–8.2 | 682 |
