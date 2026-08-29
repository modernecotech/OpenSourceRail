#!/usr/bin/env python3
"""Generate deterministic OpenSourceRail country, city and partner campaigns."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import tempfile
import tomllib
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
DESIGNS = ROOT / "designs"
MARKETING = ROOT / "marketing"
CAMPAIGNS = MARKETING / "campaigns"
TARGETS_PATH = MARKETING / "international-targets.toml"
CONTACT_OVERRIDES_PATH = MARKETING / "contact-overrides.toml"
SENDER = "hayder@modernecotech.com"
GITHUB_BLOB = "https://github.com/modernecotech/OpenSourceRail/blob/main/"
GITHUB_RAW = "https://raw.githubusercontent.com/modernecotech/OpenSourceRail/main/"
UK_DIPLOMATIC_LIST = (
    "https://www.gov.uk/government/publications/foreign-embassies-in-the-uk"
)
MEDIA_CATEGORIES = {
    "city-leadership-media",
    "rail-industry-media",
    "sustainable-mobility-media",
    "urban-policy-media",
}
FINANCE_CATEGORIES = {
    "bilateral-development-finance",
    "climate-fund",
    "climate-project-facility",
    "development-finance",
    "impact-innovation-fund",
    "infrastructure-development-finance",
    "local-currency-guarantee",
    "multilateral-climate-fund",
    "multilateral-development-bank",
    "multilateral-environment-fund",
    "political-risk-guarantee",
    "project-development-finance",
    "project-preparation-facility",
    "regional-development-bank",
}
DESIGN_REGIONS = {
    "central-africa",
    "east-africa",
    "europe",
    "latin-america",
    "north-africa",
    "south-africa",
    "south-asia",
    "southeast-asia",
    "west-africa",
    "west-asia",
}


@dataclass(frozen=True)
class City:
    region: str
    country: str
    country_iso: str
    name: str
    slug: str
    design_path: Path
    scenario_path: Path
    city_readme: Path
    national_brief: Path
    network_map: Path
    dashboard: Path
    finance_path: Path
    energy_path: Path
    population: int
    line_count: int
    station_count: int
    fleet_count: int
    route_km: float
    capex_usd: float
    external_capital_usd: float
    local_capital_usd: float
    annual_opex_usd: float
    external_saving_usd: float
    practical_daily_capacity: float
    pv_kw: float
    storage_kwh: float


@dataclass(frozen=True)
class InternationalTarget:
    id: str
    name: str
    category: str
    recipient_role: str
    recipient_name: str
    email: str
    contact_url: str
    source_url: str
    fit: str
    eligibility_note: str
    regions: tuple[str, ...]
    verified_on: str


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def repo_path(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def github_url(path: Path, *, raw: bool = False) -> str:
    prefix = GITHUB_RAW if raw else GITHUB_BLOB
    return prefix + quote(repo_path(path), safe="/._-")


def markdown_relative(source: Path, target: Path) -> str:
    relative = os.path.relpath(target, source.parent).replace(os.sep, "/")
    return quote(relative, safe="/._-")


def money(value: float) -> str:
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.2f} B"
    if value >= 1_000_000:
        return f"${value / 1_000_000:.0f} M"
    if value >= 1_000:
        return f"${value / 1_000:.0f} k"
    return f"${value:.0f}"


def power(value_kw: float) -> str:
    if value_kw >= 1_000:
        return f"{value_kw / 1_000:.1f} MW"
    return f"{value_kw:.0f} kW"


def energy(value_kwh: float) -> str:
    if value_kwh >= 1_000:
        return f"{value_kwh / 1_000:.1f} MWh"
    return f"{value_kwh:.0f} kWh"


def percentage(part: float, total: float) -> str:
    return f"{part / total:.0%}" if total > 0 else "n/a"


def count_label(value: int, singular: str, plural: str | None = None) -> str:
    return f"{value} {singular if value == 1 else plural or singular + 's'}"


def engagement_kind(target: InternationalTarget) -> str:
    if target.category in MEDIA_CATEGORIES:
        return "media"
    if target.category in FINANCE_CATEGORIES:
        return "finance"
    if "philanthropy" in target.category:
        return "philanthropy"
    return "partnership"


def engagement_label(target: InternationalTarget) -> str:
    return {
        "media": "Independent editorial pitch",
        "finance": "Eligibility and project-preparation enquiry",
        "philanthropy": "Programme-fit and catalytic-support enquiry",
        "partnership": "Technical partnership and peer-review enquiry",
    }[engagement_kind(target)]


def target_cities(target: InternationalTarget, cities: list[City]) -> list[City]:
    if "all" in target.regions:
        return cities
    selected = [city for city in cities if city.region in target.regions]
    if not selected:
        raise ValueError(f"{target.id}: declared regions contain no city designs")
    return selected


def campaign_examples(cities: list[City], limit: int = 2) -> list[City]:
    ordered = sorted(
        cities, key=lambda city: (-city.population, city.country, city.name)
    )
    selected = [ordered[0]]
    for city in ordered[1:]:
        if city.country != selected[0].country:
            selected.append(city)
            break
    for city in ordered[1:]:
        if city not in selected:
            selected.append(city)
        if len(selected) == limit:
            break
    return selected[:limit]


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def discover_cities() -> list[City]:
    cities: list[City] = []
    for design_path in sorted(DESIGNS.glob("*/*/*/design.toml")):
        region, country, name = design_path.parts[-4:-1]
        with design_path.open("rb") as handle:
            design = tomllib.load(handle)
        city_data = design["city"]
        slug = str(city_data["slug"])
        city_dir = design_path.parent
        finance_path = city_dir / "engineering/finance/summary.json"
        energy_path = city_dir / "engineering/energy/summary.json"
        required = [
            city_dir / f"{slug}.toml",
            city_dir / "README.md",
            city_dir.parent / "NATIONAL-BRIEF.md",
            city_dir / f"{slug}-network-map.png",
            city_dir / "engineering/screenshots" / f"{slug}-simulation-dashboard.png",
            finance_path,
            energy_path,
        ]
        missing = [repo_path(path) for path in required if not path.is_file()]
        if missing:
            raise ValueError(f"{name}: missing campaign sources: {', '.join(missing)}")
        finance = read_json(finance_path)
        energy_summary = read_json(energy_path)
        if not finance.get("passed") or not energy_summary.get("passed"):
            raise ValueError(f"{name}: finance or energy evidence is not passing")
        capex = finance["capex_usd"]
        comparator = finance["foreign_turnkey_comparator"]["default_comparison"]
        revenue = finance["revenue_basis"]
        cities.append(
            City(
                region=region,
                country=country,
                country_iso=str(city_data["country"]),
                name=name,
                slug=slug,
                design_path=design_path,
                scenario_path=city_dir / f"{slug}.toml",
                city_readme=city_dir / "README.md",
                national_brief=city_dir.parent / "NATIONAL-BRIEF.md",
                network_map=city_dir / f"{slug}-network-map.png",
                dashboard=city_dir
                / "engineering/screenshots"
                / f"{slug}-simulation-dashboard.png",
                finance_path=finance_path,
                energy_path=energy_path,
                population=int(city_data["population"]),
                line_count=len(design.get("lines", [])),
                station_count=len(design.get("stations", [])),
                fleet_count=sum(
                    int(fleet.get("trainset_count", 0))
                    for fleet in design.get("fleets", [])
                ),
                route_km=sum(
                    float(line.get("length_m", 0)) for line in design.get("lines", [])
                )
                / 1_000,
                capex_usd=float(capex["reconciled_project_total"]),
                external_capital_usd=float(capex["imported_external_capital"]),
                local_capital_usd=float(capex["local_capital"]),
                annual_opex_usd=float(finance["annual_opex_usd"]["total"]),
                external_saving_usd=float(
                    comparator["osr_external_capital_saving_usd"]
                ),
                practical_daily_capacity=float(
                    revenue["practical_capacity_passenger_trips_per_day"]
                ),
                pv_kw=float(energy_summary["pv_nameplate_kw"]),
                storage_kwh=float(energy_summary["storage_capacity_kwh"]),
            )
        )
    return cities


def load_targets() -> list[InternationalTarget]:
    with TARGETS_PATH.open("rb") as handle:
        document = tomllib.load(handle)
    verified_on = str(document["verified_on"])
    targets = [
        InternationalTarget(
            id=str(item["id"]),
            name=str(item["name"]),
            category=str(item["category"]),
            recipient_role=str(item["recipient_role"]),
            recipient_name=str(item.get("recipient_name", "")),
            email=str(item["email"]),
            contact_url=str(item["contact_url"]),
            source_url=str(item["source_url"]),
            fit=str(item["fit"]),
            eligibility_note=str(item["eligibility_note"]),
            regions=tuple(str(value) for value in item["regions"]),
            verified_on=verified_on,
        )
        for item in document.get("target", [])
    ]
    ids = [target.id for target in targets]
    if len(ids) != len(set(ids)):
        raise ValueError("international target IDs must be unique")
    for target in targets:
        if not target.contact_url.startswith("https://"):
            raise ValueError(f"{target.id}: contact_url must use HTTPS")
        if not target.source_url.startswith("https://"):
            raise ValueError(f"{target.id}: source_url must use HTTPS")
        if target.email and "@" not in target.email:
            raise ValueError(f"{target.id}: invalid public email")
        regions = set(target.regions)
        if "all" in regions and len(regions) != 1:
            raise ValueError(f"{target.id}: 'all' cannot be combined with regions")
        unknown_regions = regions - DESIGN_REGIONS - {"all"}
        if unknown_regions:
            raise ValueError(
                f"{target.id}: unknown regions: {', '.join(sorted(unknown_regions))}"
            )
    return targets


def load_contact_overrides() -> dict[tuple[str, str], dict[str, str]]:
    with CONTACT_OVERRIDES_PATH.open("rb") as handle:
        document = tomllib.load(handle)
    if document.get("schema_version") != 1:
        raise ValueError("marketing/contact-overrides.toml: unsupported schema")
    overrides: dict[tuple[str, str], dict[str, str]] = {}
    for item in document.get("contact", []):
        campaign_id = str(item["campaign_id"])
        recipient_id = str(item["recipient_id"])
        key = (campaign_id, recipient_id)
        if key in overrides:
            raise ValueError(
                f"duplicate contact override: {campaign_id}/{recipient_id}"
            )
        values = {name: str(value) for name, value in item.items()}
        for field in ("organization", "official_url", "verified_on", "source_url"):
            if not values.get(field):
                raise ValueError(f"{campaign_id}/{recipient_id}: {field} is required")
        if not values["official_url"].startswith("https://"):
            raise ValueError(
                f"{campaign_id}/{recipient_id}: official_url must use HTTPS"
            )
        if not values["source_url"].startswith("https://"):
            raise ValueError(f"{campaign_id}/{recipient_id}: source_url must use HTTPS")
        if values.get("email") and "@" not in values["email"]:
            raise ValueError(f"{campaign_id}/{recipient_id}: invalid public email")
        overrides[key] = values
    return overrides


def city_campaign_id(city: City) -> str:
    return f"city:{city.region}/{city.country}/{city.name}"


def country_campaign_id(region: str, country: str) -> str:
    return f"country:{region}/{country}"


def city_recipient_records(city: City) -> list[tuple[str, str]]:
    return [
        ("mayor-office", f"Office of the Mayor or city executive for {city.name}"),
        (
            "transport-planning",
            f"{city.name} municipal transport and urban-planning authority",
        ),
        (
            "sustainability-office",
            f"{city.name} climate, energy or sustainability office",
        ),
        (
            "municipal-finance",
            f"{city.name} municipal finance and investment unit",
        ),
    ]


def country_recipient_records(country: str) -> list[tuple[str, str]]:
    return [
        (
            "transport-ministry",
            f"{country} ministry responsible for transport and urban mobility",
        ),
        (
            "climate-energy-authority",
            f"{country} national climate, energy or Green Climate Fund authority",
        ),
        (
            "public-investment-authority",
            f"{country} public investment, planning or finance authority",
        ),
        (
            "uk-embassy-economic-section",
            f"Embassy or High Commission of {country} in the United Kingdom — economic section",
        ),
    ]


def city_recipient_roles(city: City) -> list[str]:
    return [role for _, role in city_recipient_records(city)]


def country_recipient_roles(country: str) -> list[str]:
    return [role for _, role in country_recipient_records(country)]


def city_email(city: City) -> str:
    roles = "; ".join(city_recipient_roles(city))
    local_share = percentage(city.local_capital_usd, city.capex_usd)
    return f"""From: {SENDER}
