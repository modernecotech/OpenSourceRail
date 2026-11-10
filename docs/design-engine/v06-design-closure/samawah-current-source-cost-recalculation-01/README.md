# Samawah current-source cost comparison

This run recalculates two Samawah map cases under the exact published v0.6
vehicle and planning seed, with both the project make/buy and China bulk-buy
price bases:

1. The published `original` alignment.
2. An unselected 20 m route simplification freshly generated from the exact current
   canonical plan, with each operational station coordinate held fixed and a
   20 m maximum two-way sampled-deviation screen.

The older merged-route packet is validated as provenance for continuing the
alignment improvement work. Its geometry is not transferred: one of its merged-stop positions
differs from the current canonical plan by 28.3 m. The simplification is
recomputed from the current published route at 20 m tolerance, with the current
operational stop coordinates fixed as route vertices. A 5 m sampled check is
performed in both directions in a local spherical azimuthal-equidistant
projection. The canonical plan supplies stop identities, dwell values and the
design-speed cap. Each city workflow is replay-verified, and the cost evaluator
must return all fourteen low/base/high scope totals.

The price comparison is a calculated Class C estimate, not a supplier
quotation. Each route edit proportionally transfers existing civil-class
chainage intervals and flags them for reassessment. It does not verify surveyed
right-of-way, access, crossings, utilities, ground, civil loads or buildability.
The study is restricted to Samawah and does not reprice the other 265 cities.

Run from a complete checkout containing source epoch
`897e36510812966bcef0e04fddebdd98bedee4af`:

```sh
python3 docs/design-engine/v06-design-closure/samawah-current-source-cost-recalculation-01/run.py \
  --root . \
  --output-dir /tmp/osr-samawah-current-source-cost-recalculation
```

The current agent workspace is a sparse checkout. Its temporary verification
mirror restores missing tracked city-source files from Git objects; the runner
does not alter sparse-checkout settings. A complete source tree is required for
standalone replay because the publication manifest pins all city inputs.
