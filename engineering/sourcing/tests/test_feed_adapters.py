"""Constructed schema fixtures are not live commodity, FX or price evidence."""
from io import BytesIO
import json
import hashlib
from zipfile import ZipFile
import pytest

from engineering.sourcing.model import record, validate_record
from engineering.sourcing.adapters import fetch, FetchError, parse_ecb_xml, parse_world_bank_xlsx


def source(kind):
    return record("source", publisher="Synthetic adapter test fixture",
        url="https://www.worldbank.org/test-only", retrieved_at="2026-10-29",
        access="constructed-test-fixture-not-live-data", source_kind=kind,
        document_sha256=None, licence="test-only")


def xlsx(*, missing=False, badunit=False, extra=None):
    stream = BytesIO()
    with ZipFile(stream, "w") as z:
        z.writestr("xl/workbook.xml", '''<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Hidden" state="hidden" r:id="rId1"/><sheet name="Monthly Prices" r:id="rId2"/></sheets></workbook>''')
        z.writestr("xl/_rels/workbook.xml.rels", '''<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Target="worksheets/sheet1.xml"/><Relationship Id="rId2" Target="worksheets/sheet2.xml"/></Relationships>''')
        z.writestr("xl/worksheets/sheet1.xml", "<wrong/>")
        def cell(ref, text):
            return '<c r="'+ref+'" t="inlineStr"><is><t>'+text+'</t></is></c>'
        rows = '<row r="5">'+cell("B5", "Aluminum")+cell("C5", "Copper")+'</row>'
        rows += '<row r="6">'+cell("B6", "($/unknown)" if badunit else "($/mt)")+cell("C6", "($/mt)")+'</row>'
        rows += '<row r="7">'+cell("A7", "2026M08")+cell("B7", "1000")+cell("C7", "5000")+'</row>'
        rows += '<row r="8">'+cell("A8", "2026M09")+cell("B8", "…" if missing else "1200")+cell("C8", "6000")+'</row>'
        z.writestr("xl/worksheets/sheet2.xml", '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'+rows+'</sheetData></worksheet>')
        if extra:z.writestr(*extra)
    return stream.getvalue()


def ecb(rates='<Cube currency="USD" rate="1.1"/><Cube currency="GBP" rate="0.8"/>', when="2026-10-28"):
    return ('<Envelope xmlns="http://www.ecb.int/vocabulary/2002-08-01/eurofxref"><Cube><Cube time="'+when+'">'+rates+'</Cube></Cube></Envelope>').encode()


def test_world_bank_named_sheet_and_units_are_preserved():
    result = parse_world_bank_xlsx(xlsx(), source("commodity_benchmark"))
    assert len(result) == 2
    assert [r["unit_price"] for r in result] == ["1200", "6000"]
    assert all(r["quantity_unit"] == "t" and not r["is_manufactured_product_price"] for r in result)
    assert all(validate_record(r) for r in result)


def test_missing_latest_price_is_not_zero():
    result = parse_world_bank_xlsx(xlsx(missing=True), source("commodity_benchmark"))
    assert result[0]["unit_price"] == "1000" and result[0]["observation_period"] == "2026-08"


@pytest.mark.parametrize("raw", [b"not-an-xlsx", xlsx(badunit=True), xlsx(extra=("../escape", "x"))])
def test_unsafe_or_ambiguous_workbooks_rejected(raw):
    with pytest.raises(ValueError):parse_world_bank_xlsx(raw, source("commodity_benchmark"))


def test_ecb_base_date_and_no_identity_fx():
    result = parse_ecb_xml(ecb(), source("exchange_rate"))
    assert {r["quote_currency"] for r in result} == {"USD", "GBP"}
    assert all(r["base_currency"] == "EUR" and r["rate_date"] == "2026-10-28" for r in result)


@pytest.mark.parametrize("raw", [ecb(when="2026-11-01"), ecb('<Cube currency="USD" rate="0"/>'), ecb('<Cube currency="USD" rate="1"/><Cube currency="USD" rate="2"/>'), b'<!DOCTYPE x [<!ENTITY x "bad">]><x/>'])
def test_fx_future_duplicate_zero_or_entity_rejected(raw):
    with pytest.raises(ValueError):parse_ecb_xml(raw, source("exchange_rate"))


def test_missing_currency_is_not_invented():
    with pytest.raises(ValueError, match="absent"):parse_ecb_xml(ecb(), source("exchange_rate"), currencies=["IQD"])


def transport(method, url, **kwargs):
    return 200, {"Content-Type":"text/plain", "Set-Cookie":"private-cookie", "Authorization":"secret"}, b"public"


def test_public_fetch_filters_metadata_and_hashes_actual_bytes():
    result = fetch("https://www.worldbank.org/data", transport=transport)
    assert result["raw"] == b"public" and set(result["headers"]) == {"content-type"}
    assert "secret" not in json.dumps({k:v for k,v in result.items() if k != "raw"})


@pytest.mark.parametrize("url", ["http://www.worldbank.org/a", "https://user:secret@www.worldbank.org/a", "https://evil.example/a", "https://www.worldbank.org/a?access_token=secret", "https://127.0.0.1/a"])
def test_public_fetch_rejects_nonpublic_or_secret_urls(url):
    with pytest.raises(FetchError):fetch(url, transport=transport)


def test_public_fetch_rejects_credentials_headers_and_oversized_bodies():
    with pytest.raises(FetchError):fetch("https://www.worldbank.org/a", headers={"Authorization":"Bearer secret"}, transport=transport)
    with pytest.raises(FetchError):fetch("https://www.worldbank.org/a", max_bytes=2, transport=transport)


def test_unvalidated_redirect_and_transport_error_do_not_expose_secrets():
    def redirect(*args, **kwargs):return 302, {"Location":"https://evil.example/steal"}, b""
    with pytest.raises(FetchError):fetch("https://www.worldbank.org/a", transport=redirect)
    def error(*args, **kwargs):raise RuntimeError("secret-token")
    with pytest.raises(FetchError) as caught:fetch("https://www.worldbank.org/a", transport=error)
    assert "secret-token" not in str(caught.value)


def test_feed_document_hash_binds_actual_source_bytes():
    body = {k:v for k,v in source('exchange_rate').items() if k not in ('record_id','schema','kind')}
    body['document_sha256'] = hashlib.sha256(ecb()).hexdigest()
    src = record('source',**body)
    assert len(parse_ecb_xml(ecb(),src)) == 2
    with pytest.raises(ValueError,match='hash differs'):parse_ecb_xml(ecb()+b' ',src)
