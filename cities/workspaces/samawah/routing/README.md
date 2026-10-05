# Samawah City Studio routing bundle

This directory contains the source-locked planning surface used when
City Studio creates a demand-aware manual line. The raster files are raw
little-endian arrays despite their `.npy` suffix, matching `osr-routing`.

The bundle retains the pipeline's 20 m Samawah planning resolution (factor 1).
This avoids treating a platform on a narrow dry river bank as a station in a
predominantly wet 100 m aggregate cell. Aggregation preserves any buildable cell,
water coverage percentage, the minimum buildable cost and maximum demand.
Elevation is averaged and slope is recalculated on the retained grid to avoid
amplifying one-pixel DEM noise. The derivation record pins the SHA-256 of every
upstream file. Elevation comes from the public NASA/NGA SRTM-derived Skadi HGT
tiles in the AWS Open Data Terrain Tiles bucket; it is planning evidence, not a
surveyed ground model.

Add or refresh open terrain and independent water evidence before downsampling:

    python3 tools/automation/augment-routing-terrain.py \
      --osm-json .cache/osr-pipeline/osm/samawah.json \
      --sidecar .cache/osr-pipeline/rasters/samawah.grid.json \
      --terrain-cache .cache/osr-pipeline/terrain

Regenerate or verify it from a populated local pipeline cache:

    python3 tools/automation/downsample-routing-bundle.py \
      .cache/osr-pipeline/rasters/samawah.grid.json \
      cities/workspaces/samawah/routing --slug samawah --factor 1

    python3 tools/automation/downsample-routing-bundle.py \
      .cache/osr-pipeline/rasters/samawah.grid.json \
      cities/workspaces/samawah/routing --slug samawah --factor 1 --check

This surface supports deterministic comparison of city-scale alternatives. It
is not survey data, a final alignment, or evidence of detailed constructability.
