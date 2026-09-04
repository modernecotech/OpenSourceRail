# LM3 Portable Field-Rerailing Concept

Status: design-reference coordination basis. This is not a certified recovery
method, equipment selection, ground-bearing calculation, or authority to lift a
damaged vehicle.

## Design Decision

LM3 shall be designed for recovery by a small, specifically trained response
crew using portable rail-rated hydraulic equipment. Ordinary automotive
scissor jacks are outside the concept. The normal kit uses synchronized
telescopic cylinders, wide baseplates, keyed/tilting vehicle adapters,
mechanical cribbing, and a transverse rerailing bridge.

The controlled source assemblies are:

- `portable-field-rerailing-kit` for the recovery equipment envelope;
- `underframe-jacking-recovery-interface` for the installed J1--J4 pads,
  lifting-eye bosses, tow/rerailing lugs, and labels; and
- `civil-wayside-rerailing-access-interface` for optional hardstanding and
  equipment access at selected road-accessible response nodes.

All three use the same jack centres: X = +/-5,600 mm and Y = +/-1,180 mm from
the car centreline/top-of-rail coordinate system.

## Mass Sensitivity

The controlled planning tare remains 78,750 kg until supplier-frozen, detailed
CAD, and weighed evidence closes the mass budget. The lower cases below are
sensitivity studies, not released tare values.

| Case | Train tare | Mean car tare | Ideal four-point static reaction |
|---|---:|---:|---:|
| Controlled planning tare | 78,750 kg | 26,250 kg | 64.36 kN per point |
| 10% lower sensitivity | 70,875 kg | 23,625 kg | 57.92 kN per point |
| 20% lower sensitivity | 63,000 kg | 21,000 kg | 51.48 kN per point |

The current design-space search does not establish a large mass saving. Its
light-body/light-bogie candidate is 73.376 t before reserve, only 1.932 t below
the selected 75.308 t modeled subtotal. A materially lighter train therefore
requires a new structural/material design and full crash, fatigue, fire,
running-dynamics, braking, and manufacturability closure.

## Preliminary Load Screen

For coordination only, each permitted load case applies a 1.35 unequal-load
factor and a 1.50 action factor. The one-end case assigns 60% of the car tare to
the raised end to screen longitudinal centre-of-gravity movement.

| Load case | Active points | Supported tare | Required capacity per point | 200 kN equipment-envelope margin |
|---|---:|---:|---:|---:|
| Complete car with running gear retained | 4 | 100% | 130.32 kN | 69.68 kN |
| One end with its bogie retained | 2 | 60% | 156.39 kN | 43.61 kN |

Passing this screen only shows that a portable 200 kN cylinder class is worth
developing. It does not release the car structure, the jack, or the lift. The
final reactions shall use individual-car masses and centre-of-gravity
envelopes for every passenger/load condition, suspension state, bogie-retained
condition, tilt, damaged-point availability, and supplier load path.

## Recovery Modes

| Condition | Preferred response |
|---|---|
| Healthy wheels, train immobilized | Isolate, release/pipe the brake as designed, fit the recovery coupling, and tow or propel under the operating rulebook. Do not lift merely because traction power is unavailable. |
| One locked or locally damaged wheelset | Use the released wheel dolly/skate and rescue coupling if gauging, braking, axlebox condition, and infrastructure permit. |
| Upright, minor derailment with intact lift points | Stabilize and crib; lift one end or the complete car on a synchronized transverse pair/four-point set; translate on the rerailing bridge; lower to rail; inspect before any movement. |
| Pad inaccessible, unstable/rolled vehicle, structural damage, poor ground, bridge/tunnel constraint, or hazardous battery condition | Escalate to the specialist heavy-recovery plan and crane or alternative engineered method. The portable method is prohibited. |

## Equipment Envelope

- Four rail-rated telescopic cylinders, at least 200 kN rated capacity each and
  no more than 30 kg per cylinder envelope for two-person/manual team handling.
- Four wide-area baseplates/ground spreaders and four keyed, angular-tolerant
  adapters that positively locate on J1--J4.
- Two modular transverse rerailing bridges with locking traverse sleds.
- Mechanical cribbing and secondary retention. Hydraulic pressure is never the
  sole means of supporting a vehicle while personnel enter a hazard zone.
- A separately metered four-circuit pump/control unit allowing synchronized or
  deliberate individual correction from outside the exclusion zone.
- Hoses, rupture protection, gauges/load monitoring, lighting, bonding and
  isolation equipment, chocks, wheel dollies/skates, rescue coupler, and the
  controlled recovery manual.

Commercial technology demonstrates that portable equipment in this class is
feasible: LUKAS publishes a 24 kg internal rerailing jack with 204 kN lifting
force and transverse bridge systems; Holmatro publishes compact rerailing
cylinders with hose-rupture-controlled lowering. These are capability
references, not selected suppliers.

## Vehicle Detail Requirements

1. Prove complete-car and one-end lifting with running gear mechanically
   retained, including articulation anti-lift and service-loop conditions.
2. Keep J1--J4 visible and accessible after suspension collapse; provide
   removable skirt panels without personnel entering beneath an unsupported
   vehicle.
3. Key every portable adapter so it cannot be mistaken for a depot column head
   or applied to non-structural cladding.
4. Provide externally readable mass, centre-of-gravity range, permitted
   support combinations, isolation, brake-release, bogie-retention, and
   lifting diagrams at both car sides and in the digital recovery manual.
5. Keep the rescue coupler, tow lugs, brake connection, dead-battery controls,
   and HV isolation accessible after loss of normal auxiliary power.
6. Treat a missing/damaged required pad, lateral single-side lift, or work under
   hydraulic support without mechanical retention as a stop condition.

## Release Hold Points

1. Replace planning mass with weighed individual-car values and signed
   centre-of-gravity/load-condition envelopes.
2. Release underframe, articulation, bogie-retention and coupler calculations;
   weld/NDT schedules; adapter drawings; and pad proof loads.
3. Freeze a cylinder, bridge, pump, hose, control, cribbing and dolly supplier
   set with inspection and maintenance requirements.
4. Complete geotechnical/ground-bearing checks for designated access nodes and
   define the field method for non-designated locations.
5. Conduct no-load, representative ballast, asymmetric, loss-of-pressure,
   emergency-lowering, full-car, one-end and translate/lower trials.
6. Train and assess the recovery crew using the production vehicle, timed
   deployment, communications, exclusion-zone, battery and evidence-preservation
   procedures.
7. Issue vehicle-specific jacking/lifting diagrams and instructions before
   entry into service.

## Reference Requirements And Capability Examples

- [UK LOC&PAS NTSN, Issue 2 (May 2025)](https://assets.publishing.service.gov.uk/media/681488175966d01801999ec5/ntsn-rolling-stock-locomotive-and-passenger-issue-2-May-2025.pdf)
- [RSSB RIS-2780-RST Issue 1.1 — Rail Vehicle Structures](https://www.rssb.co.uk/standards-catalogue/CatalogueItem/RIS-2780-RST-Iss-1-1)
- [LUKAS HP 21 / 300 R rerailing jack](https://lukas.com/rerailing/en/products/rerailing-systems/217/hp-21/300r?c=374)
- [LUKAS rerailing systems](https://lukas.com/rerailing/en/products/rerailing-systems/)
- [Holmatro rerailing cylinders](https://www.holmatro.com/hydraulic-solutions/rerailing-vehicle-recovery/lifting-sliding-components/hydraulic-cylinders/)

