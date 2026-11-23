"""Compile planning prices and sourcing boundaries for the published Airport prototype."""

from hashlib import sha256
from itertools import repeat
import json
from math import isclose
from pathlib import Path
import tomllib
from zipfile import ZipFile

from engineering.outline.baghdad_system import _id

HERE = Path(__file__).resolve().parent
CITY = HERE.parents[1]
ROOT = CITY.parents[1]
PACKET = HERE / "airport-prototype.zip"
DATE = "2026-11-23"
PRICE_BASIS = "constant 2026 USD"
CASES = ("low", "base", "high")
MILLION = 1_000_000
REPO = "https://github.com/modernecotech/OpenSourceRail/blob/main/"
MEMBERS = {
    "opening": "opening.json",
    "mechanical": "mechanical.json",
    "civil-article": "civil-article.json",
    "work-orders": "draft-work-orders.json",
    "service": "service.json",
    "cash": "cash.json",
    "feeder-options": "feeder-options.json",
    "decision-register": "decision-register.json",
    "radial-return": "returns/priced_radial-feeder.json",
    "six-site-return": "returns/six_site_quotation-feeder.json",
    "paired-return": "returns/six_site_parallel-feeder.json",
}
ADDITIVE_GROUPS = {
    "opening-direct": "Published one-time construction scopes, after replacement of the generic site allowance.",
    "opening-allowances": "Published owner design, commissioning and project allowances, each counted once.",
    "first-full-year-operations": "Operating expenditure for one full year, after the embedded payroll credit.",
    "renewal-schedule": "Named undiscounted renewal events in constant money. Expenditure falls in the specified operating year.",
}


def _source(path, raw, **metadata):
    relative = path.relative_to(ROOT).as_posix()
    return {"path": relative, "url": REPO + relative, "sha256": sha256(raw).hexdigest(), **metadata}


def _load(packet_path):
    data, sources = {}, {}
    with ZipFile(packet_path) as archive:
        manifest = json.loads(archive.read("manifest.json"))
        hashes = manifest["sha256"]
        names = archive.namelist()
        if (len(names) != len(set(names)) or set(names) != {"manifest.json", *hashes}
                or _id(hashes) != manifest["evaluation_id"]):
            raise ValueError("Airport packet manifest and archive inventory differ")
        for key, member in MEMBERS.items():
            raw = archive.read(member)
            if sha256(raw).hexdigest() != hashes[member]:
                raise ValueError(f"Airport packet member changed: {member}")
            data[key] = json.loads(raw)
            sources[key] = {
                "url": REPO + PACKET.relative_to(ROOT).as_posix(),
                "member": member,
                "sha256": hashes[member],
                "packet_evaluation_id": manifest["evaluation_id"],
            }

    opening, mechanical, cash, civil, work, service, decision = (
        data[key] for key in ("opening", "mechanical", "cash", "civil-article", "work-orders",
                              "service", "decision-register")
    )
    candidate, evaluation = opening["candidate_id"], opening["evaluation_id"]
    feeder = opening["section_power"]
    expected_evaluation = _id({
        "bundle": opening["bundle"], "sources": opening["sources"],
        "service": service["evaluation_id"], "power": opening["power"]["evaluation_id"],
        "feeder": feeder["evaluation_id"],
    })
    frame = opening["bundle"]["vehicle_revision"]
    binding = {
        "opening_candidate_id": candidate, "opening_evaluation_id": evaluation,
        "feeder_design_id": feeder["design_id"], "feeder_evaluation_id": feeder["evaluation_id"],
        "power_evaluation_id": opening["power"]["evaluation_id"],
    }
    if (
        candidate != _id(opening["bundle"]) or evaluation != expected_evaluation
        or _id({key: value for key, value in service.items() if key != "evaluation_id"}) != service["evaluation_id"]
        or any(doc["candidate_id"] != candidate for doc in (manifest, mechanical, cash, civil, work))
        or decision["airport_candidate_id"] != candidate
        or cash["opening_evaluation_id"] != evaluation
        or cash["matched_supplier_lots"] or cash["site_replacements"] or cash["demand_survey"] is not None
        or cash["evaluation_id"] != decision["commercial_evaluation"]
        or civil["evaluation_id"] != decision["civil_evaluation_id"]
        or mechanical["evaluation_id"] != civil["mechanical_evaluation_id"]
        or any(doc["frame_revision"] != frame for doc in (mechanical, work))
        or manifest["article"] != frame
        or data["feeder-options"]["evaluation_id"] != decision["electrical_evaluation"]
        or any(data[key]["binding"] != binding for key in (
            "feeder-options", "radial-return", "six-site-return", "paired-return"
        ))
    ):
        raise ValueError("Sourcing requires the matched Airport prototype and its unquoted cash schedule")

    for key, path in (
        ("system-rates", CITY / "system.toml"),
        ("market-rates", CITY / "iraq-capital.toml"),
        ("local-works", CITY / "airport-works.toml"),
        ("iraq-energy", CITY / "iraq-power.toml"),
    ):
        raw = path.read_bytes()
        byte_source = _source(path, raw)
        if key != "market-rates" and opening["sources"][byte_source["path"]] != byte_source["sha256"]:
            raise ValueError(f"Airport priced opening uses a different source revision: {path.name}")
        data[key] = tomllib.loads(raw.decode())
        sources[key] = byte_source
    sources["estimate-method"] = _source(Path(__file__).resolve(), Path(__file__).read_bytes())
    data["manifest"] = manifest
    return data, sources


