"""Detailed public city brief from current maglev quantities and declared scope."""
from pathlib import Path
from . import affordability

BENEFITS = (
    ('Affordable reach', 'Compact repeated elevated beams, straight demand-led tangents and independent fixed lines with passenger transfers.', 'Compare complete CAPEX per route km and residents served; survey access, rights, ground and crossings.'),
    ('Simpler rolling stock', 'Station/located-booster LSMs replace onboard main traction motors and inverters; passive ferrite bias with active support remains.', 'Price retained coils, drives, sensing, braking, cooling, batteries, doors and HVAC; measure mass, energy and maintenance.'),
    ('Station-led GOA4 dispatch', 'Prepare receiving resources, prove doors/platform safe, commit launch, verify full-tail clearance, then consider the following departure.', 'Retain separation, stopping authority, receiving readiness, intrusion detection, integrity, protection and degraded recovery.'),
    ('Domestic productive capacity', 'Local precast units, GFRP bodies, steel carriers, winding cassettes, wiring, Rust integration and serial QA.', 'Audit imported raw materials, semiconductors and machine tools; count domestic value added rather than a local supplier address.'),
    ('Lower operating burden', 'Aim for less contact wear, fewer propulsion components per moving vehicle and repeatable wayside maintenance.', 'Include support power, launch losses, staff across shifts, rescue, maintenance, renewals and availability; no automatic saving percentage.'),
    ('Manageable repayment', 'Phase useful corridors; minimise whole-life public cash and foreign-currency borrowing alongside construction cost.', 'Separate resource cost, borrower cash, imported procurement and debt currency; demonstrate affordable annual funding before expansion.'),
    ('Open and repairable systems', 'Published hardware/process quantities, reproducible Rust tests, interchangeable interfaces and local tooling skills.', 'Qualify interfaces, independent assurance, spares and second sources; software licences alone do not qualify a train.'),
)


def usp_markdown():
    return ['## Why this architecture', '',
        '**The main proposition is useful city-wide reach with less construction capital, operating expenditure and long-term debt repayment.** PM-maglev station-launched monorail is the means being investigated. Affordability and domestic capability must be demonstrated at equal passenger service.', '',
        '| Intended advantage | Design mechanism | Evidence and cost test |', '|---|---|---|',
        *['| '+' | '.join(row)+' |' for row in BENEFITS], '']


def dispatch_markdown():
    return ['## Station-led GOA4 operation', '',
        'Normal operation centres on the station: reserve a protected receiving path/berth, prove vehicle support and services ready, prove doors/platform safe, prepare and commit the finite powered launch, monitor coast/booster/arrival, then release each resource with valid train-identity and full-consist clearance evidence. A leading train leaving a station can make its berth available to the next train once its entire tail is proved clear and the following movement has protected authority. A launch command or elapsed timer alone does not release occupancy.', '',
        'Fixed lines eliminate mainline route-switch choices. Wayside launch/receive equipment concentrates primary propulsion and dispatch infrastructure at known sites. Independent onboard support/guidance current control and protection continue during coasting. Receiving plant must remain protected after launch; a fault cannot be resolved by simply cancelling a coasting train.', '',
        'Current city fleet/capacity calculations retain exclusive whole-leg reservation. The separate progressive-departure Rust candidate tests release behind a verified full tail, finite stopping envelopes and faults at180s headway. Local results have not qualified route-wide distributed detectors, cross-controller authority, degraded recovery or a city timetable. Driverless/GOA4 is the operating target, without operational authorisation or an assumed zero staff budget. [ORR unattended-operation principles](https://www.orr.gov.uk/sites/default/files/2024-07/railway-safety-principles-factors-for-safe-operation-of-goa4-uto.pdf) are a design reference for departure, passenger protection and degraded operation; they are not Iraqi operational approval.', '']


