# RFC 0029 — Maintenance Schedule System

**Status:** Draft — proposed
**Date:** 2026-06-12
**Depends on:** [RFC 0008 Rolling-Stock Reference Design](0008-rolling-stock-reference-design.md), [RFC 0009 Track Design Standard](0009-track-design-standard.md), [RFC 0010 Station Design Standard](0010-station-design-standard.md), [RFC 0011 Civil Infrastructure Design Standard](0011-civil-infrastructure-design-standard.md), [RFC 0013 Operations Rulebook](0013-operations-rulebook.md), [RFC 0014 Depot Design Standard](0014-depot-design-standard.md), [RFC 0016 Wayside Track Intrusion](0016-wayside-track-intrusion.md), [RFC 0021 Battery Traction](0021-battery-traction.md), [RFC 0028 Construction Quality Assurance System](0028-construction-quality-assurance.md)

## 1. Summary

OpenSourceRail commits to a **single maintenance schedule system** for
rolling stock, stations, track/civil works, structures, energy assets,
signalling/comms, depots, and the railway production plant.

The system has three layers:

1. **Baseline intervals** by asset class, stored in
   [`lib/templates/maintenance-schedule.toml`](../../lib/templates/maintenance-schedule.toml).
2. **Condition-based escalation** from telemetry, inspections, and
   defect reports.
3. **Work-order closeout** that proves the asset is safe to return to
   service.

Generated city READMEs render the baseline schedule with that city's
fleet, station, route-km, and train-km context.

## 2. Non-goals

- **Not a CMMS product choice.** A deployment may use open-source CMMS,
  a national operator system, or a simple database during pilot service.
- **Not a parts catalogue.** Spare parts lists live with the asset and
  BOM documents.
- **Not a replacement for inspections mandated by local law.** Local
  statutory inspections are additive.
- **Not a vendor maintenance contract.** OSR assumes the owner maintains
  the railway; outside specialists can support but do not own the
  maintenance evidence.

## 3. Asset Register

Every maintainable asset must have an id before revenue service:

| Asset class | Minimum id structure |
|---|---|
| Trainset | trainset id, car ids, bogie ids, battery pack ids, major module serials |
| Station | station id, platform ids, canopy/PV id, public systems, emergency equipment |
| Track section | line id, chainage range, civil class, drainage and fence assets |
| Switch/crossing | switch id, point machine id, detection channel ids |
| Structure | span id, pier id, bearing id, expansion joint id |
| Energy site | PV strings, BESS rack ids, charger ids, protection devices |
| Signalling/comms | W-SBC id, radio/cabinet ids, sensor ids, firmware baseline |
| Depot/plant | bay id, pit id, tool/fixture id, lathe/lift/calibration device id |

The construction QA system in RFC 0028 creates the starting asset
register. This RFC keeps it alive through operations.

## 4. Work-Order Rule

Every maintenance action produces a work order with:

- Asset id.
- Trigger: calendar, km, cycle count, telemetry, defect, event, or
  regulatory inspection.
- Task procedure/version.
- Findings and severity.
- Parts used and removed.
- Test/inspection evidence.
- Return-to-service authority.
- Next due date or next due km/cycle.

No asset returns to service after a red defect without a signed
return-to-service record.

## 5. Baseline Schedule

The baseline schedule is:

| Group | Cadence | Scope |
|---|---|---|
| Rolling stock | Daily / each depot return | Walk-around, wheel/tread visual, doors, HVAC, coupler face, saloon damage, emergency kit, fault-log download |
| Rolling stock | 7 days | Wheel wear, brake pads, BMS cell spread, harness chafe, roof/PV cleaner, door obstruction sensors |
| Rolling stock | 30 days | BMS deep scan, motor-bearing vibration, inverter thermal log, HVAC filters, PIS/CCTV, firmware inventory |
| Rolling stock | 150,000 km or wear limit | Wheel reprofiling |
| Rolling stock | 600,000 km | Bogie overhaul |
| Rolling stock | 10 years | Body/interior/HVAC/cable overhaul |
| Stations | Daily | Cleaning, lighting, platform edge, PA/PIS/fare equipment, CCTV, emergency equipment |
| Stations | 7 days | Canopy/fixings, drainage, accessibility path, charger cabinet visual, extinguishers, signage |
| Stations | 30 days | Emergency lighting, fire alarm, UPS, lift/escalator where fitted, access control, comms cabinets |
| Stations | 12 months | Structural survey, canopy PV fixings, drainage capacity, accessibility audit, passenger-flow review |
| Track/civil | 7 days | Track walk, fasteners, slab cracking, drainage, fencing, vegetation |
| Track/civil | 60-90 days | Geometry run and trend comparison |
| Switches/crossings | 30 days | Point closure, detection, lubrication, bolts, weld cracks, drive inspection |
| Structures | 12 months | Viaduct/bridge visual inspection, bearings, joints, parapets, walkways, drainage, scour |
| Energy | Daily remote | SCADA alarms, charger availability, SOC/temperature, PV yield anomaly, grid import/export |
| Energy | 30 days | Charger sample load test, BESS thermal inspection, PV soiling, cabinet seals, protection status |
| Energy | 12 months | Relay test, earthing resistance, emergency isolation drill, BESS capacity sample, PV insulation |
| Signalling/comms | Daily remote | OCC/W-SBC health, radio alarms, time sync, authentication failures, CCTV/fare/PIS fault queue |
| Signalling/comms | 30 days | Switch proof test, sensor calibration sample, comms cabinet inspection, backup link, UPS |
| Signalling/comms | 90 days | Firmware inventory, vulnerability review, backup restore, degraded-mode drill, simulator replay |
| Depot/production plant | 30-180 days | Tool calibration, lifting equipment, pits/stingers, wheel lathe, welding fixture survey |

