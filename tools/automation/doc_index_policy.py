"""Shared inclusion policy for the maintained Markdown index."""

from __future__ import annotations

from pathlib import Path


SKIP_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    ".venv-search",
    "node_modules",
    "target",
}

EXCLUDED_PREFIXES = (
    "legacy/",
    "docs/archives/",
    "docs/design-engine/.",  # Private/retired working directories are not maintained entrypoints.
    "docs/design-engine/ferrite-maglev/",
    "docs/design-engine/design-search/",
    "docs/design-engine/design-search-twins/",
    "docs/design-engine/electropermanent/",
    "docs/design-engine/halbach-scaling/",
    "docs/design-engine/magnetic-confirmation/",
    "docs/design-engine/passive-suspension/",
    "docs/design-engine/trip-dynamics/",
    "docs/design-engine/vehicle-optimisation/",
    "docs/releases/v0.6.0/",
    "engineering/assurance/v052-",
    "engineering/assurance/v053-",
    "engineering/electropermanent/",
    "engineering/magnetic_confirmation/",
    "engineering/trip_dynamics/",
)

EXCLUDED_DOCS = {
    "cities/Baghdad/CENTRAL-RING-NETWORK.md",
    "cities/Baghdad/NETWORK.md",
    "cities/Baghdad/RING-GRID.md",
    "cities/Baghdad/RING-NETWORK.md",
    "cities/Baghdad/SPACED-RINGS.md",
    "cities/Baghdad/WIDER-RING.md",
    "engineering/ferrite_maglev/README.md",
    "engineering/ferrite_maglev/city-index.md",
    "engineering/ferrite_maglev/observer-prototype/README.md",
    "control-electronics/README.md",
    "crates/osr-maglev-control/README.md",
    "docs/design-engine/design-search-interpretation.md",
    "docs/design-engine/ferrite-maglev/pilot-delivery/README.md",
    "docs/design-engine/ferrite-maglev/capability-migration/README.md",
    "docs/releases/v0.5.1.md",
    "docs/releases/v0.5.2.md",
}

CURRENT_DESIGN_ENTRYPOINTS = {
    "docs/design-engine/current/README.md",
    "docs/design-engine/city-atlas/README.md",
    "docs/design-engine/city-dossiers/README.md",
    "docs/design-engine/outline-completion/README.md",
    "docs/design-engine/line30-current-20261117/README.md",
    "docs/design-engine/v07-affordable-corridor/README.md",
    "docs/design-engine/v07-architecture-decision/README.md",
    "docs/design-engine/v07-prototype-bundle/README.md",
    "docs/design-engine/v07-powered-bogie/README.md",
    "docs/design-engine/v07-powered-vehicle/README.md",
    "docs/design-engine/v07-powered-cost/README.md",
    "docs/design-engine/v07-independent-brake/README.md",
    "docs/design-engine/v07-simple-span/README.md",
    "docs/design-engine/v07-representative-car/README.md",
    "docs/design-engine/v07-segmented-span/README.md",
}


def is_indexed_markdown(path: Path) -> bool:
    """Return whether a repository-relative Markdown path belongs in docs/INDEX."""
    name = path.as_posix()
    if not SKIP_PARTS.isdisjoint(path.parts):
        return False
    if name.startswith(EXCLUDED_PREFIXES):
        return False
    if name.startswith("docs/design-engine/"):
        return name in CURRENT_DESIGN_ENTRYPOINTS
    if name.startswith("cities/catalogue/") and name != "cities/catalogue/README.md":
        return False
    return name not in EXCLUDED_DOCS
