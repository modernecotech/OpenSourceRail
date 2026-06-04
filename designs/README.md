# Generated City Designs

This folder is the generated design catalogue. It is intentionally the single place for city outputs so the repo does not scatter deployment models across docs, scripts, and examples.

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

## Regenerate A City

```bash
scripts/regenerate-city.sh samawah
```

## Regenerate The Catalogue

```bash
scripts/regenerate-all.sh --jobs 4
```

The source city list and country assumptions live in [../lib/city-batches/world-sample.toml](../lib/city-batches/world-sample.toml) and [../lib/templates/](../lib/templates/).

## Representative Designs

- [Samawah, Iraq](west-asia/Iraq/Samawah/README.md): brownfield pilot
- [Baghdad, Iraq](west-asia/Iraq/Baghdad/README.md): megacity network
- [Karachi, Pakistan](south-asia/Pakistan/Karachi/README.md): largest catalogue catchment
- [Lyon, France](europe/France/Lyon/README.md): high-OSM-density solver test

For hand-authored scenarios, use [../lib/examples/](../lib/examples/).

## City Catalogue

Generated from `designs/*/*/*/design.toml`. Sorted by USD CAPEX per route-km, then high-demand coverage.

High-demand coverage is the share of high-demand raster cells (demand >= 0.5) within about 400 m of a planned line. It is a demand / catchment proxy, not a land-area percentage.

