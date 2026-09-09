# Diwaniyah civil soil screening

99 route/station sample locations; 98 complete profiles; 1 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 1 |
| fine-soil-plasticity-and-shrink-swell-tests | 59 |
| granular-density-and-groundwater-tests | 77 |
| silt-moisture-frost-and-erosion-review | 6 |

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
| 0..30cm | clay | % | 17–26 | 4–36 | 98 |
| 0..30cm | sand | % | 37–57 | 16–81 | 98 |
| 0..30cm | silt | % | 26–37 | 11–50 | 98 |
| 0..30cm | bd.core | kg/m3 | 1490–1520 | 1280–1720 | 98 |
| 0..30cm | soc | g/kg | 2.2–4.2 | 0.4–9.2 | 98 |
| 0..30cm | ph.h2o | pH | 8–8.4 | 7.5–9.6 | 98 |
| 30..60cm | clay | % | 18–27 | 2–39 | 98 |
| 30..60cm | sand | % | 37–55 | 14–91 | 98 |
| 30..60cm | silt | % | 25–35 | 5–50 | 98 |
| 30..60cm | bd.core | kg/m3 | 1450–1540 | 1230–1760 | 98 |
| 30..60cm | soc | g/kg | 1.8–2.8 | 0–8.3 | 98 |
| 30..60cm | ph.h2o | pH | 8.3–8.8 | 7.6–10.1 | 98 |
| 60..100cm | clay | % | 18–27 | 3–40 | 98 |
| 60..100cm | sand | % | 37–55 | 15–91 | 98 |
| 60..100cm | silt | % | 26–36 | 5–50 | 98 |
| 60..100cm | bd.core | kg/m3 | 1460–1570 | 1230–1820 | 98 |
| 60..100cm | soc | g/kg | 1.4–2.5 | 0–6.5 | 98 |
| 60..100cm | ph.h2o | pH | 8.3–8.9 | 7.6–10.2 | 98 |
