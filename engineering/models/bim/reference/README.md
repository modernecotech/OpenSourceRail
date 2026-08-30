# Civil BIM Reference Package

This is the tracked, deterministic public-review federation. It lets GitHub
users inspect the current IFC4.3 model and its requirements/evidence without
installing the complete engineering toolchain.

| File | Purpose |
|---|---|
| [`civil-coordination.ifc`](civil-coordination.ifc) | IFC4.3 rail/civil/station/rolling-stock coordination model |
| [`civil-coordination.index.json`](civil-coordination.index.json) | Stable IDs, classifications, source revisions, quantities and relationships |
| [`civil-coordination.validation.json`](civil-coordination.validation.json) | IFC schema and project validation summary |
| [`civil-information-requirements.ids`](civil-information-requirements.ids) | Machine-checkable information requirements |
| [`civil-information-requirements.report.json`](civil-information-requirements.report.json) | Complete IDS result report |
| [`civil-coordination-issues.bcf`](civil-coordination-issues.bcf) | Open coordination issues in BCF 3.0 form |
| [`civil-coordination-issues.index.json`](civil-coordination-issues.index.json) | Reviewable BCF issue index |
| [`civil-construction-sequence.json`](civil-construction-sequence.json) | Deterministic construction stages and object assignments |
| [`lm3-manufacturing-reference.ifc`](lm3-manufacturing-reference.ifc) | IFC4.3 LM3 product hierarchy, semantic doors/windows/fixtures/motors, manufacturing methods, sequenced tasks and 20 tooling families |
| [`lm3-manufacturing-reference.index.json`](lm3-manufacturing-reference.index.json) | IFC counts, source hashes, semantic classes and deterministic validation summary |

Regenerate it from the authoritative component geometry and engineering
interchange code:

```bash
tools/automation/bonsai-civil.sh --generate \
  --out-dir engineering/models/bim/reference \
  --revision-id repository-reference
python3 engineering/interchange/trainset_manufacturing_ifc.py
```

These models are coordination, product-structure and manufacturing-method
evidence, not a construction release. The LM3 IFC deliberately distinguishes
multi-part tooling coordination geometry from controlled fabrication/NC
surfaces. Repeated City Studio jobs and render intermediates remain under
`build/`; only this named review set is retained in Git.
