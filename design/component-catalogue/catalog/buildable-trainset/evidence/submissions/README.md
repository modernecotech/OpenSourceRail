# First-Article Evidence Submissions

This folder accepts reviewed evidence metadata, not placeholder results. Name a submission `{evidence-package-id}-{test-or-review-id}.json` and include:

- `evidence_package_id` and status (`evidence-received` or `independently-accepted`);
- accountable `performed_by` and independent `reviewed_by` identities;
- exact LM3 configuration and procedure revision;
- test date and calibrated equipment ids/due dates;
- repository-relative raw/report/photo artifacts with their SHA-256 values.

Run `python3 tools/automation/validate-lm3-first-article-evidence.py`. The validator rejects missing artifacts and checksum drift. Do not add a record for a test that has not been performed.
