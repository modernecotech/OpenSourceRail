# Retained civil campaign review

`first-campaign.json` is the compact intentional review output of
`tools/automation/civil-study.py run`, exported with:

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
