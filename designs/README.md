# Generated City Designs

This folder is the generated design catalogue. It is intentionally the
single place for city outputs so the repo does not scatter deployment
models across docs, scripts, and examples.

## What Each City Folder Contains

City folders follow:

```text
designs/<region>/<country>/<City>/
```

Typical contents:

| File | Purpose |
|---|---|
| `README.md` | Human-readable generated design report |
| `design.toml` | Machine-readable design summary |
| `<slug>.toml` | Simulator scenario |
| `*-network-map.png` | Network map render |
| route GeoJSON | Line/station geometry |
| design-quality YAML | Soft/hard design gate results |

The generated catalogue index is [INDEX.md](INDEX.md).

## Regenerate A City

```bash
scripts/regenerate-city.sh samawah
```

## Regenerate The Catalogue

```bash
scripts/regenerate-all.sh --jobs 4
```

The source city list and country assumptions live in
[../lib/city-batches/world-sample.toml](../lib/city-batches/world-sample.toml)
and [../lib/templates/](../lib/templates/).

## Representative Designs

- [Samawah, Iraq](west-asia/Iraq/Samawah/README.md): brownfield pilot
- [Baghdad, Iraq](west-asia/Iraq/Baghdad/README.md): megacity network
- [Karachi, Pakistan](south-asia/Pakistan/Karachi/README.md): largest catalogue catchment
- [Lyon, France](europe/France/Lyon/README.md): high-OSM-density solver test

For hand-authored scenarios, use [../lib/examples/](../lib/examples/).
