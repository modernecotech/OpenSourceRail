# Al-Kharj civil soil screening

1,251 route/station sample locations; 1,027 complete profiles; 224 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 224 |
| fine-soil-plasticity-and-shrink-swell-tests | 119 |
| granular-density-and-groundwater-tests | 1017 |
| silt-moisture-frost-and-erosion-review | 229 |

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
| 0..30cm | clay | % | 10–22 | 0–35 | 1027 |
| 0..30cm | sand | % | 42–67 | 18–90 | 1027 |
| 0..30cm | silt | % | 23–36 | 8–53 | 1027 |
| 0..30cm | bd.core | kg/m3 | 1400–1490 | 1220–1680 | 1027 |
| 0..30cm | soc | g/kg | 2.6–4.5 | 0.7–13.9 | 1027 |
| 0..30cm | ph.h2o | pH | 8.1–8.4 | 7.3–9.6 | 1027 |
| 30..60cm | clay | % | 14–24 | 0–41 | 1027 |
| 30..60cm | sand | % | 43–61 | 15–92 | 1027 |
| 30..60cm | silt | % | 23–34 | 4–50 | 1027 |
| 30..60cm | bd.core | kg/m3 | 1350–1490 | 1160–1670 | 1027 |
| 30..60cm | soc | g/kg | 1.9–3.3 | 0.3–11.6 | 1027 |
| 30..60cm | ph.h2o | pH | 8.1–8.7 | 7–9.7 | 1027 |
| 60..100cm | clay | % | 14–23 | 0–41 | 1027 |
| 60..100cm | sand | % | 43–60 | 15–92 | 1027 |
| 60..100cm | silt | % | 24–34 | 4–57 | 1027 |
| 60..100cm | bd.core | kg/m3 | 1410–1520 | 1230–1740 | 1027 |
| 60..100cm | soc | g/kg | 1.5–3 | 0.4–8.1 | 1027 |
| 60..100cm | ph.h2o | pH | 8.1–8.7 | 7.4–10.1 | 1027 |
