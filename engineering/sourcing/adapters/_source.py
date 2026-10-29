"""Bind parsed bytes to a declared document hash when one was supplied."""
import hashlib
from ..model import validate_record


def checked_source(source, expected_kind, raw):
    validate_record(source, "source")
    if source["source_kind"] != expected_kind:
        raise ValueError("Wrong source category for adapter")
    expected = source.get("document_sha256")
    if expected is not None:
        if isinstance(raw, str):
            raw = raw.encode("utf-8")
        if not isinstance(raw, bytes):
            raise ValueError("Original document bytes required for hash-bound source")
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError("Document source hash differs")
    return source["record_id"]
