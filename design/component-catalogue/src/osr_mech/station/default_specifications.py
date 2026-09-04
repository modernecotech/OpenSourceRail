"""Supplier-neutral reference defaults for open station product families.

Defaults make concept design, RFQs and cost comparison concrete.  They do not
replace site data, a selected supplier configuration or engineering release.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class DefaultProductSpecification:
    product_id: str
    default_name: str
    use_class: str
    parameters: tuple[str, ...]
    affordability_basis: str
    source_ids: tuple[str, ...]
    must_override_when: tuple[str, ...]


def reference_sources() -> dict[str, dict[str, str]]:
    """Primary references used as architecture anchors, not nominated makes."""

    return {
        "OSR-STATION": {
            "title": "OpenSourceRail station, energy, depot and turnout controlled design basis",
            "url": "../../../../docs/rfcs/0010-station-design-standard.md",
            "kind": "repository-controlled-design-basis",
            "retrieved": "2026-09-04",
        },
        "IEC-61215": {
            "title": "IEC 61215-2 terrestrial photovoltaic module design qualification",
            "url": "https://webstore.iec.ch/en/publication/24311",
            "kind": "official-standard",
            "retrieved": "2026-09-04",
        },
        "IEC-62446": {
            "title": "IEC 62446-1 PV system documentation, commissioning tests and inspection",
            "url": "https://webstore.iec.ch/en/publication/24057",
            "kind": "official-standard",
            "retrieved": "2026-09-04",
        },
        "TRINA-450": {
            "title": "Trina Solar Vertex S+ 450 W module public data sheet",
            "url": "https://static.trinasolar.com/sites/default/files/VertexS-450W.pdf",
            "kind": "manufacturer-architecture-anchor",
            "retrieved": "2026-09-04",
        },
        "ABB-TPSS": {
            "title": "ABB DC railway traction power switchgear and conversion portfolio",
            "url": "https://new.abb.com/medium-voltage/cs/rozvadece/rozvadece-pro-zeleznice-se-stejnosmernym-trakcnim-napajenim",
            "kind": "manufacturer-architecture-anchor",
            "retrieved": "2026-09-04",
        },
        "KONE-MRL": {
            "title": "KONE MonoSpace 500 machine-room-less lift planning guide",
            "url": "https://www.kone.co.uk/Images/8573_KONE-monospace%20500%20GBIR_tcm45-82369.pdf",
            "kind": "manufacturer-architecture-anchor",
            "retrieved": "2026-09-04",
        },
        "PRM-TSI": {
            "title": "Commission Regulation (EU) 1300/2014 accessibility TSI",
            "url": "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32014R1300",
            "kind": "official-regulation-reference",
            "retrieved": "2026-09-04",
        },
        "VOESTALPINE-TURNOUT": {
            "title": "voestalpine urban-rail turnout system portfolio",
            "url": "https://www.voestalpine.com/railway-systems/en/products/turnout-systems/turnouts/",
            "kind": "manufacturer-architecture-anchor",
            "retrieved": "2026-09-04",
        },
        "VOESTALPINE-ECOSTAR": {
            "title": "voestalpine ECOSTAR compact electro-hydraulic point machine",
            "url": "https://cdnstorevoestalpine.blob.core.windows.net/documents/659575/original/railwaysystems_factsheet_Point_Machine_with_External_Lock_ECOSTAR_en_070918.pdf",
            "kind": "manufacturer-architecture-anchor",
            "retrieved": "2026-09-04",
        },
        "AXIS-M11": {
            "title": "Axis M11 affordable outdoor network camera family",
            "url": "https://www.axis.com/products/axis-m11-series",
            "kind": "manufacturer-architecture-anchor",
            "retrieved": "2026-09-04",
        },
        "GUNNEBO-FL": {
            "title": "Gunnebo SpeedStile FL gate technical specification",
            "url": "https://www.gunneboentrancecontrol.com/wp-content/uploads/2024/07/Gunnebo-AE-specs_Speed-Gates-FLS_v2.pdf",
            "kind": "manufacturer-architecture-anchor",
            "retrieved": "2026-09-04",
        },
        "CATL-ENERONE": {
            "title": "CATL EnerOne modular outdoor liquid-cooled LFP storage system",
            "url": "https://www.catl.com/en/news/935.html",
            "kind": "manufacturer-architecture-anchor",
            "retrieved": "2026-09-04",
        },
        "DAIKIN-ROOFTOP": {
            "title": "Daikin UATYA packaged rooftop unit catalogue",
            "url": "https://catalogues.daikin.eu/flipbooks/EN/General_catalogue/06rooftop/index.html",
            "kind": "manufacturer-architecture-anchor",
            "retrieved": "2026-09-04",
        },
    }


def _default(
    product_id: str,
    default_name: str,
    use_class: str,
    parameters: tuple[str, ...],
    affordability_basis: str,
    source_ids: tuple[str, ...],
    must_override_when: tuple[str, ...],
) -> DefaultProductSpecification:
    return DefaultProductSpecification(
        product_id, default_name, use_class, parameters,
        affordability_basis, source_ids, must_override_when,
    )


def default_product_specifications() -> tuple[DefaultProductSpecification, ...]:
    """Return one practical reference default for every open product family."""

    supplier = "rfq-default-not-selected"
    preliminary = "preliminary-design-default-not-construction-release"
    return (
        _default(
            "STN-CNP-P030", "commodity mono-PERC/TOPCon modules on insulated standing-seam roof", supplier,
            ("6,000 x 4,200 x 55 mm bay cassette", "200 W/m2 gross design yield; about 5.0 kWp/bay", "20 kg/m2 maximum complete cassette mass", "1,000 VDC-rated string components", "IEC 61215/61730-qualified module; 450 W class reference", "40 mm insulated core; white underside; factory MC4-compatible leads"),
            "Uses high-volume framed modules and a repeated dry-fixed roof cassette rather than a bespoke BIPV laminate.",
            ("OSR-STATION", "IEC-61215", "TRINA-450"),
            ("site wind/snow/hail loads exceed qualified module values", "fire or roof warranty disallows the selected bond/rail system", "local module price or availability favours a different certified format"),
        ),
        _default(
            "STN-CNP-P040", "one independently isolated PV string group per platform", supplier,
            ("1,000 VDC equipment rating", "6 mm2 UV-resistant copper PV cable baseline", "lockable DC isolator and Type 2 DC surge protection", "one monitored combiner/downlink per platform", "string voltage kept within selected inverter/MPPT window at local minimum temperature", "IEC 62446-1 inspection, polarity, insulation and handover record"),
            "Standard string hardware and one downlink per platform minimize field joints and specialist site labour.",
            ("OSR-STATION", "IEC-62446"),
            ("cold-corrected open-circuit voltage exceeds equipment margin", "parallel-string current requires larger protection/cable", "lightning or utility study requires Type 1 protection"),
        ),
        _default(
            "STN-CNP-P050", "repeatable auxiliary PV roof bay", supplier,
            ("8,500 x 22,000 mm module planning grid", "187 m2 gross roof area", "31.8 kWp nominal after 15% packing allowance", "20 kg/m2 roof/PV cassette mass allowance", "3,850 mm minimum clear height", "dry-bolted panel rails and replaceable commodity PV modules"),
            "One repeated 187 m2 grid shares frames between bays and uses the same commodity PV family as platform canopies.",
            ("OSR-STATION", "IEC-61215", "TRINA-450"),
            ("site circulation or fire access cannot fit the module grid", "wind/snow/seismic calculation changes frame spacing", "local solar yield makes partial PV coverage preferable"),
        ),
        _default(
            "STN-CNP-P060", "galvanised bolted/welded S355 auxiliary Warren truss", preliminary,
            ("22,000 mm clear span planning envelope", "2,000 mm truss depth", "S355 steel baseline", "HSS 200 mm column and HSS 150 mm chord planning envelopes", "8,500 mm frame spacing", "hot-dip galvanised after fabrication; bolted site splices where transport requires"),
            "Common structural hollow sections, repeated jigs and shared N+1 frames support local fabrication and low part variety.",
            ("OSR-STATION",),
            ("signed structural model changes any member", "transport envelope requires additional splices", "corrosivity category requires a duplex coating system"),
        ),
        _default(
            "STN-CNP-P070", "reinforced-concrete pad with reusable anchor cage", preliminary,
            ("2.0 x 2.0 x 0.65 m pad allowance for estimating only", "C30/37 concrete and B500 reinforcement baseline", "100 kPa preliminary allowable bearing pressure", "four M24 cast-in anchors on removable steel template", "75 mm nominal soil-face cover", "top of pedestal kept 150 mm above finished drainage level"),
            "A simple square pad, common bar grades and reusable anchor template are normally cheaper than piles on competent ground.",
            ("OSR-STATION",),
            ("geotechnical report gives less than 100 kPa or settlement risk", "uplift/sliding/seismic calculation fails", "buried utilities, flood level or expansive/aggressive soil affects the location"),
        ),
        _default(
            "STN-CNP-P080", "modular auxiliary-canopy PV combiner groups", supplier,
            ("one independently isolated group per 10 or fewer roof modules", "1,000 VDC equipment rating", "Type 2 DC surge protection baseline", "string current monitoring at combiner", "lockable local isolation plus remote inverter trip", "IEC 62446-1 commissioning dossier"),
            "Repeating one protected group avoids a bespoke combiner for every station size and limits fault/maintenance isolation scope.",
            ("OSR-STATION", "IEC-62446"),
            ("selected module/inverter electrical window changes string length", "lightning study requires Type 1 SPD", "cable voltage-drop or fault study changes conductor size"),
        ),
        _default(
            "STN-CNP-P090", "gravity drainage, LPS and guarded maintenance kit", preliminary,
            ("200 mm minimum eaves gutter planning size", "DN150 downpipe at each low point and no more than one bay per outlet baseline", "600 mm clear anti-slip maintenance route", "1,100 mm guardrail where fall exposure remains", "LPS Class III planning basis with bonded metalwork", "removable debris baskets and rodding access at every outlet"),
            "Gravity drainage, standard pipe sizes and permanent simple access reduce pumps, bespoke parts and recurring cleaning labour.",
            ("OSR-STATION",),
            ("local design storm exceeds hydraulic capacity", "roof geometry creates additional low points", "lightning risk assessment changes LPS class", "fall-risk assessment permits or requires a different access system"),
        ),
        _default(
            "STN-MEP-P020", "400/230 V modular LV board with one-hour online UPS", supplier,
            ("400/230 V 3-phase 4-wire 50 Hz default", "25 kA minimum board short-circuit rating pending utility study", "20% spare ways and 25% spare load capacity", "10 kVA online double-conversion UPS starting point", "60 minutes autonomy for life-safety/control loads only", "TN-S downstream earthing with monitored surge protection"),
            "A standard modular IEC LV board and small centralized critical-load UPS avoid maintaining many proprietary batteries.",
            ("OSR-STATION",),
            ("utility voltage/frequency or fault level differs", "life-safety load schedule exceeds 8 kW", "local code requires a generator or different earthing arrangement"),
        ),
        _default(
            "STN-PAX-P030", "PoE fixed-camera, 100 V PA and SIP help-point platform kit", supplier,
            ("four 2 MP H.265 fixed cameras per 60 m platform starting layout", "outdoor devices IP66 and IK10; -30 to +55 degC baseline", "IEEE 802.3at PoE with 20% switch power reserve", "two weatherproof loudspeakers plus one help point per platform baseline", "managed gigabit fibre uplink with physically separate life-safety VLANs", "coverage and speech-intelligibility model governs final quantity"),
            "Fixed PoE cameras and standard IP networking are cheaper to buy, cable and replace than PTZ/proprietary field networks.",
            ("OSR-STATION", "AXIS-M11"),
            ("coverage model finds blind spots", "facial/incident evidential requirements need higher resolution", "PA is part of voice evacuation and must use the approved EN 54 system"),
        ),
        _default(
            "STN-PAX-P040", "compact bidirectional flap gate with one wide accessible lane", supplier,
            ("600 mm clear standard lane", "900 mm clear accessible lane minimum", "fail-safe open on loss of power or fire input", "contactless bank-card, account token and QR reader interfaces", "dry-contact/Ethernet controller interface", "indoor IP20 equipment only under weatherproof canopy; outdoor-rated gate otherwise"),
            "Uses a conventional compact speed-gate envelope and open reader interfaces instead of custom mechanical gates.",
            ("OSR-STATION", "PRM-TSI", "GUNNEBO-FL"),
            ("local accessibility rule requires a wider lane", "unpaid-area weather exposure requires outdoor equipment", "evacuation analysis prohibits barriers or demands more free-exit width"),
        ),
        _default(
            "STN-PAX-P050", "cashless outdoor ticket/validation terminal", supplier,
            ("15 inch sunlight-readable capacitive display baseline", "contactless EMV/account token and QR issuance/reading", "no cash module by default; staffed/offline exception process", "IP54 and IK10 minimum enclosure target", "230 VAC input with internal 15 minute orderly-shutdown reserve", "wheelchair reach and knee/toe clearance governed by local access code"),
            "Omitting cash acceptors, printers where e-ticketing permits, and proprietary fare media lowers purchase and field-maintenance cost.",
            ("OSR-STATION", "PRM-TSI"),
            ("cash acceptance is a legal or inclusion requirement", "fare policy requires a printed ticket", "solar gain, dust, rain or vandalism needs a higher enclosure rating"),
        ),
        _default(
            "STN-CHG-P010", "shared 500 kW modular bidirectional DC charger", supplier,
            ("500 kW continuous station cabinet", "650-700 VDC normal train connection", "825 A maximum equipment current", "1,000 VDC insulation/equipment class", "two mechanically separate platform contacts interlocked so total cabinet power remains 500 kW", "IP55 outdoor cabinet; liquid-cooled power modules at high ambient"),
            "One shared modular cabinet uses established DC power-stage building blocks and avoids duplicating 500 kW hardware per platform.",
            ("OSR-STATION", "ABB-TPSS"),
            ("timetable energy model needs simultaneous charging", "selected train voltage/current envelope changes", "utility/harmonic study or 50 degC duty requires derating/additional modules"),
        ),
        _default(
            "STN-CHG-P020", "prefabricated dry-type transformer/rectifier substation", supplier,
            ("11 kV 3-phase 50 Hz incoming planning default", "750 VDC nominal traction/energy bus", "12-pulse diode rectifier baseline", "catalogue ratings 800/1,000/1,500/2,000 kVA by archetype", "metal-enclosed MV, dry transformer, DC switchgear, protection and SCADA in one e-house", "20% physical spare feeder capacity; no installed redundant transformer unless RAM study requires it"),
            "A factory-integrated e-house and passive diode rectifier are widely used, locally installable and simpler than a bespoke building or active front end.",
            ("OSR-STATION", "ABB-TPSS"),
            ("utility supply voltage/fault level differs", "regeneration/export study requires active conversion", "RAM, fire or load-flow study requires N+1 capacity"),
        ),
        _default(
            "STN-ACC-P020", "machine-room-less through-car passenger lift core", supplier,
            ("1,150 kg / 15-person nominal capacity", "1.0 m/s nominal speed", "1,100 mm minimum clear door target", "through-car doors preferred where they remove wheelchair turning", "two-way alarm, fire recall and automatic rescue/backup lowering", "external weatherproof shaft/enclosure where not inside a conditioned concourse"),
            "A standard machine-room-less 1,150 kg catalogue lift avoids a plant room while supporting wheelchairs, attendants and luggage.",
            ("OSR-STATION", "KONE-MRL", "PRM-TSI"),
            ("local lift/access/fire code changes car or door dimensions", "travel or passenger demand needs higher speed/capacity", "flood, seismic or exposed climate conditions need a special package"),
        ),
        _default(
            "STN-ACC-P030", "simple weather-protected steel pedestrian bridge", preliminary,
            ("4,000 mm clear walking width planning default", "5,500 mm minimum rail clearance planning envelope pending infrastructure gauge", "5.0 kPa crowd live-load starting case", "two simply supported transportable spans preferred", "anti-slip drained deck and 1,400 mm high non-climbable side enclosure", "lift/stair cores structurally independent where practical"),
            "Straight repeated steel spans and independent vertical cores reduce bespoke geometry, erection possessions and future lift replacement risk.",
            ("OSR-STATION", "PRM-TSI"),
            ("railway gauge/electrification requires more clearance", "crowd/egress analysis changes width", "span, wind, seismic, impact or foundation design changes the structural system"),
        ),
        _default(
            "STN-TRK-P010", "60E1 1:9 fixed-frog turnout rail kit", preliminary,
            ("1,435 mm gauge", "60E1 rail family", "1:9 tangent; 27,000 mm overall planning length", "190 m nominal diverging radius", "7,800 mm switch blade and 4,200 mm crossing envelopes", "40 km/h maximum reverse-route planning speed"),
            "One standard-gauge 1:9 family covers terminal and depot low-speed moves with common spares and training.",
            ("OSR-STATION", "VOESTALPINE-TURNOUT"),
            ("wheel/rail study selects another profile", "required diverging speed exceeds 40 km/h", "supplier system geometry or slab-track interface differs"),
        ),
        _default(
            "STN-TRK-P020", "cast-manganese fixed crossing with external mechanical lock", supplier,
            ("fixed crossing for 40 km/h reverse-route duty", "cast manganese frog baseline", "adjustable check rails and replaceable wear components", "positive external blade lock independent of motor force", "one common stretcher/lock family across terminal and depot", "insulated joints omitted unless signalling design explicitly requires them"),
            "A fixed frog and common mechanical lock are lower-cost and simpler to maintain than a movable-point crossing at this speed.",
            ("OSR-STATION", "VOESTALPINE-TURNOUT"),
            ("RAM/wear analysis favours a different crossing", "axle load or wheel profile changes check-rail geometry", "signalling architecture requires insulated joints or another lock arrangement"),
        ),
        _default(
            "STN-TRK-P030", "42-position prestressed turnout bearer set", supplier,
            ("42 numbered sleeper/bearer positions per turnout", "prestressed concrete baseline with supplier-drilled inserts", "elastic rail fastening with replaceable pads/insulators", "galvanised slide chairs with low-friction replaceable plates", "deliver as sequenced packs matching erection plan", "same fastener family as plain line where technically compatible"),
            "Supplier-numbered concrete bearers and shared elastic fasteners reduce site drilling, inventory and installation error.",
            ("OSR-STATION", "VOESTALPINE-TURNOUT"),
            ("trackform requires steel or composite bearers", "supplier layout changes bearer count", "stray-current or vibration study changes pads/insulation"),
        ),
        _default(
            "STN-TRK-P040", "compact electro-hydraulic point machine with external lock", supplier,
            ("6 kN nominal and 12 kN peak operating-force requirement", "18 kN ultimate proof requirement", "3 second maximum normal throw", "integral hand-wind/manual release", "separate lock and dual end-position detection", "weatherproof low-profile assembly suitable for urban track"),
            "A proven compact point-machine architecture fits multiple turnout types and reduces bespoke mechanisms and maintenance burden.",
            ("OSR-STATION", "VOESTALPINE-ECOSTAR"),
            ("measured switch force exceeds duty", "interlocking safety case requires another actuator/lock architecture", "flood, sand, temperature or tunnel envelope exceeds qualification"),
        ),
        _default(
            "STN-TRK-P050", "two-channel fail-safe end-position detection kit", supplier,
            ("two electrically independent detector channels", "normal, reverse and neither/unknown states", "24 VDC field circuits with isolated safety inputs baseline", "IP67 junction box and halogen-free armoured home-run cable", "no software-only inference of blade position", "bench and installed route-lock proof for every turnout"),
            "Simple hardwired independent detectors keep the safety boundary inspectable and avoid an unnecessary proprietary fieldbus.",
            ("OSR-STATION", "VOESTALPINE-ECOSTAR"),
            ("interlocking interface voltage differs", "safety integrity allocation requires a certified fieldbus", "cable distance/EMC study changes transmission or protection"),
        ),
        _default(
            "STN-TRK-P060", "thermostatic resistance points-heating kit", supplier,
            ("3 kW installed heat per turnout baseline", "two or more replaceable heater strips", "rail-temperature plus precipitation enable logic", "IP67 local isolation/control cabinet", "30 mA personnel RCD only where permitted by railway earthing design; dedicated fault monitoring otherwise", "omit entirely in climates with no credible ice/snow case"),
            "Basic resistance strips are widely serviceable; climate gating avoids buying and energising heaters where they provide no benefit.",
            ("OSR-STATION",),
            ("climate study removes the ice case", "thermal test needs more/less power", "railway earthing and protection rules prohibit the baseline RCD arrangement"),
        ),
        _default(
            "STN-TRK-P070", "energy-absorbing terminal buffer stop and passive marker", supplier,
            ("friction/hydraulic energy-absorbing stop selected to site approach case", "10 km/h maximum design-impact starting case for restricted terminal track", "bright passive end marker with retroreflective face", "independent reinforced-concrete foundation allowance", "minimum 2,000 mm protected overrun/service zone behind stop for planning", "no reliance on buffer stop as normal stopping control"),
            "A proprietary tested buffer stop is safer and usually cheaper than locally designing impact hardware; only its foundation is localized.",
            ("OSR-STATION", "VOESTALPINE-TURNOUT"),
            ("signalling hazard analysis sets another impact speed", "train mass/coupler interface changes", "available overrun or foundation conditions change"),
        ),
        _default(
            "STN-DEP-P010", "compact main-heavy depot site shell", preliminary,
            ("8,000 m2 reference footprint", "1.0% minimum paved surface fall away from buildings", "separate clean stormwater and wash/contaminated drainage", "6.0 m two-way service road planning width", "2.4 m anti-climb perimeter fence with controlled vehicle/pedestrian gates", "100-year local storm plus authority climate allowance for concept drainage"),
            "A compact rectilinear site, gravity drainage and standard fencing minimize land, pumps and custom civil details.",
            ("OSR-STATION",),
            ("survey/ground/flood study changes levels or drainage", "fire access or swept-path study changes roads", "security or planning authority changes the boundary treatment"),
        ),
        _default(
            "STN-DEP-P020", "four-road 400 track-m inspection/stabling package", preliminary,
            ("400 track-m total across four reference roads", "60E1 rail and common elastic fastener baseline", "minimum 80 m useful clear length per road", "one drained wash road and one inspection/lift road", "1,200 mm minimum side walkway planning width", "low-speed 10 km/h depot operating limit"),
            "Four repeated roads match the base maintenance concurrency and reuse the line rail/fastener family.",
            ("OSR-STATION", "VOESTALPINE-TURNOUT"),
            ("fleet/concurrency plan requires more roads", "site geometry changes road length or throat", "maintenance equipment requires pits, embedded rail or different trackform"),
        ),
        _default(
            "STN-DEP-P030", "two common 1:9 depot-throat turnouts", preliminary,
            ("two turnout assemblies for four reference workshop roads", "same 60E1 1:9 geometry and spares as terminal", "shop-preassembled panels where transport permits", "10 km/h depot operating limit", "independent lock/detection proof before route use", "manual hand-wind and clipped/scotched degraded mode"),
            "Reusing the terminal turnout family avoids a depot-only geometry, spares stock and competence set.",
            ("OSR-STATION", "VOESTALPINE-TURNOUT"),
            ("yard layout needs another turnout count/tangent", "transport prevents panel delivery", "signalling or degraded-operation rules differ"),
        ),
        _default(
            "STN-DEP-P040", "150 kW outdoor plug-in charger per maintenance stall", supplier,
            ("four 150 kW charger/data docks in the reference depot", "650-700 VDC operating range", "250 A connector/cable continuous rating minimum", "IP55 charger and IP67 stowed connector target", "overhead retractable/suspended cable with mechanical strain relief", "Ethernet maintenance-data dock kept electrically isolated from HV"),
            "One modest modular charger per active bay supports 12-minute turnaround/overnight work without installing a 500 kW unit at every stall.",
            ("OSR-STATION", "ABB-TPSS"),
            ("maintenance timetable needs faster simultaneous charging", "selected connector or train voltage differs", "ambient/solar load causes supplier derating"),
        ),
        _default(
            "STN-DEP-P050", "600 kWp PV plus four modular 500 kWh outdoor LFP blocks", supplier,
            ("4,000 m2 PV canopy and 600 kWp nominal array", "2,000 kWh gross stationary LFP storage", "four independently isolatable 500 kWh blocks", "500 kW bidirectional PCS starting rating", "outdoor liquid-cooled containers/cabinets with off-gas detection and remote isolation", "6 m preliminary separation zone from occupied/control buildings pending fire strategy"),
            "Repeated outdoor LFP blocks can be procured competitively, phased and isolated individually; factory integration reduces site labour.",
            ("OSR-STATION", "CATL-ENERONE", "IEC-62446"),
            ("energy simulation changes capacity/power", "cell-to-pack fire evidence or authority changes separation/containment", "utility export/protection rules change PCS architecture"),
        ),
        _default(
            "STN-DEP-P060", "four-bay modular workshop with synchronized vehicle lift", supplier,
            ("1,800 m2 workshop reference envelope", "four concurrent inspection/maintenance bays", "40 t overhead crane", "40 t synchronized four-column vehicle lift minimum system SWL", "10 t minimum rated capacity per column with mechanical locks", "one bogie-change/extraction path, wheel lathe and recycling wash plant"),
            "A repeatable portal building and commercial synchronized columns avoid a bespoke buried lifting table while retaining full-car/bogie change capability.",
            ("OSR-STATION",),
            ("weighed car/recovery load case exceeds lift allowance", "supplier column reactions change foundations", "fleet maintenance plan removes/adds heavy equipment", "crane runway or building calculation changes geometry"),
        ),
        _default(
            "STN-DEP-P070", "separate cooled controls room with N+1 packaged DX", supplier,
            ("two independent 30 kW nominal packaged DX units", "one unit carries the 30 kW design sensible duty", "automatic duty/standby rotation and high-temperature alarm", "400/230 V modular LV, UPS, fire alarm, PoE CCTV/LAN and access control", "8 bar oil-free compressed-air ring baseline", "no shared return air with workshop or battery/charger compound"),
            "Two commodity packaged units provide maintainable N+1 cooling without a central chilled-water plant.",
            ("OSR-STATION", "DAIKIN-ROOFTOP", "AXIS-M11"),
            ("room heat-load test exceeds 30 kW", "maximum ambient exceeds selected unit envelope", "fire strategy changes room separation/ventilation", "tool air demand changes compressor/ring size"),
        ),
    )


def default_specification_payload(open_product_ids: set[str]) -> dict[str, object]:
    """Serialize and validate the default set against live open products."""

    rows = default_product_specifications()
    row_ids = [row.product_id for row in rows]
    sources = reference_sources()
    unknown_sources = sorted(
        {source for row in rows for source in row.source_ids} - set(sources)
    )
    validation = {
        "all_open_products_have_defaults": set(row_ids) == open_product_ids,
        "product_ids_unique": len(row_ids) == len(set(row_ids)),
        "all_defaults_have_parameters": all(row.parameters for row in rows),
        "all_defaults_have_override_triggers": all(row.must_override_when for row in rows),
        "all_source_ids_resolve": not unknown_sources,
    }
    if not all(validation.values()):
        raise ValueError(
            "station default specification validation failed: "
            f"{validation}; missing={sorted(open_product_ids - set(row_ids))}; "
            f"extra={sorted(set(row_ids) - open_product_ids)}; sources={unknown_sources}"
        )
    return {
        "schema": "org.opensourcerail.station-product-default-specifications.v1",
        "status": "recommended-reference-defaults-not-procurement-or-construction-release",
        "default_count": len(rows),
        "source_count": len(sources),
        "sources": sources,
        "defaults": [
            {key: list(value) if isinstance(value, tuple) else value for key, value in asdict(row).items()}
            for row in rows
        ],
        "validation": validation,
        "release_boundary": (
            "Defaults support concept design, RFQs and cost comparison. Exact supplier data, "
            "site survey, geotechnical/utility inputs, calculations, approvals and performed "
            "tests still govern fabrication, construction, energisation and operation."
        ),
    }


def render_default_specifications(payload: dict[str, object], titles: dict[str, str]) -> str:
    """Render the default set for engineering and procurement review."""

    lines = [
        "# Station open-product reference defaults",
        "",
        "**Status:** recommended concept/RFQ defaults; not a supplier selection or construction release.",
        "",
        "These values close avoidable ambiguity in the open product rows with common,",
        "serviceable configurations. A default remains subordinate to every listed",
        "override trigger and the factory/release evidence gate.",
        "",
        f"Coverage: **{payload['default_count']}** defaults for **{payload['default_count']}** open product families; **{payload['source_count']}** source anchors.",
    ]
    for row in payload["defaults"]:  # type: ignore[union-attr]
        lines.extend(
            [
                "",
                f"## `{row['product_id']}` — {titles[row['product_id']]}",
                "",
                f"Default: **{row['default_name']}**",
                "",
                f"Use class: `{row['use_class']}`",
                "",
                "Values:",
                "",
                *(f"- {value}" for value in row["parameters"]),
                "",
                f"Affordability: {row['affordability_basis']}",
                "",
                "Must override when:",
                "",
                *(f"- {value}" for value in row["must_override_when"]),
                "",
                "Sources: " + ", ".join(f"[`{source}`](#source-{source.lower()})" for source in row["source_ids"]) + ".",
            ]
        )
    lines.extend(["", "## Sources", ""])
    for source_id, source in payload["sources"].items():  # type: ignore[union-attr]
        lines.extend(
            [
                f"### Source `{source_id}`",
                "",
                f"[{source['title']}]({source['url']}) — `{source['kind']}`; checked {source['retrieved']}.",
                "",
            ]
        )
    lines.extend([f"Boundary: {payload['release_boundary']}", ""])
    return "\n".join(lines)
