"""Shared inclusion policy for the maintained Markdown index."""

from __future__ import annotations

from pathlib import Path


SKIP_PARTS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "node_modules",
    "target",
}

EXCLUDED_PREFIXES = (
    "legacy/",
    "docs/archives/",
    "docs/design-engine/ferrite-maglev/",
    "docs/design-engine/design-search/",
    "docs/design-engine/design-search-twins/",
    "docs/design-engine/electropermanent/",
    "docs/design-engine/halbach-scaling/",
    "docs/design-engine/magnetic-confirmation/",
    "docs/design-engine/passive-suspension/",
    "docs/design-engine/trip-dynamics/",
    "docs/design-engine/vehicle-optimisation/",
    "engineering/assurance/v052-",
    "engineering/assurance/v053-",
    "engineering/electropermanent/",
    "engineering/magnetic_confirmation/",
    "engineering/trip_dynamics/",
)

EXCLUDED_DOCS = {
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


def is_indexed_markdown(path: Path) -> bool:
    """Return whether a repository-relative Markdown path belongs in docs/INDEX."""
    name = path.as_posix()
    if not SKIP_PARTS.isdisjoint(path.parts):
        return False
    if name.startswith(EXCLUDED_PREFIXES):
        return False
    if name.startswith("cities/catalogue/") and name != "cities/catalogue/README.md":
        return False
    return name not in EXCLUDED_DOCS