def _external_sources(data):
    site = data["local-works"]
    train = data["market-rates"]["trains"]
    energy = data["iraq-energy"]
    return {
        "iqd-conversion": {
            "title": "Central Bank selling rate used in the Airport model",
            "url": data["opening"]["iraq_site_estimate"]["currency_source"],
            "source_date": "2026-10-07",
        },
        "iraq-material": {
            "title": "Iraqi Statistics and GIS Authority construction materials, tables 1–2",
            "url": site["materials"]["source"], "source_date": "2026-10",
        },
        "baghdad-road": {
            "title": "Iraqi Ministry of Planning, Baghdad–Wasit mixed road and interchange comparator",
            "url": site["corridor"]["road_source"],
        },
        "iraq-rail": {
            "title": "World Bank Iraq Railways Extension and Modernization project appraisal, P507282",
            "url": site["rail"]["rail_source"], "source_date": "2025",
        },
        "chennai-trains": {
            "title": "Alstom Chennai Metro 78-car contract announcement, EUR 98m",
            "url": train["source"], "source_date": "2022-11-11",
        },
        "award-currency": {
            "title": "Federal Reserve historical exchange rates",
            "url": train["exchange_source"], "source_date": "2022-11-14",
        },
        "us-passenger-study": {
            "title": "Solano Transportation Authority, Vallejo Passenger Rail Study agenda item 8.D",
            "url": "https://www.sta.ca.gov/wp-content/uploads/2022/09/STA-Board-Packet_04-12-2023.pdf",
            "source_date": "2023-04-12", "comparator_amount_usd": 280_000,
        },
        "uk-survey-award": {
            "title": "Network Rail West Coast South Earthwork Management Strategy, notice 2026/S 000-002326",
            "url": "https://www.find-tender.service.gov.uk/Notice/002326-2026/PDF",
            "source_date": "2026-01-12", "comparator_amount_gbp_ex_vat": 400_000,
        },
        "nsw-ground-scope": {
            "title": "Transport for NSW, Country Regional Network site investigations IPD-22-12012",
            "url": "https://www.transport.nsw.gov.au/system/files/media/documents/2023/CQR%20-%20Site%20Investigations%20Contract%20%28Contract%20No.%20IPD-22-12012%29.PDF",
            "scope_use": "Investigation work scope only",
        },
        "jica-tariff": {
            "title": "JICA Iraq grid electricity source",
            "url": energy["energy"]["grid_reference"],
        },
        "undp-alternate-power": {
            "title": "UNDP Energy Transition in Iraq",
            "url": energy["energy"]["alternate_reference"], "source_date": "2025",
        },
        "iraq-grid-contracts": {
            "title": "Twanist contractor's completed Iraq utility equipment contracts, rows 69 and 93",
            "url": energy["equipment"]["source"], "source_date": "2022–2023",
        },
        "reference-baseline": {
            "title": "OpenSourceRail six-car, passive-wheel development reference",
            **_source(ROOT / "engineering/development-baseline.toml",
                      (ROOT / "engineering/development-baseline.toml").read_bytes()),
        },
    }


def _lot(lot_id, description, quantity, unit, amounts, *, basis, exclusions,
         deliverables, sources, group="reconcile-before-addition", price_period="one-time",
         evidence_class="published-planning-allowance", **details):
    low, base, high = (None, None, None) if amounts is None else amounts
    rounded = round(quantity, 3)
    if rounded != quantity:
        basis += " Enquiry quantity rounded to three decimals. Prices retain the source quantity."
        details["source_quantity"] = quantity
    return {
        "lot_id": lot_id, "description": description, "quantity": rounded, "unit": unit,
        "low_usd": low, "base_usd": base, "high_usd": high, "price_period": price_period,
        "price_basis": PRICE_BASIS, "estimate_date": DATE, "evidence_class": evidence_class,
        "price_status": "unpriced" if amounts is None else "planning-price", "firm_price_usd": None,
        "inclusion_group": group, "basis": basis, "exclusions": exclusions,
        "deliverables": deliverables, "sources": list(sources), "physical_acceptance": "open",
        **details,
    }


def _opening_lots(data):
    opening, work = data["opening"], data["work-orders"]
    bundle, civil = opening["bundle"], opening["civil"]
    priced = opening["iraq_site_estimate"]["scenarios"]
    route, stop_count = bundle["route_km"], len(bundle["stops"])
    power = opening["section_power"]["procurement"]
    design = bundle["feeder_design_id"]

    def direct(lot_id, scope, quantity, unit, basis, exclusions, deliverables, **details):
        return _lot(
            lot_id, scope, quantity, unit,
            [priced[case]["scopes_usd_m"][scope] * MILLION for case in CASES],
            basis=basis, exclusions=exclusions, deliverables=deliverables,
            sources=("opening", "system-rates", *details.pop("extra_sources", ())),
            group="opening-direct", published_scope=scope, **details,
        )

    return [
        direct("fleet", "Fleet, including spare sets", work["opening_trainsets"], "six-car trainsets",
               "Published repeat-set allowance applied to three diagrammed sets and three spares. The opening holds the same fleet rate across the site scenarios.",
               "Owner programme tests, wayside recovery, fixed production tooling and incremental spares or heavy repairs.",
               "Serial BOM with consumed and installed mass, axle loads, powered bogies, doors, controls, traction/brakes, service power, heat duty, factory trials, local repair support and independently witnessed evidence.",
               supplier_return="trainsets", fleet_cars=work["fleet_cars"],
               opening_installed_tare_kg=data["mechanical"]["mass"]["complete_installed_tare_kg"],
               extra_sources=("work-orders", "mechanical")),
        direct("elevated-civil", "Viaduct, piers and foundations", civil["beam_count"], "single-track spans",
               "Published standard separate-track series including supports, bearings, routine lifts and associated elevated works.",
               "Site extras for bored shafts, exceptional crossings, temporary access and incremental beam haul. Credit any subcontract package already in this price.",
               "Itemize casting and track-seat works, reinforcement, strand, bearings, supports, lifts, staging, survey and as-built inspection. Return the priced source quantities and independent structural review.",
               supplier_return="civil", supports=civil["pier_foundation_count"],
               bearing_units=civil["bearing_unit_allowance"], lifts=civil["lift_count"],
               extra_sources=("civil-article",)),
        direct("stations", "Six station shells and accessible approaches", stop_count, "station sites",
               "Published per-station rate for six retained stops.",
               "Airport landside forecourt, separately allocated train controls, offsite utilities and exceptional land works.",
               "Per-stop shell, circulation and step-free egress, equipment, lifts, measured boarding interface, fire and evacuation demonstrations and responsibility matrix.",
               supplier_return="stations", stop_ids=bundle["stops"], extra_sources=("civil-article",)),
        direct("track", "Track and walkways", power["protected_track_km"], "track-km",
               "Twin-track running route priced at the published track-and-walkway rate.",
               "Protected traction conductor, terminal turnout premiums and depot lead/refuge additions.",
               "Rail, fasteners, track joints, survey datums, expansion/wear limits, inspection and walkway continuity.",
               extra_sources=("iraq-rail",)),
        direct("signalling", "Signalling and communications", route, "route-km",
               "Published route rate plus quantities of station and line interfaces identified by the control register.",
               "Equipment assigned to onboard, power protection or OCC fit-outs and separately priced integrated test programme.",
               "Installed ATP/ATO interface schedule, station interlocking, train detection, radio, network segmentation and witnessed loss-of-communications and safe-stop tests."),
        direct("wayside-braking", "Wayside braking and recovery", route, "route-km",
               "Published route protection and rescue rate, applied at the same price in all three site scenarios.",
               "Onboard brake equipment within fleet, fixed rescue tooling, operator drills and major renewal.",
               "Verified stopping and work-zone limits, rescue coupling and movement interfaces, failed-train recovery and drill records."),
        direct("traction-line", "Protected conductor and switchgear", power["protected_track_km"], "track-km",
               "Published allowance for protected conductor, outgoing breaker circuits and normally open midpoint ties on the 30-site layout.",
               "Substation conversion, offsite AC utility scope and six-site alternative branches. Reconcile the AC/DC termination and switchgear boundary with the site-conversion bid.",
               "Return the positive and return conductors, bonds, switches, guarding, hot resistance and loss, coordinated fault protection, isolation and access records.",
               supplier_return="line_power", design_id=design, outgoing_circuits=power["dc_outgoing_breaker_circuits"],
               midpoint_ties=power["normally_open_track_ties"], extra_sources=("radial-return",)),
        direct("traction-sites", "Grid supply sites", power["dc_source_groups"], "DC source groups",
               "Published railway-side allowance sizes the site rating to the planning peak DC request.",
               "Offsite distribution feeders, alternative six-site arrangement and separately priced line equipment.",
               "Utility availability and connection capacity, transformer/rectifier duty, cooling, switchgear interfaces, power quality, earthing, protection and metering by site.",
               supplier_return="line_power", design_id=design, peak_dc_mw=power["minimum_site_peak_dc_mw"],
               extra_sources=("radial-return", "iraq-grid-contracts")),
        direct("depot-control", "Depot and control centre", bundle["depots"] + bundle["control_centres"], "facilities",
               "Published rates for one permanent depot and one control centre.",
               "Extra lead track, traction sites and fixed production tooling. Host, shared and temporary facilities require alternative matched installed bids.",
               "Workshop and stabling layout, storage and lifting, access, OCC extent, failover, operator training and equipment scope."),
        direct("tooling", "Fixed production setup and route tooling", 1, "programme",
               "Published fixed production and recovery tooling allowance plus route-km tooling increment.",
               "Plant already in depot or supplier prices, annual yard rent premium and trial article charges pending price reconciliation.",
               "Jigs, moulds, proving pieces, calibrated tooling, recovery equipment, lead times, local content and inspection records."),
    ]


