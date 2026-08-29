from __future__ import annotations

import csv
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MARKETING = ROOT / "marketing"


def test_marketing_campaigns_are_current_and_complete() -> None:
    completed = subprocess.run(
        ["python3", "scripts/generate-marketing-campaigns.py", "--check"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr

    manifest = json.loads((MARKETING / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["sender"] == "hayder@modernecotech.com"
    assert manifest["country_campaign_count"] == 44
    assert manifest["city_campaign_count"] == 266
    assert manifest["international_campaign_count"] >= 50
    assert manifest["recipient_role_count"] >= 1_290


def test_city_email_uses_current_evidence_and_images() -> None:
    campaign = MARKETING / "campaigns/west-asia/Iraq/Samawah"
    readme = (campaign / "README.md").read_text(encoding="utf-8")
    email = (campaign / "email.txt").read_text(encoding="utf-8")

    assert "3 / 50.4 km" in readme
    assert "$415 M" in readme
    assert "10.7 MW / 49.5 MWh" in readme
    assert "samawah-network-map.png" in readme
    assert "samawah-simulation-dashboard.png" in readme
    assert email.startswith("From: hayder@modernecotech.com\n")
    assert "not a tender price" in email
    assert "raw.githubusercontent.com/modernecotech/OpenSourceRail" in email


def test_contact_queue_distinguishes_research_from_verified_routes() -> None:
    with (MARKETING / "contact-research.csv").open(
        newline="", encoding="utf-8"
    ) as handle:
        rows = list(csv.DictReader(handle))

    city_rows = [row for row in rows if row["geography_type"] == "city"]
    country_rows = [row for row in rows if row["geography_type"] == "country"]
    international = [row for row in rows if row["geography_type"] == "international"]
    assert len(city_rows) == 266 * 4
    assert len(country_rows) == 44 * 4
    assert all(row["verification_status"] == "research_required" for row in city_rows)
    assert all(not row["email"] for row in city_rows + country_rows)
    assert all(row["source_url"].startswith("https://") for row in international)
    assert all(
        row["verification_status"] == "official_source_checked" for row in international
    )
    assert {row["recipient_id"] for row in international} >= {
        "ifc-sustainable-infrastructure",
        "global-environment-facility",
        "fia-foundation",
        "railway-gazette",
    }


def test_international_emails_are_tuned_to_the_audience() -> None:
    finance = (MARKETING / "campaigns/international/eib-global/email.txt").read_text(
        encoding="utf-8"
    )
    media = (MARKETING / "campaigns/international/railway-gazette/email.txt").read_text(
        encoding="utf-8"
    )
    charity = (
        MARKETING / "campaigns/international/fia-foundation/email.txt"
    ).read_text(encoding="utf-8")

    assert "project-preparation enquiry" in finance
    assert "Story pitch" in media
    assert "editorial pitch, not a request for endorsement" in media
    assert "programme-fit discussion" in charity