To: {roles}
Subject: Open, locally buildable renewable rail concept for {city.name}

Dear {city.name} leadership and transport-planning team,

I am writing from Modern EcoTech to share OpenSourceRail's open, reproducible urban-rail planning concept for {city.name}, {city.country}.

The current screening model covers {city.line_count} lines and {city.route_km:.1f} route-km, with {city.fleet_count:,} trainsets, {power(city.pv_kw)} of station/depot solar and {energy(city.storage_kwh)} of storage. Its planning CAPEX is {money(city.capex_usd)}, with {local_share} assigned to local capital and value creation under the current assumptions.

The design, cost model, GIS inputs and deterministic simulation evidence are open for technical review. These are early planning outputs—not a tender price, demand forecast, funding approval or construction-ready design—and we would like to test them with local data and institutional priorities.

Could you direct this to the appropriate urban-mobility, planning and climate-finance officials? We would welcome a 30-minute technical review to identify the correct local counterpart, data gaps and a credible feasibility-study pathway.

City brief: {github_url(city.city_readme)}
Network image: {github_url(city.network_map, raw=True)}
Simulation dashboard: {github_url(city.dashboard, raw=True)}

Images to attach from the repository:
- {repo_path(city.network_map)}
- {repo_path(city.dashboard)}

Kind regards,
Hayder
Modern EcoTech / OpenSourceRail
{SENDER}
"""


def city_readme(city: City, output: Path) -> str:
    roles = "\n".join(f"- {role}" for role in city_recipient_roles(city))
    email_path = output.parent / "email.txt"
    local_share = percentage(city.local_capital_usd, city.capex_usd)
    return f"""# {city.name} OpenSourceRail Campaign
