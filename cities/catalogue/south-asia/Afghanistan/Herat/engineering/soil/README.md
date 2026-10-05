# Herat civil soil screening

164 route/station sample locations; 161 complete profiles; 3 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| coverage-gap | 3 |
| fine-soil-plasticity-and-shrink-swell-tests | 161 |
| granular-density-and-groundwater-tests | 121 |
| silt-moisture-frost-and-erosion-review | 63 |

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
| 0..30cm | clay | % | 18–27 | 4–39 | 161 |
| 0..30cm | sand | % | 32–52 | 9–77 | 161 |
| 0..30cm | silt | % | 27–41 | 13–58 | 161 |
| 0..30cm | bd.core | kg/m3 | 1380–1440 | 1170–1650 | 161 |
| 0..30cm | soc | g/kg | 2.9–7 | 1.1–14.8 | 161 |
| 0..30cm | ph.h2o | pH | 7.5–7.9 | 6.8–8.4 | 161 |
| 30..60cm | clay | % | 21–29 | 6–42 | 161 |
| 30..60cm | sand | % | 36–52 | 13–82 | 161 |
| 30..60cm | silt | % | 26–35 | 9–51 | 161 |
| 30..60cm | bd.core | kg/m3 | 1400–1520 | 1230–1720 | 161 |
| 30..60cm | soc | g/kg | 2.3–4.4 | 0.6–9.5 | 161 |
| 30..60cm | ph.h2o | pH | 7.4–7.9 | 6.6–8.9 | 161 |
| 60..100cm | clay | % | 22–31 | 6–45 | 161 |
| 60..100cm | sand | % | 38–52 | 9–84 | 161 |
| 60..100cm | silt | % | 25–32 | 5–51 | 161 |
| 60..100cm | bd.core | kg/m3 | 1420–1570 | 1210–1780 | 161 |
| 60..100cm | soc | g/kg | 1.9–2.9 | 0.2–6.5 | 161 |
| 60..100cm | ph.h2o | pH | 7.3–7.9 | 6.5–9.1 | 161 |
