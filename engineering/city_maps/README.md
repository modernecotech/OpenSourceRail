# City maps with retained geographic context

OpenSourceRail aims for simple construction, low whole-life cost and high passenger throughput. These maps place the current proposed corridors, stops and transfer locations in their real city surroundings. They retain roads, waterways, land use, building areas and place names; they do not establish surveyed alignment or clearance.

The v0.4 renderer used street-map backgrounds. Its v0.5 replacement retained routes and stops but omitted the background entirely. The restored renderer uses a common Web Mercator projection for both layers, with legible line colours, a distinct ring, terminal markers and transfer locations. Current corridor and service inputs are preserved.

Each city retains `map-context.json.gz`, a bounded cutout of the 24 October 2026 Protomaps OpenStreetMap-derived basemap. The packet records the archive header/metadata pins, exact HTTP byte ranges, tile hashes, source versions and feature counts. It does not claim verification of the entire planet archive. Missing or mismatched context stops rendering explicitly. Ordinary city regeneration and viewing are offline; no browser tile service, API key or old route image is required.

Acquire contexts in a separate environment, preserving the engineering environment's dependency versions:

```bash
python3 -m venv build/city-maps/venv
build/city-maps/venv/bin/pip install -r engineering/city_maps/requirements.txt
build/city-maps/venv/bin/python -m engineering.city_maps extract --all --workers 2
./osr city --all
build/city-maps/venv/bin/python -m pytest -q engineering/city_maps/tests
```

Use `--city baghdad` for one city. Existing valid inputs are reused; extraction is bounded to one zoom and at most 64 tiles per city. The renderer reads only retained local inputs. Labels and outlines are generalised map context, with incomplete source coverage possible; neither detailed buildings nor absence of a mapped feature provides clearance evidence.

Static labels use source-provided English or Latin-script names supported by the export fonts. Other scripts remain in the retained context and the map receipt counts omitted place labels; no translation is invented. This avoids unreadable square glyphs in offline PDF/image exports.

Map data © [OpenStreetMap contributors](https://www.openstreetmap.org/copyright), [Natural Earth](https://www.naturalearthdata.com/about/terms-of-use/) and [Protomaps](https://docs.protomaps.com/basemaps/downloads). The downloadable Protomaps basemap is distributed as an ODbL Produced Work and explicitly supports regional extraction. Attribution is visible on every map. [Project approach](../../README.md).