<!-- Generated by scripts/generate-marketing-campaigns.py. -->

Municipality outreach package for **{city.name}, {city.country}**. Figures are
screening outputs for discussion, not a bid, endorsement or construction release.

## Audience

{roles}

## Local proposition

| Measure | Current planning result |
|---|---:|
| Population represented | {city.population:,} |
| Lines / route length | {city.line_count} / {city.route_km:.1f} km |
| Line-platform stops / fleet | {city.station_count} / {city.fleet_count:,} trainsets |
| Practical capacity ceiling | {city.practical_daily_capacity:,.0f} passenger-trips/day |
| Station/depot PV / storage | {power(city.pv_kw)} / {energy(city.storage_kwh)} |
| City programme CAPEX | {money(city.capex_usd)} |
| Local capital and value share | {money(city.local_capital_usd)} ({local_share}) |
| Illustrative external-capital saving | {money(city.external_saving_usd)} |
| Annual OPEX planning value | {money(city.annual_opex_usd)} |

Lead with locally buildable infrastructure, open design review, renewable-energy
integration and a staged feasibility process. Do not lead with the comparator;
it is an illustrative sensitivity, not a vendor quotation.

## Visuals and evidence

| Network concept | Deterministic simulation |
|---|---|
| ![{city.name} network map]({markdown_relative(output, city.network_map)}) | ![{city.name} simulation dashboard]({markdown_relative(output, city.dashboard)}) |