_SITE = (
    ("land-utilities", "Land, utility conflicts and traffic reinstatement",
     "Baghdad–Wasit mixed-road benchmark times the corridor share.",
     "Standard civil possessions, offsite distribution feeders and exceptional road crossings.",
     "Legal land and utility register, mapped conflicts, relocation plan, traffic plan and segregated reinstatement bill.",
     ("baghdad-road",)),
    ("turnouts", "Terminal and depot turnout premiums",
     "Quantity and incremental turnout premiums from the Airport site schedule.",
     "Base running rail, separately priced signalling controllers and depot buildings.",
     "Survey throat and refuge geometry, return detailed switch, actuator, drainage and interlock quantities and price interfaces.",
     ()),
    ("depot-lead", "Extra depot lead and refuge track",
     "Iraqi track renewal benchmark times the new-build short-package factor and extra track length.",
     "Major grade separation, depot internal tracks and terminal turnout premiums.",
     "Define yard boundary, formation and track, conductor, controls and refuge lengths at chainage.",
     ("iraq-rail",)),
    ("airport-forecourt", "Landside airport forecourt and security interface",
     "Airport site schedule allowance for incremental landside interface.",
     "Standard station and access works. Land acquisition and offsite utility feeders are separate.",
     "Secure boundary and traffic plan, egress and step-free route survey, airport authority consent and dated scope price.",
     ()),
    ("offsite-feed", "Offsite distribution feeders and tie-ins",
     "Fixed 30-site layout multiplied by low/base/high local connection allowance per site.",
     "Railway-side converter and DC works. Reconcile credits if the utility interface is included in a complete feeder offer.",
     "Written utility scopes by site with metering point, firm capacity, energy and standby terms, independent source availability and asset ownership.",
     ()),
    ("extra-foundation", "Additional foundation shafts under standard caps",
     "Bored shaft quantity sensitivity and Iraqi materials with installed-to-material multiplier.",
     "Repeated standard foundations, owner geotechnical investigation and unforeseen ground improvement.",
     "Survey bore-lengths and affected supports, drilling and casing, cage, spoil, trial and actual pile-test reports.",
     ("iraq-material",)),
    ("exceptional-crossings", "Exceptional road-crossing works",
     "Additional crossings and strengthening allowances above ordinary spans.",
     "Ordinary span erection and routine traffic reinstatement.",
     "Crossing-by-crossing possessions, temporary deck, approvals, clearances, staged lifts and risk owners.",
     ()),
    ("yard-access", "Incremental yard premises and temporary access",
     "Yard-months from the erection programme multiplied by variable temporary access and premises rates.",
     "Permanent depot, included moulds and plant, ordinary shipping and incremental road haul.",
     "Yard lease, hardstanding, access permits, productive shifts, reinstatement and release timetable.",
     ()),
    ("extra-haul", "Extra beam haul above standard delivery",
     "Incremental loaded-equivalent distance per dispatch from the Airport site schedule.",
     "Standard delivery already in civil rates and temporary yard access already priced separately.",
     "Dispatch and haul route records, axle permits, mobilization boundary, owner possessions and return distances.",
     ()),
)


