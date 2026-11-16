"""Resolve the current official release, then seal exact tool bytes for a run.

Network access belongs to explicit install/refresh actions. Numerical workers
consume the resolved source-bound manifest and never upgrade during a solve.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
import tarfile
import time
from urllib.request import Request, urlopen

API = "https://api.github.com/repos/{repository}"
SHA256 = re.compile(r"sha256:([0-9a-f]{64})\Z")
TAG = re.compile(r"v(\d+\.\d+\.\d+)\Z")
MAX_METADATA_BYTES = 2 * 1024 * 1024
MAX_ASSET_BYTES = 1024 * 1024 * 1024
MAX_UNPACKED_BYTES = 2 * 1024 * 1024 * 1024
MIN_FREE_BYTES = 1024 * 1024 * 1024


def _json(url: str, *, opener=urlopen) -> dict:
    request = Request(url, headers={"Accept": "application/vnd.github+json",
                                    "User-Agent": "OpenSourceRail-toolchain-resolver"})
    with opener(request, timeout=30) as response:
        raw = response.read(MAX_METADATA_BYTES + 1)
    if len(raw) > MAX_METADATA_BYTES:
        raise ValueError("Release metadata exceeds bounded response size")
    value = json.loads(raw)
    if type(value) is not dict:
        raise ValueError("Expected official release metadata object")
    return value


def latest_asset(repository: str, asset_name: str, *, opener=urlopen) -> dict:
    """Return a source/asset identity from GitHub's current stable release."""
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("Explicit GitHub owner/repository required")
    release = _json(API.format(repository=repository) + "/releases/latest", opener=opener)
    tag = release.get("tag_name")
    if release.get("draft") is not False or release.get("prerelease") is not False or not isinstance(tag, str) or not TAG.fullmatch(tag):
        raise ValueError("Latest release is not a stable semantic version")
    version = TAG.fullmatch(tag).group(1)
    expected_name = asset_name.format(version=version)
    assets = [item for item in release.get("assets", []) if item.get("name") == expected_name]
    if len(assets) != 1:
        raise ValueError("Latest release lacks exactly one requested Linux asset")
    asset = assets[0]
    digest = asset.get("digest")
    size = asset.get("size")
    url = asset.get("browser_download_url")
    expected_url = f"https://github.com/{repository}/releases/download/{tag}/{expected_name}"
    if (asset.get("state") != "uploaded" or not isinstance(digest, str)
            or not SHA256.fullmatch(digest) or type(size) is not int
            or not 0 < size <= MAX_ASSET_BYTES or url != expected_url):
        raise ValueError("Latest release asset lacks a bounded official digest")
    ref = _json(API.format(repository=repository) + "/git/ref/tags/" + tag, opener=opener)
    obj = ref.get("object", {})
    if obj.get("type") == "tag":
        annotated = _json(API.format(repository=repository) + "/git/tags/" + str(obj.get("sha")), opener=opener)
        obj = annotated.get("object", {})
    commit = obj.get("sha")
    if obj.get("type") != "commit" or not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("Latest release tag lacks an exact commit")
    return dict(repository=repository, version=tag, commit=commit,
                release_immutable=release.get("immutable") is True,
                release_published_at=release.get("published_at"),
                asset=expected_name, asset_id=asset.get("id"), url=url,
                bytes=size, asset_sha256=SHA256.fullmatch(digest).group(1))


def file_sha256(path: Path) -> str:
    value = sha256()
    with Path(path).open("rb") as stream:
        while block := stream.read(1024 * 1024):
            value.update(block)
    return value.hexdigest()


def download_asset(asset: dict, archive: Path, *, opener=urlopen, maximum_wall_s=600) -> Path:
    """Resume verified ranges; publish only complete size/hash-verified bytes."""
    archive = Path(archive)
    archive.parent.mkdir(parents=True, exist_ok=True)
    expected_size = asset["bytes"]
    expected_hash = asset["asset_sha256"]
    if type(expected_size) is not int or not 0 < expected_size <= MAX_ASSET_BYTES:
        raise ValueError("Bounded tool asset size required")
    if archive.exists():
        if archive.stat().st_size != expected_size or file_sha256(archive) != expected_hash:
            raise ValueError("Existing tool archive differs from official release")
        return archive
    partial = archive.with_name(archive.name + ".partial")
    received = partial.stat().st_size if partial.exists() else 0
    if received >= expected_size:
        if received == expected_size and file_sha256(partial) == expected_hash:
            partial.rename(archive)
            return archive
        raise ValueError("Interrupted tool bytes differ from official release; partial retained")
    if shutil.disk_usage(archive.parent).free < expected_size - received + MIN_FREE_BYTES:
        raise ValueError("Insufficient disk reserve for latest tool archive")
    started = time.monotonic()
    headers = {"User-Agent": "OpenSourceRail-toolchain-resolver"}
    if received:
        headers["Range"] = f"bytes={received}-"
    request = Request(asset["url"], headers=headers)
    with opener(request, timeout=60) as response:
        status = getattr(response, "status", None)
        if received:
            content_range = response.headers.get("Content-Range", "")
            match = re.fullmatch(r"bytes (\d+)-(\d+)/(\d+)", content_range)
            if (status != 206 or match is None
                    or int(match.group(1)) != received
                    or int(match.group(2)) != expected_size - 1
                    or int(match.group(3)) != expected_size):
                raise ValueError("Latest tool server refused exact HTTP range; partial retained")
        elif status not in (200, None):
            raise ValueError("Latest tool server returned unexpected status")
        with partial.open("ab" if received else "xb") as output:
            while block := response.read(1024 * 1024):
                received += len(block)
                if received > expected_size or time.monotonic() - started > maximum_wall_s:
                    raise ValueError("Latest tool download exceeded byte or wall budget; partial retained")
                output.write(block)
    if received != expected_size or file_sha256(partial) != expected_hash:
        raise ValueError("Latest tool archive size/checksum differs; partial retained")
    partial.rename(archive)
    return archive


def tar_member_sha256(archive: Path, name: str) -> str:
    """Hash one ordinary member without buffering a compressed tool archive."""
    expected = Path(name)
    if expected.is_absolute() or ".." in expected.parts:
        raise ValueError("Ordinary archive member required")
    found = None
    total = 0
    with tarfile.open(archive, mode="r|gz") as stream:
        for member in stream:
            total += member.size
            if total > MAX_UNPACKED_BYTES or not (member.isfile() or member.isdir()):
                raise ValueError("Tool archive exceeds ordinary-file budget")
            if Path(member.name).is_absolute() or ".." in Path(member.name).parts:
                raise ValueError("Unsafe tool archive path")
            if member.name != name:
                continue
            if found is not None or not member.isfile():
                raise ValueError("Expected one ordinary executable member")
            source = stream.extractfile(member)
            value = sha256()
            while block := source.read(1024 * 1024):
                value.update(block)
            found = value.hexdigest()
    if found is None:
        raise ValueError("Tool archive lacks expected executable: " + name)
    return found
