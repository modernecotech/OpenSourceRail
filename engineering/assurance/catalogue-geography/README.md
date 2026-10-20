# Catalogue network geometry audit

The [current independent audit](summary.json) checks all **266 city examples** against their exported route geometry, proposed platform groups and retained independent water evidence. All 266 networks form one connected line graph and one connected proposed transfer graph. No missing grouped platforms at checked dry crossings, wet platform cells, unknown platform cells or unapproved water runs above 1 km are reported.

**The complete geometry audit remains open:** 31 self-intersecting lines remain in 29 older city layouts. Connectivity is not sufficient for a usable alignment. These findings are retained explicitly below; they are not engineering or operating releases.

[39 regenerated cities and correction evidence](../catalogue-network-layout/README.md) include Kisangani, Lubumbashi, Garissa, the other disconnected examples, and all nine Angola cities. All 39 pass the expanded local map audit. Angola is classified as Central Africa (UN M49 Middle Africa).

The common planner restores source-routed radials where forced core chords distorted them, removes only bounded local raster knots, and joins disconnected components using constrained continuous corridors. Protected land, known water, unknown coverage, retained population-priority stops and maximum added route scope remain explicit. Larger unresolvable loops require another controlled alignment decision.

Checks use Shapely independently of native station generation. Projected line crossings over mapped water cannot create passenger transfers. Dry geometric crossings require grouped proposed platforms within the native 60 m raster tolerance. Continuous geometry, walking access, levels, foundations and site acceptance remain open.

| City with remaining self-intersections | Lines |
|---|---|
| kinshasa | line-9 |
| kakamega | line-1 |
| mombasa | line-3, line-6 |
| antananarivo | line-8 |
| mogadishu | line-4 |
| dar-es-salaam | line-9 |
| tangier | line-8 |
| khartoum | line-9 |
| tunis | line-6 |
| kabul | line-7 |
| bhopal | line-6 |
| patna | line-3, line-6 |
| vijayawada | line-6 |
| kathmandu | line-6 |
| karachi | line-9 |
| colombo | line-9 |
| bandung | line-6 |
| mandalay | line-6 |
| yangon | line-9 |
| davao | line-6 |
| conakry | line-3 |
| bamako | line-6 |
| dakar | line-6 |
| karbala | line-3 |
| beirut | line-6 |
| dammam | line-6 |
| aleppo | line-1 |
| damascus | line-6 |
| hama | line-3 |

The [earlier baseline audit](baseline.json) records the previous water-placement campaign. Its narrower checks did not establish whole-network connectivity or absence of self-intersections. Earlier operating and energy results remain valid only for their recorded source revisions. Changed alignments require new runs; each updated city publishes an incomplete package manifest and an explicit revalidation notice.

Each city retains its grid, ESA WorldCover 2021 class samples, OSM water geometries, combined mask and source receipts. Checks reconstruct these masks from retained inputs. Historical satellite classification and mapped features are planning evidence, not current shoreline surveys. Attribution: © ESA WorldCover project 2021 / Contains modified Copernicus Sentinel data; OSM supplement © OpenStreetMap contributors, ODbL.

Sources: [ESA WorldCover](https://esa-worldcover.org/en/data-access), [UN Angola classification](https://data.un.org/legacy/en/iso/ao.html).
