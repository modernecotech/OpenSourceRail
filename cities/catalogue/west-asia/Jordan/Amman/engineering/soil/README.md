# Amman civil soil screening

745 route/station sample locations; 732 complete profiles; 13 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 13 |
| fine-soil-plasticity-and-shrink-swell-tests | 731 |
| granular-density-and-groundwater-tests | 527 |
| silt-moisture-frost-and-erosion-review | 208 |

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
| 0..30cm | clay | % | 20–30 | 5–43 | 732 |
| 0..30cm | sand | % | 34–55 | 8–84 | 732 |
| 0..30cm | silt | % | 24–37 | 9–54 | 732 |
| 0..30cm | bd.core | kg/m3 | 1360–1460 | 1160–1630 | 732 |
| 0..30cm | soc | g/kg | 2.5–12.3 | 0.9–28.1 | 732 |
| 0..30cm | ph.h2o | pH | 7.6–8.1 | 6.8–8.8 | 732 |
| 30..60cm | clay | % | 20–32 | 4–46 | 732 |
| 30..60cm | sand | % | 33–57 | 9–87 | 732 |
| 30..60cm | silt | % | 22–36 | 4–52 | 732 |
| 30..60cm | bd.core | kg/m3 | 1430–1580 | 1260–1790 | 732 |
| 30..60cm | soc | g/kg | 1.7–5.1 | 0.4–12.1 | 732 |
| 30..60cm | ph.h2o | pH | 7.5–8.3 | 6.6–9.3 | 732 |
| 60..100cm | clay | % | 21–33 | 4–48 | 732 |
| 60..100cm | sand | % | 33–58 | 8–89 | 732 |
| 60..100cm | silt | % | 21–35 | 0–54 | 732 |
| 60..100cm | bd.core | kg/m3 | 1440–1610 | 1230–1840 | 732 |
| 60..100cm | soc | g/kg | 1.3–3.7 | 0.1–7.9 | 732 |
| 60..100cm | ph.h2o | pH | 7.4–8.4 | 6.6–9.5 | 732 |
