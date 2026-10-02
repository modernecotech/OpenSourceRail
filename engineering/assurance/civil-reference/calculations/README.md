# Civil calculation records

Small native CalculiX input/result files and OpenSees nodal results accompany `beam-sanity.json`. `drainage-sanity.json` records SWMM engine statistics for all three [synthetic scenarios](../drainage/). Their source and output digests are validated by the [civil compiler](../../../../tools/automation/civil_reference.py).

Reproduce from the repository root with `.venv/bin/python tools/automation/civil_reference.py --run-solvers`. The [package](../README.md) describes the elastic formulas, surrogate section and synthetic hydraulic limits. These are software/calculation demonstrations with project acceptance explicitly false.