The calendar intervals are the floor. Hot desert, monsoon, flood,
coastal corrosion, dust, high ridership, or poor grid quality can only
shorten intervals, never lengthen them without owner-engineer approval.

## 6. Condition-Based Escalation

Telemetry and inspection findings override the calendar:

| Condition | Response |
|---|---|
| Green | Continue normal service; next baseline interval applies |
| Amber | Schedule work within 7 days; asset may stay in service if risk assessment permits |
| Red | Hold asset out of service or isolate the affected section until rectified |
| Unknown on safety asset | Treat as red when the asset protects movement authority, intrusion, braking, switching, charging isolation, or emergency response |

Examples:

- Battery cell spread over amber limit schedules a 7-day intervention;
  red limit holds the trainset.
- Sustained intrusion-sensor `Unknown` holds or restricts the affected
  section per RFC 0016 and the operations rulebook.
- Track geometry trend that crosses amber schedules possession work;
  red geometry holds the track section.
- Charger insulation or earthing failure isolates that charger until
  re-tested.

## 7. Rolling-Stock Maintenance

Rolling-stock maintenance is depot-led:

- `main-heavy` performs daily, weekly, monthly, wheel reprofiling,
  bogie overhaul, body overhaul, and major component rebuild.
- `secondary-medium` performs daily, weekly, monthly light work and
  module swaps.
- `layup-minimal` performs visual checks and fault reporting only.

The maintenance reserve in
[`lib/templates/fleet-sizing.toml`](../../lib/templates/fleet-sizing.toml)
exists so scheduled work can happen without cancelling service.

## 8. Stations and Passenger Assets

Station maintenance covers public safety and revenue equipment:

- Platforms, tactile paving, ramps, edge markings, lighting, signage.
- Canopy, roof PV, drainage, gutters, fixings.
- PA, passenger information, CCTV, fare validators/gates, Wi-Fi where
  fitted.
- Fire extinguishers, emergency lighting, call points, first-aid kits.
- Lifts/escalators only where the station archetype requires them.

Station staff perform daily observations. Maintenance staff perform the
weekly/monthly technical checks. The owner engineer performs or accepts
the annual structural/accessibility condition report.

## 9. Track, Civil, and Structures

Maintenance of way covers:

- Track walks and defect classification.
- Geometry measurement and trend comparison.
- Switches and point machines.
- Drainage, culverts, vegetation, and fencing.
- Viaducts, bridges, bearings, expansion joints, parapets, walkways,
  and bridge scour.

Post-weather inspections are additional to the baseline schedule. Flood,
dust storm, heatwave, lightning, collision, derailment, trespass, or
reported structure strike triggers event-based inspection before normal
speed resumes.

## 10. Energy and Charging

Energy maintenance covers:

- PV strings and cleaning/soiling checks.
- Stationary storage, thermal management, racks, contactors, and BMS.
- Train chargers and charger rails/connectors.
- Protection relays, earthing, isolation, and grid/PPA interface.
- Daily SCADA review for yield, SOC, temperature, charger uptime, and
  grid import/export anomalies.

Energy defects can affect both service and safety. Charger faults may
reduce timetable capacity; earthing, isolation, or BESS thermal faults
hold the affected energy site.

## 11. Signalling, Comms, and Software

Systems maintenance covers:

- OCC health, dashboards, logs, backups, and time sync.
- W-SBCs, switches, sensors, cabinets, UPS, and comms links.
- Radio coverage and backup communications.
- CCTV, passenger information, fare systems, and platform systems.
- Firmware inventory, vulnerability review, restore drills, and
  simulator replay.

Software maintenance is not casual patching. Any firmware or safety
software change requires a versioned work order, rollback plan, replay
test, and updated configuration baseline.

## 12. Depot and Production Plant

Depot and plant maintenance covers:

- Pit tracks, stinger supply, isolation equipment, wash plant, stores,
  compressed air, cranes/lifts where fitted.
- Wheel lathe and measuring equipment.
- Welding fixtures, jigs, calibration tools, torque tools, test benches.
- Lifting equipment statutory inspection.
- Production plant fixtures and commissioning bay equipment.

Tool calibration defects can block new train acceptance and heavy
maintenance release. The production plant is therefore part of the
railway asset base, not a one-off construction convenience.

## 13. Samawah Application

For the current Samawah generated instance, the maintenance system
starts with:

- 96 trainsets: 86 peak-revenue, 7 planned spares, and 3 cold reserves;
  depot turnaround service uses peak-fleet surplus in off-peak windows.
- 31 stations.
- 58.4 route-km.
- 29,515 scheduled train-km/day before depot/deadhead factor.
- 29 station/depot energy sites plus the dedicated solar plant/PPA
  interface.

The daily service intensity makes train-km and telemetry-based triggers
as important as calendar triggers. The battery adequacy warning in the
Samawah README should also be tracked as a maintenance-risk item:
operating near reserve limits increases charger, battery, and timetable
discipline sensitivity.
