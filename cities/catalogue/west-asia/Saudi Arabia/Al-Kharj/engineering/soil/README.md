# Al-Kharj civil soil screening

554 route/station sample locations; 407 complete profiles; 147 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 147 |
| fine-soil-plasticity-and-shrink-swell-tests | 24 |
| granular-density-and-groundwater-tests | 406 |
| silt-moisture-frost-and-erosion-review | 53 |

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
| 0..30cm | clay | % | 10–22 | 0–34 | 407 |
| 0..30cm | sand | % | 43–66 | 18–89 | 407 |
| 0..30cm | silt | % | 23–36 | 8–53 | 407 |
| 0..30cm | bd.core | kg/m3 | 1400–1490 | 1230–1670 | 407 |
| 0..30cm | soc | g/kg | 3–4.8 | 0.5–14.4 | 407 |
| 0..30cm | ph.h2o | pH | 8.1–8.5 | 7.3–9.5 | 407 |
| 30..60cm | clay | % | 14–23 | 0–41 | 407 |
| 30..60cm | sand | % | 43–62 | 16–92 | 407 |
| 30..60cm | silt | % | 24–34 | 4–50 | 407 |
| 30..60cm | bd.core | kg/m3 | 1360–1480 | 1170–1670 | 407 |
| 30..60cm | soc | g/kg | 1.9–4.1 | 0.3–14.9 | 407 |
| 30..60cm | ph.h2o | pH | 8.1–8.7 | 7–10 | 407 |
| 60..100cm | clay | % | 14–22 | 0–40 | 407 |
| 60..100cm | sand | % | 44–61 | 16–92 | 407 |
| 60..100cm | silt | % | 25–34 | 4–56 | 407 |
| 60..100cm | bd.core | kg/m3 | 1410–1500 | 1230–1740 | 407 |
| 60..100cm | soc | g/kg | 1.5–3.5 | 0.3–11.4 | 407 |
| 60..100cm | ph.h2o | pH | 8.1–8.8 | 7.4–10.2 | 407 |
