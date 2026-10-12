# Hillah civil soil screening

1,906 route/station sample locations; 1,906 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| fine-soil-plasticity-and-shrink-swell-tests | 1142 |
| granular-density-and-groundwater-tests | 1329 |
| silt-moisture-frost-and-erosion-review | 269 |

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
| 0..30cm | clay | % | 17–30 | 4–41 | 1906 |
| 0..30cm | sand | % | 30–57 | 10–84 | 1906 |
| 0..30cm | silt | % | 26–40 | 10–52 | 1906 |
| 0..30cm | bd.core | kg/m3 | 1460–1510 | 1260–1710 | 1906 |
| 0..30cm | soc | g/kg | 2.5–6.7 | 0.6–13.9 | 1906 |
| 0..30cm | ph.h2o | pH | 7.9–8.4 | 7.1–9.5 | 1906 |
| 30..60cm | clay | % | 18–30 | 3–42 | 1906 |
| 30..60cm | sand | % | 32–57 | 10–90 | 1906 |
| 30..60cm | silt | % | 25–38 | 5–53 | 1906 |
| 30..60cm | bd.core | kg/m3 | 1430–1620 | 1220–1790 | 1906 |
| 30..60cm | soc | g/kg | 1.7–3.3 | 0–8.4 | 1906 |
| 30..60cm | ph.h2o | pH | 8.2–8.9 | 7.2–10.1 | 1906 |
| 60..100cm | clay | % | 17–30 | 3–42 | 1906 |
| 60..100cm | sand | % | 32–57 | 10–91 | 1906 |
| 60..100cm | silt | % | 25–39 | 4–53 | 1906 |
| 60..100cm | bd.core | kg/m3 | 1440–1690 | 1230–1940 | 1906 |
| 60..100cm | soc | g/kg | 1.4–2.7 | 0–8.6 | 1906 |
| 60..100cm | ph.h2o | pH | 8.2–9 | 7.3–10.3 | 1906 |