def _site_and_owner_lots(data):
    scenarios = data["opening"]["iraq_site_estimate"]["scenarios"]
    for lot_id, name, basis, exclusions, deliverables, external_sources in _SITE:
        case_rows = [scenarios[case]["items"][name] for case in CASES]
        base = case_rows[1]
        yield _lot(
            lot_id, name, base["quantity"], base["unit"],
            [row["direct_usd_m"] * MILLION for row in case_rows],
            basis=basis, exclusions=exclusions, deliverables=deliverables,
            sources=("opening", "local-works", "iqd-conversion", *external_sources),
            group="opening-direct", evidence_class="local-works-sensitivity", site_return=name,
            scenario_quantities={case: row["quantity"] for case, row in zip(CASES, case_rows, strict=True)},
            scenario_unit_iqd={case: row["unit_iqd"] for case, row in zip(CASES, case_rows, strict=True)},
        )
    for lot_id, scope, fraction, boundary, deliverables in (
        ("design-assurance", "Design and assurance", "design_fraction",
         "Direct supplier detail design and shop inspection included in supply prices.",
         "Owner design interface register, site investigations scope, independent design assurance, procurement and contract package mapping."),
        ("integrated-test", "Testing and commissioning", "testing_fraction",
         "Factory acceptance tests, direct subcontract shop evidence and routine QA already allowed in other lots.",
         "Commissioning plan, staged access, independent witnessing, owner test records with approved limits and authority sign-offs."),
        ("programme-allowance", "Project allowance", "project_allowance_fraction",
         "Unpriced costs remain open. This allowance does not cover funding fees, escalation or unknown tax treatment automatically.",
         "Quantified risk register, residual scope exposure and separately agreed owner contingency draw conditions."),
    ):
        rate = data["system-rates"]["capital_rates_usd_m"][fraction]
        denominator = "direct plus design and testing" if lot_id == "programme-allowance" else "direct"
        yield _lot(
            lot_id, scope, 1, "opening programme",
            [scenarios[case]["scopes_usd_m"][scope] * MILLION for case in CASES],
            basis=f"Published {rate:.1%} of {denominator}.",
            exclusions=boundary, deliverables=deliverables, sources=("opening", "system-rates"),
            group="opening-allowances",
        )


def _operations_lots(data):
    opening = data["opening"]
    ops = opening["iraq_operations"]["cases"]
    scenarios = [ops[key] for key in ("upside", "central", "downside")]
    definitions = (
        ("opex-power", "Delivered electricity", ops["central"]["total_grid_gwh"], "GWh/year",
         "electricity_usd_m", "Delivered tariff and grid/alternate supply sensitivity including non-revenue movements.",
         "Site maintenance, exceptional service charges and major renewals.",
         "Return tariff class and meter boundary, weighted backup source prices, fixed charges and annual metered demand.",
         ("iraq-energy", "iqd-conversion", "jica-tariff", "undp-alternate-power")),
        ("opex-payroll", "Core operations payroll", ops["central"]["total_fte"] - ops["central"]["airport_liaison_fte"],
         "full-time equivalents", "payroll_usd_m",
         "Published Iraqi loaded payroll for core station, control centre, depot, civil, power and support roles.",
         "Incremental airport liaison and power equipment upkeep. Embedded payroll is credited once in other operations.",
         "Shift roster, relief factors, salaries and employer contributions by role.",
         ("iqd-conversion",)),
        ("opex-feeder", "Incremental site and switch upkeep", opening["bundle"]["grid_sites"], "DC source groups",
         "incremental_site_and_switch_upkeep_usd_m",
         "0.5% / 1% / 2% of the additional rail-side equipment value above the three-site comparator, applied in annual service.",
         "Basic track-side upkeep, electrical tariff, extraordinary tie or onsite service charges and named renewals.",
         "Return preventive and corrective work, hours, parts, outage windows, service level and callout prices.",
         ("local-works", "radial-return")),
        ("opex-other", "Other recurring operations and maintenance", opening["power"]["common_service"]["service_days_per_year"],
         "service days/year", None,
         "Remaining published O&M after subtracting the other three rows. Includes credited non-energy train, station and baseline line work, incremental liaison and non-revenue non-labour costs.",
         "Core payroll, the energy bill and additional feeder upkeep shown separately. Exceptional site costs remain open.",
         "Separate labour, replacement consumables, station attendance, security, cleaning, incident response, workshop and maintainer callouts.",
         ("service", "system-rates")),
    )
    for lot_id, name, quantity, unit, cost_key, basis, exclusions, deliverables, references in definitions:
        amounts = ([case[cost_key] * MILLION for case in scenarios] if cost_key else [
            (case["opex_usd_m"] - case["electricity_usd_m"] - case["payroll_usd_m"]
             - case["incremental_site_and_switch_upkeep_usd_m"]) * MILLION
            for case in scenarios
        ])
        yield _lot(
            lot_id, name, quantity, unit, amounts, basis=basis, exclusions=exclusions,
            deliverables=deliverables, sources=("opening", *references), group="first-full-year-operations",
            price_period="annual", evidence_class="published-operating-sensitivity",
        )
    for event in opening["renewals"]:
        description = event["component"].replace("_", " ").capitalize()
        year = event["year"]
        yield _lot(
            "renewal-" + event["component"].replace("_", "-"), description, 1, "renewal event",
            list(repeat(event["usd_m"] * MILLION, 3)),
            basis="Published opening schedule using modelled replacement fractions. The same event allowance is held across site scenarios.",
            exclusions="Routine upkeep, debt service, escalation and other unpriced replacements.",
            deliverables="Confirm replacement population, trigger, quantities, possession plan, parts availability and price by operating year.",
            sources=("opening", "system-rates"), group="renewal-schedule", price_period="scheduled",
            operating_year=year,
        )


