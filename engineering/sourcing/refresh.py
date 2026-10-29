"""Append dated public commodity/FX observations without contacting suppliers."""
from pathlib import Path
import os

from .adapters import fetch, parse_ecb_xml, parse_world_bank_xlsx
from .model import identity, record, validate_record


_FEEDS = (
    ("ecb-daily", "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml",
     "exchange_rate", "ECB daily reference rates", parse_ecb_xml, "daily.xml"),
    ("world-bank-monthly",
     "https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx",
     "commodity_benchmark", "World Bank monthly commodity benchmark", parse_world_bank_xlsx, "monthly.xlsx"),
)


def _cache(cache_dir, sha256, suffix, raw):
    if cache_dir is None:
        return None
    folder = Path(cache_dir)
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    if folder.is_symlink():
        raise ValueError("Private regular cache directory required")
    target = folder / (sha256 + suffix)
    if target.exists():
        if target.is_symlink() or not target.is_file() or target.stat().st_size != len(raw):
            raise ValueError("Existing source-cache entry differs")
        import hashlib
        if hashlib.sha256(target.read_bytes()).hexdigest() != sha256:
            raise ValueError("Existing source-cache bytes differ")
    else:
        descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(raw)
    return target.name


def refresh_public_feeds(store, *, cache_dir=None, transport=None):
    """Fetch only the fixed official public feeds and append immutable records.

    Raw bytes are optional and cached by content hash outside the checkout by
    the CLI. Repeated identical documents reuse their existing source snapshot.
    A network/parser failure is a held result with a sanitized reason.
    """
    existing = store.all("source")
    output = []
    for key, url, source_kind, title, parser, suffix in _FEEDS:
        try:
            downloaded = fetch(url, transport=transport)
            raw = downloaded["raw"]
            cached = _cache(cache_dir, downloaded["sha256"], suffix, raw)
            prior = [value for value in existing
                     if value.get("source_key") == key and
                     value.get("document_sha256") == downloaded["sha256"]]
            if prior:
                source = sorted(prior, key=lambda item: (item["retrieved_at"], item["record_id"]))[-1]
                state = "unchanged"
            else:
                source = record("source", source_key=key, publisher=title, url=downloaded["url"],
                    retrieved_at=downloaded["retrieved_at"], access="public dated feed; raw response SHA-256 retained",
                    source_kind=source_kind, document_sha256=downloaded["sha256"])
                store.put(source)
                existing.append(source)
                state = "updated"
            if key == "world-bank-monthly":
                observations = parser(raw, source, series=("Aluminum", "Copper"), latest_only=True)
            else:
                observations = parser(raw, source)
            added = store.insert_many(observations)
            output.append(dict(source_key=key, status=state, source_id=source["record_id"],
                source_sha256=downloaded["sha256"], retrieved_at=downloaded["retrieved_at"],
                observation_ids=added, observation_count=len(added),
                cache_file=cached, **{"supplier_contacts_sent": 0}))
        except Exception as error:
            # Adapter/transport exceptions are deliberately sanitized. Do not
            # return a URL, response body, token, or arbitrary exception text.
            code = getattr(error, "code", None)
            output.append(dict(source_key=key, status="held",
                reason=code if isinstance(code, str) else type(error).__name__,
                observation_count=0, supplier_contacts_sent=0))
    result = dict(refresh_schema="osr-sourcing-public-feed-refresh/1", feeds=output,
                  supplier_contacts_sent=0, supplier_quotes_updated=0,
                  price_observations_are_current_snapshot_only=True,
                  physical_qualification=None, complete_cost=None)
    return record("run", purpose="official-public-feed-refresh", **result)
