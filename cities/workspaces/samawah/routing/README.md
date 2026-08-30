# Samawah City Studio routing bundle

This directory contains the compact, source-locked planning surface used when
City Studio creates a demand-aware manual line. The raster files are raw
little-endian arrays despite their `.npy` suffix, matching `osr-routing`.

The bundle is a deterministic 5× downsample of the pipeline's 20 m Samawah
rasters, giving a 100 m planning grid. Aggregation preserves any buildable cell,
the minimum buildable cost, and maximum demand in each block. The derivation
record pins the SHA-256 of every upstream file.

Regenerate or verify it from a populated local pipeline cache:

    python3 tools/automation/downsample-routing-bundle.py \
      .cache/osr-pipeline/rasters/samawah.grid.json \
      cities/workspaces/samawah/routing --slug samawah --factor 5

    python3 tools/automation/downsample-routing-bundle.py \
      .cache/osr-pipeline/rasters/samawah.grid.json \
      cities/workspaces/samawah/routing --slug samawah --factor 5 --check

This surface supports deterministic comparison of city-scale alternatives. It
is not survey data, a final alignment, or evidence of detailed constructability.
