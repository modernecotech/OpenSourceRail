"""Factory input/source closure, usable without importing numerical libraries."""

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PACKAGE = Path(__file__).resolve().parent


def source_hashes():
    paths = [
        *PACKAGE.glob("*.py"),
        *PACKAGE.glob("data/*.json"),
        ROOT / "lib/templates/baghdad-factory.toml",
        ROOT / "design/component-catalogue/src/osr_mech/civil/decked_pi.py",
        ROOT / "engineering/industrialisation/assembly.py",
        ROOT / "engineering/industrialisation/common.py",
        ROOT / "engineering/design_engine/civil_qualification.py",
        ROOT / "engineering/design_engine/contracts.py",
        ROOT / "design/component-catalogue/src/osr_mech/freecad_assembly_review.py",
    ]
    return {
        p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(paths)
    }
