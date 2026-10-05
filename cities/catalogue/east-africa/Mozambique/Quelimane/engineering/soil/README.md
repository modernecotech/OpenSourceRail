# Quelimane civil soil screening

48 route/station sample locations; 48 complete profiles; 0 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 27 |
| fine-soil-plasticity-and-shrink-swell-tests | 48 |
| granular-density-and-groundwater-tests | 48 |

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
| 0..30cm | clay | % | 24–34 | 10–52 | 48 |
| 0..30cm | sand | % | 44–62 | 6–86 | 48 |
| 0..30cm | silt | % | 14–22 | 1–41 | 48 |
| 0..30cm | bd.core | kg/m3 | 1260–1310 | 1010–1480 | 48 |
| 0..30cm | soc | g/kg | 6.9–10.4 | 3.3–21.2 | 48 |
| 0..30cm | ph.h2o | pH | 6.5–6.8 | 5.5–7.9 | 48 |
| 30..60cm | clay | % | 26–36 | 10–55 | 48 |
| 30..60cm | sand | % | 44–61 | 8–88 | 48 |
| 30..60cm | silt | % | 13–20 | 0–38 | 48 |
| 30..60cm | bd.core | kg/m3 | 1210–1280 | 840–1560 | 48 |
| 30..60cm | soc | g/kg | 4.1–6.1 | 1.8–12.9 | 48 |
| 30..60cm | ph.h2o | pH | 6.7–7 | 5.6–8.4 | 48 |
| 60..100cm | clay | % | 27–37 | 10–57 | 48 |
| 60..100cm | sand | % | 43–60 | 8–88 | 48 |
| 60..100cm | silt | % | 12–20 | 0–37 | 48 |
| 60..100cm | bd.core | kg/m3 | 1120–1220 | 760–1630 | 48 |
| 60..100cm | soc | g/kg | 3.9–6.1 | 1.7–12.2 | 48 |
| 60..100cm | ph.h2o | pH | 6.7–7 | 5–8.6 | 48 |