def frontdoor(report, design):
    t, s = report['totals'], report['affordability']
    operation = s['service']
    population = design['city'].get('population')
    rows = [f"# {report['name']} — PM-maglev station-launched monorail", '',
        f"**Country:** {design['city']['country']} · **Retained population input:** {population:,}" if population else f"**Country:** {design['city']['country']}", '',
        '**Design objective: broad urban access with low CAPEX, low OPEX and affordable debt repayment, while building domestic manufacturing and maintenance capacity.**', '',
        '![Current geographic network proposal](engineering/maglev/network.svg)', '',
        'This brief restores network, service, energy, funding and local-production detail for the current PM-maglev city inputs. Old wheel/rail fleet, coverage, energy and savings figures are not transferred. Physical and manufacturing acceptance remain open.', '',
        '| City planning measure | Current result |', '|---|---:|',
        f"| Fixed lines / mapped transfer junctions | {t['lines']} / {len(design.get('interchanges', []))} |",
        f"| Measured corridor route length | {s['route_km']:,.1f} km, two directional guideways |",
        f"| Proposed mainline line-stop packages | {t['station_records']} |",
        f"| Original station access records retained | {t['retained_station_records']} |",
        f"| Additional terminal motor zones / midway boosters | {t['added_terminal_service_zones']} / {t['powered_top_up_zones']} |",
        f"| Provisional fleet / cars | {t['trainsets']} / {t['cars']} |",
        f"| Equivalent scheduled train-km/day incl. loops | {operation['train_km_per_day']:,.0f} |",
        f"| Capacity-shortfall lines / transfer-spacing conflicts | {len(report['diagnostics']['unresolved_capacity_targets'])} / {t['transfer_spacing_conflicts']} |",
        '| Accepted engineering / physical releases | 0 |', '',
        'Line-stop packages count platforms on independent lines separately, not unique station buildings. Retained population is a planning input, not a measured catchment. Walking catchments, coverage, accessibility and paid-trip forecasts need regeneration against proposed sparse stops; no old coverage percentage is inherited.', '',
        '## Lines and service', '',
        '| Line | Route km | Stops | Cars / AW2 passengers | Peak / total trains | Headway s | AW2 passengers/h/direction | Service hours/day |',
        '|---|---:|---:|---:|---:|---:|---:|---:|']
    for line, duty in zip(report['lines'], operation['lines']):
        rows.append(f"| {line['line']} | {line.get('operational_route_length_m', line['retained_length_m'])/1000:,.1f} | {len(line['stations'])} | {line['formation']['cars']} / {line['formation']['aw2_passengers']} | {line['fleet']['peak']} / {line['fleet']['total']} | {line['selected_peak_headway_seconds']:g} | {line['aw2_capacity_per_direction_hour']:,.0f} | {duty['service_hours']:g} |")
    rows += ['', 'Headways are the current exclusive protected-resource comparison, not an accepted timetable. Urban stops target1.5km minimum/about2km average; classified suburban legs target4–5km with located acceleration where needed. Junctions transfer passengers between fixed lines. Close transfer nodes, terminal loops and capacity shortfalls remain explicit design work.', '']
    rows += usp_markdown()+affordability.markdown(report, prefix='engineering/maglev/')+dispatch_markdown()
    rows += ['## Energy and local delivery', '',
        'Energy uses daily service windows capped by current resource headways, hot full-load services duty, positive traction without regeneration credit, charging conversion, additional fixed-zone losses and station auxiliaries. Each affordability case exposes its tariff and loss assumptions. PV, storage, backup, depot movements and electrical diversity need site sizing; no zero-grid-import promise is inherited.', '',
        'Factory routes cover precast mould/cage/cast/cure/survey, GFRP layup/cure/hardpoints, iron/carrier fabrication, ferrite cartridge assembly, coil winding/impregnation, LSM cassette and power-cabinet assembly, software/IO tests and serial QA. Erection requires surveyed access, crane-at-radius checks, temporary stability, positively locked connections and final alignment. Quantities, equipment leads and process steps are in the manufacturing bill.', '',
        'Prioritise machinery verified as made in Britain when UK capability is needed, and maximise qualified local manufacture/repair in the destination country. Imported inputs, machine tools, electronics and specialist services need order-specific origin and price records. Local-content percentages, jobs and economic multipliers remain unquantified.', '',
        '## Phased realisation and evidence', '',
        'Start with a useful connected corridor, its depot/energy/rescue access and the factory capacity it needs. Prove that service before committing the next production batch. Phase boundaries, minimum useful network, demand, procurement, lender terms and annual affordability require a city business case; the five-year drawdown is a sensitivity rather than an approved programme.', '',
        '[Full city design, limitations and open gates](engineering/maglev/README.md) · [Structured service, CAPEX/OPEX and annual debt cash flows](engineering/maglev/summary.json) · [Manufacturing bills and UK equipment leads](engineering/maglev/manufacturing.json) · [Preserved geography and demand](engineering/maglev/retained-records.json)', '',
        'Regenerate with `./osr city '+report['city']+'`. The same detailed template and whole-life arithmetic apply across the catalogue.', '']
    return '\n'.join(rows)


def source_paths():
    return [Path(__file__), *affordability.source_paths()]
