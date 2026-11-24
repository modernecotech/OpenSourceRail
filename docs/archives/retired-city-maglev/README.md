# Retired city maglev study packets

The 265 former PM-maglev city study directories outside Baghdad have been removed from active city paths. They contained 1,060 files and 2,701,587,089 bytes of historical `summary.json`, `network.svg`, `manufacturing.json` and `retained-records.json` payloads. Their [inventory](manifest.json) pins each complete four-file Git tree at commit `001ae0807cf070716bcc57d8746b0765eeb672fc`. The Baghdad packet remains at its original path for explicit retained analysis readers. No city input, maintained outline, map context, current candidate selection or physical disposition changes with this retirement.

Current city maps and estimates are in each city's `engineering/outline/` directory and the [city dossier index](../../design-engine/city-dossiers/index.json). The retired maglev studies remain reproducible only as their original historical evaluations; their results must not be transferred to the selected wheel-supported reference.

The [hydration utility](../../../tools/automation/hydrate-retired-city-maglev.py) checks every pinned tree and Git blob. It never fetches over the network implicitly. On a shallow clone that lacks the commit, first run:

```sh
git fetch --no-tags --depth=1 origin 001ae0807cf070716bcc57d8746b0765eeb672fc
```

Then verify or restore into a **new, nonexistent destination** under the ignored build directory:

```sh
python3 tools/automation/hydrate-retired-city-maglev.py --city samawah --check
python3 tools/automation/hydrate-retired-city-maglev.py --city samawah --output build/retired-samawah
python3 tools/automation/hydrate-retired-city-maglev.py --all --check
python3 tools/automation/hydrate-retired-city-maglev.py --all --output build/retired-city-maglev-all
```

The utility uses `git archive`, compares every restored file with its source Git blob and publishes the destination only after complete verification. It reserves projected disk space and checks the 20 GiB floor during extraction. A direct `git archive` of an individual manifest path also recovers the original bytes if the pinned commit is present; compare `git rev-parse COMMIT:PATH` with the manifest's `git_tree_oid` before using them.