- [City design brief]({markdown_relative(output, city.city_readme)})
- [National programme]({markdown_relative(output, city.national_brief)})
- [Finance evidence]({markdown_relative(output, city.finance_path)})
- [Energy evidence]({markdown_relative(output, city.energy_path)})
- [Send-ready plain-text email]({markdown_relative(output, email_path)})

## Call to action

Ask for a 30-minute technical review, nomination of a municipal counterpart,
access to current mobility/land/utility data, and agreement on the scope of an
independent feasibility study. Verify the recipient in
[`contact-research.csv`]({markdown_relative(output, MARKETING / 'contact-research.csv')})
before sending.
"""


def aggregate(cities: list[City]) -> dict[str, float]:
    return {
        "population": sum(city.population for city in cities),
        "lines": sum(city.line_count for city in cities),
        "route_km": sum(city.route_km for city in cities),
        "fleet": sum(city.fleet_count for city in cities),
        "capex": sum(city.capex_usd for city in cities),
        "external": sum(city.external_capital_usd for city in cities),
        "local": sum(city.local_capital_usd for city in cities),
        "external_saving": sum(city.external_saving_usd for city in cities),
        "pv_kw": sum(city.pv_kw for city in cities),
        "storage_kwh": sum(city.storage_kwh for city in cities),
    }


def country_email(country: str, cities: list[City]) -> str:
    values = aggregate(cities)
    roles = "; ".join(country_recipient_roles(country))
    examples = sorted(cities, key=lambda city: (-city.population, city.name))[:3]
    example_names = ", ".join(city.name for city in examples)
    links = "\n".join(
        f"- {city.name}: {github_url(city.city_readme)}" for city in examples
    )
    images = "\n".join(f"- {repo_path(city.network_map)}" for city in examples[:2])
    return f"""From: {SENDER}
To: {roles}
Subject: OpenSourceRail — an open national pathway for locally built renewable urban rail in {country}

Dear transport, planning and climate-finance colleagues,

Modern EcoTech's OpenSourceRail project has prepared open, reproducible urban-rail screening concepts for {len(cities)} cities in {country}, representing {int(values['population']):,} people and {values['route_km']:,.0f} route-km.

Across the catalogue, the current city-level models indicate {money(values['capex'])} of planning CAPEX, {percentage(values['local'], values['capex'])} local capital/value allocation, {power(values['pv_kw'])} of station/depot solar and {energy(values['storage_kwh'])} of storage. A shared national manufacturing strategy and city-by-city evidence are set out in the national brief.

These are transparent screening models—not bids, sovereign commitments, demand forecasts or funding approvals. We are seeking a government counterpart to review assumptions, select a pilot city and define an independently governed feasibility programme.

Could your office route this to the appropriate urban-mobility, industrial-policy and climate-finance teams, and advise whether a technical introductory meeting would be useful?

Representative city concepts: {example_names}
{links}
National catalogue: {github_url(cities[0].national_brief)}