def _enquiry_lots(data, sources, owner):
    opening = data["opening"]
    market = data["market-rates"]
    work = data["work-orders"]
    fleet_cars = work["fleet_cars"]
    route = opening["bundle"]["route_km"]
    train = market["trains"]
    market_rates = [
        (train["contract_eur_m"] * MILLION / train["contract_cars"]
         * train["award_usd_per_eur"] * factor)
        for factor in train["delivered_price_factor"]
    ]
    yield _lot(
        "fleet-market-sensitivity", "Chennai package comparison for matched Airport fleet quantities",
        fleet_cars, "cars", [fleet_cars * rate for rate in market_rates],
        basis="EUR 98m for 78 Chennai cars at USD 1.0176/EUR. The Baghdad market study applies 1.00 / 1.20 / 1.55 factors for date, imports, duty, spares and adaptation. Chennai formations, traction and purchase scale differ.",
        exclusions="This sensitivity replaces the fleet allowance only through a matched return. Owner trials, exceptional local tooling and application-specific changes require separate scope allocation.",
        deliverables="Return six complete six-car sets on the published Airport formation and interfaces with explicit spares, training, commissioning and warranty boundaries.",
        sources=("market-rates", "chennai-trains", "award-currency", "work-orders"),
        group="comparison-only", evidence_class="published-contract-comparator",
        alternative_to_lot_ids=["fleet"],
    )
    passenger = sources["us-passenger-study"]["comparator_amount_usd"]
    survey = sources["uk-survey-award"]["comparator_amount_gbp_ex_vat"] * 1.3
    for lot_id, desc, qty, unit, amounts, basis, exclusions, deliverables, refs in (
        ("demand-survey", "Passenger origins, destinations, counts and fare survey",
         len(opening["bundle"]["stops"]), "station catchments",
         [passenger * factor for factor in (0.5, 1, 2)],
         "USD 280k unindexed 2023 Vallejo study envelope, multiplied by 0.5 / 1 / 2 as a planning sensitivity. Limited corridor counts at the low end and repeat weekday, weekend and seasonal work at the high end. Local labour and sampling prices still require bids.",
         "Airport tenant or airline commercial studies and comprehensive metropolitan assignment modelling.",
         "Provide sampling frame, coverage, directional OD with paying and total counts, boarding and alighting at six stops, dates, bias, linked journeys, fare net of collection costs and independently reviewed raw records.",
         ("us-passenger-study", "service")),
        ("alignment-survey", "Route, utilities, land and accessibility survey", route, "route-km",
         [survey * factor for factor in (0.5, 1, 2)],
         "GBP 400k excluding VAT for Network Rail aerial survey and terrain models, translated at an assumed USD 1.30/GBP. The 0.5 / 1 / 2 factors bracket desk work with selective field checks through detailed control, utilities and access mapping. Scope and labour adjustment need local offers.",
         "Ground investigations, easement purchases, utility relocations and airport permit costs.",
         "Provide tied control and levels, utilities and land boundaries, 3D deliverables, surveyed longitudinal profiles, crossing envelopes and matched accessibility measurements.",
         ("uk-survey-award", "opening")),
        ("ground-investigation", "Geotechnical investigation and foundation parameters", route, "route-km",
         [owner["design-assurance"][f"{case}_usd"] * share for case, share in zip(CASES, (0.01, 0.025, 0.05), strict=True)],
         "Reserve 1% / 2.5% / 5% of owner design and assurance for corridor reconnaissance, field investigation and expanded work at difficult sites. This is an allocation sensitivity pending a borehole and laboratory bill from the geotechnical lead.",
         "Construction shafts, production pile tests assigned to direct supply and remedial works.",
         "Return staged borehole and lab schedule, access and spoil handling, verified logs and samples, interpreted parameters and design ground model with remaining uncertainty.",
         ("nsw-ground-scope", "civil-article", "opening")),
        ("procurement-assurance", "Tender preparation and independent interface review", 1, "opening programme",
         [owner["design-assurance"][f"{case}_usd"] * share for case, share in zip(CASES, (0.005, 0.01, 0.02), strict=True)],
         "Reserve 0.5% / 1% / 2% of owner design and assurance as an internal scope allocation pending priced services. Allow for tender quantities, supplier comparisons and independent technical/commercial review.",
         "Supplier design, physical witness testing, legal approvals and actual tax or financing charges.",
         "Issue interface and exclusions matrix, traceable bill, acceptance schedule, local content evidence, ERP item and revision mapping and independent award recommendation.",
         ("work-orders", "opening")),
    ):
        yield _lot(
            lot_id, desc, qty, unit, amounts, basis=basis, exclusions=exclusions, deliverables=deliverables,
            sources=refs, group="nested-owner-enquiry", overlaps_lot_ids=["design-assurance"],
            evidence_class=("comparator-sensitivity" if lot_id in ("demand-survey", "alignment-survey")
                            else "owner-allowance-allocation"),
        )

    for lot_id, desc, quantity, unit, shares, boundary, deliverables, refs in (
        ("test-vehicle", "Vehicle, doors, brakes and bogie physical test programme", 1, "article programme",
         (0.02, 0.05, 0.10), "Fitted vehicle procurement, supplier factory acceptance and integrated route trial.",
         "Independently witness weighing, structural/fatigue tests with approved limits, fitted door and boarding measurements, brake and emergency release tests, hot duty and bogie removal.",
         ("mechanical", "work-orders")),
        ("test-civil", "Beam, bearing, erection and accessible-bay physical test programme", 1, "article programme",
         (0.02, 0.05, 0.10), "Article fabrication and quality-control checks already in the civil supply offer.",
         "Submit transfer-strength and bar/strand verification, proof-load and staged lift records, bearing restraint and movement, fitted bay drainage, door gap, step and egress checks.",
         ("civil-article", "work-orders")),
        ("test-traction-controls", "Traction hot-duty, isolation and automatic-control trials", 1, "integrated programme",
         (0.04, 0.10, 0.20), "Supplier type tests, instruments and normal installation QA already in a matched direct bid.",
         "Supply approved limits, calibrated time series, simultaneous loads, breaker grading and earthing evidence, interlocks, failed-feed recovery, blocked/wrong-side doors and emergency stop trials.",
         ("feeder-options", "service")),
        ("test-operator", "Operational proving and emergency drills", 1, "opening programme",
         (0.02, 0.05, 0.10), "Annual service budget and train factory acceptance tests.",
         "Run restricted operation, rescue, outage, fire, emergency communications and step-free evacuation exercises. Return signed operator, airport and emergency service evidence.",
         ("service", "decision-register")),
    ):
        yield _lot(
            lot_id, desc, quantity, unit,
            [owner["integrated-test"][f"{case}_usd"] * share for case, share in zip(CASES, shares, strict=True)],
            basis="Internal carve-out of the owner integrated test allowance at "
            + " / ".join(f"{share:.0%}" for share in shares)
            + " for planning test coverage, repetition and independent witnessing. Obtain lab and trial quotes.",
            exclusions=boundary, deliverables=deliverables,
            sources=("opening", "system-rates", *refs), group="nested-owner-enquiry",
            overlaps_lot_ids=["integrated-test"], evidence_class="owner-allowance-allocation",
        )


