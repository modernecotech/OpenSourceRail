# Contributing To OpenSourceRail

OpenSourceRail is pre-1.0 infrastructure software and documentation. It
welcomes review, tests, corrections, reproducible data, and narrowly
scoped implementation work, but it is not yet a certified railway
product and should not be described as one.

## Good First Contributions

- Fix stale links, unclear wording, units, assumptions, or generated
  documentation drift.
- Add simulator scenarios, fault-injection cases, or city data that can
  be regenerated.
- Improve tests for existing Rust crates and Python sidecars.
- Review operations, maintenance, manufacturing, QA, hardware, and
  certification evidence from real practitioner experience.
- Validate COTS hardware, BOM rows, wiring maps, CAD assumptions, or
  rolling-stock manufacturing steps against real supplier data.

## Safety And Certification Boundaries

Safety-related changes need extra care:

- Use "SIL target" or "target assurance tier" unless an independent
  assessor has accepted a deployment-specific case.
- Do not remove fail-restrictive behavior without replacing the hazard
  argument and tests.
- Link safety claims to evidence: code, tests, formal model, hazard log,
  RFC, generated matrix, or field evidence.
- Keep production-service claims out of comments, docs, and release
  notes unless they are backed by deployment evidence.

OpenSourceRail produces reference artifacts. Operators, owners, prime
integrators, assessors, insurers, and regulators carry the statutory
safety case for a real railway.

## Development Workflow

1. Open or reference an issue for behavioral changes, safety claims,
   architecture decisions, generated data changes, or new public docs.
2. Keep pull requests focused. Separate wording cleanup, generated
   artifacts, code changes, and large data refreshes when practical.
3. Follow the local style. Prefer existing helpers, templates, and RFC
   patterns over new parallel structures.
4. Regenerate derived artifacts when sources change.
5. Include the checks you ran in the PR description.

Useful checks:

```bash
python3 scripts/repo-health.py --quiet
python3 scripts/check-markdown-links.py
python3 scripts/generate-doc-index.py
cargo test --workspace
pytest design-py/tests -q
PYTHONPATH=mechanical-py/src pytest mechanical-py/tests -q
```

For Samawah/RFC consistency:

```bash
PYTHONPATH=design-py/src pytest -q design-py/tests/test_rfc_drift.py
```

For the reader edition:

```bash
python3 scripts/build-doc-book.py
```

## Generated Artifacts

Generated city, operations, CAD, and evidence files should remain
reproducible from tracked sources. If a generated file changes, include
the command that produced it and avoid hand-editing generated rows unless
the generator is also updated.

## AI-Assisted Contributions

AI-assisted contributions are acceptable when the contributor takes
responsibility for the result. Do not submit code, text, data, images, or
technical claims copied from proprietary or incompatible sources. Check
citations, units, and generated artifacts before opening a PR.

## Licensing

The project split is:

- Software: Apache 2.0.
- Hardware designs: CERN-OHL-S v2.
- Documentation: CC-BY-SA 4.0.

By contributing, you agree that your contribution may be distributed
under the applicable license for the files you change. The complete
texts and path mapping are in [`LICENSE.md`](LICENSE.md) and
[`LICENSES/`](LICENSES/README.md).

## Communication

Use GitHub issues and pull requests for now. Prefer concrete reports:
file path, command, observed behavior, expected behavior, and any source
data needed to reproduce the result.
