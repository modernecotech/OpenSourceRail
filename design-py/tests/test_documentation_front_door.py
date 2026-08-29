"""Keep public entry points concise and tied to canonical evidence."""

from __future__ import annotations

import runpy
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def test_root_readme_is_a_concise_developing_world_front_door() -> None:
    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert len(text.splitlines()) <= 220
    assert "265 cities in 43 developing countries" in text
    assert "one European comparison model" in text
    assert "Lyon" not in text
    assert "open-source-rail-introduction.html" not in text
    assert "docs/outreach" not in text
    assert "marketing/" not in text
    assert "## Find Your Way" in text
    assert "## Source Of Truth" in text
    assert "only human-facing front door" in text


def test_navigation_and_setup_have_one_documented_source() -> None:
    root = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    hub = (REPO_ROOT / "docs/README.md").read_text(encoding="utf-8")
    inventory = (REPO_ROOT / "docs/INDEX.md").read_text(encoding="utf-8")

    assert len(hub.splitlines()) <= 30
    assert "root README" in hub
    assert "does not repeat" in hub
    assert "not a reading path or a technical source of truth" in hub
    assert inventory.startswith("# Generated Markdown Inventory\n")
    assert "not a\nreading path or source of truth" in inventory

    tracked = subprocess.check_output(
        ["git", "ls-files", "*.md"], cwd=REPO_ROOT, text=True
    ).splitlines()
    setup_sources = [
        relative
        for relative in tracked
        if (REPO_ROOT / relative).is_file()
        and "./install.sh" in (REPO_ROOT / relative).read_text(encoding="utf-8")
    ]
    assert setup_sources == ["README.md"]

    for source in (
        "docs/ARCHITECTURE.md",
        "lib/city-batches/world-sample.toml",
        "projects/README.md",
        "mechanical-py/src/osr_mech/",
        "docs/repository-artifact-policy.md",
    ):
        assert source in root


def test_documentation_and_tooling_have_no_host_specific_paths() -> None:
    tracked = subprocess.check_output(
        ["git", "ls-files"], cwd=REPO_ROOT, text=True
    ).splitlines()
    text_suffixes = {".md", ".py", ".sh", ".toml", ".yml", ".yaml"}
    host_paths = ("/home/" + "hayder/", "/home/" + "ha/")
    offenders: list[str] = []
    for relative in tracked:
        path = REPO_ROOT / relative
        if path.suffix not in text_suffixes or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if any(host_path in text for host_path in host_paths):
            offenders.append(relative)
    assert offenders == []


def test_thin_wrapper_directories_do_not_return() -> None:
    for relative in (
        "docs/brochures",
        "docs/city-studio",
        "docs/hardware",
        "docs/releases",
        "engineering/energy",
        "engineering/gis",
        "engineering/software",
        "hardware/trainset-interiors",
    ):
        assert not (REPO_ROOT / relative).exists()
    assert list((REPO_ROOT / "hardware").glob("*/bom/.gitkeep")) == []
    assert list((REPO_ROOT / "hardware").glob("*/gerbers/.gitkeep")) == []


def test_public_overview_is_generated_from_current_metrics() -> None:
    generator = runpy.run_path(
        str(REPO_ROOT / "scripts/generate-introduction-brochure.py")
    )
    output = generator["OUTPUT"]
    actual = output.read_text(encoding="utf-8")
    assert actual == generator["render"]()
    assert "265" in actual
    assert "43" in actual
    assert "$900k" in actual
    assert "$885k" in actual
    assert "$2.98M" not in actual
    assert "Lyon" not in actual
    assert "campaign" not in actual.lower()
    assert "hayder@modernecotech.com" not in actual
    assert not (
        REPO_ROOT / "docs/brochures/open-source-rail-introduction.html"
    ).exists()


def test_public_portfolio_and_deployment_examples_exclude_europe() -> None:
    portfolio = (REPO_ROOT / "docs/portfolio-summary.md").read_text(encoding="utf-8")
    deployment = (REPO_ROOT / "docs/deployment-model.md").read_text(encoding="utf-8")
    assert "265-city / 43-country" in portfolio
    assert "European comparison designs" in portfolio
    assert "266-city / 44-country" not in portfolio
    assert "Lyon" not in portfolio
    assert "Lyon" not in deployment
    assert not (
        REPO_ROOT / "docs/outreach/open-source-rail-outreach-contacts.md"
    ).exists()


def test_private_campaign_material_is_not_in_the_public_tree() -> None:
    assert not (REPO_ROOT / "marketing").exists()
    assert not (REPO_ROOT / "scripts/generate-marketing-campaigns.py").exists()
    assert not (REPO_ROOT / "design-py/tests/test_marketing_campaigns.py").exists()
    for path in (
        REPO_ROOT / "README.md",
        REPO_ROOT / "docs/README.md",
        REPO_ROOT / "docs/ARCHITECTURE.md",
        REPO_ROOT / ".github/workflows/ci.yml",
    ):
        assert "marketing/" not in path.read_text(encoding="utf-8")