def _pilot_lots(data):
    opening, civil, work = (data[key] for key in ("opening", "civil-article", "work-orders"))
    cfg = data["system-rates"]
    rates = cfg["power_price_allowances_usd_m"]
    ctrl = cfg["control_electronics_price_allocations_usd_m"]
    car_rate = work["fleet_purchase_allowance_usd_m"] * MILLION / work["fleet_cars"]
    motors = data["mechanical"]["proposed_service_inventory"]["per_car"]["powered_axle_modules"] / 2
    bogie_drive = motors * rates["motor_inverter_module_per_axle"] * MILLION
    beam_rate = cfg["civil_rates"]["selected_10m_beam_usd"]
    lift_rate = cfg["civil_rates"]["selected_10m_lift_usd"]
    bay_panels = 4
    station_rate = opening["scopes_usd_m"]["Six station shells and accessible approaches"] * MILLION / len(opening["bundle"]["stops"])
    # The quotation unit is one cabinet/contact demonstrator, sized with one representative drive channel.
    module_rate = MILLION * (
        rates["motor_inverter_module_per_axle"] + rates["protected_shoe_sets_per_trainset"] / 4
        + ctrl["tcms_node"] + ctrl["inverter_control_unit"] + ctrl["train_service_power_unit"]
        + 2 * ctrl["shoe_status_channel"] + 2 * ctrl["brake_controller"] + 8 * ctrl["door_controller"]
    )
    pilots = (
        ("pilot-car", ["fleet", "tooling", "test-vehicle"], [car_rate * x for x in (1.2, 1.6, 2.4)],
         "One sixth of the published six-car repeat-set price, multiplied by 1.2 / 1.6 / 2.4 for first-of-kind engineering, setup, fitting and production learning.",
         "Budget includes the car and fitted subsystems as one unit. Credit component pilots reused in the car. Separate independent trials and production mould/tool ownership.",
         ("opening", "mechanical")),
        ("pilot-bogie", ["pilot-car", "fleet", "test-vehicle"],
         [bogie_drive / share * markup for share, markup in zip((0.65, 0.55, 0.40), (1.15, 1.35, 1.65), strict=True)],
         "Two axle drive modules at the published USD 90k per module. Treat them as 65% / 55% / 40% of the repeat powered bogie, then apply 1.15 / 1.35 / 1.65 for first-article design, jigs and setup.",
         "Excludes witnessed load and reliability trials. Quote a standalone hardware unit once and show the credit if fitted in the representative car.",
         ("system-rates", "mechanical")),
        ("pilot-beam", ["elevated-civil", "tooling", "test-civil"],
         [beam_rate * fab + lift_rate * lift for fab, lift in zip((1.5, 2.25, 3.5), (1.5, 2, 3), strict=True)],
         "Published series allowance USD 14,240 per 10 m beam and USD 5,000 per routine lift. Multiply fabrication and delivery by 1.5 / 2.25 / 3.5 and lift by 1.5 / 2 / 3 for short-run casting, inspection and crane mobilization.",
         "Excludes independent load trials, new piers, geotechnics and extraordinary access. Cage and strand are inside the beam proxy.",
         ("system-rates", "civil-article", "iraq-material")),
        ("pilot-station-bay", ["stations", "test-civil"],
         [station_rate * bay_panels / civil["station_panels"]["panels_per_island_template"] * share * factor
          for share, factor in zip((0.03, 0.06, 0.10), (2, 3, 4), strict=True)],
         "Take four of the 100 template panels. Allocate 3% / 6% / 10% of the published station allowance to the platform deck and edges, then multiply by 2 / 3 / 4 for one 5 m trial bay, edge/drainage equipment and standalone setup.",
         "Excludes the rest of the station, passenger lifts, structure below the bay and witnessed boarding trials.",
         ("opening", "civil-article")),
        ("pilot-traction-controls", ["pilot-car", "fleet", "signalling", "test-traction-controls"],
         [module_rate * factor for factor in (1.3, 1.8, 2.5)],
         "One drive module, shoe allocation, TCMS node, inverter controller, one service power unit, two shoe and two brake channels and eight door controllers at Baghdad installed budget rates. Multiply by 1.3 / 1.8 / 2.5 for one-off cabinet integration, harness and assembly.",
         "Excludes substations, route communications, additional axle drives or cabinets, station controls and independent integrated testing.",
         ("system-rates", "mechanical", "radial-return")),
    )
    orders = work["draft_work_orders"]
    if [order["article"] for order in orders] != [
        "Representative car", "Powered bogie", "Viaduct beam", "Accessible station bay", "Traction and control module"
    ]:
        raise ValueError("Price proxies need review against the current pilot work orders")
    for order, (lot_id, overlap, amounts, basis, exclusions, refs) in zip(orders, pilots, strict=True):
        yield _lot(
            lot_id, order["article"], order["qty"], "first article",
            [round(amount * order["qty"], -3) for amount in amounts],
            basis=f'{basis} {order["routing"]}', exclusions=exclusions,
            deliverables=order["inspection_and_handoff"], sources=("work-orders", *refs),
            evidence_class="first-article-budget-proxy", overlaps_lot_ids=overlap,
            design_documents=order["documents"],
        )


