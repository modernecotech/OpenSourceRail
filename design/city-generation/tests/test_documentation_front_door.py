"""Keep public entry points concise and tied to canonical evidence."""

from __future__ import annotations

import runpy
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_root_readme_is_a_concise_developing_world_front_door() -> None:
    text = (REPO_ROOT / "README.md").read_text(encoding="utf-8")
    assert len(text.splitlines()) <= 220
    assert "265 cities in 43 developing countries" in text
    assert "one european comparison model" in text.lower()
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
        "cities/workspaces/README.md",
        "design/component-catalogue/src/osr_mech/",
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


def test_frontend_ci_provisions_the_complete_ifc_runtime() -> None:
    workflow = (REPO_ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    requirement_lines = (
        REPO_ROOT / "engineering/toolchain/python-requirements.txt"
    ).read_text(encoding="utf-8").splitlines()
    pins = {
        name: next(line for line in requirement_lines if line.startswith(f"{name}=="))
        for name in ("networkx", "pytest")
    }

    assert all(pin in workflow for pin in pins.values())
    assert "import _pytest, bcf, ifcopenshell, ifctester, networkx" in workflow


def test_thin_wrapper_directories_do_not_return() -> None:
    for relative in (
        "docs/brochures",
        "docs/city-studio",
        "docs/hardware",
        "docs/releases",
        "engineering/energy",
        "engineering/gis",
        "engineering/software",
        "control-electronics/trainset-interiors",
    ):
        assert not (REPO_ROOT / relative).exists()
    assert list((REPO_ROOT / "control-electronics").glob("*/bom/.gitkeep")) == []
    assert list((REPO_ROOT / "control-electronics").glob("*/gerbers/.gitkeep")) == []


def test_public_overview_is_generated_from_current_metrics() -> None:
    generator = runpy.run_path(
        str(REPO_ROOT / "tools/automation/generate-public-overview.py")
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
    assert not (REPO_ROOT / "cities/catalogue/europe/France/NATIONAL-BRIEF.md").exists()
    lyon = (REPO_ROOT / "cities/catalogue/europe/France/Lyon/README.md").read_text()
    assert "Technical comparison only" in lyon
    assert "National brief" not in lyon
    assert "Foreign-capital advantage" not in lyon
    assert not (
        REPO_ROOT / "docs/outreach/open-source-rail-outreach-contacts.md"
    ).exists()


def test_private_campaign_material_is_not_in_the_public_tree() -> None:
    assert not (REPO_ROOT / "marketing").exists()
    assert not (REPO_ROOT / "tools/automation/generate-marketing-campaigns.py").exists()
    assert not (REPO_ROOT / "design/city-generation/tests/test_marketing_campaigns.py").exists()
    for path in (
        REPO_ROOT / "README.md",
        REPO_ROOT / "docs/README.md",
        REPO_ROOT / "docs/ARCHITECTURE.md",
        REPO_ROOT / ".github/workflows/ci.yml",
    ):
        assert "marketing/" not in path.read_text(encoding="utf-8")


def test_complete_book_manifest_covers_reader_documentation() -> None:
    builder = runpy.run_path(str(REPO_ROOT / "tools/automation/build-doc-book.py"))
    sources = builder["_doc_sources"]()
    relative = [source.path.relative_to(REPO_ROOT).as_posix() for source in sources]
    included = set(relative)

    assert len(relative) == len(included)
    assert {
        "README.md",
        "CONTRIBUTING.md",
        "GOVERNANCE.md",
        "CHANGELOG.md",
        "LICENSE.md",
        "LICENSES/README.md",
        "docs/ARCHITECTURE.md",
        "docs/cost-model.md",
        "crates/osr-city-studio/README.md",
        "deployment/README.md",
        "engineering/toolchain/README.md",
        "engineering/assurance/formal/tla/README.md",
        "control-electronics/README.md",
        "design/README.md",
        "design/city-generation/README.md",
        "design/component-catalogue/README.md",
        "design/component-catalogue/catalog/buildable-trainset/current-design-buildability-review.md",
        "design/component-catalogue/catalog/buildable-trainset/small-component-standard.md",
        "cities/workspaces/README.md",
        "engineering/README.md",
        "tools/README.md",
        "tools/automation/README.md",
        "tools/reference-ma/README.md",
    }.issubset(included)

    for root in (
        "docs",
        "crates",
        "deployment",
        "engineering",
        "control-electronics",
        "lib",
        "cities/workspaces",
        "design/city-generation",
        "tools",
    ):
        for path in (REPO_ROOT / root).rglob("*.md"):
            rel = path.relative_to(REPO_ROOT).as_posix()
            if rel not in {"docs/README.md", "docs/INDEX.md"} and ".pytest_cache" not in rel:
                assert rel in included

    country_briefs = [path for path in relative if path.endswith("/NATIONAL-BRIEF.md")]
    assert len(country_briefs) == 43
    assert not any(path.startswith("cities/catalogue/europe/") for path in country_briefs)
    assert "docs/README.md" not in included
    assert "docs/INDEX.md" not in included
    assert "cities/catalogue/README.md" not in included
    assert not any("/definitions/" in path or "/travelers/" in path for path in relative)


def test_complete_book_manifest_covers_every_public_city_model() -> None:
    builder = runpy.run_path(str(REPO_ROOT / "tools/automation/build-doc-book.py"))
    models = builder["_city_models"]()
    model_paths = {model.path.relative_to(REPO_ROOT).as_posix() for model in models}
    expected = {
        path.parent.relative_to(REPO_ROOT).as_posix()
        for path in (REPO_ROOT / "cities/catalogue").glob("*/*/*/design.toml")
        if path.relative_to(REPO_ROOT / "cities/catalogue").parts[0] != "europe"
    }
    assert model_paths == expected
    assert len(models) == len(expected) == 265


def test_book_renderer_preserves_titles_callouts_images_and_html() -> None:
    builder = runpy.run_path(str(REPO_ROOT / "tools/automation/build-doc-book.py"))
    builder["_register_fonts"]()
    styles = builder["_styles"]()

    def descendants(value):
        if isinstance(value, (list, tuple)):
            for child in value:
                yield from descendants(child)
            return
        yield value
        if hasattr(value, "_cellvalues"):
            yield from descendants(value._cellvalues)

    root_flows = builder["_render_markdown"](
        REPO_ROOT / "README.md",
        styles,
        page_width=500,
        page_height=750,
        max_image_px=500,
        image_quality=60,
        include_images=True,
    )
    rendered = list(descendants(root_flows))
    texts = [flow.getPlainText() for flow in rendered if hasattr(flow, "getPlainText")]
    assert "OpenSourceRail" not in texts
    assert any("Repository outputs are planning" in text for text in texts)
    assert sum(type(flow).__name__ == "Image" for flow in rendered) >= 7

    city_studio_flows = builder["_render_markdown"](
        REPO_ROOT / "docs/city-studio.md",
        styles,
        page_width=500,
        page_height=750,
        max_image_px=500,
        image_quality=60,
        include_images=False,
    )
    city_studio_text = " ".join(
        flow.getPlainText()
        for flow in descendants(city_studio_flows)
        if hasattr(flow, "getPlainText")
    )
    assert "<hash>" in city_studio_text
