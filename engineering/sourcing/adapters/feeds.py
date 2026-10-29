"""ECB reference FX and World Bank commodity observations, not supplier quotes."""
from datetime import date
from io import BytesIO
from pathlib import PurePosixPath
import re
import stat
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile

from ..model import decimal_text, record, validate_record
from ._source import checked_source

MAX_XML = 20 * 1024 * 1024
SHEET_NS = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def _xml(raw):
    if not isinstance(raw, bytes) or len(raw) > MAX_XML:
        raise ValueError("Bounded XML bytes required")
    if b"<!DOCTYPE" in raw.upper() or b"<!ENTITY" in raw.upper():
        raise ValueError("DTD/entity declarations are not source data")
    try:
        return ET.fromstring(raw)
    except ET.ParseError:
        raise ValueError("Malformed source XML") from None


def parse_ecb_xml(raw, source, *, currencies=None):
    sid = checked_source(source, "exchange_rate", raw)
    root = _xml(raw)
    ns = {"e": "http://www.ecb.int/vocabulary/2002-08-01/eurofxref"}
    days = root.findall("e:Cube/e:Cube", ns)
    if len(days) != 1 or "time" not in days[0].attrib:
        raise ValueError("Exactly one dated ECB daily observation required")
    day = days[0].attrib["time"]
    if date.fromisoformat(day) > date.fromisoformat(source["retrieved_at"][:10]):
        raise ValueError("Future FX observation is not a current reference rate")
    rates = {}
    for row in days[0]:
        currency = row.attrib.get("currency")
        if not currency or not re.fullmatch("[A-Z]{3}", currency) or currency in rates:
            raise ValueError("Distinct ISO ECB currency required")
        rates[currency] = decimal_text(row.attrib.get("rate"), "ECB rate", positive=True)
    if not rates:
        raise ValueError("Empty ECB rate file")
    wanted = set(rates) if currencies is None else set(currencies)
    if wanted - set(rates):
        raise ValueError("Requested currency absent from ECB reference observations")
    return [record("fx", source_id=sid, base_currency="EUR", quote_currency=key,
                   rate=rates[key], rate_date=day, rate_kind="reference",
                   executable_transaction_rate=False)
            for key in sorted(wanted) if key != "EUR"]


def _cells(root, shared):
    values = {}
    for number, cell in enumerate(root.findall("s:sheetData/s:row/s:c", SHEET_NS)):
        if number >= 200000:
            raise ValueError("Worksheet cell budget exceeded")
        address = cell.attrib.get("r", "")
        if not re.fullmatch("[A-Z]{1,4}[1-9][0-9]{0,6}", address) or address in values:
            raise ValueError("Unique bounded XLSX cell addresses required")
        value = cell.find("s:v", SHEET_NS)
        if cell.attrib.get("t") == "inlineStr":
            inline = cell.find("s:is", SHEET_NS)
            if inline is None:
                raise ValueError("Inline-string cell is incomplete")
            text = "".join(inline.itertext())
        elif value is None:
            text = ""
        elif cell.attrib.get("t") == "s":
            try:
                index = int(value.text)
                if index < 0:
                    raise ValueError
                text = shared[index]
            except (ValueError, IndexError):
                raise ValueError("Invalid shared-string cell") from None
        else:
            text = value.text or ""
        values[address] = text.strip()
    return values


