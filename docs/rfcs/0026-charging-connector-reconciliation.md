# RFC 0026 — Automated Conductive Charging Interface

**Status:** Current
**Depends on:** [RFC 0010](0010-station-design-standard.md), [RFC 0021](0021-battery-traction.md)

## 1. Decision

The standard passenger interface is an automated side conductive contact fed
by the 500 kW station DC/DC cabinet. Up to two platform contacts share one
cabinet budget. Terminals use identical hardware with longer dwell.

Depot maintenance stalls use a separate low-C plug-in service connector for
balancing, diagnostics, and long holds. It is not a passenger-platform power
tier and does not define the train DC architecture.

## 2. Electrical interface

| Parameter | Reference |
|---|---:|
| Train voltage | 650–700 V nominal |
| Normal cabinet power | 500 kW total |
| Cabinet current ceiling | 825 A |
| Contacts per cabinet | 2, interlocked |
| Planning efficiency | 98% |
| Normal dwell transfer | approximately 8 kWh in 60 seconds |

Four-car high-throughput deployments use three complete
storage/cabinet/contact modules and six-car deployments use four. Aggregate
power is never represented as a different converter product.

## 3. Sequence

1. Train proves stopped, correctly aligned, braked, and movement-inhibited.
2. Wayside and train exchange identity, voltage, SOC, temperature, and charge
   limits over the safety-related control link.
3. Protective earth/bond, insulation, HVIL, and contact-clear checks pass.
4. The mechanism closes, weld detection and precharge complete, then the BMS
   permits current.
5. Either side can abort; current reaches zero before mechanical separation.
6. The mechanism proves stowed before movement authority can be released.

## 4. Mechanical and safety requirements

The interface is touch-safe when open, tolerant of the qualified alignment
envelope, protected against water/dust/debris, guarded from passengers, and
replaceable without civil reconstruction. Breakaway, welded-contact,
unexpected-voltage, comms-loss, train-movement, emergency-stop, and two-train
contention cases fail safe.

## 5. Acceptance

FAT and SAT cover voltage/current, insulation, earthing, temperature rise,
contact resistance, cycle endurance, alignment, contamination, ingress,
emergency isolation, aborted sequences, vehicle movement interlock,
simultaneous arrivals, cabinet outage, and rescue/recovery access.
