# Trainset interiors — COTS equipment catalogue

The structural car body in
[`mechanical-py/src/osr_mech/rolling_stock/car_body.py`](../../mechanical-py/src/osr_mech/rolling_stock/car_body.py)
is a cabless box with door cutouts — a steel / aluminium shell
on a bogie. Everything a passenger sees and uses on top of that
shell is a **commodity item** bought from the open market:
windows, HVAC, seats, grab poles, LED lighting, passenger-
information screens, intercom.

This file is the builder's shopping list. The reference SKU for
each row is a worked example — any replacement that fits inside
the reserved envelope and the quoted power budget is a valid
substitute. The envelope is the contract; the SKU is a
suggestion.

Parametric source: [`cots_equipment.py`](../../mechanical-py/src/osr_mech/rolling_stock/cots_equipment.py).
STEP visualisation: [`car-body-17m-cots-fit-out.step`](../../mechanical-py/catalog/rolling_stock/car-body-17m-cots-fit-out.step)
(the plain body overlaid with every reserved envelope in its
catalogue colour).

![Car-body interior fit-out with COTS envelopes](../../docs/screenshots/trainset-interior-fit-out.png)

Rendered rear-quarter view: the structural shell is drawn translucent
so the reserved envelopes read through — HVAC on the roof, seats below
the windows, grab poles at the centre doors, PIS screens above the doors,
intercom at each end.

## Per-car fit-out BOM (17 m self-contained car, 1 door/side)

| Category | Reference SKU class | Qty / car | Unit mass kg | Unit power W | Mount pattern |
|---|---|---|---|---|---|
| Side glazing | Laminated 8+1.52 PVB+8, Pilkington Optilam class | 4 | 25 | 0 | Bonded frame, Sikaflex 252 |
| Rooftop HVAC | 15 kW bus-HVAC — Sutrak CC 210 / Thermo King T-1080R / Hispacold Compact | 1 | 250 | 15 000 | 8× M10 on 1200 × 600 pitch |
| Ceiling lighting | Osram Ledvance T5-equivalent, 15 W/m @ 24 VDC | 2 strips (17 m each) | 35 | 255 | M6 clips at 600 mm pitch |
| PIS screen | 21.5" industrial LCD — Advantech OSD-215 / Lilliput FA1200-NP | 2 | 6 | 30 | VESA 200 × 100, 4× M4 |
| Longitudinal seat | Kiel Avant Metro / Grammer Ipano, textile upholstery | 4 | 25 | 0 | 4× M10 on 800 × 300 base frame |
| Grab pole | Stainless 304, Ø35 × 2.5 wall, satin | 2 | 8 | 0 | Flanged floor + ceiling, 3× M8 |
| Emergency intercom | Zenitel Vingtor-Stentofon TMIS-2, IP-SIP | 2 | 3.5 | 10 | Recessed 250 × 150 cutout |

**Totals (per 17 m car): ~555 kg interior fit-out, ~15.4 kW
active electrical load.** The HVAC unit dominates; changing consist
length scales by adding the same fitted car module.

(Quantities are from the parametric BOM in
`cots_equipment.bom_per_car()`. All current families use the same
one-centre-door car module; a future dwell-driven variant can still
increase `doors_per_side` and the quantities will scale.)

## Per-trainset rollup

| Family | Cars | Fit-out mass kg | Fit-out active load kW |
|---|---|---|---|
| tram-2car | 2 | ~1 110 | ~31 |
| light-metro-3car | 3 | ~1 670 | ~46 |
| metro-4car | 4 | ~2 220 | ~61 |
| metro-6car | 6 | ~3 330 | ~92 |

The HVAC line dominates both. These totals feed the auxiliary-
converter sizing in [RFC 0008 §3.5](../../docs/rfcs/0008-rolling-stock-reference-design.md)
and the consist-mass budget in §3.4.

## Wiring + services

All COTS interior equipment runs off three low-voltage buses
fed from the auxiliary converter:

- **400 VAC 3-phase** — HVAC only. 30 A breaker per car.
- **24 VDC** — lighting, PIS screens, intercom, grab-pole lit
  handles (if equipped). 60 A breaker per car.
- **Ethernet 1000BASE-T** — PIS screens (Cat 6 to each LCD),
  intercom (IP-SIP). Runs on the TSN car-bus.

None of this is safety-rated. The SIL-4 chain (ATP, brake,
obstacle-detect, door interlock) runs on the independent TCN
bus described in [RFC 0005](../../docs/rfcs/0005-sbc-software-architecture.md)
and does not depend on — and is not affected by — any COTS
interior component.

## Installation order

1. **Shell first** — car body exits the fab with door cutouts
   already machined, window apertures already ground flush for
   bonding, and a pre-installed ceiling channel for the
   lighting clips. Don't skip the ceiling channel; retrofitting
   it after the HVAC goes on the roof is painful.
2. **HVAC** before ceiling lining — the HVAC duct trunks feed
   through a roof penetration plate bolted on the bench, then
   lined over.
3. **Windows** — bond in with Sikaflex 252 at ambient > 5 °C.
   48 h cure before first pressure / weather test.
4. **Interior fit-out** — lighting strips, grab poles, seats,
   PIS screens, intercom. All of these mount to pre-tapped
   inserts on the body shell + ceiling channel. No welding
   inside the passenger envelope.
5. **Commissioning** — power up the 24 VDC + 400 VAC buses,
   verify screens enumerate on the TSN car-bus, run the HVAC
   self-test, open + close every door through the interlock,
   verify emergency intercom routes to the OCC.

## Swapping vendors

To swap any row — e.g., drop Sutrak HVAC for Hispacold:

1. Check the replacement's envelope is ≤ `length_mm × width_mm × height_mm`
   in [`cots_equipment.py`](../../mechanical-py/src/osr_mech/rolling_stock/cots_equipment.py).
2. Check the replacement's mass is ≤ the published row + 20 %
   (the body sub-frame is rated to that margin).
3. Check the replacement's power draw is ≤ the published row
   (the auxiliary converter is sized around the published
   totals).
4. Check the mount pattern matches, *or* add a transition
   plate. Transition plates are fine — they weigh a few kg
   and don't affect the envelope.
5. Update the SKU reference line in `CATALOGUE` + regenerate
   the STEP via `python3 -m osr_mech.catalog`.

No other code changes. The car body's reserved volume + the
trainset mass / power budget are what matter; the specific
vendor is interchangeable.
