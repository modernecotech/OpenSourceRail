# Authority and stopping sensitivity on the corrected Airport alignment

The [Airport ATP replay](airport-atp-replay.json) binds the paired six-site desktop configuration to its exact [graded route and high-load vehicle evaluation](../simulation/GIS-SIMULATION.md). It gives simulated lead and following trains the mapped interstation distances and exercises the Rust interlocking and ATP together. Occupancy, train positions and motion uncertainty are scenario inputs. The stopping sensitivity uses the 246.04 t train at 72 km/h, with wheel brakes unavailable and one rail brake module out. The vehicle calculation includes the two-second downhill coast. ATP evaluates the resulting head position and speed and uses the comparator's net deceleration, rounded down to integer millimetres per second squared. [Vehicle braking assumptions](../simulation/vehicle-audit-guide.md)

| Situation | Result |
| --- | --- |
| Next section clear | The braking envelope permits the sampled head speed. |
| Lead train occupies the next section | The authority stops at the section boundary. At 409.607 m remaining after the coast, ATP commands emergency braking. |
| Add 5 m head-position uncertainty and 0.1 m/s speed uncertainty | ATP reduces available distance to 404.607 m, lowers the envelope and commands emergency braking. |
| Authority at its expiry, authority addressed to the other train, or authority with no known position | Each condition commands emergency braking with its own diagnostic reason. |

The 2% downgrade is an adverse comparator for this test. The profile used in the desktop operating simulation has its own grades. The record shows the braking envelope at a fixed snapshot and leaves proposed speed limits, protection overlaps, local resource proofs, real localisation, actual brake performance and communication timing open. In particular, using station chainages as section boundaries for this replay leaves the actual signalling layout unspecified. The replay remains separate from the historical station dossier and from [hardware-in-the-loop evidence](STATION-BENCH.md).

```sh
python3 -m engineering.performance reserve-run --target . --reservation-action airport-atp-replay \
  --projected-bytes 536870912 --minimum-free-gib 20 --receipt-to-stderr -- \
  python3 -m cities.Baghdad.engineering.controls.airport_atp_replay --check
```
