# Public Overview

The [one-page OpenSourceRail overview](open-source-rail-overview.html) is a
generated public introduction. Its scope counts come from
`marketing/manifest.json`; its trainset figures come from the generated LM3
build-cost record. It is not a second technical source of truth.

Regenerate or check it:

```bash
python3 scripts/generate-introduction-brochure.py
python3 scripts/generate-introduction-brochure.py --check
```

Create a release PDF when WeasyPrint is available:

```bash
mkdir -p build/releases
weasyprint docs/brochures/open-source-rail-overview.html \
  build/releases/open-source-rail-overview.pdf
```

Release PDFs belong under `build/releases/` or in a tagged GitHub release;
only the generated HTML review copy is tracked.
