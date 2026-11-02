# Conditional vehicle mass and support sensitivity

This selected-car calculation uses pinned located geometry and replaces each named residual account once. Every residual centroid is independently assumed to lie within the 17 m car body; these synthetic inputs are not verified installation envelopes or guaranteed physical bounds.

| Mass case | Accounted mass per car (kg) | Assumed longitudinal CG interval (m) | Left bogie reaction interval (kN) |
|---|---:|---:|---:|
| low | 17203.96 | -3.989 to 3.987 | 31.80 to 136.94 |
| base | 19222.00 | -4.463 to 4.461 | 28.55 to 159.97 |
| high | 21240.04 | -4.846 to 4.845 | 25.31 to 183.01 |

The calculation assumes two vertical point supports and rigid static equilibrium. Account overlap, actual installed mass and CG, load sharing among axles, suspension behaviour and physical qualification remain unknown. Negative reactions are reported, not clipped. These conditional results do not change the selected railway or authorize manufacture or operation.

Original worker packages and independent replay preserve v1 and v2 as superseded, and v3 as the current analytical sensitivity. Recorded worker resource limits and runtimes are not independently attested; no filesystem or network sandbox was enforced. In v2 and v3, the `source-base-revision.txt` files identify the preparation predecessor; the recorded source commits were instead based on `dad8c4bedb2361d3e621e9def312273167279027`, as stated in their manifests.
