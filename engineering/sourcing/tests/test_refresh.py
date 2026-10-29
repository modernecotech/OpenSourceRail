import stat

from engineering.sourcing.catalogue import seed
from engineering.sourcing.database import Store
from engineering.sourcing.refresh import refresh_public_feeds
from engineering.sourcing.tests.test_feed_adapters import xlsx, ecb


def test_public_feed_refresh_appends_or_reuses_hash_bound_snapshots(tmp_path):
    bodies = {
        "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml": ecb(),
        "https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx": xlsx(),
    }

    def transport(method, url, **kwargs):
        assert method == "GET"
        return 200, {"Content-Type": "application/octet-stream"}, bodies[url]

    with Store(tmp_path / "sourcing.sqlite") as store:
        seed(store)
        initial = len(store.all())
        cache = tmp_path / "outside-checkout-feed-cache"
        first = refresh_public_feeds(store, cache_dir=cache, transport=transport)
        assert [item["status"] for item in first["feeds"]] == ["updated", "updated"]
        assert all(item["observation_count"] > 0 for item in first["feeds"])
        after_first = len(store.all())
        assert after_first > initial
        files = list(cache.iterdir())
        assert len(files) == 2
        assert all(stat.S_IMODE(path.stat().st_mode) == 0o600 for path in files)
        second = refresh_public_feeds(store, cache_dir=cache, transport=transport)
        assert [item["status"] for item in second["feeds"]] == ["unchanged", "unchanged"]
        assert len(store.all()) == after_first


def test_public_feed_refresh_reports_sanitized_access_hold(tmp_path):
    with Store(tmp_path / "sourcing.sqlite") as store:
        result = refresh_public_feeds(store, transport=lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("secret body")))
        assert all(feed["status"] == "held" for feed in result["feeds"])
        assert all("secret" not in str(feed) for feed in result["feeds"])
