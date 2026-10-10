# Retained civil campaign review

`first-campaign.json` is the compact intentional review output of
`tools/automation/civil-study.py run --deployment reference`, exported with:

```sh
tools/automation/osr-python tools/automation/export-civil-study-review.py \
  build/engineering/civil-studies/first-campaign
```

Its named consumer is `engineering/analysis/tests/test_civil_exploration_review.py`.
It retains the frozen inputs, exact dependency/native identities, independent
benchmarks, quantity/response summaries, convergence, failures and native output
checksums. Full native fields remain under `build/engineering/civil-studies/`;
regenerate them with the [workbench](../README.md). These are research results
with unresolved engineering feasibility and no physical or operating release.

Run the exporter with `--check` against the same sealed bundle to verify this
compact derivative. Historical review inputs stay explicit; future material,
train or model changes require a new campaign and intentional fixture refresh.

`programme-review.json` and `programme-review.md` retain the expanded C01–C14
software audit, component benchmarks, multi-seed search, range sensitivity,
native solid/nonlinear shortlist checks, commercial unknowns, safe retrieval
and the blocked promotion proposal. Generate them with:

```sh
tools/automation/osr-python tools/automation/export-civil-programme-review.py \
  build/engineering/civil-studies/completed-software-programme
```

The named consumer is
`engineering/analysis/tests/test_civil_exploration_programme_review.py`.
Every external acceptance item remains visible; actual physical measurements,
supplier commitments and authority signatures are not supplied by these records.

`baghdad-qualification/qualification.json` and `.md` retain the user-selected
deployment readiness and source hashes. They are input-gap records, with no
solver results or release claim. Their generator is `civil-study.py qualification`
and their named consumer is `engineering/analysis/tests/test_civil_qualification.py`.
Regenerate into a fresh scratch directory, compare to the retained pair, and
refresh intentionally if the controlled inputs change.

`complete-system-review.json` and `.md` retain the expanded whole-package search,
source/native identities, conditional cost/mass/time leaders, failed/provisional
outcomes, diverse 3D/solid confirmations and all external gates.
`system-choices.svg` shows canonical sections/footprints; `pareto.svg` shows
synthetic scenario tradeoffs. Actual prices remain null and no qualified/global
optimum is claimed. The named consumer is
`engineering/analysis/tests/test_civil_system_choices.py`; the generator is:

```sh
tools/automation/osr-python tools/automation/export-civil-system-review.py \
  build/engineering/civil-studies/baghdad-complete-systems-v2 --update-readme
```
