# Historical publications before the comfort default

These records preserve the source-bound publications at revision `578ee3950b872bf30fbf9e4207b2bda85951bdd7`. The current comfort development design is selected through [the repository selector](../../../engineering/development-baseline.toml) and [current engineering dossier](../../design-engine/current/README.md).

Historical source hashes are checked against the recorded Git revision. They are not edited to match a different working tree. City root introductions can therefore move to the new default while earlier city calculations and source records remain traceable.

[Former reader](OpenSourceRail-Book.pdf) · [Former roadmap](ROADMAP.md) · [Archive receipt](manifest.json).

Use `./osr legacy verify` for historical source/payload integrity. This does not rerun numerical solvers or grant physical acceptance. To reproduce these pre-comfort publications, create a detached checkout at their exact recorded source with `./osr legacy checkout pre-comfort-default --path /tmp/opensourcerail-pre-comfort`; run the historical tools from that directory and keep outputs there. To run the original v0.4 applications, use `./osr legacy checkout v0.4.0 --path /tmp/opensourcerail-v04`. Remove each worktree when finished. Historical quantities and results remain separate from the current v0.6 candidate.
