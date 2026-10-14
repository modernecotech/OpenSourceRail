"""Controlled, hashed local downloads; sealed packages remain independently verifiable."""

from pathlib import Path
import shutil
import zipfile

from .publication import digest
from .export import verify_export

CHUNK_BYTES = 45 * 1024**2


def bundle(folder, output):
    folder, output = Path(folder).resolve(), Path(output).resolve()
    manifest = verify_export(folder)
    if output.exists():
        raise ValueError("download bundles are immutable")
    output.mkdir(parents=True)
    archive = output / "review.zip"
    with zipfile.ZipFile(archive, "x", compression=zipfile.ZIP_DEFLATED) as package:
        for name in sorted([*manifest["files"], "manifest.json"]):
            package.write(folder / name, name)
    # A writer cannot change a source while we are constructing its package.
    verify_export(folder)
    archive_sha256 = digest(archive)
    chunks = []
    with archive.open("rb") as stream:
        while data := stream.read(CHUNK_BYTES):
            part = output / f"review.zip.part-{len(chunks) + 1:04d}"
            part.write_bytes(data)
            chunks.append(dict(name=part.name, bytes=len(data), sha256=digest(part)))
    archive.unlink()
    return dict(
        schema="osr-review-download/1",
        archive_sha256=archive_sha256,
        chunks=chunks,
        restore="Concatenate chunks in numbered order, verify archive SHA256, then unzip and verify manifest.json.",
        physical_release=False,
    )


def controlled_file(root, name):
    root = Path(root).resolve()
    if (
        not isinstance(name, str)
        or not name
        or Path(name).is_absolute()
        or ".." in Path(name).parts
    ):
        raise ValueError("controlled relative artifact required")
    path = root / name
    if any(
        p.is_symlink()
        for p in [path, *path.parents]
        if p != root and p.is_relative_to(root)
    ):
        raise ValueError("artifact symlinks are forbidden")
    if not path.resolve().is_relative_to(root) or not path.is_file():
        raise ValueError("artifact is unavailable")
    return path


def send_file(handler, path):
    handler.send_response(200)
    handler.send_header("Content-Type", "application/octet-stream")
    handler.send_header("Content-Length", str(path.stat().st_size))
    handler.send_header(
        "Content-Disposition",
        'attachment; filename="' + path.name.replace('"', "") + '"',
    )
    handler.send_header("Cache-Control", "private, no-store")
    handler.send_header("X-Content-Type-Options", "nosniff")
    handler.send_header("X-OSR-SHA256", digest(path))
    handler.end_headers()
    with path.open("rb") as stream:
        shutil.copyfileobj(stream, handler.wfile, length=1024**2)
