# Baghdad proposal publication

The complete proposal integrates Baghdad network, trains, civil and energy systems, Iraqi manufacturing, operations, delivery, financing and early repayment. Future national development has its own chapter and reconciled catalogue budget; no additional city is included in Baghdad finance.

- [Complete proposal PDF](Baghdad-Proposal.pdf)
- [Editable proposal](BAGHDAD-PROPOSAL.md)
- [Detailed schedules](DETAILED-SCHEDULES.md)
- [Supporting data archive](Baghdad-Proposal-Supporting-Data.zip)
- [Source inventory](source-inventory.csv)
- [National context and capital reconciliation](national-context.json)
- [Appendix source list](appendix-sources.json)
- [Publication manifest](manifest.json)
- [Archive member checksums](archive-manifest.json)

The PDF includes every current Baghdad Markdown report and selected shared standards. The archive preserves repository paths for all controlled Baghdad files, full operations tasks, every Baghdad financing case, national city design/scenario inputs and cited shared documents. References to other repository material remain links to the wider repository; the archive is an evidence publication rather than a standalone build environment. The archive member manifest checks all packaged files; the publication manifest is delivered alongside the archive and additionally checks the archive itself. No private credentials, operational databases or user identities are collected.

The urban railway is a planning proposal, with physical and operating gates open. The national chapter is a future option, without national loan commitments or revenue added to Baghdad. The shared plant and its EPC are counted once. Source values and all monthly/six-month calculations retain their evidence limits.

Regenerate with `.venv/bin/python tools/automation/build-baghdad-proposal.py`; validate with the same command plus `--check`. If the complete Baghdad operations payload is missing, first restore the exact archived input with `.venv/bin/python tools/automation/bootstrap_baghdad_tests.py`. Solver/geospatial files retained in the workspace are included and identified in the inventory.
