"""Comprehensive ebook receipt checks without the held integrated dossier."""

import shutil
import re

import pytest

from engineering import platform_book


def test_reader_chapters_exclude_audit_identifiers():
    assert all(name == platform_book.SOURCE or name.startswith("docs/book/")
               for _, name in platform_book.CHAPTERS)
    for _, name in platform_book.CHAPTERS:
        chapter = (platform_book.ROOT / name).read_text()
        assert "Audit anchors:" not in chapter
        assert not re.search(r"\b[0-9a-f]{40,}\b", chapter)


def test_historical_renderer_has_separate_default_output():
    render = platform_book._renderer(platform_book.ROOT)
    assert render.DEFAULT_OUT != platform_book.ROOT / platform_book.BOOK


def test_platform_book_receipt_binds_sources_and_pdf(tmp_path):
    source_root = platform_book.ROOT
    assert len(platform_book.CHAPTERS) == 69
    assert len(platform_book.PARTS) == 12
    for name in (*platform_book._inputs(source_root), platform_book.BOOK, platform_book.RECEIPT):
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_root / name, target)

    assert platform_book.build(root=tmp_path, check=True)["cached"] is True

    book_source = tmp_path / platform_book.SOURCE
    original = book_source.read_bytes()
    book_source.write_bytes(original + b"\nchanged\n")
    with pytest.raises(ValueError, match="sources, PDF or receipt differ"):
        platform_book.build(root=tmp_path, check=True)

    book_source.write_bytes(original)
    illustration = tmp_path / "docs/images/v06/v06-cabin.webp"
    with illustration.open("ab") as stream:
        stream.write(b"changed")
    with pytest.raises(ValueError, match="sources, PDF or receipt differ"):
        platform_book.build(root=tmp_path, check=True)

    shutil.copyfile(source_root / "docs/images/v06/v06-cabin.webp", illustration)
    with (tmp_path / platform_book.BOOK).open("ab") as stream:
        stream.write(b"\nchanged\n")
    with pytest.raises(ValueError, match="sources, PDF or receipt differ"):
        platform_book.build(root=tmp_path, check=True)
