"""Stable content provenance and portable gzip for generated engineering packages."""
from __future__ import annotations
import gzip
import hashlib
import io


def input_revision(sources_sha256: dict[str,str]) -> str:
    """Identify inputs independently of the commit that later contains outputs."""
    digest=hashlib.sha256()
    for path,sha in sorted(sources_sha256.items()):
        digest.update(path.encode('utf-8'));digest.update(b'\0')
        digest.update(sha.encode('ascii'));digest.update(b'\0')
    return digest.hexdigest()


def deterministic_gzip(raw: bytes) -> bytes:
    """GzipFile fixes mtime, filename and OS header across Python runtimes."""
    buffer=io.BytesIO()
    with gzip.GzipFile(fileobj=buffer,mode='wb',filename='',mtime=0,compresslevel=9) as handle:
        handle.write(raw)
    return buffer.getvalue()