def _feeder_alternatives(data):
    opening, cfg, evidence = (data[key] for key in ("opening", "system-rates", "feeder-options"))
    site_scenarios = opening["iraq_site_estimate"]["scenarios"]
    prices = cfg["power_price_allowances_usd_m"]
    capital = cfg["capital_rates_usd_m"]
    radial = data["radial-return"]["scope"]["design"]
    site_count = opening["bundle"]["grid_sites"]
    paired_quantities = evidence["parallel_quotation"]["quantity_enquiry"]
    for key, name, paired in (
        ("six-site-return", "Six-site single-path feeder", False),
        ("paired-return", "Six-site paired-path feeder", True),
    ):
        option = data[key]["scope"]
        feeders = option["rectifier_sites"]
        track_km = option["protected_track_km"]
        switching = option["outgoing_circuits"] + option["midpoint_ties"]
        design = option["design"]
        if paired:
            site_rating = evidence["parallel_quotation"]["site_output_rating_request_mw_at_nominal_voltage"]
            branch_ends = (paired_quantities["positive_branch_disconnect_points"]
                           + paired_quantities["return_branch_test_points"])
        else:
            site_rating = design["source_kv"] * max(
                condition["current_ka"] for condition in evidence["six_site_quotation"]["cases"].values()
            )
            branch_ends = 0
        conductance_factor = max(
            radial["outward_ohm_per_km"] / design["outward_ohm_per_km"],
            radial["return_ohm_per_km"] / design["return_ohm_per_km"],
        )
        paths = design.get("parallel_positive_paths", 1)
        base_site_usd_m = capital["traction_supply_site"] + max(
            0, site_rating - prices["traction_supply_site_base_rating_mw"]
        ) * prices["additional_site_capacity_per_mw"]
        funding_breakdown = {}
        for case, section, site_factor, switch_factor, terminals, offsite_factor in zip(
            CASES, (0.25, 0.40, 0.60), (0.85, 1.10, 1.40), (1.0, 1.4, 2.0),
            (0.10, 0.20, 0.40), (1, 1.5, 2.5), strict=True
        ):
            offsite = site_scenarios[case]["items"]["Offsite distribution feeders and tie-ins"]["direct_usd_m"]
            # Half of the balance of the baseline path cost is shared structure.
            # The other half scales with installed paths alongside the conductor metal.
            path_factor = section * conductance_factor * paths + (1 - section) * (1 + paths) / 2
            components = {
                "railway-side supply sites and plant": feeders * base_site_usd_m * site_factor,
                "positive and return paths including guarding and bonds": track_km * prices["protected_conductor_per_track_km"] * path_factor,
                "outgoing breakers, ties and branch points": (
                    switching * switch_factor + branch_ends * terminals
                ) * prices["protected_section_switchgear_each"],
                "offsite utility tie-ins": feeders * offsite / site_count * offsite_factor,
            }
            funding_breakdown[case] = {part: round(value * MILLION, -3) for part, value in components.items()}
        lot_id = option["option"].replace("_", "-")
        amounts = [sum(funding_breakdown[case].values()) for case in CASES]
        basis = (
            f"Six sites at a {site_rating:.2f} MW DC sizing proxy. Apply the radial USD 8m/site base plus "
            "USD 1m/MW above 10 MW, multiplied by 0.85 / 1.10 / 1.40 for revised conversion duty. "
            f"For {track_km:g} track-km, use the radial USD 1.05m/track-km and allocate 25% / 40% / 60% "
            f"to conductor capacity. That share scales by {conductance_factor:.2f} times the installed path count, "
            "using resistance ratios as a material proxy. Half of the remaining price scales with path count "
            "and half is shared. Price each outgoing breaker and tie at the radial USD 50k times "
            "1 / 1.4 / 2 and each additional branch point at 10% / 20% / 40% of that USD 50k. "
            "Apply 1 / 1.5 / 2.5 to the local site works offsite rate per new site for uncertainty in utility concentration."
        )
        yield _lot(
            lot_id, name, feeders, "DC source groups", amounts, basis=basis,
            exclusions="Price bound for this topology only. On-site control and earthing are requested inside plant and installation prices. Programme commissioning, major utility reinforcement, taxes and finance remain separate.",
            deliverables="Quote conversions, positive/return paths, protection, earthing, owner/supplier testing, AC tie-ins, annual upkeep and renewal years. Return approved capacity, hot-circuit and isolation evidence before selection.",
            sources=(key, "feeder-options", "radial-return", "opening", "system-rates", "local-works"),
            design_id=option["design_id"], outgoing_circuits=option["outgoing_circuits"],
            midpoint_ties=option["midpoint_ties"], protected_track_km=track_km,
            branch_disconnect_and_test_points=branch_ends, site_peak_dc_mw_proxy=site_rating,
            direct_breakdown_by_scenario_usd=funding_breakdown,
            group="alternative-budget-proxy", evidence_class="topology-scaled-budget-proxy",
            alternative_to_lot_ids=["traction-line", "traction-sites", "offsite-feed"],
        )
        yield _lot(
            lot_id + "-upkeep", name + " rail-side upkeep sensitivity", feeders, "DC source groups",
            [round((gross - funding_breakdown[case]["offsite utility tie-ins"]) * share, -3)
             for gross, case, share in zip(amounts, CASES, (0.005, 0.01, 0.02), strict=True)],
            basis="Apply published 0.5% / 1% / 2% upkeep fractions to estimated railway-side capital. This applies the fractions to the whole six-site plant and line price, with no assumed shared maintenance credit.",
            exclusions="Energy, separate utility service charges, scheduled renewals and shared basic maintenance. Known boundaries differ from the radial incremental upkeep.",
            deliverables="Return full annual and unit upkeep rates, common-scope deductions, spares and maintenance windows before using this sensitivity in an alternative lifecycle comparison.",
            sources=(key, "local-works", "system-rates"), design_id=option["design_id"],
            group="alternative-budget-proxy", evidence_class="topology-scaled-budget-proxy",
            price_period="annual", alternative_to_lot_ids=["opex-feeder"],
        )


