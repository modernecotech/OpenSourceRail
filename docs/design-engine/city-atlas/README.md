# City railway atlas

The city railway atlas is a source-bound planning publication for the mapped
city networks. Its [manifest](manifest.json) identifies the published atlas;
the per-city records and [summary](summary.json) carry route, service and cost
results under their recorded assumptions. They are planning evidence, not
site surveys, physical acceptance or operating approval.

Open the [interactive Workbench atlas](../../workbench/current/index.html) to
inspect published city maps and start a separate local calculation. Baghdad
and Samawah also have readable city dossiers in the catalogue.

Verify the committed atlas without recalculating the city network studies:

```sh
python -m engineering.outline.city_atlas verify docs/design-engine/city-atlas
```

Verification checks the published files against their source identities. It
does not replay their engineering calculations or establish physical
qualification.
