# Mosul surveyed-ground-model gate

- Status: **awaiting-ground-model-data**
- Technical inspection completed: **no**
- Technical screen passed: **no**
- Survey authority accepted: **no**

> Automated inspection checks file integrity, GeoPackage structure, independent-check residuals and processing-report completeness. It does not prove feature completeness, datum correctness or fitness for design.

> Only the appointed survey authority and information manager can accept the master ground model after control, coverage, void, epoch, uncertainty, CRS and vertical-datum review.

## Current gates

- Missing technical roles: control_acceptance_report, topographic_features, terrain_dtm, checkpoint_residuals, odm_processing_report, orthophoto, registered_point_cloud, cloudcompare_qa_report, void_register, master_ground_model
- Duplicate roles: none
- Missing authority-review roles: control_acceptance_report, topographic_features, terrain_dtm, checkpoint_residuals, odm_processing_report, orthophoto, registered_point_cloud, cloudcompare_qa_report, void_register, master_ground_model, ground_model_acceptance_record
- Authority-record findings:
  - ground-model acceptance record not received

## Controlled workflow

Keep source imagery, raw scans and intermediate dense clouds in access-controlled project storage. Git records requirements, file hashes, non-sensitive QA summaries and accepted derivatives only.

1. Complete accepted survey control before registering terrain or clouds.
2. Process imagery in OpenDroneMap and registration/comparison in CloudCompare; preserve settings, source/output hashes and QA reports.
3. Build the federated master GeoPackage in the approved horizontal CRS and vertical datum.
4. Add every derivative to the shared receipt with its immutable hash and independent checker.
5. Run inspection, resolve residual/coverage findings, and obtain the controlled authority acceptance record.