def _remaining_gaps(data):
    opening, cash = data["opening"], data["cash"]
    site_cases = opening["iraq_site_estimate"]["scenarios"]
    capital = opening["scopes_usd_m"]
    grid = (capital["Grid supply sites"] + capital["Protected conductor and switchgear"]) * MILLION
    extra_civil = [
        sum(site_cases[case]["items"][name]["direct_usd_m"] for name in (
            "Additional foundation shafts under standard caps", "Exceptional road-crossing works",
            "Landside airport forecourt and security interface"
        )) * MILLION for case in CASES
    ]
    loan_share = sum(row["borrowing"] for row in cash["annual_cash"]) / cash["priced_capital_usd_m"]
    for lot_id, description, quantity, unit, amounts, basis, deliverables, price_period, overlap in (
        ("additional-grid-operations", "Additional recurring site and protection work",
         opening["bundle"]["grid_sites"], "DC source groups",
         [grid * share for share in (0.002, 0.005, 0.01)],
         "Illustrate a 0.2% / 0.5% / 1% annual exposure on the priced radial sites and switchgear. This is a sensitivity for ancillary recurring services above the known operating allowance.",
         "Obtain recurring utility, site and tie-protection prices outside existing energy and maintenance allowances.",
         "annual", ["opex-power", "opex-feeder", "opex-other"]),
        ("approvals-exceptional-works", "Residual exceptional works and owner approvals",
         1, "opening programme", [amount * share for amount, share in zip(extra_civil, (0.1, 0.25, 0.5), strict=True)],
         "Sensitivity of 10% / 25% / 50% of the existing extra shaft, major road crossing and forecourt scopes. It represents residual complexity risk pending survey and does not estimate authority fees.",
         "Survey approval conditions and exceptional works, then return the scope and price with an accountable party.",
         "one-time", ["programme-allowance", "extra-foundation", "exceptional-crossings", "airport-forecourt"]),
        ("lender-fee-sensitivity", "Illustrative financing arrangement costs",
         1, "opening programme",
         [site_cases[case]["capital_usd_m"] * MILLION * loan_share * share
          for case, share in zip(CASES, (0.0025, 0.005, 0.01), strict=True)],
         "Illustrate a 0.25% / 0.5% / 1% one-time arrangement cost on the modelled borrowing share of each priced capital scenario. No lender offer is assumed.",
         "Obtain comparable term sheets including arrangement, lender due diligence, undrawn facility fees and funding conditions.",
         "one-time", []),
        ("tax-and-duties", "Tax and customs duty treatment",
         1, "opening programme", None,
         "Separate owner tax/customs determination needed by package, origin, declaration and contracting structure.",
         "Return applicable tax and duty basis and dated rulings or fiscal agreements for the buyer and supplier.",
         "one-time", []),
    ):
        yield _lot(
            lot_id, description, quantity, unit,
            None if amounts is None else [round(amount, -3) for amount in amounts],
            basis=basis, exclusions="Priced construction allowances, recurring base operations and modelled debt payments where applicable.",
            deliverables=deliverables, sources=("cash", "opening"),
            evidence_class="buyer-evidence-required" if amounts is None else "contingent-exposure-sensitivity",
            price_period=price_period, overlaps_lot_ids=overlap,
        )


def _totals(lots, opening):
    groups = {}
    for group, description in ADDITIVE_GROUPS.items():
        selected = [row for row in lots if row["inclusion_group"] == group]
        groups[group] = {
            "description": description, "lot_ids": [row["lot_id"] for row in selected],
            "price_period": selected[0]["price_period"],
            **{f"{case}_usd": sum(row[f"{case}_usd"] for row in selected) for case in CASES},
        }
    capital = {}
    for case, ops_case in zip(CASES, ("upside", "central", "downside"), strict=True):
        key = f"{case}_usd"
        capital[key] = groups["opening-direct"][key] + groups["opening-allowances"][key]
        if not isclose(capital[key], opening["iraq_site_estimate"]["scenarios"][case]["capital_usd_m"] * MILLION):
            raise ValueError("Sourcing direct costs and owner allowances do not reconcile to the priced opening")
        if not isclose(groups["first-full-year-operations"][key],
                       opening["iraq_operations"]["cases"][ops_case]["opex_usd_m"] * MILLION):
            raise ValueError("Sourcing annual costs do not reconcile to the priced operations")
    return groups, capital


def estimate_lots(packet_path=PACKET):
    """Return reproducible, source-linked planning totals, alternatives and supplier enquiries."""
    data, sources = _load(packet_path)
    sources.update(_external_sources(data))
    opening, mechanical = data["opening"], data["mechanical"]
    owner_rows = list(_site_and_owner_lots(data))
    owner_by_id = {row["lot_id"]: row for row in owner_rows}
    lots = [
        *_opening_lots(data), *owner_rows, *_operations_lots(data),
        *_enquiry_lots(data, sources, owner_by_id), *_pilot_lots(data),
        *_feeder_alternatives(data), *_remaining_gaps(data),
    ]
    groups, capital = _totals(lots, opening)
    result = {
        "schema": "baghdad-airport-sourcing-estimates/1",
        "candidate_id": opening["candidate_id"], "opening_evaluation_id": opening["evaluation_id"],
        "parent_candidate_id": mechanical["parent_candidate_id"], "network_parent_candidate_id": opening["parent"],
        "frame_revision": mechanical["frame_revision"], "mechanical_evaluation_id": mechanical["evaluation_id"],
        "opening_packet_evaluation_id": data["manifest"]["evaluation_id"],
        "commercial_evaluation_id": data["cash"]["evaluation_id"],
        "citywide_selection_id": data["decision-register"]["network_selection_id"],
        "estimate_date": DATE, "price_basis": PRICE_BASIS,
        "amount_semantics": "Extended lot totals. Annual prices cover one full operating year. Scheduled prices apply once in the indicated operating year. Null prices and quantities require buyer or supplier evidence.",
        "scenario_semantics": "Published opening ranges vary local works while holding a common direct reference for other scopes. Single-point allowances carry equal endpoints. Comparator and owner allocations are sensitivities outside the additive subtotals.",
        "reproducibility": "Read named data members of the published packet, verify their manifest checksums and design bindings, and apply source-linked allowances. External comparator observations are recorded with their published terms for offline reproduction.",
        "reference_boundary": "Independent Airport research opening with six-car powered-wheel trains and protected conductor. The project retains its six-car passive-wheel development reference and its separately named crowd and capacity controls.",
        "physical_acceptance": "open", "authorised_for_purchase": False,
        "funded_opening_capital_usd": None, "complete_opening_cost_usd": None,
        "opening_date": None,
        "physical_obligations_open": [
            "Survey, utility access, ground conditions, civil detailing, staged erection and accessible egress",
            "Signed installed masses, joint fatigue, fitted doors, brake performance, rescue and maintainability",
            "Measured hot duty, isolation, breaker discrimination, ATP/ATO interlocks and witnessed integrated trials",
            "Authority review, accepted commercial scope, appropriated funding and operating authorisation",
        ],
        "subtotal_opening_priced_allowances": capital, "additive_groups": groups,
        "sources": sources, "lots": lots,
    }
    result["evaluation_id"] = _id(result)
    return result
