# Converter Golden Fixtures

The files in this directory are synthetic, abbreviated golden fixtures for
`osr-aln-convert`. They are retained because the round-trip test compares the
generated OSR-ALN output byte-for-byte.

Despite the historical `samawah-line1` filename and plausible coordinates,
these files are **not survey data, not the current Samawah network, and not a
deployment alignment**. The geometry is only 3 km long, station IDs are
placeholders, and the civil class is intentionally all at grade so every
converter review hook remains visible.

Deployment-controlled alignments live under `docs/civil/` and require the
survey and approval fields specified by `docs/civil/osr-aln-format.md`.
