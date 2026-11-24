# Retired digital twin candidate exports

The 42 tar archives listed in [the manifest](manifest.json) are earlier
research exports. They are absent from the current digital twin publication
manifest and have no live test, workflow input, or validation page link. Their
original paths, Git blob IDs, and exact byte sizes are pinned to commit
`001ae0807cf070716bcc57d8746b0765eeb672fc`. The original payloads and
their historical references remain retrievable without changing the executed
records or claiming physical acceptance.

Six archives bound by `docs/design-engine/digital-twin/manifest.json` remain
in the checkout. Six different archives linked by its historical
`validation.md` also remain, including the archive used by sourcing tests and
the sourcing workflow. The two sets retain their own source epochs.

To restore the first export in the manifest to an empty directory, run:

```sh
mkdir -p build/retired-twin
archive=docs/design-engine/digital-twin/075afc1dffe6af7915132a52cf1a6f8b002bf70a043f937d41ce170c9a6ae254.tar.gz
git archive 001ae0807cf070716bcc57d8746b0765eeb672fc "$archive" | tar -x -C build/retired-twin
git hash-object "build/retired-twin/$archive"
```

The expected Git blob ID for this example is `d056c005786b7456eb1403d88553ef0de97104b8`. Use the path and expected blob ID in the corresponding manifest row for any other export.
