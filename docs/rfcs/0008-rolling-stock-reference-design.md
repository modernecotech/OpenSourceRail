# RFC 0008 — Rolling-Stock Reference Families

**Status:** Current
**Depends on:** [RFC 0020](0020-crashworthiness.md), [RFC 0021](0021-battery-traction.md), [RFC 0022](0022-bogie-traction-drive.md), [RFC 0023](0023-door-system-reference-design.md)

## 1. Common platform

Every OSR train family is assembled from self-contained, driverless car
modules. A car has one powered bogie, one trailer bogie, one 225 kWh gross /
180 kWh usable LFP pack, two motor/controller channels, direct-HV DC HVAC,
isolated low-voltage domains, and roof-PV MPPT.

The welded S355 underframe/spaceframe is the safety load path. Side and roof
weather skins use CNC-trimmed fiberglass modules on a common 1,000 mm
longitudinal pitch. Keyed hooks, captive over-centre clips, independent
anti-lift retainers, and dry EPDM seals attach them to the frame without a
production adhesive cure. The front/rear fiberglass shell remains
sacrificial over the steel crash structure.

## 2. Families

Canonical values live in `lib/templates/rolling-stock.toml`.

| Family | Cars | Gross / usable energy | Primary use |
|---|---:|---:|---|
| `urban-shuttle-1car` | 1 | 225 / 180 kWh | Low-demand shuttle |
| `tram-2car` | 2 | 450 / 360 kWh | Street/urban tram |
| `light-metro-3car` | 3 | 675 / 540 kWh | Promoted reference train |
| `metro-4car` | 4 | 900 / 720 kWh | Higher-capacity metro |
| `metro-6car` | 6 | 1,350 / 1,080 kWh | High-throughput metro |

The population-to-family mapping is a planning default. Platform, depot,
alignment, demand, evacuation, and operating studies may select another
family without changing its internal interfaces.

## 3. Promoted three-car train

| Parameter | Reference |
|---|---:|
| Cars | 3 repeated 16.5 m modules |
| Overall length | 49.5 m over couplers |
| Bogies | 3 powered + 3 trailer |
| Powered axles | 6 |
| Installed motor capability | 2.1 MW short duration |
| Operational traction cap | 1.8 MW |
| Passenger capacity | 360 AW2 / 480 AW3 |
| Seats | 60 longitudinal |
| Door arrangement | 2 pairs per side per car |
| Low-floor centre | approximately 10 m per car |
| Maximum axle load | 14 t at AW3 target |
| Maximum speed | 90 km/h |

The end saloons have panoramic glazing and no driving cab. T-OBS sensing,
lighting, washer/heater, and service access are mounted in identical end-cowl
modules.

## 4. Modular body rules

- 3-2-1 datum location with an asymmetric anti-reversal feature;
- 1,000 mm standard longitudinal mould/clip pitch, with shorter steel end-ring transitions outside the module grid;
- captive mechanical clips, anti-lift retention, and dry replaceable seals for side/roof modules;
- mechanical fail-safe retention;
- replaceable side, portal, skirt, ceiling, roof, and nose cassettes;
- molded empty ducts, drains, raceways, and mounting bosses; and
- no encapsulated cable, pipe, sensor, fan, filter, light, or connector.

For the promoted three-car family, 144 prefinished side/roof modules may be
installed on three painted and dimensionally released frames in one eight-hour
shift by six parallel two-person crews. This timing excludes doors, glazing,
systems, bogies, commissioning, homologation, and first-article testing.

## 5. Compatibility

The generator selects a track preset that lists the family in
`compatible_consists`, derives platform length from the consist, and rejects
incompatible station/track/family combinations. The source templates, rather
than prose copies, are authoritative for numerical compatibility values.

## 6. Release gates

Release requires supplier envelopes, mass closure, axle loads, kinematic
gauge, crash analysis, structural/fatigue FEA, weld and composite process
qualification, fire/smoke/toxicity evidence, door/HVAC/traction integration,
accessibility, EMC, maintainability, and first-article running evidence.
