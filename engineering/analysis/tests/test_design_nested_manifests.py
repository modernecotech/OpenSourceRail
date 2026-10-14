"""Native producer manifests remain ordinary hashed attempt artifacts."""

import os

import pytest

from engineering.analysis.tests.test_design_engine import minimal_request
from engineering.design_engine.contracts import fingerprint
from engineering.design_engine.publication import digest
from engineering.design_engine.store import Store, write_new


@pytest.mark.parametrize("mutation", [None, "corrupt", "extra", "missing"])
def test_sealed_nested_native_manifest_is_verified_and_membership_is_exact(
    tmp_path, mutation
):
    store = Store(tmp_path)
    job = store.create(minimal_request())
    folder = store.begin(job["id"], os.getpid())
    nested = folder / "candidate/native-campaign/manifest.json"
    write_new(nested, dict(schema="native-fixture/1", inputs_sha256="a" * 64))
    write_new(
        folder / "candidate/native-campaign/case/result.json",
        dict(state="failed", physical_release=False),
    )
    manifest = dict(
        schema="osr-design-attempt/1",
        request_sha256=fingerprint(job["request"]),
        artifacts={
            p.relative_to(folder).as_posix(): digest(p)
            for p in folder.rglob("*")
            if p.is_file()
        },
        physical_release=False,
    )
    write_new(folder / "manifest.json", manifest)
    store.finish(job["id"], "failed", "Retained diagnostic fixture", manifest)
    assert Store(tmp_path).verify_attempt(job["id"], 1) == manifest
    if mutation is None:
        return
    if mutation == "corrupt":
        nested.write_text("changed native producer bytes")
    elif mutation == "extra":
        write_new(folder / "unlisted/manifest.json", dict(undeclared=True))
    else:
        nested.unlink()
    with pytest.raises((ValueError, FileNotFoundError)):
        Store(tmp_path).verify_attempt(job["id"], 1)
