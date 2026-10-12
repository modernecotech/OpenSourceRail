# Hyderabad-Pk civil soil screening

5,732 route/station sample locations; 5,699 complete profiles; 33 profiles with missing data.

Published soilDB 2020–2022 predictions, 120 m pixels, 0–30 / 30–60 / 60–100 cm depths. Mean and p16–p84 are retained for clay, sand, silt, bulk density, organic carbon and pH.

The [samples](samples.csv), [source receipt](source-receipt.json), [map](sample-locations.geojson) and [civil investigation plan](civil-investigation-plan.json) are reproducible planning inputs. Each station and civil segment has an investigation scope. These records do not close the surveyed ground-model or foundation-design gates.

| Investigation trigger | Sample locations |
|---|---:|
| acidic-soil-durability-testing | 319 |
| coverage-gap | 33 |
| fine-soil-plasticity-and-shrink-swell-tests | 2646 |
| granular-density-and-groundwater-tests | 5699 |

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
| 0..30cm | clay | % | 13–22 | 0–37 | 5699 |
| 0..30cm | sand | % | 49–69 | 26–96 | 5699 |
| 0..30cm | silt | % | 18–29 | 3–43 | 5699 |
| 0..30cm | bd.core | kg/m3 | 1420–1550 | 1200–1690 | 5699 |
| 0..30cm | soc | g/kg | 1.9–5.7 | 0.4–13.2 | 5699 |
| 0..30cm | ph.h2o | pH | 6.5–8.3 | 4.8–9.2 | 5699 |
| 30..60cm | clay | % | 14–24 | 0–40 | 5699 |
| 30..60cm | sand | % | 49–70 | 16–99 | 5699 |
| 30..60cm | silt | % | 16–27 | 0–43 | 5699 |
| 30..60cm | bd.core | kg/m3 | 1450–1570 | 1210–1770 | 5699 |
| 30..60cm | soc | g/kg | 1.1–3.8 | 0–10.9 | 5699 |
| 30..60cm | ph.h2o | pH | 6.3–8.8 | 4.3–9.7 | 5699 |
| 60..100cm | clay | % | 15–24 | 0–42 | 5699 |
| 60..100cm | sand | % | 50–70 | 16–98 | 5699 |
| 60..100cm | silt | % | 15–26 | 0–46 | 5699 |
| 60..100cm | bd.core | kg/m3 | 1460–1590 | 1210–1820 | 5699 |
| 60..100cm | soc | g/kg | 1–3.7 | 0–9.5 | 5699 |
| 60..100cm | ph.h2o | pH | 6.3–8.9 | 4.3–10.2 | 5699 |
