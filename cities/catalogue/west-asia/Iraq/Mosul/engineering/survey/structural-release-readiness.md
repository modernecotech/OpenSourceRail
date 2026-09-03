# Mosul structural-release gate

- Status: **awaiting-structural-evidence**
- Lines: 6
- Technical screen passed: **no**
- Authority accepted: **no**

> The automated gate checks immutable solver provenance, per-asset schedule coverage, load-case/result reconciliation and independent-check completeness. It does not validate modelling assumptions, codes, loads, mesh quality, reinforcement, prestress, soil springs, fatigue detail, seismic response or structural safety.

> Only the structural and geotechnical engineers of record, independent checker, asset owner and approving authority can release the project structures in a signed controlled record.

## Current gates

- Missing technical roles: drainage_ground_readiness, structural_design_basis, structural_asset_schedule, load_case_register, opensees_model, opensees_report, calculix_input, calculix_report, structural_verification_report, independent_check_record
- Duplicate roles: none
- Authority findings:
  - structural acceptance record not received

## Controlled workflow

1. Accept drainage/ground design and freeze the project structural basis and load combinations.
2. Schedule every span, pier, abutment, foundation and special structure against line chainage.
3. Preserve OpenSees global/seismic/soil-spring and CalculiX component input/output hashes and convergence evidence.
4. Reconcile foundation, wind, seismic, fatigue and bearing/movement results per scheduled asset.
5. Close independent-check comments and obtain the signed structural release.
