# Current development-design adapters

OpenSourceRail seeks simple, affordable, locally maintainable urban transport. This package connects the selected six-car comfort/NdFeB design to current service, cities, delivery records, reader and Workbench. All magnets and suspension controls stay onboard; ordinary guideway is concrete with passive steel facings and stations provide propulsion.

The authoritative input is [development-baseline.toml](../development-baseline.toml). The [current dossier](../../docs/design-engine/current/README.md) states the 44-seat plus two-wheelchair vehicle, one-sided doors, lightweight structure and 120-second target. Development adoption never grants physical, manufacturing or operating acceptance.

`selection` authenticates the retained body/magnet packet; `evaluate` regenerates the selected72km/h service; `cities` recalculates all route plans; `exports` compiles matched delivery records and verifies portable CAD/IFC; `publication` seals current evidence; `book` generates the reader; `entrypoint` and `server` expose the same default. Historical source-bound packets are checked at their original Git revision by `legacy`.

```bash
./osr status
./osr build
./osr verify
./osr test
```

Unknown installed mass, current authority, cost or physical performance remains unknown. Native protection fixtures use synthetic healthy gaps and assumed braking; neither they nor ideal-force dynamics qualify the train.