def parse_world_bank_xlsx(raw, source, *, series=("Aluminum", "Copper"), latest_only=True):
    sid = checked_source(source, "commodity_benchmark", raw)
    if not isinstance(raw, bytes) or len(raw) > MAX_XML:
        raise ValueError("Bounded XLSX bytes required")
    try:
        archive = ZipFile(BytesIO(raw))
    except BadZipFile:
        raise ValueError("Actual XLSX archive required") from None
    with archive as z:
        members = z.infolist()
        if len(members) > 256 or sum(m.file_size for m in members) > 80 * 1024**2:
            raise ValueError("XLSX extraction budget exceeded")
        seen = set()
        for member in members:
            path = PurePosixPath(member.filename)
            if (member.filename in seen or path.is_absolute() or ".." in path.parts
                    or "\\" in member.filename or member.file_size > MAX_XML
                    or stat.S_ISLNK(member.external_attr >> 16) or member.flag_bits & 1):
                raise ValueError("Unsafe XLSX member")
            seen.add(member.filename)
        try:
            workbook = _xml(z.read("xl/workbook.xml"))
            relationships = _xml(z.read("xl/_rels/workbook.xml.rels"))
            sheet = [s for s in workbook.findall("s:sheets/s:sheet", SHEET_NS)
                     if s.attrib.get("name") == "Monthly Prices"]
            if len(sheet) != 1:
                raise ValueError("Named Monthly Prices worksheet required")
            rid = sheet[0].attrib.get("{" + REL_NS + "}id")
            relation = [r for r in relationships if r.attrib.get("Id") == rid]
            if len(relation) != 1 or relation[0].attrib.get("TargetMode") == "External":
                raise ValueError("Internal worksheet relationship required")
            target = relation[0].attrib["Target"]
            if target.startswith("/"):
                target = target[1:]
            else:
                target = "xl/" + target
            if ".." in PurePosixPath(target).parts or not target.startswith("xl/"):
                raise ValueError("Worksheet path escapes workbook")
            strings = []
            if "xl/sharedStrings.xml" in seen:
                strings = ["".join(s.itertext()) for s in _xml(z.read("xl/sharedStrings.xml")).findall("s:si", SHEET_NS)]
            cells = _cells(_xml(z.read(target)), strings)
        except KeyError:
            raise ValueError("Incomplete XLSX workbook") from None
    requested = tuple(series)
    if not requested or len(set(requested)) != len(requested):
        raise ValueError("Distinct requested commodity series required")
    headers = {}
    for name in requested:
        matches = [cell for cell, value in cells.items() if value == name]
        if len(matches) != 1:
            raise ValueError("Exact commodity header missing or ambiguous: " + name)
        match = re.fullmatch("([A-Z]+)([0-9]+)", matches[0])
        headers[name] = (match[1], int(match[2]))
    records = []
    missing = {"", "...", "..", "…", "n/a", "N/A"}
    for name, (column, header_row) in headers.items():
        unit = cells.get(column + str(header_row + 1), "").strip()
        units = {"($/mt)": "t", "($/kg)": "kg", "($/cubic meter)": "m3"}
        if unit not in units:
            raise ValueError("Unsupported commodity unit; no guessed conversion")
        observations = []
        for address, period in cells.items():
            if not address.startswith("A") or not re.fullmatch("[0-9]{4}M(?:0[1-9]|1[0-2])", period):
                continue
            row_number = re.sub("^[A-Z]+", "", address)
            if address != "A" + row_number or int(row_number) <= header_row + 1:
                continue
            value = cells.get(column + row_number, "")
            if value in missing:
                continue
            day = period[:4] + "-" + period[5:] + "-01"
            if date.fromisoformat(day) > date.fromisoformat(source["retrieved_at"][:10]):
                raise ValueError("Future commodity observation")
            observations.append(record("benchmark", source_id=sid,
                benchmark_key="world-bank:" + name + ":" + day[:7],
                observation_date=day, observation_period=day[:7], unit_price=value,
                currency="USD", quantity_unit=units[unit], series=name,
                workbook_sheet="Monthly Prices", source_cell=column + row_number,
                cost_scope="primary-commodity-benchmark",
                is_manufactured_product_price=False, delivered_cost_complete=False))
        if not observations:
            raise ValueError("No actual observations for commodity: " + name)
        observations.sort(key=lambda r: r["observation_date"])
        records.extend(observations[-1:] if latest_only else observations)
    return records
