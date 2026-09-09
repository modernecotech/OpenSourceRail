# Khartoum civil soil screening

906 route/station sample locations; 881 complete profiles; 25 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 229 |
| coverage-gap | 25 |
| fine-soil-plasticity-and-shrink-swell-tests | 880 |
| granular-density-and-groundwater-tests | 42 |

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
| 0..30cm | clay | % | 20–32 | 6–41 | 881 |
| 0..30cm | sand | % | 32–59 | 15–83 | 881 |
| 0..30cm | silt | % | 21–37 | 8–45 | 881 |
| 0..30cm | bd.core | kg/m3 | 1380–1500 | 1110–1730 | 881 |
| 0..30cm | soc | g/kg | 2.4–5.5 | 0.6–10.7 | 881 |
| 0..30cm | ph.h2o | pH | 6.8–7.9 | 4.9–9.1 | 881 |
| 30..60cm | clay | % | 22–35 | 6–43 | 881 |
| 30..60cm | sand | % | 27–58 | 12–86 | 881 |
| 30..60cm | silt | % | 20–38 | 6–47 | 881 |
| 30..60cm | bd.core | kg/m3 | 1420–1540 | 1210–1770 | 881 |
| 30..60cm | soc | g/kg | 1.4–2.7 | 0–6.5 | 881 |
| 30..60cm | ph.h2o | pH | 6.8–8.6 | 4.9–9.6 | 881 |
| 60..100cm | clay | % | 23–35 | 5–43 | 881 |
| 60..100cm | sand | % | 27–56 | 11–88 | 881 |
| 60..100cm | silt | % | 21–38 | 5–48 | 881 |
| 60..100cm | bd.core | kg/m3 | 1380–1560 | 1120–1790 | 881 |
| 60..100cm | soc | g/kg | 1.3–2.7 | 0–6.5 | 881 |
| 60..100cm | ph.h2o | pH | 6.8–8.6 | 4.8–9.8 | 881 |