Images to attach from the repository:
{images}

Kind regards,
Hayder
Modern EcoTech / OpenSourceRail
{SENDER}
"""


def country_readme(country: str, cities: list[City], output: Path) -> str:
    values = aggregate(cities)
    roles = "\n".join(f"- {role}" for role in country_recipient_roles(country))
    rows = []
    for city in sorted(cities, key=lambda item: (-item.population, item.name)):
        campaign = output.parent / city.name / "README.md"
        rows.append(
            f"| [{city.name}]({markdown_relative(output, campaign)}) | "
            f"{city.population:,} | {city.line_count} | {city.route_km:.1f} km | "
            f"{money(city.capex_usd)} |"
        )
    email_path = output.parent / "email.txt"
    national = cities[0].national_brief
    return f"""# {country} OpenSourceRail Campaign
<!-- Generated by scripts/generate-marketing-campaigns.py. -->

National outreach package covering **{len(cities)} catalogued cities**. Values
below aggregate city screening models; the national brief separately treats the
shared manufacturing plant.

## Audience

{roles}

## National proposition

| Measure | Catalogue result |
|---|---:|
| Population represented | {int(values['population']):,} |
| Lines / route length | {int(values['lines'])} / {values['route_km']:,.0f} km |
| Fleet | {int(values['fleet']):,} trainsets |
| City programme CAPEX | {money(values['capex'])} |
| Local capital and value allocation | {money(values['local'])} ({percentage(values['local'], values['capex'])}) |
| Station/depot PV / storage | {power(values['pv_kw'])} / {energy(values['storage_kwh'])} |
| Illustrative external-capital saving | {money(values['external_saving'])} |

Lead with a government-reviewed pilot, local manufacturing and construction,
open standards, renewable-energy integration and independently checked demand,
environmental, social and engineering studies.

- [National design and funding brief]({markdown_relative(output, national)})
- [Send-ready plain-text email]({markdown_relative(output, email_path)})
- [Recipient research queue]({markdown_relative(output, MARKETING / 'contact-research.csv')})

## City campaigns

| City | Population | Lines | Route | CAPEX |
|---|---:|---:|---:|---:|
{chr(10).join(rows)}
"""


def international_email(target: InternationalTarget, cities: list[City]) -> str:
    scoped = target_cities(target, cities)
    values = aggregate(scoped)
    examples = campaign_examples(scoped)
    country_count = len({city.country for city in scoped})
    example_links = "\n".join(
        f"{city.name} example: {github_url(city.city_readme)}" for city in examples
    )
    image_paths = [examples[0].network_map, examples[0].dashboard]
    if len(examples) > 1:
        image_paths.append(examples[1].network_map)
    images = "\n".join(f"- {repo_path(path)}" for path in image_paths)
    recipient = target.email or f"[official contact route: {target.contact_url}]"
    greeting = target.recipient_name or target.recipient_role
    kind = engagement_kind(target)
    if kind == "media":
        subject = (
            "Story pitch — open-source city and rail generation across "
            + count_label(len(scoped), "city", "cities")
        )
        relevance = (
            f"The work may be relevant to your coverage of {target.fit.lower()}. "
            "The repository includes inspectable assumptions, generated maps, "
            "engineering models, tests and before/after regeneration evidence."
        )
        request = (
            "Would an editor be interested in a repository-led demonstration, "
            "technical briefing or interview? This is an editorial pitch, not a "
            "request for endorsement or guaranteed coverage."
        )
    elif kind == "finance":
        subject = "OpenSourceRail project-preparation enquiry — reproducible urban-rail concepts"
        relevance = (
            f"The work may align with your mandate for {target.fit.lower()}. "
            "These are transparent screening concepts intended to make the next "
            "stage of public review and project preparation cheaper and faster."
        )
        request = (
            "Could you advise whether there is an eligible project-preparation, "
            "technical-assistance, guarantee or investment route, and which "
            "public-sector counterpart should lead it?"
        )
    elif kind == "philanthropy":
        subject = (
            "OpenSourceRail programme enquiry — open tools for equitable clean mobility"
        )
        relevance = (
            f"The work may complement programmes concerned with {target.fit.lower()}. "
            "A bounded pilot could focus on open evidence, municipal capability, "
            "safety, access and local skills rather than construction capital."
        )
        request = (
            "Would a short programme-fit discussion be appropriate, or could you "
            "direct us to a current catalytic-support or learning partnership route?"
        )
    else:
        subject = (
            "OpenSourceRail technical partnership — reproducible urban-rail concepts"
        )
        relevance = (
            f"The work appears relevant to your work on {target.fit.lower()}. "
            "We would welcome independent challenge, standards guidance and a route "
            "to the appropriate regional or member-city team."
        )
        request = (
            "Would a 30-minute technical discussion, peer review or knowledge-sharing "
            "session be appropriate, or could you direct us to the correct team?"
        )
    return f"""From: {SENDER}
