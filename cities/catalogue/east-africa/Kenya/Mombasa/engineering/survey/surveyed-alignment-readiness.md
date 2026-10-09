# Mombasa surveyed-alignment gate

- Status: **awaiting-surveyed-alignments**
- Lines expected: line-1, line-2, line-3, line-4, line-5, line-6, line-7, line-8, line-9, line-10, line-11, line-12, line-13, line-14, line-15, line-16, line-17
- Technical screen passed: **no**
- Authority accepted: **no**

> The automated gate proves receipt integrity, OSR-ALN hard-gate compliance, explicit horizontal/vertical/cant content, line and station reconciliation, deterministic LandXML re-import, and recorded interface tolerances. It does not establish that the survey, fit, clearances, possessions or construction design are correct.

> Only the appointed alignment designer, survey authority, track engineer and information manager can accept an alignment for design use in a controlled signed record.

## Current gates

- Missing technical roles: *:ground_model_readiness, *:interface_verification_report, line-1:surveyed_osr_aln, line-1:landxml_export, line-1:landxml_roundtrip_report, line-2:surveyed_osr_aln, line-2:landxml_export, line-2:landxml_roundtrip_report, line-3:surveyed_osr_aln, line-3:landxml_export, line-3:landxml_roundtrip_report, line-4:surveyed_osr_aln, line-4:landxml_export, line-4:landxml_roundtrip_report, line-5:surveyed_osr_aln, line-5:landxml_export, line-5:landxml_roundtrip_report, line-6:surveyed_osr_aln, line-6:landxml_export, line-6:landxml_roundtrip_report, line-7:surveyed_osr_aln, line-7:landxml_export, line-7:landxml_roundtrip_report, line-8:surveyed_osr_aln, line-8:landxml_export, line-8:landxml_roundtrip_report, line-9:surveyed_osr_aln, line-9:landxml_export, line-9:landxml_roundtrip_report, line-10:surveyed_osr_aln, line-10:landxml_export, line-10:landxml_roundtrip_report, line-11:surveyed_osr_aln, line-11:landxml_export, line-11:landxml_roundtrip_report, line-12:surveyed_osr_aln, line-12:landxml_export, line-12:landxml_roundtrip_report, line-13:surveyed_osr_aln, line-13:landxml_export, line-13:landxml_roundtrip_report, line-14:surveyed_osr_aln, line-14:landxml_export, line-14:landxml_roundtrip_report, line-15:surveyed_osr_aln, line-15:landxml_export, line-15:landxml_roundtrip_report, line-16:surveyed_osr_aln, line-16:landxml_export, line-16:landxml_roundtrip_report, line-17:surveyed_osr_aln, line-17:landxml_export, line-17:landxml_roundtrip_report
- Duplicate roles: none
- Authority findings:
  - alignment acceptance record not received

## Controlled workflow

Keep signed source surveys, native authoring files and large point clouds in controlled project storage. Git carries the empty receipt, requirements, reproducible checks and non-sensitive accepted exchange derivatives.

1. Accept survey control and the surveyed ground model.
2. Fit each line in the confirmed CRS/datum; explicitly issue horizontal, vertical and cant schedules.
3. Export one OSR-ALN and LandXML file per line and record the deterministic re-import hash and comparison tolerances.
4. Reconcile every platform and record yard, turnout and clearance dispositions per line.
5. Run this inspection and obtain the controlled multi-discipline acceptance record.
