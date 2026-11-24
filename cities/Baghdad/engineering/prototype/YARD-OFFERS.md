# Compare precast yard offers

Specify the number of accepted beams, the deadline and the workcells each bidder can staff. Each comparison reports the last beam’s release, the number of casting attempts and the total price if offered. The scope is casting and release of the issued 10 m box. A different girder needs newly timed operations, compatible beds and lifting checks. [Issued workcell and article identity](infrastructure/civil-resources.toml) · [Full factory and construction simulation](../simulation/production-guide.md)

For 80 accepted beams and an 11-day deadline, the issued example has three pour crews working seven usable hours of one eight-hour shift. One casting occupies a crew for two hours. Elapsed mould occupation includes that pour and continues off shift.

| Installed moulds | Occupied cycle | Last release after first pour | Meets deadline |
|---:|---:|---:|---|
| 8 | 24 h | 10 days 4 h | Yes |
| 8 | 48 h | 20 days 4 h | No |
| 16 | 48 h | 11 days 4 h | No |

The last offer restores the steady production rate. It still needs four additional hours to finish this order. A quote can be missing even when the entered workcell has sufficient capacity.

```sh
python3 -m cities.Baghdad.engineering.prototype.yard_offers --beams 80 --deadline-days 11
python3 -m cities.Baghdad.engineering.prototype.yard_offers --beams 80 --deadline-days 11 --moulds 16 --cycle-hours 48
```

Use repeated `--offer FILE` arguments to compare additional complete offers on the same quantity and deadline. The files use JSON. Omit `quote_usd` if the scope has no total price. Record a total covering the same quantity and services in every offer before comparing prices.

```json
{
  "name": "Illustrative second-shift offer",
  "moulds": 16,
  "cycle_hours": 48,
  "crews": 3,
  "shifts": 2,
  "shift_hours": 8,
  "availability": 0.875,
  "yield_rate": 0.8,
  "pour_hours": 2
}
```

The yield assumption gives a deterministic number of attempts. At 80% yield an order for 80 accepted units needs 100 casts. Each crew must fit its uninterrupted pour in the staffed portion of a shift. Shifts begin at the start of successive shift windows on each production day. Within each shift, available hours are grouped at the start. Several crews can pour concurrently into separate moulds. The supplier's occupied cycle runs from the start of pouring to release of the mould. Include stripping, testing and resetting in that duration. Confirm that the concrete achieves release strength on the offered cycle.

Use `--json` to inspect the first and last releases, occupied crew and mould time, peak use, source hashes and article identity. The schedule assumes raw materials, cages and prestress equipment are available at the start of each cast and the same calendar repeats daily. Holidays, competing orders, downstream storage, haul and erection require the wider programme and a supplier return. The issued factory files remain reproducible with their original assumptions.
