# RFC 0021 — Battery Traction Architecture

**Status:** Draft — catenary-free battery-electric-only, under-seat pack packaging
**Date:** 2026-04-24
**Depends on:** [RFC 0002 Energy Sizing](0002-energy-sizing.md), [RFC 0008 Rolling-Stock Reference Design](0008-rolling-stock-reference-design.md), [RFC 0014 Depot Design Standard](0014-depot-design-standard.md)

## 1. Summary

Every OSR trainset is a **battery-electric multiple unit (BEMU) —
without the catenary option**. This distinguishes it from the
Stadler FLIRT Akku (which carries a pantograph for AC charging on
electrified sections), from the Alstom Coradia Stream H (which is
hydrogen-fuel-cell plus battery), and from conventional metro stock
(which runs on third rail or overhead contact line).

OSR trainsets:

- Draw all traction energy from on-board **sodium-ion (Na-ion)
  batteries** — the primary chemistry per [RFC 0008 §3.2](0008-rolling-stock-reference-design.md)
  — with **lithium-iron-phosphate (LFP)** as the drop-in
  alternative for operators with established LFP supply chains or
  spares. Both chemistries fit the same under-seat module envelope
  (§5).
- Charge at passenger stations during the normal dwell. The station
  charger is fed by canopy solar PV plus a stationary battery buffer;
  depots provide overnight, balancing, and maintenance charging.
- Capture regenerative-braking energy back into the same pack
  (no brake resistors burning it off).
- Are fed by **station + depot solar-PV canopies** via the grid or
  a behind-the-meter battery (the wayside half of the energy
  story — see [RFC 0002](0002-energy-sizing.md)).

This RFC fixes:

1. The packaging (§5 — under the seats, not rooftop or deep underfloor).
2. The energy capacity targets per consist family (§4).
3. The charging interface (§6).
4. The thermal-management strategy for 50 °C ambient (§7).
5. The safety case (§8 — thermal runaway, crashworthiness, service
   fire).

## 2. Why battery-only (no catenary)

Catenary adds three large sources of complexity that a developing-
nation deployment should not have to import:

| Catenary system | Cost | OSR avoids |
|---|---|---|
| Overhead contact line + support masts + tensioning | €400 k – €1 M / km | Nothing to build |
| Traction substations every 3–5 km + HV grid interconnect | €2–5 M / substation | Smaller + cheaper depot-side interconnect only |
| Ongoing maintenance (wire replacement, insulator cleaning, sectioning) | Recurring OPEX | Zero line maintenance |

Battery-only also removes the *legal* complexity of medium-voltage
AC distribution along the ROW — avoiding a whole tier of electrical
safety regulation in the host country.

The tradeoff is **range limited by pack size × route length**. §4
sizes the pack to carry about one route length plus reserve; routine
energy is replaced by 60-second station charging events at roughly
1 km stop spacing.

## 3. Non-goals

- **Not hydrogen fuel-cell.** Hydrogen supply chain + refuelling
  logistics are out of scope for a developing-nation urban-metro
  mission.
- **Not third-rail or catenary.** Explicitly rejected per §2.
- **Not sodium-nickel-chloride (ZEBRA-class) or lead-acid.**
  LFP + sodium-ion are the two chemistries in scope.

## 4. Capacity targets

Minimum usable energy per consist, sized for one route length plus
reserve, with routine energy replaced at station dwells. Assumes:

- ~3.0 kWh/car-km net traction + auxiliary draw for a 17 m OSR car
  at 1 km stop spacing, including regenerative braking and hot-climate
  HVAC.
- Max 20 % state-of-charge reserve (below which the vehicle
  self-limits speed until it reaches the nearest terminal).
- 30 min HVAC worst-case at 10 kW per car (50 °C ambient, full load).
- 500 kW to 1 MW station charger class. A 60 s dwell replaces
  8–17 kWh before charger losses, enough for several 1 km hops.

| Family | Reference route | Min usable energy | Per-car share |
|---|---|---|---|
| urban-shuttle-1car | ≤ 25–30 km route | 120 kWh | 120 kWh |
| tram-2car | ≤ 25–30 km route | 240 kWh | 120 kWh |
| light-metro-3car | ≤ 25–30 km route | 360 kWh | 120 kWh |
| metro-4car | ≤ 25–30 km route | 480 kWh | 120 kWh |
| metro-6car | ≤ 25–30 km route | 720 kWh | 120 kWh |

