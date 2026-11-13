"""Current reader receipt checks without the held integrated engineering dossier."""

import shutil

import pytest

from engineering import platform_book


def test_platform_book_receipt_binds_sources_and_pdf(tmp_path):
    source_root = platform_book.ROOT
    for name in (*platform_book.INPUTS, platform_book.BOOK, platform_book.RECEIPT):
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
    with (tmp_path / platform_book.BOOK).open("ab") as stream:
        stream.write(b"\nchanged\n")
    with pytest.raises(ValueError, match="sources, PDF or receipt differ"):
        platform_book.build(root=tmp_path, check=True)
