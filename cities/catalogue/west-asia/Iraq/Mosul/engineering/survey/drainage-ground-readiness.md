# Mosul drainage and ground-design gate

- Status: **awaiting-drainage-ground-evidence**
- Lines/stations: 6 / 69
- SWMM/ground technical screen passed: **no**
- OpenGeoSys required by received decision: **no**
- Authority accepted: **no**

> The automated gate reruns the received SWMM model, checks continuity and report provenance, reconciles drainage and geotechnical design to every current line and station, and validates catalogue foundation/ground-treatment selections. It does not validate rainfall, flood levels, soil parameters, hydraulic boundaries, structural capacity, settlement predictions or construction suitability.

> The drainage and geotechnical engineers of record, asset owner, relevant authority and information manager must accept the project inputs, calculations, selected variants, residual risks and immutable evidence record.

## Current gates

- Missing technical roles: ground_model_readiness, route_station_fit_readiness, accepted_hydrology_basis, swmm_model, swmm_processing_report, geotechnical_ground_model, foundation_ground_schedule, ground_design_verification_report, groundwater_coupling_decision
- Duplicate roles: none
- Authority findings:
  - drainage/ground acceptance record not received

## Controlled workflow

Keep borehole logs, laboratory results, sensitive asset data, native calculations and large model results in controlled project storage. Git carries requirements, receipts, hashes, reproducible exchange inputs and non-sensitive summaries.

1. Accept the ground model, route fit, hydrology basis and geotechnical model.
2. Run the project SWMM model; retain its input, report, source hashes and continuity results.
3. Size a checked catalogue foundation or ground-treatment system for every line and station scope.
4. Record whether groundwater/coupled analysis is warranted; require OpenGeoSys evidence only when the reviewed triggers say yes.
5. Close residual risks and obtain the signed drainage/geotechnical acceptance record.