**Usable** excludes the 20 % reserve. The nameplate pack sizes
are 25 % larger to account for cycle-life degradation over
15 years at 2 cycles/day — so a 107 kWh-per-car usable figure
ships as ~150 kWh nameplate per car at depot commissioning.

Cell-to-pack density target: **220 Wh/L** (Na-ion, primary) /
**350 Wh/L** (LFP, alternative). §5 sizes the module envelope for
the less-dense Na-ion case so switching chemistries later doesn't
require a body redesign.

## 5. Packaging — under-seat modules

The traction pack lives under the longitudinal bench seats, split
into low modules along both sides of the saloon. The centre aisle and
large low-floor door zone remain clear.

```
                    ┌─────── door ────┬──────── door ──────┬────── door ─┐
     seat bench ──►│  SEAT           │  SEAT              │  SEAT       │
                   │  ─ ─ ─ ─ ─ ─ ─ ─│  ─ ─ ─ ─ ─ ─ ─ ─ ─│  ─ ─ ─ ─ ─ ─│
     battery  ──►  │ UNDER-SEAT PACK │ UNDER-SEAT PACK    │ UNDER-SEAT  │
     module        │ (~2 m × 0.55 m  │ (~2 m × 0.55 m     │ PACK        │
                   │   × 0.45 m)     │   × 0.45 m)        │             │
                   ├──────floor──────┼────────floor───────┼─────floor───┤
                   ▲ low-floor centre aisle and door zone, clear
```

Per 22 m car:

- **8 under-seat modules** (4 per side) totalling ~1 200 L of
  reserved envelope per car.
- Actual battery fills ~25–30 % of the envelope — the rest is
  cooling duct, structural framing, cell spacing, and access.
- Each pack is an independently-swappable module. Access from
  inside: lift the bench cushion → remove the pack top cover →
  lift the pack with integrated lifting-eye hooks. No crane.

### Why under-seat (vs. rooftop or deep underfloor)

| Criterion | Rooftop (Akku) | Deep underfloor | Under-seat (OSR) |
|---|---|---|---|
| Centre of gravity | High | Lowest | Low-medium |
| Solar gain at 50 °C ambient | Worst (direct sun on roof) | None (shaded) | Minimal (shaded by skirt + wall) |
| Thermal-runaway vent path | Up (clear of passengers) | Down (onto bogie / track) | Laterally out through side vent duct |
| Competes with other kit | Shares with HVAC + aux | Shares with traction inverter + brake + aux | Uses seat plinth volume |
| Maintenance access | Overhead crane or shed | Pit or side jack | Bench cushion, no crane |
| Charging-cable routing | Must come down from roof | Plug at side | Plug at side (natural) |
| Low-floor aisle | Preserved | Harder near bogies | Preserved (aisle and door zone are central, clear) |

Under-seat packaging keeps the mass low without putting high-voltage
boxes in the bogie swept envelope. It also makes the battery visible
to maintenance without pit access, which matters for small depots.

## 6. Charging interface

### 6.1 Depot charging (primary)

Every depot has one **plug-in fast-charger cabinet** per stabling
track. The charger is a 600 VDC, 350 A (210 kW) CCS2-class
industrial plug-in dock, wall-mounted at platform height adjacent
to the stall's stop block.

- Cable reach: 3 m flexible, counterweight-suspended.
- Connector: CCS2 Type 2 + DC coupler (EV-industry standard), one
  receptacle per car on the +Y side, 400 mm above rail head.
- Charge time to 80 % SoC: 30 min for a 3-car consist at 210 kW
  (×3 cars = 630 kW simultaneous across three receptacles).
- Depot-side supply: 11 kV MV ring, transformer to 600 VDC, UPS-
  backed for graceful shutdown on grid loss.

### 6.2 Passenger-station charging (normal service)

Every passenger station on a stop-spaced OSR route is provisioned
for automated conductive charging unless the energy model proves
it can be skipped. The nominal design point is:

- Stop spacing: ~1 km.
- Dwell: ~60 s.
- Train-side connector: side-pin or pantograph-down per
  [RFC 0026](0026-charging-connector-reconciliation.md).
- Charger power: 500 kW standard, 1 MW at terminals and high-load
  stations.
- Energy per 60 s dwell: ~8 kWh at 500 kW, ~17 kWh at 1 MW before
  losses.
- Station supply: solar-PV canopy + stationary Na-ion battery buffer,
  with grid-tie where available.

