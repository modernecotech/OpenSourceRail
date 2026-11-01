"""Canonical gzip wrapper for byte-exact research publication replay.

gzip.compress(mtime=0) delegated its OS header byte to zlib in Python 3.11/3.12.
GzipFile writes the specified, version-independent header. Explicit level nine
also avoids changes to the library's default compression level.
"""
import gzip
import io


def compress(payload):
    if not isinstance(payload,bytes):
        raise ValueError("Explicit encoded publication bytes required")
    stream=io.BytesIO()
    with gzip.GzipFile(filename="",mode="wb",compresslevel=9,mtime=0,fileobj=stream) as writer:
        writer.write(payload)
    return stream.getvalue()