To: {recipient}
Subject: {subject}

Dear {greeting},

I am writing from Modern EcoTech about OpenSourceRail, an open-source programme that has generated reproducible urban-rail screening concepts for {count_label(len(cities), 'city', 'cities')} in {count_label(len({city.country for city in cities}), 'country', 'countries')}. The design scope relevant to {target.name} contains {count_label(len(scoped), 'city', 'cities')} in {count_label(country_count, 'country', 'countries')}.

The scoped catalogue links network design, GIS, service planning, locally buildable rolling stock, renewable charging, cost and finance models, deterministic simulation and Git-reviewable evidence. It represents {int(values['population']):,} people, {values['route_km']:,.0f} route-km and {power(values['pv_kw'])} of station/depot PV in the screening models.

{relevance}

We are not presenting these outputs as feasibility studies, funding applications, procurement proposals or evidence of eligibility. {request}

Project: {GITHUB_BLOB}README.md
City catalogue: {GITHUB_BLOB}designs/README.md
{example_links}

Images to attach from the repository:
{images}

Kind regards,
Hayder
Modern EcoTech / OpenSourceRail
{SENDER}
"""


def international_readme(
    target: InternationalTarget, cities: list[City], output: Path
) -> str:
    scoped = target_cities(target, cities)
    values = aggregate(scoped)
    examples = campaign_examples(scoped)
    primary = examples[0]
    secondary = examples[1] if len(examples) > 1 else examples[0]
    region_label = "global" if "all" in target.regions else ", ".join(target.regions)
    email_path = output.parent / "email.txt"
    recipient = target.email or "Official form/contact route only"
    return f"""# OpenSourceRail × {target.name}
<!-- Generated by scripts/generate-marketing-campaigns.py. -->

Tailored partnership approach for **{target.name}**.

| Target detail | Value |
|---|---|
| Category | `{target.category}` |
| Engagement route | {engagement_label(target)} |
| Design regions | {region_label} |
| Applicable city models | {count_label(len(scoped), 'city', 'cities')} across {count_label(len({city.country for city in scoped}), 'country', 'countries')} |
| Intended recipient | {target.recipient_role} |
| Named public contact | {target.recipient_name or 'None; use the official organisational route'} |
| Public route | {recipient} |
| Official contact | [{target.contact_url}]({target.contact_url}) |
| Contact source | [{target.source_url}]({target.source_url}) |
| Last checked | {target.verified_on} |
| Programme fit | {target.fit} |

**Routing constraint:** {target.eligibility_note}

## Partnership proposition

OpenSourceRail offers a transparent early-stage pipeline spanning {count_label(len(scoped), 'city', 'cities')},
{count_label(len({city.country for city in scoped}), 'country', 'countries')}, {values['route_km']:,.0f}
route-km and {power(values['pv_kw'])} of station/depot PV in the current
screening models. The request is for technical routing, pilot preparation and
independent review—not endorsement or funding on the strength of screening data.

| {primary.name} network | {secondary.name} simulation |
|---|---|
| ![{primary.name} network]({markdown_relative(output, primary.network_map)}) | ![{secondary.name} simulation]({markdown_relative(output, secondary.dashboard)}) |

- [Send-ready plain-text email]({markdown_relative(output, email_path)})
- [OpenSourceRail overview]({markdown_relative(output, ROOT / 'README.md')})
- [City catalogue]({markdown_relative(output, DESIGNS / 'README.md')})
"""


def campaigns_index(
    cities: list[City], targets: list[InternationalTarget], output: Path
) -> str:
    countries: dict[tuple[str, str], list[City]] = {}
    for city in cities:
        countries.setdefault((city.region, city.country), []).append(city)
    rows = []
    for (region, country), members in sorted(countries.items()):
        campaign = CAMPAIGNS / region / country / "README.md"
        rows.append(
            f"| [{country}]({markdown_relative(output, campaign)}) | {region} | "
            f"{len(members)} | {sum(city.population for city in members):,} |"
        )
    partner_rows = "\n".join(
        f"| [{target.name}]({markdown_relative(output, CAMPAIGNS / 'international' / target.id / 'README.md')}) | "
        f"{target.category} | "
        f"{'global' if 'all' in target.regions else ', '.join(target.regions)} | "
        f"{len(target_cities(target, cities))} | "
        f"{target.email or 'official contact route'} |"
        for target in targets
    )
    engagement_counts = Counter(engagement_kind(target) for target in targets)
    engagement_rows = "\n".join(
        f"| {label} | {engagement_counts[kind]} |"
        for kind, label in (
            ("finance", "Development finance, funds and guarantees"),
            ("partnership", "Technical, city and transport networks"),
            ("philanthropy", "Philanthropic organisations"),
            ("media", "Specialist media"),
        )
    )
    return f"""# OpenSourceRail Campaign Catalogue
