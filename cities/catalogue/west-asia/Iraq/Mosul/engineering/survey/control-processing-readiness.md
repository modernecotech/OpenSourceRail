# Mosul survey-control processing

- Status: **awaiting-field-data**
- RTKLIB runtime: **not probed**
- Processing completed: **no**
- Technical screen passed: **no**
- Survey authority accepted: **no**

> The automated result is a reproducibility and solution-quality screen. It is not a network adjustment, survey certification or permission to use the control for design or construction.

> Only the appointed deployment survey authority can accept the control network after redundant occupations, independent checks, network adjustment, datum/geoid review and monument documentation.

## Current gates

- Missing processing roles: rover_observation, base_observation, navigation, rtklib_configuration
- Duplicate processing roles: none
- Processing-configuration findings: 0
- Missing authority-review roles: rover_observation, base_observation, navigation, rtklib_configuration, field_log, monument_schedule, network_adjustment_report, authority_acceptance_record

## Controlled-storage workflow

RINEX observations and navigation data remain in access-controlled project storage. Git records only the receipt manifest, file hashes, requirements and non-sensitive processing/acceptance summaries.

1. Put received files in access-controlled project storage.
2. Add one `SUR-CTRL` manifest row per file, including `file_role`, metadata and SHA-256.
3. Freeze the required RTKLIB settings, then run this processor; the four processing roles must occur exactly once.
4. Review RTKLIB outputs, complete independent checks and network adjustment, then add the controlled acceptance record.
5. Re-run; only the appointed survey authority's explicit record can close the authority gate.