| City | ISO | Family | Lines | Stations | km | Fleet | High-demand coverage | CAPEX | CAPEX/km | Charging microgrids |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| [Bafoussam](west-africa/Cameroon/Bafoussam/) | CM | `light-metro-3car` | 3 | 34 | 73 | 72 | 47% | $162M | $2M | $6M |
| [Fayoum](west-asia/Egypt/Fayoum/) | EG | `light-metro-3car` | 3 | 36 | 69 | 67 | 72% | $159M | $2M | $8M |
| [Tanta](west-asia/Egypt/Tanta/) | EG | `light-metro-3car` | 3 | 35 | 75 | 73 | 56% | $176M | $2M | $7M |
| [Huye](east-africa/Rwanda/Huye/) | RW | `tram-2car` | 3 | 28 | 46 | 61 | 23% | $108M | $2M | $6M |
| [Hofuf](west-asia/Saudi%20Arabia/Hofuf/) | SA | `light-metro-3car` | 3 | 46 | 78 | 77 | 50% | $184M | $2M | $10M |
| [Agadir](north-africa/Morocco/Agadir/) | MA | `light-metro-3car` | 3 | 44 | 83 | 80 | 65% | $195M | $2M | $9M |
| [Omdurman](north-africa/Sudan/Omdurman/) | SD | `metro-4car` | 6 | 104 | 255 | 207 | 47% | $615M | $2M | $21M |
| [Bamenda](west-africa/Cameroon/Bamenda/) | CM | `light-metro-3car` | 3 | 31 | 54 | 55 | 59% | $130M | $2M | $6M |
| [Vientiane](southeast-asia/Laos/Vientiane/) | LA | `light-metro-3car` | 3 | 46 | 81 | 78 | 43% | $195M | $2M | $10M |
| [Arusha](east-africa/Tanzania/Arusha/) | TZ | `light-metro-3car` | 3 | 44 | 73 | 72 | 36% | $176M | $2M | $9M |
| [Dammam](west-asia/Saudi%20Arabia/Dammam/) | SA | `metro-4car` | 4 | 95 | 210 | 168 | 28% | $511M | $2M | $21M |
| [Kenitra](north-africa/Morocco/Kenitra/) | MA | `light-metro-3car` | 3 | 35 | 60 | 60 | 66% | $146M | $2M | $8M |
| [Hail](west-asia/Saudi%20Arabia/Hail/) | SA | `light-metro-3car` | 3 | 35 | 63 | 62 | 47% | $154M | $2M | $7M |
| [Kisumu](east-africa/Kenya/Kisumu/) | KE | `light-metro-3car` | 3 | 42 | 75 | 74 | 31% | $185M | $2M | $8M |
| [Damietta](west-asia/Egypt/Damietta/) | EG | `light-metro-3car` | 3 | 38 | 74 | 73 | 72% | $180M | $2M | $7M |
| [Khamis Mushait](west-asia/Saudi%20Arabia/Khamis-Mushait/) | SA | `light-metro-3car` | 3 | 38 | 69 | 68 | 35% | $169M | $2M | $8M |
| [Nablus](west-asia/Palestine/Nablus/) | PS | `light-metro-3car` | 3 | 34 | 65 | 65 | 84% | $159M | $2M | $7M |
| [Lyon](europe/France/Lyon/) | FR | `metro-4car` | 6 | 122 | 287 | 232 | 45% | $704M | $2M | $25M |
| [Bukavu](central-africa/DR%20Congo/Bukavu/) | CD | `light-metro-3car` | 3 | 37 | 60 | 60 | 60% | $148M | $2M | $8M |
| [Asyut](west-asia/Egypt/Asyut/) | EG | `light-metro-3car` | 3 | 31 | 63 | 62 | 58% | $155M | $2M | $6M |
| [Hebron](west-asia/Palestine/Hebron/) | PS | `light-metro-3car` | 3 | 40 | 69 | 68 | 61% | $171M | $2M | $9M |
| [Lira](east-africa/Uganda/Lira/) | UG | `tram-2car` | 3 | 23 | 45 | 61 | 64% | $113M | $2M | $5M |
| [Gulu](east-africa/Uganda/Gulu/) | UG | `light-metro-3car` | 3 | 36 | 64 | 63 | 50% | $159M | $2M | $8M |
| [Port Harcourt](west-africa/Nigeria/Port-Harcourt/) | NG | `metro-4car` | 4 | 95 | 199 | 160 | 31% | $497M | $2M | $20M |
| [Dodoma](east-africa/Tanzania/Dodoma/) | TZ | `light-metro-3car` | 3 | 36 | 66 | 66 | 40% | $166M | $2M | $8M |
| [Kampala](east-africa/Uganda/Kampala/) | UG | `metro-4car` | 4 | 99 | 201 | 160 | 24% | $503M | $2M | $22M |
| [Taif](west-asia/Saudi%20Arabia/Taif/) | SA | `light-metro-3car` | 3 | 42 | 73 | 73 | 41% | $184M | $3M | $9M |
| [Al Kharj](west-asia/Saudi%20Arabia/Al-Kharj/) | SA | `light-metro-3car` | 3 | 38 | 68 | 67 | 70% | $170M | $3M | $8M |
| [Galle](south-asia/Sri%20Lanka/Galle/) | LK | `light-metro-3car` | 3 | 37 | 64 | 64 | 56% | $162M | $3M | $8M |
| [Rahim Yar Khan](south-asia/Pakistan/Rahim-Yar-Khan/) | PK | `light-metro-3car` | 3 | 24 | 46 | 47 | 37% | $115M | $3M | $5M |
| [Hama](west-asia/Syria/Hama/) | SY | `light-metro-3car` | 3 | 31 | 55 | 55 | 53% | $139M | $3M | $7M |
| [Bloemfontein](south-africa/South%20Africa/Bloemfontein/) | ZA | `light-metro-3car` | 3 | 42 | 72 | 71 | 35% | $181M | $3M | $8M |
| [Eldoret](east-africa/Kenya/Eldoret/) | KE | `light-metro-3car` | 3 | 39 | 65 | 64 | 46% | $164M | $3M | $8M |
| [Tangier](north-africa/Morocco/Tangier/) | MA | `metro-4car` | 5 | 64 | 153 | 129 | 57% | $387M | $3M | $13M |
| [Sylhet](south-asia/Bangladesh/Sylhet/) | BD | `light-metro-3car` | 3 | 40 | 73 | 72 | 45% | $184M | $3M | $8M |
| [Mwanza](east-africa/Tanzania/Mwanza/) | TZ | `metro-4car` | 5 | 70 | 162 | 136 | 45% | $410M | $3M | $15M |
| [Thika](east-africa/Kenya/Thika/) | KE | `light-metro-3car` | 3 | 38 | 76 | 74 | 63% | $192M | $3M | $7M |
| [Rangpur](south-asia/Bangladesh/Rangpur/) | BD | `light-metro-3car` | 3 | 36 | 59 | 59 | 47% | $152M | $3M | $8M |
| [Ibb](west-asia/Yemen/Ibb/) | YE | `light-metro-3car` | 3 | 40 | 72 | 71 | 58% | $182M | $3M | $9M |
| [Zagazig](west-asia/Egypt/Zagazig/) | EG | `light-metro-3car` | 3 | 30 | 56 | 57 | 59% | $143M | $3M | $7M |
| [Pokhara](south-asia/Nepal/Pokhara/) | NP | `light-metro-3car` | 3 | 44 | 82 | 80 | 52% | $210M | $3M | $10M |
| [Namibe](east-africa/Angola/Namibe/) | AO | `tram-2car` | 3 | 25 | 40 | 55 | 61% | $103M | $3M | $6M |
| [Hillah](west-asia/Iraq/Hillah/) | IQ | `light-metro-3car` | 3 | 42 | 69 | 68 | 43% | $177M | $3M | $9M |
| [Nakuru](east-africa/Kenya/Nakuru/) | KE | `light-metro-3car` | 3 | 37 | 60 | 61 | 46% | $153M | $3M | $8M |
| [Lubango](east-africa/Angola/Lubango/) | AO | `light-metro-3car` | 3 | 31 | 55 | 55 | 63% | $140M | $3M | $7M |
| [Tripoli Lb](west-asia/Lebanon/Tripoli-Lb/) | LB | `light-metro-3car` | 3 | 30 | 53 | 55 | 50% | $136M | $3M | $6M |
| [Kigali](east-africa/Rwanda/Kigali/) | RW | `metro-4car` | 4 | 86 | 171 | 139 | 34% | $438M | $3M | $19M |
| [Rajshahi](south-asia/Bangladesh/Rajshahi/) | BD | `light-metro-3car` | 3 | 30 | 50 | 52 | 30% | $128M | $3M | $6M |
| [Davao](southeast-asia/Philippines/Davao/) | PH | `metro-4car` | 6 | 108 | 229 | 186 | 72% | $589M | $3M | $25M |
| [Dhamar](west-asia/Yemen/Dhamar/) | YE | `tram-2car` | 3 | 18 | 32 | 46 | 76% | $83M | $3M | $4M |
| [Mecca](west-asia/Saudi%20Arabia/Mecca/) | SA | `metro-4car` | 6 | 114 | 251 | 205 | 46% | $647M | $3M | $25M |
| [Gujranwala](south-asia/Pakistan/Gujranwala/) | PK | `metro-4car` | 4 | 72 | 160 | 130 | 39% | $413M | $3M | $16M |
| [Mukalla](west-asia/Yemen/Mukalla/) | YE | `light-metro-3car` | 3 | 33 | 61 | 61 | 72% | $157M | $3M | $7M |
| [Erbil](west-asia/Iraq/Erbil/) | IQ | `metro-4car` | 6 | 97 | 199 | 166 | 42% | $514M | $3M | $23M |
| [Ilorin](west-africa/Nigeria/Ilorin/) | NG | `light-metro-3car` | 3 | 39 | 60 | 60 | 31% | $156M | $3M | $9M |
| [Buraidah](west-asia/Saudi%20Arabia/Buraidah/) | SA | `light-metro-3car` | 3 | 54 | 80 | 78 | 35% | $205M | $3M | $13M |
| [Mombasa](east-africa/Kenya/Mombasa/) | KE | `metro-4car` | 6 | 95 | 201 | 167 | 52% | $518M | $3M | $21M |
| [Aleppo](west-asia/Syria/Aleppo/) | SY | `metro-4car` | 5 | 89 | 176 | 145 | 46% | $454M | $3M | $20M |
| [San Salvador](latin-america/El%20Salvador/San-Salvador/) | SV | `metro-4car` | 6 | 121 | 255 | 207 | 50% | $659M | $3M | $28M |
| [Comilla](south-asia/Bangladesh/Comilla/) | BD | `light-metro-3car` | 3 | 38 | 66 | 65 | 41% | $170M | $3M | $8M |
| [Shinyanga](east-africa/Tanzania/Shinyanga/) | TZ | `tram-2car` | 3 | 20 | 37 | 51 | 83% | $95M | $3M | $5M |
| [Ranchi](south-asia/India/Ranchi/) | IN | `metro-4car` | 6 | 96 | 216 | 179 | 50% | $559M | $3M | $21M |
| [Jinja](east-africa/Uganda/Jinja/) | UG | `tram-2car` | 3 | 29 | 46 | 61 | 41% | $119M | $3M | $6M |
| [Irbid](west-asia/Jordan/Irbid/) | JO | `light-metro-3car` | 3 | 33 | 56 | 56 | 42% | $146M | $3M | $8M |
| [Gaza City](west-asia/Palestine/Gaza-City/) | PS | `light-metro-3car` | 1 | 15 | 24 | 24 | 30% | $62M | $3M | $3M |
| [Tunis](north-africa/Tunisia/Tunis/) | TN | `metro-4car` | 5 | 118 | 240 | 194 | 48% | $627M | $3M | $27M |
| [Suez](west-asia/Egypt/Suez/) | EG | `light-metro-3car` | 3 | 32 | 59 | 60 | 65% | $154M | $3M | $6M |
| [Marrakech](north-africa/Morocco/Marrakech/) | MA | `metro-4car` | 6 | 79 | 191 | 159 | 58% | $500M | $3M | $16M |
| [Kandahar](south-asia/Afghanistan/Kandahar/) | AF | `light-metro-3car` | 3 | 43 | 64 | 62 | 53% | $167M | $3M | $10M |
| [Meerut](south-asia/India/Meerut/) | IN | `metro-4car` | 4 | 84 | 180 | 146 | 43% | $470M | $3M | $18M |
| [Kakamega](east-africa/Kenya/Kakamega/) | KE | `tram-2car` | 3 | 24 | 42 | 58 | 77% | $111M | $3M | $5M |
| [Maputo](east-africa/Mozambique/Maputo/) | MZ | `metro-4car` | 6 | 83 | 186 | 156 | 71% | $487M | $3M | $18M |
| [Gazipur](south-asia/Bangladesh/Gazipur/) | BD | `metro-4car` | 6 | 127 | 308 | 245 | 38% | $808M | $3M | $27M |
| [Mazar E Sharif](south-asia/Afghanistan/Mazar-E-Sharif/) | AF | `light-metro-3car` | 3 | 37 | 63 | 61 | 59% | $165M | $3M | $8M |
| [Mbuji Mayi](central-africa/DR%20Congo/Mbuji-Mayi/) | CD | `metro-4car` | 4 | 55 | 118 | 101 | 70% | $311M | $3M | $13M |
| [Huambo](east-africa/Angola/Huambo/) | AO | `light-metro-3car` | 3 | 31 | 53 | 55 | 72% | $139M | $3M | $7M |
| [Benguela](east-africa/Angola/Benguela/) | AO | `light-metro-3car` | 3 | 28 | 50 | 51 | 69% | $131M | $3M | $6M |
| [Visakhapatnam](south-asia/India/Visakhapatnam/) | IN | `metro-4car` | 6 | 110 | 240 | 196 | 52% | $631M | $3M | $25M |
| [Aqaba](west-asia/Jordan/Aqaba/) | JO | `tram-2car` | 3 | 23 | 34 | 48 | 57% | $90M | $3M | $5M |
| [Abha](west-asia/Saudi%20Arabia/Abha/) | SA | `light-metro-3car` | 3 | 45 | 70 | 68 | 34% | $184M | $3M | $10M |
| [Vijayawada](south-asia/India/Vijayawada/) | IN | `metro-4car` | 6 | 94 | 225 | 184 | 58% | $594M | $3M | $20M |
| [Madurai](south-asia/India/Madurai/) | IN | `metro-4car` | 6 | 104 | 222 | 183 | 59% | $588M | $3M | $23M |
| [Latakia](west-asia/Syria/Latakia/) | SY | `light-metro-3car` | 3 | 26 | 41 | 43 | 54% | $108M | $3M | $6M |
| [Onitsha](west-africa/Nigeria/Onitsha/) | NG | `metro-4car` | 4 | 76 | 184 | 148 | 30% | $486M | $3M | $16M |
| [Jizan](west-asia/Saudi%20Arabia/Jizan/) | SA | `light-metro-3car` | 3 | 28 | 47 | 48 | 64% | $123M | $3M | $6M |
| [Samawah](west-asia/Iraq/Samawah/) | IQ | `light-metro-3car` | 3 | 33 | 55 | 55 | 56% | $145M | $3M | $8M |
| [Jaffna](south-asia/Sri%20Lanka/Jaffna/) | LK | `light-metro-3car` | 3 | 34 | 52 | 52 | 42% | $137M | $3M | $7M |
| [Medina](west-asia/Saudi%20Arabia/Medina/) | SA | `metro-4car` | 5 | 104 | 211 | 171 | 47% | $561M | $3M | $23M |
| [Niamey](west-africa/Niger/Niamey/) | NE | `metro-4car` | 4 | 80 | 146 | 120 | 38% | $387M | $3M | $19M |
| [Nelspruit](south-africa/South%20Africa/Nelspruit/) | ZA | `tram-2car` | 3 | 22 | 39 | 53 | 68% | $104M | $3M | $5M |
| [Mbarara](east-africa/Uganda/Mbarara/) | UG | `light-metro-3car` | 3 | 36 | 59 | 59 | 53% | $156M | $3M | $8M |
| [Ismailia](west-asia/Egypt/Ismailia/) | EG | `light-metro-3car` | 3 | 33 | 53 | 55 | 63% | $143M | $3M | $8M |
| [Kigoma](east-africa/Tanzania/Kigoma/) | TZ | `tram-2car` | 3 | 24 | 35 | 49 | 77% | $93M | $3M | $6M |
| [Damascus](west-asia/Syria/Damascus/) | SY | `metro-4car` | 6 | 113 | 233 | 192 | 45% | $622M | $3M | $26M |
| [East London Za](south-africa/South%20Africa/East-London-Za/) | ZA | `light-metro-3car` | 3 | 36 | 63 | 63 | 51% | $169M | $3M | $7M |
| [Ouagadougou](west-africa/Burkina%20Faso/Ouagadougou/) | BF | `metro-4car` | 6 | 138 | 264 | 213 | 37% | $706M | $3M | $33M |
| [Baqubah](west-asia/Iraq/Baqubah/) | IQ | `light-metro-3car` | 3 | 37 | 60 | 60 | 50% | $161M | $3M | $8M |
| [Jalalabad Af](south-asia/Afghanistan/Jalalabad-Af/) | AF | `light-metro-3car` | 3 | 32 | 51 | 53 | 69% | $136M | $3M | $7M |
| [Idlib](west-asia/Syria/Idlib/) | SY | `tram-2car` | 3 | 18 | 35 | 49 | 79% | $94M | $3M | $4M |
| [Rubavu](east-africa/Rwanda/Rubavu/) | RW | `tram-2car` | 3 | 28 | 45 | 61 | 48% | $122M | $3M | $6M |
| [Cuenca](latin-america/Ecuador/Cuenca/) | EC | `light-metro-3car` | 3 | 48 | 79 | 77 | 57% | $212M | $3M | $11M |
| [Nampula](east-africa/Mozambique/Nampula/) | MZ | `light-metro-3car` | 3 | 30 | 52 | 54 | 67% | $140M | $3M | $6M |
| [Conakry](west-africa/Guinea/Conakry/) | GN | `metro-4car` | 3 | 55 | 93 | 78 | 40% | $252M | $3M | $13M |
| [Sulaymaniyah](west-asia/Iraq/Sulaymaniyah/) | IQ | `metro-4car` | 4 | 59 | 127 | 106 | 49% | $344M | $3M | $13M |
| [Minya](west-asia/Egypt/Minya/) | EG | `light-metro-3car` | 3 | 32 | 53 | 53 | 69% | $144M | $3M | $7M |
| [Chimoio](east-africa/Mozambique/Chimoio/) | MZ | `light-metro-3car` | 2 | 20 | 35 | 35 | 55% | $94M | $3M | $4M |
| [El Obeid](north-africa/Sudan/El-Obeid/) | SD | `light-metro-3car` | 3 | 28 | 46 | 47 | 72% | $125M | $3M | $6M |
| [Zanzibar City](east-africa/Tanzania/Zanzibar-City/) | TZ | `light-metro-3car` | 3 | 32 | 56 | 56 | 70% | $153M | $3M | $7M |
| [Damanhur](west-asia/Egypt/Damanhur/) | EG | `light-metro-3car` | 3 | 22 | 41 | 44 | 77% | $113M | $3M | $5M |
| [Agra](south-asia/India/Agra/) | IN | `metro-4car` | 5 | 98 | 191 | 156 | 39% | $521M | $3M | $23M |
| [Nador](north-africa/Morocco/Nador/) | MA | `tram-2car` | 3 | 19 | 34 | 48 | 70% | $94M | $3M | $4M |
| [Arua](east-africa/Uganda/Arua/) | UG | `tram-2car` | 3 | 23 | 37 | 51 | 78% | $101M | $3M | $5M |
| [Beira](east-africa/Mozambique/Beira/) | MZ | `light-metro-3car` | 3 | 39 | 54 | 54 | 37% | $148M | $3M | $9M |
| [Kandy](south-asia/Sri%20Lanka/Kandy/) | LK | `light-metro-3car` | 3 | 43 | 78 | 76 | 56% | $214M | $3M | $9M |
| [Fort Portal](east-africa/Uganda/Fort-Portal/) | UG | `tram-2car` | 3 | 21 | 36 | 51 | 84% | $100M | $3M | $5M |
| [Homs](west-asia/Syria/Homs/) | SY | `light-metro-3car` | 3 | 33 | 51 | 53 | 42% | $141M | $3M | $8M |
| [Mogadishu](east-africa/Somalia/Mogadishu/) | SO | `metro-4car` | 4 | 68 | 128 | 106 | 40% | $353M | $3M | $16M |
| [Mandalay](southeast-asia/Myanmar/Mandalay/) | MM | `metro-4car` | 6 | 88 | 187 | 156 | 60% | $516M | $3M | $20M |
| [Mansoura Eg](west-asia/Egypt/Mansoura-Eg/) | EG | `light-metro-3car` | 3 | 34 | 56 | 56 | 54% | $155M | $3M | $8M |
| [Luxor](west-asia/Egypt/Luxor/) | EG | `light-metro-3car` | 3 | 34 | 54 | 54 | 73% | $149M | $3M | $8M |
| [Meknes](north-africa/Morocco/Meknes/) | MA | `light-metro-3car` | 3 | 23 | 39 | 42 | 58% | $109M | $3M | $5M |
| [Raipur](south-asia/India/Raipur/) | IN | `metro-4car` | 5 | 88 | 185 | 151 | 43% | $514M | $3M | $19M |
| [Multan](south-asia/Pakistan/Multan/) | PK | `metro-4car` | 4 | 64 | 115 | 98 | 42% | $320M | $3M | $16M |
| [Duhok](west-asia/Iraq/Duhok/) | IQ | `light-metro-3car` | 3 | 32 | 53 | 54 | 53% | $148M | $3M | $8M |
| [Narayanganj](south-asia/Bangladesh/Narayanganj/) | BD | `light-metro-3car` | 3 | 50 | 82 | 80 | 27% | $228M | $3M | $10M |
| [Kumba](west-africa/Cameroon/Kumba/) | CM | `light-metro-3car` | 3 | 29 | 43 | 45 | 68% | $119M | $3M | $6M |
| [Hyderabad Pk](south-asia/Pakistan/Hyderabad-Pk/) | PK | `metro-4car` | 6 | 84 | 182 | 152 | 61% | $507M | $3M | $19M |
| [Tanga](east-africa/Tanzania/Tanga/) | TZ | `light-metro-3car` | 3 | 27 | 48 | 50 | 72% | $135M | $3M | $6M |
| [Polokwane](south-africa/South%20Africa/Polokwane/) | ZA | `light-metro-3car` | 3 | 34 | 52 | 52 | 60% | $144M | $3M | $8M |
| [Morogoro](east-africa/Tanzania/Morogoro/) | TZ | `light-metro-3car` | 3 | 32 | 55 | 55 | 61% | $154M | $3M | $7M |
| [Peshawar](south-asia/Pakistan/Peshawar/) | PK | `metro-4car` | 4 | 87 | 197 | 158 | 33% | $551M | $3M | $18M |
| [Mahalla](west-asia/Egypt/Mahalla/) | EG | `light-metro-3car` | 3 | 22 | 38 | 42 | 69% | $107M | $3M | $5M |
| [Goma](central-africa/DR%20Congo/Goma/) | CD | `light-metro-3car` | 3 | 39 | 58 | 58 | 60% | $164M | $3M | $9M |
| [Mbeya](east-africa/Tanzania/Mbeya/) | TZ | `light-metro-3car` | 3 | 39 | 55 | 55 | 44% | $155M | $3M | $9M |
| [Entebbe](east-africa/Uganda/Entebbe/) | UG | `tram-2car` | 3 | 28 | 43 | 59 | 70% | $122M | $3M | $6M |
| [Vadodara](south-asia/India/Vadodara/) | IN | `metro-4car` | 5 | 89 | 164 | 137 | 48% | $461M | $3M | $22M |
| [Bhopal](south-asia/India/Bhopal/) | IN | `metro-4car` | 6 | 107 | 206 | 169 | 52% | $581M | $3M | $26M |
| [Naivasha](east-africa/Kenya/Naivasha/) | KE | `tram-2car` | 3 | 20 | 33 | 48 | 86% | $93M | $3M | $5M |
| [Khartoum](north-africa/Sudan/Khartoum/) | SD | `metro-6car` | 5 | 152 | 363 | 287 | 22% | $1.03bn | $3M | $30M |
| [Bandung](southeast-asia/Indonesia/Bandung/) | ID | `metro-4car` | 6 | 126 | 257 | 208 | 41% | $729M | $3M | $29M |
| [Beirut](west-asia/Lebanon/Beirut/) | LB | `metro-4car` | 6 | 83 | 159 | 134 | 70% | $452M | $3M | $20M |
| [Nacala](east-africa/Mozambique/Nacala/) | MZ | `tram-2car` | 3 | 25 | 39 | 54 | 80% | $111M | $3M | $6M |
| [Masaka](east-africa/Uganda/Masaka/) | UG | `tram-2car` | 3 | 20 | 32 | 46 | 56% | $91M | $3M | $5M |
| [Nairobi](east-africa/Kenya/Nairobi/) | KE | `metro-6car` | 8 | 191 | 476 | 378 | 43% | $1.36bn | $3M | $38M |
| [Hoima](east-africa/Uganda/Hoima/) | UG | `tram-2car` | 3 | 19 | 31 | 45 | 84% | $89M | $3M | $5M |
| [Aden](west-asia/Yemen/Aden/) | YE | `light-metro-3car` | 3 | 28 | 44 | 46 | 43% | $127M | $3M | $6M |
| [Taiz](west-asia/Yemen/Taiz/) | YE | `light-metro-3car` | 3 | 33 | 49 | 51 | 55% | $140M | $3M | $8M |
| [Malindi](east-africa/Kenya/Malindi/) | KE | `tram-2car` | 3 | 20 | 29 | 44 | 79% | $84M | $3M | $5M |
| [Kananga](central-africa/DR%20Congo/Kananga/) | CD | `metro-4car` | 2 | 18 | 38 | 34 | 73% | $110M | $3M | $4M |
| [Jos](west-africa/Nigeria/Jos/) | NG | `light-metro-3car` | 3 | 40 | 54 | 55 | 26% | $155M | $3M | $9M |
| [Sidon](west-asia/Lebanon/Sidon/) | LB | `tram-2car` | 3 | 23 | 37 | 52 | 71% | $107M | $3M | $6M |
| [Raqqa](west-asia/Syria/Raqqa/) | SY | `light-metro-3car` | 3 | 25 | 45 | 46 | 86% | $129M | $3M | $6M |
| [Herat](south-asia/Afghanistan/Herat/) | AF | `light-metro-3car` | 3 | 43 | 65 | 64 | 36% | $186M | $3M | $10M |
| [Kisangani](central-africa/DR%20Congo/Kisangani/) | CD | `metro-4car` | 2 | 27 | 47 | 40 | 64% | $136M | $3M | $7M |
| [Arish](west-asia/Egypt/Arish/) | EG | `tram-2car` | 1 | 7 | 13 | 18 | 44% | $37M | $3M | $2M |
| [Fez](north-africa/Morocco/Fez/) | MA | `metro-4car` | 4 | 58 | 113 | 94 | 73% | $326M | $3M | $13M |
| [Bahawalpur](south-asia/Pakistan/Bahawalpur/) | PK | `light-metro-3car` | 3 | 29 | 46 | 49 | 42% | $134M | $3M | $7M |
| [Quetta](south-asia/Pakistan/Quetta/) | PK | `metro-4car` | 5 | 78 | 140 | 120 | 54% | $406M | $3M | $19M |
| [Lucknow](south-asia/India/Lucknow/) | IN | `metro-6car` | 6 | 164 | 375 | 297 | 31% | $1.09bn | $3M | $34M |
| [Sohag](west-asia/Egypt/Sohag/) | EG | `light-metro-3car` | 3 | 32 | 60 | 60 | 68% | $175M | $3M | $7M |
| [Kisii](east-africa/Kenya/Kisii/) | KE | `tram-2car` | 3 | 17 | 30 | 43 | 67% | $86M | $3M | $4M |
| [Barisal](south-asia/Bangladesh/Barisal/) | BD | `light-metro-3car` | 3 | 30 | 59 | 60 | 50% | $171M | $3M | $6M |
| [Varanasi](south-asia/India/Varanasi/) | IN | `metro-4car` | 5 | 100 | 202 | 165 | 47% | $590M | $3M | $23M |
| [Kirkuk](west-asia/Iraq/Kirkuk/) | IQ | `metro-4car` | 6 | 92 | 170 | 142 | 60% | $497M | $3M | $22M |
| [Khulna](south-asia/Bangladesh/Khulna/) | BD | `metro-4car` | 6 | 82 | 182 | 152 | 57% | $534M | $3M | $18M |
| [Rajkot](south-asia/India/Rajkot/) | IN | `metro-4car` | 5 | 76 | 143 | 121 | 58% | $419M | $3M | $18M |
| [Karbala](west-asia/Iraq/Karbala/) | IQ | `metro-4car` | 6 | 89 | 170 | 144 | 67% | $498M | $3M | $22M |
| [Kanpur](south-asia/India/Kanpur/) | IN | `metro-6car` | 7 | 150 | 339 | 273 | 44% | $995M | $3M | $32M |
| [Tabuk](west-asia/Saudi%20Arabia/Tabuk/) | SA | `light-metro-3car` | 3 | 45 | 63 | 63 | 27% | $185M | $3M | $11M |
| [Patna](south-asia/India/Patna/) | IN | `metro-4car` | 5 | 84 | 185 | 152 | 50% | $546M | $3M | $18M |
| [Oujda](north-africa/Morocco/Oujda/) | MA | `light-metro-3car` | 3 | 33 | 47 | 48 | 48% | $138M | $3M | $8M |
| [Lobito](east-africa/Angola/Lobito/) | AO | `light-metro-3car` | 3 | 25 | 38 | 41 | 69% | $112M | $3M | $6M |
| [Maroua](west-africa/Cameroon/Maroua/) | CM | `light-metro-3car` | 3 | 29 | 53 | 54 | 74% | $156M | $3M | $6M |
| [Ramadi](west-asia/Iraq/Ramadi/) | IQ | `light-metro-3car` | 3 | 35 | 47 | 49 | 39% | $139M | $3M | $9M |
| [Fallujah](west-asia/Iraq/Fallujah/) | IQ | `light-metro-3car` | 3 | 28 | 46 | 48 | 57% | $136M | $3M | $7M |
| [Baghdad](west-asia/Iraq/Baghdad/) | IQ | `metro-6car` | 9 | 218 | 509 | 408 | 45% | $1.51bn | $3M | $46M |
| [Dar Es Salaam](east-africa/Tanzania/Dar-Es-Salaam/) | TZ | `metro-6car` | 7 | 163 | 393 | 314 | 28% | $1.17bn | $3M | $32M |
| [Garissa](east-africa/Kenya/Garissa/) | KE | `tram-2car` | 3 | 19 | 29 | 43 | 71% | $86M | $3M | $4M |
| [Songea](east-africa/Tanzania/Songea/) | TZ | `tram-2car` | 1 | 7 | 11 | 16 | 73% | $34M | $3M | $2M |
| [La Paz](latin-america/Bolivia/La-Paz/) | BO | `metro-4car` | 6 | 115 | 212 | 174 | 57% | $633M | $3M | $28M |
| [Phnom Penh](southeast-asia/Cambodia/Phnom-Penh/) | KH | `metro-4car` | 6 | 107 | 228 | 186 | 48% | $680M | $3M | $24M |
| [Mosul](west-asia/Iraq/Mosul/) | IQ | `metro-4car` | 5 | 60 | 145 | 122 | 38% | $433M | $3M | $12M |
| [Colombo](south-asia/Sri%20Lanka/Colombo/) | LK | `metro-6car` | 6 | 126 | 278 | 223 | 42% | $834M | $3M | $27M |
| [Deir Ez Zor](west-asia/Syria/Deir-Ez-Zor/) | SY | `light-metro-3car` | 3 | 32 | 57 | 57 | 62% | $170M | $3M | $7M |
| [Uige](east-africa/Angola/Uige/) | AO | `light-metro-3car` | 1 | 8 | 13 | 14 | 67% | $39M | $3M | $2M |
| [Qena](west-asia/Egypt/Qena/) | EG | `light-metro-3car` | 3 | 26 | 45 | 47 | 75% | $136M | $3M | $6M |
| [Safi](north-africa/Morocco/Safi/) | MA | `light-metro-3car` | 3 | 26 | 39 | 43 | 72% | $118M | $3M | $6M |
| [Luanda](east-africa/Angola/Luanda/) | AO | `metro-6car` | 9 | 170 | 390 | 317 | 64% | $1.18bn | $3M | $35M |
| [Lubumbashi](central-africa/DR%20Congo/Lubumbashi/) | CD | `metro-4car` | 4 | 75 | 130 | 107 | 34% | $392M | $3M | $19M |
| [Kafr El Sheikh](west-asia/Egypt/Kafr-El-Sheikh/) | EG | `tram-2car` | 3 | 22 | 33 | 47 | 75% | $100M | $3M | $5M |
| [Port Sudan](north-africa/Sudan/Port-Sudan/) | SD | `light-metro-3car` | 3 | 22 | 33 | 38 | 80% | $101M | $3M | $5M |
| [Kathmandu](south-asia/Nepal/Kathmandu/) | NP | `metro-4car` | 6 | 103 | 203 | 167 | 46% | $615M | $3M | $25M |
| [Jeddah](west-asia/Saudi%20Arabia/Jeddah/) | SA | `metro-6car` | 8 | 202 | 406 | 326 | 45% | $1.23bn | $3M | $48M |
| [Kinshasa](central-africa/DR%20Congo/Kinshasa/) | CD | `metro-6car` | 8 | 183 | 385 | 310 | 49% | $1.17bn | $3M | $42M |
| [Lusaka](east-africa/Zambia/Lusaka/) | ZM | `metro-6car` | 6 | 123 | 236 | 192 | 34% | $719M | $3M | $28M |
| [Tetouan](north-africa/Morocco/Tetouan/) | MA | `light-metro-3car` | 3 | 33 | 54 | 56 | 69% | $165M | $3M | $7M |
| [Hurghada](west-asia/Egypt/Hurghada/) | EG | `tram-2car` | 3 | 28 | 43 | 57 | 56% | $131M | $3M | $7M |
| [Indore](south-asia/India/Indore/) | IN | `metro-6car` | 7 | 146 | 324 | 260 | 48% | $992M | $3M | $32M |
| [Diwaniyah](west-asia/Iraq/Diwaniyah/) | IQ | `light-metro-3car` | 3 | 36 | 54 | 55 | 43% | $165M | $3M | $9M |
| [Machakos](east-africa/Kenya/Machakos/) | KE | `tram-2car` | 3 | 16 | 27 | 40 | 76% | $81M | $3M | $4M |
| [Beni Mellal](north-africa/Morocco/Beni-Mellal/) | MA | `tram-2car` | 3 | 18 | 30 | 45 | 85% | $93M | $3M | $4M |
| [Port Said](west-asia/Egypt/Port-Said/) | EG | `light-metro-3car` | 3 | 25 | 35 | 39 | 71% | $107M | $3M | $6M |
| [Durban](south-africa/South%20Africa/Durban/) | ZA | `metro-6car` | 9 | 172 | 401 | 325 | 79% | $1.24bn | $3M | $37M |
| [Karachi](south-asia/Pakistan/Karachi/) | PK | `metro-6car` | 9 | 231 | 472 | 377 | 48% | $1.47bn | $3M | $52M |
| [Pemba Mz](east-africa/Mozambique/Pemba-Mz/) | MZ | `tram-2car` | 3 | 20 | 30 | 43 | 63% | $94M | $3M | $5M |
| [Coimbatore](south-asia/India/Coimbatore/) | IN | `metro-6car` | 5 | 121 | 268 | 214 | 31% | $834M | $3M | $26M |
| [Uyo](west-africa/Nigeria/Uyo/) | NG | `light-metro-3car` | 3 | 24 | 31 | 36 | 25% | $97M | $3M | $6M |
| [Dakar](west-africa/Senegal/Dakar/) | SN | `metro-6car` | 5 | 107 | 204 | 167 | 52% | $637M | $3M | $25M |
| [Beni Suef](west-asia/Egypt/Beni-Suef/) | EG | `light-metro-3car` | 3 | 23 | 35 | 38 | 55% | $109M | $3M | $6M |
| [Maiduguri](west-africa/Nigeria/Maiduguri/) | NG | `metro-4car` | 5 | 86 | 176 | 145 | 34% | $551M | $3M | $19M |
| [Benin City](west-africa/Nigeria/Benin-City/) | NG | `metro-4car` | 4 | 77 | 132 | 111 | 44% | $415M | $3M | $19M |
| [Antananarivo](east-africa/Madagascar/Antananarivo/) | MG | `metro-6car` | 7 | 155 | 339 | 272 | 42% | $1.07bn | $3M | $34M |
| [Amman](west-asia/Jordan/Amman/) | JO | `metro-6car` | 8 | 172 | 354 | 286 | 51% | $1.11bn | $3M | $39M |
| [Nyala](north-africa/Sudan/Nyala/) | SD | `light-metro-3car` | 3 | 29 | 47 | 48 | 61% | $147M | $3M | $6M |
| [Chittagong](south-asia/Bangladesh/Chittagong/) | BD | `metro-6car` | 8 | 161 | 374 | 302 | 64% | $1.18bn | $3M | $35M |
| [Sayun](west-asia/Yemen/Sayun/) | YE | `tram-2car` | 2 | 15 | 22 | 31 | 58% | $68M | $3M | $4M |
| [Kitale](east-africa/Kenya/Kitale/) | KE | `tram-2car` | 3 | 16 | 29 | 43 | 85% | $93M | $3M | $4M |
| [Tartus](west-asia/Syria/Tartus/) | SY | `tram-2car` | 3 | 23 | 35 | 49 | 73% | $111M | $3M | $6M |
| [Bertoua](west-africa/Cameroon/Bertoua/) | CM | `light-metro-3car` | 3 | 20 | 29 | 34 | 77% | $92M | $3M | $5M |
| [Soyo](east-africa/Angola/Soyo/) | AO | `tram-2car` | 2 | 14 | 22 | 32 | 70% | $71M | $3M | $3M |
| [Basra](west-asia/Iraq/Basra/) | IQ | `metro-6car` | 7 | 119 | 289 | 236 | 54% | $923M | $3M | $25M |
| [Hodeidah](west-asia/Yemen/Hodeidah/) | YE | `light-metro-3car` | 3 | 27 | 36 | 40 | 61% | $116M | $3M | $7M |
| [Najran](west-asia/Saudi%20Arabia/Najran/) | SA | `light-metro-3car` | 3 | 33 | 57 | 57 | 46% | $182M | $3M | $7M |
| [Najaf](west-asia/Iraq/Najaf/) | IQ | `metro-4car` | 6 | 91 | 172 | 144 | 60% | $555M | $3M | $22M |
| [Yangon](southeast-asia/Myanmar/Yangon/) | MM | `metro-6car` | 9 | 214 | 418 | 335 | 56% | $1.35bn | $3M | $52M |
| [Surabaya](southeast-asia/Indonesia/Surabaya/) | ID | `metro-6car` | 7 | 143 | 294 | 240 | 40% | $950M | $3M | $32M |
| [Yaounde](east-africa/Cameroon/Yaounde/) | CM | `metro-6car` | 8 | 136 | 267 | 219 | 43% | $862M | $3M | $32M |
| [Quelimane](east-africa/Mozambique/Quelimane/) | MZ | `light-metro-3car` | 1 | 6 | 10 | 12 | 48% | $33M | $3M | $2M |
| [Waw](north-africa/Sudan/Waw/) | SD | `tram-2car` | 2 | 11 | 18 | 27 | 73% | $58M | $3M | $3M |
| [Xai Xai](east-africa/Mozambique/Xai-Xai/) | MZ | `tram-2car` | 2 | 12 | 18 | 27 | 43% | $58M | $3M | $3M |
| [Kano](west-africa/Nigeria/Kano/) | NG | `metro-6car` | 6 | 154 | 362 | 286 | 37% | $1.18bn | $3M | $30M |
| [Lahij](west-asia/Yemen/Lahij/) | YE | `tram-2car` | 3 | 19 | 29 | 43 | 82% | $95M | $3M | $5M |
| [Kabul](south-asia/Afghanistan/Kabul/) | AF | `metro-6car` | 7 | 137 | 261 | 215 | 53% | $858M | $3M | $33M |
| [Zarqa](west-asia/Jordan/Zarqa/) | JO | `light-metro-3car` | 3 | 57 | 83 | 80 | 48% | $274M | $3M | $13M |
| [Sanaa](west-asia/Yemen/Sanaa/) | YE | `metro-6car` | 9 | 126 | 261 | 218 | 78% | $863M | $3M | $30M |
| [Edea](west-africa/Cameroon/Edea/) | CM | `tram-2car` | 1 | 7 | 10 | 14 | 61% | $32M | $3M | $2M |
| [Aba Ng](west-africa/Nigeria/Aba-Ng/) | NG | `light-metro-3car` | 3 | 26 | 34 | 38 | 40% | $114M | $3M | $7M |
| [Iringa](east-africa/Tanzania/Iringa/) | TZ | `tram-2car` | 3 | 20 | 28 | 42 | 67% | $93M | $3M | $5M |
| [Moshi](east-africa/Tanzania/Moshi/) | TZ | `tram-2car` | 3 | 21 | 36 | 51 | 76% | $120M | $3M | $5M |
| [Meru Ke](east-africa/Kenya/Meru-Ke/) | KE | `tram-2car` | 2 | 12 | 22 | 32 | 52% | $74M | $3M | $3M |
| [Douala](west-africa/Cameroon/Douala/) | CM | `metro-6car` | 5 | 129 | 228 | 184 | 37% | $770M | $3M | $31M |
| [Faisalabad](south-asia/Pakistan/Faisalabad/) | PK | `metro-6car` | 5 | 93 | 166 | 137 | 52% | $566M | $3M | $22M |
| [Ngaoundere](west-africa/Cameroon/Ngaoundere/) | CM | `light-metro-3car` | 3 | 19 | 28 | 34 | 57% | $96M | $3M | $4M |
| [Ibadan](west-africa/Nigeria/Ibadan/) | NG | `metro-6car` | 4 | 90 | 135 | 111 | 24% | $473M | $3M | $23M |
| [Bamako](west-africa/Mali/Bamako/) | ML | `metro-4car` | 6 | 118 | 257 | 207 | 31% | $903M | $4M | $25M |
| [Kut](west-asia/Iraq/Kut/) | IQ | `light-metro-3car` | 3 | 32 | 56 | 55 | 37% | $201M | $4M | $7M |
| [Nasiriyah](west-asia/Iraq/Nasiriyah/) | IQ | `light-metro-3car` | 3 | 33 | 56 | 56 | 40% | $205M | $4M | $8M |
| [Khouribga](north-africa/Morocco/Khouribga/) | MA | `tram-2car` | 2 | 11 | 15 | 23 | 57% | $54M | $4M | $3M |
| [Larkana](south-asia/Pakistan/Larkana/) | PK | `light-metro-3car` | 2 | 19 | 38 | 39 | 28% | $140M | $4M | $4M |
| [Tabora](east-africa/Tanzania/Tabora/) | TZ | `tram-2car` | 2 | 13 | 18 | 26 | 54% | $66M | $4M | $3M |
| [Kassala](north-africa/Sudan/Kassala/) | SD | `light-metro-3car` | 3 | 20 | 34 | 39 | 76% | $130M | $4M | $5M |
| [Garoua](west-africa/Cameroon/Garoua/) | CM | `light-metro-3car` | 3 | 29 | 44 | 46 | 38% | $166M | $4M | $6M |
| [Amarah](west-asia/Iraq/Amarah/) | IQ | `light-metro-3car` | 3 | 32 | 45 | 46 | 43% | $171M | $4M | $8M |
| [Tete](east-africa/Mozambique/Tete/) | MZ | `light-metro-3car` | 3 | 23 | 38 | 41 | 77% | $147M | $4M | $5M |
| [Jodhpur](south-asia/India/Jodhpur/) | IN | `metro-4car` | 5 | 82 | 150 | 124 | 44% | $579M | $4M | $20M |
| [Mymensingh](south-asia/Bangladesh/Mymensingh/) | BD | `light-metro-3car` | 3 | 37 | 67 | 67 | 41% | $263M | $4M | $7M |
| [Nyeri](east-africa/Kenya/Nyeri/) | KE | `tram-2car` | 3 | 22 | 37 | 51 | 62% | $144M | $4M | $5M |
| [Sumbawanga](east-africa/Tanzania/Sumbawanga/) | TZ | `tram-2car` | 1 | 5 | 7 | 11 | 35% | $26M | $4M | $1M |
| [Sheikhupura](south-asia/Pakistan/Sheikhupura/) | PK | `light-metro-3car` | 2 | 17 | 19 | 22 | 32% | $79M | $4M | $5M |
| [Malanje](east-africa/Angola/Malanje/) | AO | `light-metro-3car` | 2 | 12 | 15 | 19 | 57% | $63M | $4M | $3M |
| [Sialkot](south-asia/Pakistan/Sialkot/) | PK | `light-metro-3car` | 3 | 37 | 59 | 59 | 43% | $256M | $4M | $9M |
| [Sukkur](south-asia/Pakistan/Sukkur/) | PK | `light-metro-3car` | 3 | 31 | 51 | 53 | 55% | $234M | $5M | $7M |
| [Biratnagar](south-asia/Nepal/Biratnagar/) | NP | `tram-2car` | 3 | 23 | 34 | 48 | 60% | $206M | $6M | $5M |