<!-- Generated by scripts/generate-marketing-campaigns.py. -->

Deterministic outreach packages for **{len(cities)} cities**, **{len(countries)}
countries** and **{len(targets)} international organisations and media outlets**. No message has
been sent and no unverified public-sector email has been guessed.

## Countries

| Country | Region | Cities | Population represented |
|---|---|---:|---:|
{chr(10).join(rows)}

## International organisations

| Audience | Campaigns |
|---|---:|
{engagement_rows}

| Organisation | Category | Design scope | Cities | Public route |
|---|---|---|---:|---|
{partner_rows}

See the [campaign use and data-handling guide]({markdown_relative(output, MARKETING / 'README.md')})
and [recipient research queue]({markdown_relative(output, MARKETING / 'contact-research.csv')}).
"""


def contact_csv(
    cities: list[City],
    targets: list[InternationalTarget],
    overrides: dict[tuple[str, str], dict[str, str]],
) -> str:
    fields = [
        "campaign",
        "geography_type",
        "region",
        "country",
        "city",
        "recipient_id",
        "recipient_role",
        "organization",
        "recipient_name",
        "email",
        "official_url",
        "verification_status",
        "last_verified",
        "source_url",
        "notes",
    ]
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
    writer.writeheader()
    countries = sorted({(city.region, city.country) for city in cities})
    for region, country in countries:
        campaign = repo_path(CAMPAIGNS / region / country / "README.md")
        campaign_id = country_campaign_id(region, country)
        for recipient_id, role in country_recipient_records(country):
            override = overrides.get((campaign_id, recipient_id), {})
            directory_url = (
                UK_DIPLOMATIC_LIST
                if recipient_id == "uk-embassy-economic-section"
                else ""
            )
            writer.writerow(
                {
                    "campaign": campaign,
                    "geography_type": "country",
                    "region": region,
                    "country": country,
                    "city": "",
                    "recipient_id": recipient_id,
                    "recipient_role": role,
                    "organization": override.get("organization", ""),
                    "recipient_name": override.get("recipient_name", ""),
                    "email": override.get("email", ""),
                    "official_url": override.get("official_url", directory_url),
                    "verification_status": (
                        "official_source_checked" if override else "research_required"
                    ),
                    "last_verified": override.get("verified_on", ""),
                    "source_url": override.get("source_url", directory_url),
                    "notes": override.get(
                        "notes",
                        (
                            "Use the current FCDO London Diplomatic List, then verify the mission's economic section."
                            if directory_url
                            else "Verify a current official role address before individual outreach."
                        ),
                    ),
                }
            )
    for city in cities:
        campaign = repo_path(
            CAMPAIGNS / city.region / city.country / city.name / "README.md"
        )
        campaign_id = city_campaign_id(city)
        for recipient_id, role in city_recipient_records(city):
            override = overrides.get((campaign_id, recipient_id), {})
            writer.writerow(
                {
                    "campaign": campaign,
                    "geography_type": "city",
                    "region": city.region,
                    "country": city.country,
                    "city": city.name,
                    "recipient_id": recipient_id,
                    "recipient_role": role,
                    "organization": override.get("organization", ""),
                    "recipient_name": override.get("recipient_name", ""),
                    "email": override.get("email", ""),
                    "official_url": override.get("official_url", ""),
                    "verification_status": (
                        "official_source_checked" if override else "research_required"
                    ),
                    "last_verified": override.get("verified_on", ""),
                    "source_url": override.get("source_url", ""),
                    "notes": override.get(
                        "notes",
                        "Prefer a published functional mailbox over a personal address.",
                    ),
                }
            )
    for target in targets:
        writer.writerow(
            {
                "campaign": repo_path(
                    CAMPAIGNS / "international" / target.id / "README.md"
                ),
                "geography_type": "international",
                "region": ";".join(target.regions),
                "country": "",
                "city": "",
                "recipient_id": target.id,
                "recipient_role": target.recipient_role,
                "organization": target.name,
                "recipient_name": target.recipient_name,
                "email": target.email,
                "official_url": target.contact_url,
                "verification_status": "official_source_checked",
                "last_verified": target.verified_on,
                "source_url": target.source_url,
                "notes": target.eligibility_note,
            }
        )
    return stream.getvalue()


def expected_outputs() -> tuple[dict[Path, bytes], dict]:
    cities = discover_cities()
    targets = load_targets()
    overrides = load_contact_overrides()
    if len(cities) != 266:
        raise ValueError(f"expected 266 city designs, found {len(cities)}")
    valid_override_keys = {
        (city_campaign_id(city), recipient_id)
        for city in cities
        for recipient_id, _ in city_recipient_records(city)
    }
    valid_override_keys.update(
        (
            country_campaign_id(region, country),
            recipient_id,
        )
        for region, country in {(city.region, city.country) for city in cities}
        for recipient_id, _ in country_recipient_records(country)
    )
    unknown_overrides = sorted(set(overrides) - valid_override_keys)
    if unknown_overrides:
        rendered = ", ".join(
            f"{campaign}/{recipient}" for campaign, recipient in unknown_overrides
        )
        raise ValueError(f"unknown contact overrides: {rendered}")
    outputs: dict[Path, bytes] = {}

    index_path = CAMPAIGNS / "README.md"
    outputs[index_path] = campaigns_index(cities, targets, index_path).encode()

    grouped: dict[tuple[str, str], list[City]] = {}
    for city in cities:
        grouped.setdefault((city.region, city.country), []).append(city)
        readme_path = CAMPAIGNS / city.region / city.country / city.name / "README.md"
        email_path = readme_path.parent / "email.txt"
        outputs[readme_path] = city_readme(city, readme_path).encode()
        outputs[email_path] = city_email(city).encode()
    for (region, country), members in grouped.items():
        readme_path = CAMPAIGNS / region / country / "README.md"
        email_path = readme_path.parent / "email.txt"
        outputs[readme_path] = country_readme(country, members, readme_path).encode()
        outputs[email_path] = country_email(country, members).encode()

    for target in targets:
        readme_path = CAMPAIGNS / "international" / target.id / "README.md"
        email_path = readme_path.parent / "email.txt"
        outputs[readme_path] = international_readme(
            target, cities, readme_path
        ).encode()
        outputs[email_path] = international_email(target, cities).encode()

    contacts_path = MARKETING / "contact-research.csv"
    outputs[contacts_path] = contact_csv(cities, targets, overrides).encode()

    artifact_hashes = {
        repo_path(path): sha256_bytes(data)
        for path, data in sorted(outputs.items(), key=lambda item: str(item[0]))
    }
    manifest = {
        "schema_version": 1,
        "sender": SENDER,
        "country_campaign_count": len(grouped),
        "city_campaign_count": len(cities),
        "international_campaign_count": len(targets),
        "recipient_role_count": len(grouped) * 4 + len(cities) * 4 + len(targets),
        "generator": repo_path(Path(__file__)),
        "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "international_targets": repo_path(TARGETS_PATH),
        "international_targets_sha256": hashlib.sha256(
            TARGETS_PATH.read_bytes()
        ).hexdigest(),
        "contact_overrides": repo_path(CONTACT_OVERRIDES_PATH),
        "contact_overrides_sha256": hashlib.sha256(
            CONTACT_OVERRIDES_PATH.read_bytes()
        ).hexdigest(),
        "artifacts": artifact_hashes,
    }
    manifest_path = MARKETING / "manifest.json"
    outputs[manifest_path] = (
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    ).encode()
    return outputs, manifest


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        handle.write(data)
        temporary = Path(handle.name)
    os.replace(temporary, path)


def generated_files() -> set[Path]:
    files = set(CAMPAIGNS.rglob("README.md")) | set(CAMPAIGNS.rglob("email.txt"))
    for path in (MARKETING / "contact-research.csv", MARKETING / "manifest.json"):
        if path.exists():
            files.add(path)
    return files


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="fail on missing or stale output"
    )
    args = parser.parse_args()
    outputs, manifest = expected_outputs()
    expected_paths = set(outputs)
    if args.check:
        issues: list[str] = []
        for path, expected in sorted(outputs.items(), key=lambda item: str(item[0])):
            if not path.is_file():
                issues.append(f"missing {repo_path(path)}")
            elif path.read_bytes() != expected:
                issues.append(f"stale {repo_path(path)}")
        for path in sorted(generated_files() - expected_paths):
            issues.append(f"unexpected generated file {repo_path(path)}")
        if issues:
            print("\n".join(issues))
            return 1
        print(
            "marketing campaigns: OK "
            f"({manifest['country_campaign_count']} countries, "
            f"{manifest['city_campaign_count']} cities, "
            f"{manifest['international_campaign_count']} international targets)"
        )
        return 0

    for path in sorted(generated_files() - expected_paths):
        path.unlink()
    for path, data in outputs.items():
        atomic_write(path, data)
    print(
        f"generated {manifest['country_campaign_count']} country, "
        f"{manifest['city_campaign_count']} city and "
        f"{manifest['international_campaign_count']} international campaigns"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