The station battery supplies the instantaneous charge pulse; the PV
array refills it through the day. This is why the onboard train pack
can be sized for one route length rather than a full operating day.

### 6.3 Not in scope

- Roof-pantograph + overhead contact charging (Stadler Akku's
  approach, and the TINA dual-mode tram). Pantograph-down charging
  pads are permitted only as discrete station chargers, not continuous
  catenary.
- Induction / wireless charging.
- Battery swapping (tried and abandoned in taxi / bus fleets).
- Hydrogen refuelling.

## 7. Thermal management

At 50 °C ambient (Samawah design envelope), Na-ion cell
temperature must stay below 65 °C and LFP cells below 55 °C to
preserve cycle life. Strategy:

1. **Passive:** each module is shaded by the longitudinal bench.
   No direct solar gain.
2. **Active:** refrigerant cold plate per module group, fed from the
   HVAC condenser loop. Cell temperature sensor per module; BMS
   (`osr-bms`) derates charge current above 50 °C cell.
3. **Runaway containment:** each module is a sealed aluminium
   enclosure with a weak-point vent on the outer body skin. If a
   module goes thermal, vent gases are steered laterally out into
   the trackside, not into the cabin.

Na-ion runs ~10 °C hotter than LFP with no cycle-life penalty —
one of the reasons it's the primary chemistry for OSR's 50 °C
design envelope.

## 8. Safety case

### 8.1 Electrical

- Battery pack MV side isolated from body + underframe by IEC
  61140 Class II insulation.
- Pre-charge resistor in the traction inverter (matches `osr-
  traction` control).
- Ground-fault monitor per car; a fault trips the main contactor
  within 200 ms.

### 8.2 Crashworthiness ([RFC 0020](0020-crashworthiness.md))

Under-seat modules sit above the floor and inboard of the skin +
livery band. In a side impact:

- The livery-band metalwork forms an intrusion-rated rub strake
  (150 kN/m² crush rating) outside the battery enclosure.
- The module enclosure is rated for 50 kJ side impact without cell
  breach.
- Crumple energy in Zones 1 + 2 ([RFC 0020 §5](0020-crashworthiness.md#5-three-zone-absorption-layout))
  stays unchanged — the forward crumple is in the sensor cowl +
  under-frame crumple, not the side wall.

### 8.3 Fire

- Pack enclosure material: EN 45545-2 HL2 R1.
- Vent-gas chemistry depends on cell choice: Na-ion thermal
  runaway produces some SO₂ (the more conservative fire case);
  LFP produces mainly CO and CO₂. Scrubber cartridges in the
  module vent stack are sized for the Na-ion case.
- `osr-fire-safety` monitors cell-side temperature; an alert
  triggers OCC remote-assist (RFC 0015 §5.3) and prepares an
  emergency egress at the nearest station.

## 9. Software interface

The pack exposes its state to the onboard stack via `osr-bms`:

- State of charge (0..1000 ppt).
- Min / max cell voltage (mV), cell-balance state.
- Pack temperature (worst cell).
- Available charge current (derated for temperature).
- Available discharge current (derated for SoC + temperature).

These feed `osr-traction` (to limit traction request),
`osr-ato` (for range prediction), and `osr-occ`'s dispatcher
console (for fleet-level SoC visibility).

## 10. Deployment checklist

- [ ] Select chemistry (Na-ion primary per RFC 0008; LFP if local
      supply chain is already LFP-flavoured).
- [ ] Size the per-car pack against §4 and the measured line
      profile (longer routes than Samawah need more).
- [ ] Commission station charging at the route stops required by
      the timetable energy model (§6.2) plus depot plug-in charging
      for overnight and maintenance balancing (§6.1).
- [ ] Wire depot substation to PV-canopy output + grid tie (§1,
      RFC 0002).
- [ ] Fire-authority sign-off on the vent geometry for the chosen
      chemistry.
- [ ] BMS end-to-end test against a reference discharge at 50 °C
      ambient.

## 11. Revision history

| Date | Version | Change |
|---|---|---|
| 2026-05-01 | v2 | Rationalised around self-contained cars: under-seat Na-ion packs, one-route onboard energy, and solar-buffered station charging at ~1 km stops. |
| 2026-04-24 | v1 | Initial draft. Side-wall strake packaging, depot-only charging, LFP + sodium-ion in scope, Akku-inspired without catenary. |
