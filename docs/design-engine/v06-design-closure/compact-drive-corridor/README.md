# Compact-drive mapped-corridor attempt

This is the retained, source-bound result of a bounded attempt to propagate a
new compact-drive vehicle into Baghdad and Samawah corridor calculations. It
does **not** close the mapped-corridor or candidate-selection gates.

## Identity and result

| Record | Identity |
| --- | --- |
| Physical candidate | `75075df9247dfff7082a78eadc273d3a99f37e5486450621536c43b1bfa2f797` |
| Body evaluation | `fdac4907a6a867f0b4f27e0876a772d1b54d526ec323beb3b6d9a155e0e00b21` |
| Request | `0d3787c759ce6a5734de0083962fedc8ef42579b3de994f6bdf8a8d97b35b51f` |
| Corridor evaluation | `7139e31f3ba0551fb2062fc94a310f568c1c69f2bda739b80c81b29da985b180` |
| Package manifest | `a7d974d2ef678e760888abcdcd84b382a6e0b29906f89a881e2abb48cd0ffadc` |
| Source commit | `0b32f51f03cba52b2e5cca1aa3892c5f42bf40dd` |

The body layout is defined, but installed mass is incomplete. Both route
records stopped before catalogue geometry because the pinned source overlay
did not include the required Baghdad and Samawah `map-context.json.gz` files.
There were **zero geometry trials**, no project bundle, no service simulation,
no fleet/energy result, no fourteen-scope price, and no native solver run. The
input JSON bytes were subsequently recovered and added to the evidence package;
the pipeline was not rerun.

The package leaves unknown values null and all engineering, physical,
manufacturing and operating acceptance flags false. It does not change the
selected development reference. The separate 205 m route geometry result is
for a different candidate and cannot be combined with this record.

## Evidence and replay limits

- `request.json`, `result.json` and the manifest preserve the candidate,
  evaluation and request identities.
- `body.json.gz` is the candidate source artifact.
- `source-overlay-manifest.json` records the 103 exact source-overlay hashes.
- `inputs/` contains the recovered Baghdad and Samawah request bytes.
- `attempts.json`, `correction.json` and `input-resolution.json` preserve the
  failed attempts and recovery history.
- `runner-attempt-03.py` records the bounded runner source.

The manifest does not claim that every historical attempt was reproducible in
the current environment. This is digital research evidence only; it is not a
physical or financial validation.
