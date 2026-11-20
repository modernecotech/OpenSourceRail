from pathlib import Path
import runpy
import subprocess

import pytest


CHECKER = runpy.run_path(str(Path(__file__).resolve().parents[1] / "check-markdown-links.py"))


def git(repo, *args):
    return subprocess.check_output(["git", *args], cwd=repo, text=True).strip()


def test_historical_targets_use_pinned_trees_even_in_a_shallow_checkout(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    git(source, "init", "-q")
    git(source, "config", "uploadpack.allowFilter", "true")
    git(source, "config", "user.name", "Link test")
    git(source, "config", "user.email", "links@example.invalid")
    (source / "route.md").write_text("Archived route")
    git(source, "add", "route.md")
    git(source, "commit", "-qm", "Original route")
    old = git(source, "rev-parse", "HEAD")
    git(source, "mv", "route.md", "current.md")
    git(source, "commit", "-qm", "Current route")
    clone = tmp_path / "shallow"
    git(tmp_path, "clone", "--quiet", "--depth=1", source.as_uri(), str(clone))
    before = git(clone, "rev-parse", "HEAD")
    assert subprocess.run(["git", "cat-file", "-e", old], cwd=clone).returncode
    tree = CHECKER["epoch_trees"](clone, {old})[old]
    exists = CHECKER["historical_target_exists"]
    original = Path("guides/index.md")
    assert exists(original, "../route.md", tree)
    assert not exists(original, "../current.md", tree)
    assert not exists(original, "../../route.md", tree)
    assert git(clone, "rev-parse", "HEAD") == before
    assert git(clone, "status", "--porcelain") == ""


def test_invalid_revision_is_rejected_before_git(tmp_path):
    with pytest.raises(ValueError, match="Invalid archive revision"):
        CHECKER["epoch_trees"](tmp_path, {"HEAD"})
