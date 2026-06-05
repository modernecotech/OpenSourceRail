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
| [Bafoussam](west-africa/Cameroon/Bafoussam/) | CM | `light-metro-3car` | 3 | 34 | 73 | 72 | 47% | $371M | $5M | $12M |
| [Fayoum](west-asia/Egypt/Fayoum/) | EG | `light-metro-3car` | 3 | 36 | 69 | 67 | 72% | $367M | $5M | $14M |
| [Hofuf](west-asia/Saudi%20Arabia/Hofuf/) | SA | `light-metro-3car` | 3 | 46 | 78 | 77 | 50% | $426M | $5M | $18M |
| [Tanta](west-asia/Egypt/Tanta/) | EG | `light-metro-3car` | 3 | 35 | 75 | 73 | 56% | $410M | $5M | $14M |
| [Bamenda](west-africa/Cameroon/Bamenda/) | CM | `light-metro-3car` | 3 | 31 | 54 | 55 | 59% | $297M | $5M | $12M |
| [Agadir](north-africa/Morocco/Agadir/) | MA | `light-metro-3car` | 3 | 44 | 83 | 80 | 65% | $454M | $5M | $17M |
| [Huye](east-africa/Rwanda/Huye/) | RW | `tram-2car` | 3 | 28 | 46 | 61 | 23% | $252M | $5M | $10M |
| [Omdurman](north-africa/Sudan/Omdurman/) | SD | `metro-4car` | 6 | 104 | 255 | 207 | 47% | $1.42bn | $6M | $41M |
| [Kenitra](north-africa/Morocco/Kenitra/) | MA | `light-metro-3car` | 3 | 35 | 60 | 60 | 66% | $336M | $6M | $14M |
| [Arusha](east-africa/Tanzania/Arusha/) | TZ | `light-metro-3car` | 3 | 44 | 73 | 72 | 36% | $407M | $6M | $16M |
| [Vientiane](southeast-asia/Laos/Vientiane/) | LA | `light-metro-3car` | 3 | 46 | 81 | 78 | 43% | $455M | $6M | $18M |
| [Dammam](west-asia/Saudi%20Arabia/Dammam/) | SA | `metro-4car` | 4 | 95 | 210 | 168 | 28% | $1.18bn | $6M | $39M |
| [Bukavu](central-africa/DR%20Congo/Bukavu/) | CD | `light-metro-3car` | 3 | 37 | 60 | 60 | 60% | $340M | $6M | $15M |
| [Hail](west-asia/Saudi%20Arabia/Hail/) | SA | `light-metro-3car` | 3 | 35 | 63 | 62 | 47% | $357M | $6M | $13M |
| [Nablus](west-asia/Palestine/Nablus/) | PS | `light-metro-3car` | 3 | 34 | 65 | 65 | 84% | $367M | $6M | $13M |
| [Damietta](west-asia/Egypt/Damietta/) | EG | `light-metro-3car` | 3 | 38 | 74 | 73 | 72% | $418M | $6M | $13M |
| [Khamis Mushait](west-asia/Saudi%20Arabia/Khamis-Mushait/) | SA | `light-metro-3car` | 3 | 38 | 69 | 68 | 35% | $393M | $6M | $14M |
| [Lyon](europe/France/Lyon/) | FR | `metro-4car` | 6 | 122 | 287 | 232 | 45% | $1.64bn | $6M | $49M |
| [Kisumu](east-africa/Kenya/Kisumu/) | KE | `light-metro-3car` | 3 | 42 | 75 | 74 | 31% | $431M | $6M | $14M |
| [Rahim Yar Khan](south-asia/Pakistan/Rahim-Yar-Khan/) | PK | `light-metro-3car` | 3 | 24 | 46 | 47 | 37% | $263M | $6M | $10M |
| [Asyut](west-asia/Egypt/Asyut/) | EG | `light-metro-3car` | 3 | 31 | 63 | 62 | 58% | $361M | $6M | $11M |
| [Hebron](west-asia/Palestine/Hebron/) | PS | `light-metro-3car` | 3 | 40 | 69 | 68 | 61% | $398M | $6M | $16M |
| [Gulu](east-africa/Uganda/Gulu/) | UG | `light-metro-3car` | 3 | 36 | 64 | 63 | 50% | $369M | $6M | $15M |
| [Tangier](north-africa/Morocco/Tangier/) | MA | `metro-4car` | 5 | 64 | 153 | 129 | 57% | $889M | $6M | $25M |
| [Dodoma](east-africa/Tanzania/Dodoma/) | TZ | `light-metro-3car` | 3 | 36 | 66 | 66 | 40% | $385M | $6M | $14M |
| [Port Harcourt](west-africa/Nigeria/Port-Harcourt/) | NG | `metro-4car` | 4 | 95 | 199 | 160 | 31% | $1.16bn | $6M | $39M |
| [Hama](west-asia/Syria/Hama/) | SY | `light-metro-3car` | 3 | 31 | 55 | 55 | 53% | $321M | $6M | $13M |
| [Galle](south-asia/Sri%20Lanka/Galle/) | LK | `light-metro-3car` | 3 | 37 | 64 | 64 | 56% | $375M | $6M | $15M |
| [Kampala](east-africa/Uganda/Kampala/) | UG | `metro-4car` | 4 | 99 | 201 | 160 | 24% | $1.17bn | $6M | $41M |
| [Gaza City](west-asia/Palestine/Gaza-City/) | PS | `light-metro-3car` | 1 | 15 | 24 | 24 | 30% | $139M | $6M | $6M |
| [Al Kharj](west-asia/Saudi%20Arabia/Al-Kharj/) | SA | `light-metro-3car` | 3 | 38 | 68 | 67 | 70% | $394M | $6M | $14M |
| [Taif](west-asia/Saudi%20Arabia/Taif/) | SA | `light-metro-3car` | 3 | 42 | 73 | 73 | 41% | $428M | $6M | $17M |
| [Mwanza](east-africa/Tanzania/Mwanza/) | TZ | `metro-4car` | 5 | 70 | 162 | 136 | 45% | $942M | $6M | $29M |
| [Rajshahi](south-asia/Bangladesh/Rajshahi/) | BD | `light-metro-3car` | 3 | 30 | 50 | 52 | 30% | $292M | $6M | $12M |
| [Eldoret](east-africa/Kenya/Eldoret/) | KE | `light-metro-3car` | 3 | 39 | 65 | 64 | 46% | $382M | $6M | $16M |
| [Bloemfontein](south-africa/South%20Africa/Bloemfontein/) | ZA | `light-metro-3car` | 3 | 42 | 72 | 71 | 35% | $423M | $6M | $16M |
| [Dhamar](west-asia/Yemen/Dhamar/) | YE | `tram-2car` | 3 | 18 | 32 | 46 | 76% | $190M | $6M | $8M |
| [Nakuru](east-africa/Kenya/Nakuru/) | KE | `light-metro-3car` | 3 | 37 | 60 | 61 | 46% | $350M | $6M | $14M |
| [Lira](east-africa/Uganda/Lira/) | UG | `tram-2car` | 3 | 23 | 45 | 61 | 64% | $267M | $6M | $10M |
| [Tripoli Lb](west-asia/Lebanon/Tripoli-Lb/) | LB | `light-metro-3car` | 3 | 30 | 53 | 55 | 50% | $313M | $6M | $12M |
| [Zagazig](west-asia/Egypt/Zagazig/) | EG | `light-metro-3car` | 3 | 30 | 56 | 57 | 59% | $331M | $6M | $13M |
| [Rangpur](south-asia/Bangladesh/Rangpur/) | BD | `light-metro-3car` | 3 | 36 | 59 | 59 | 47% | $351M | $6M | $14M |
| [Lubango](east-africa/Angola/Lubango/) | AO | `light-metro-3car` | 3 | 31 | 55 | 55 | 63% | $322M | $6M | $12M |
| [Sylhet](south-asia/Bangladesh/Sylhet/) | BD | `light-metro-3car` | 3 | 40 | 73 | 72 | 45% | $430M | $6M | $14M |
| [Namibe](east-africa/Angola/Namibe/) | AO | `tram-2car` | 3 | 25 | 40 | 55 | 61% | $239M | $6M | $11M |
| [Ilorin](west-africa/Nigeria/Ilorin/) | NG | `light-metro-3car` | 3 | 39 | 60 | 60 | 31% | $359M | $6M | $16M |
| [Ibb](west-asia/Yemen/Ibb/) | YE | `light-metro-3car` | 3 | 40 | 72 | 71 | 58% | $426M | $6M | $17M |
| [Kigali](east-africa/Rwanda/Kigali/) | RW | `metro-4car` | 4 | 86 | 171 | 139 | 34% | $1.02bn | $6M | $37M |
| [Erbil](west-asia/Iraq/Erbil/) | IQ | `metro-4car` | 6 | 97 | 199 | 166 | 42% | $1.19bn | $6M | $45M |
| [Hillah](west-asia/Iraq/Hillah/) | IQ | `light-metro-3car` | 3 | 42 | 69 | 68 | 43% | $412M | $6M | $18M |
| [Latakia](west-asia/Syria/Latakia/) | SY | `light-metro-3car` | 3 | 26 | 41 | 43 | 54% | $245M | $6M | $11M |
| [Mombasa](east-africa/Kenya/Mombasa/) | KE | `metro-4car` | 6 | 95 | 201 | 167 | 52% | $1.20bn | $6M | $42M |
| [Mukalla](west-asia/Yemen/Mukalla/) | YE | `light-metro-3car` | 3 | 33 | 61 | 61 | 72% | $364M | $6M | $14M |
| [Aleppo](west-asia/Syria/Aleppo/) | SY | `metro-4car` | 5 | 89 | 176 | 145 | 46% | $1.05bn | $6M | $40M |
| [Khartoum](north-africa/Sudan/Khartoum/) | SD | `metro-6car` | 5 | 152 | 363 | 287 | 22% | $2.18bn | $6M | $57M |
| [Thika](east-africa/Kenya/Thika/) | KE | `light-metro-3car` | 3 | 38 | 76 | 74 | 63% | $454M | $6M | $13M |
| [Davao](southeast-asia/Philippines/Davao/) | PH | `metro-4car` | 6 | 108 | 229 | 186 | 72% | $1.38bn | $6M | $50M |
| [Gujranwala](south-asia/Pakistan/Gujranwala/) | PK | `metro-4car` | 4 | 72 | 160 | 130 | 39% | $963M | $6M | $30M |
| [Mecca](west-asia/Saudi%20Arabia/Mecca/) | SA | `metro-4car` | 6 | 114 | 251 | 205 | 46% | $1.51bn | $6M | $49M |
| [Ranchi](south-asia/India/Ranchi/) | IN | `metro-4car` | 6 | 96 | 216 | 179 | 50% | $1.30bn | $6M | $40M |
| [Pokhara](south-asia/Nepal/Pokhara/) | NP | `light-metro-3car` | 3 | 44 | 82 | 80 | 52% | $495M | $6M | $18M |
| [Shinyanga](east-africa/Tanzania/Shinyanga/) | TZ | `tram-2car` | 3 | 20 | 37 | 51 | 83% | $222M | $6M | $9M |
| [Comilla](south-asia/Bangladesh/Comilla/) | BD | `light-metro-3car` | 3 | 38 | 66 | 65 | 41% | $396M | $6M | $15M |
| [Buraidah](west-asia/Saudi%20Arabia/Buraidah/) | SA | `light-metro-3car` | 3 | 54 | 80 | 78 | 35% | $480M | $6M | $24M |
| [Mbuji Mayi](central-africa/DR%20Congo/Mbuji-Mayi/) | CD | `metro-4car` | 4 | 55 | 118 | 101 | 70% | $713M | $6M | $25M |
| [Huambo](east-africa/Angola/Huambo/) | AO | `light-metro-3car` | 3 | 31 | 53 | 55 | 72% | $319M | $6M | $13M |
| [San Salvador](latin-america/El%20Salvador/San-Salvador/) | SV | `metro-4car` | 6 | 121 | 255 | 207 | 50% | $1.54bn | $6M | $56M |
| [Irbid](west-asia/Jordan/Irbid/) | JO | `light-metro-3car` | 3 | 33 | 56 | 56 | 42% | $339M | $6M | $15M |
| [Suez](west-asia/Egypt/Suez/) | EG | `light-metro-3car` | 3 | 32 | 59 | 60 | 65% | $356M | $6M | $12M |
| [Nairobi](east-africa/Kenya/Nairobi/) | KE | `metro-6car` | 8 | 191 | 476 | 378 | 43% | $2.88bn | $6M | $73M |
| [Benguela](east-africa/Angola/Benguela/) | AO | `light-metro-3car` | 3 | 28 | 50 | 51 | 69% | $303M | $6M | $11M |
| [Aqaba](west-asia/Jordan/Aqaba/) | JO | `tram-2car` | 3 | 23 | 34 | 48 | 57% | $208M | $6M | $10M |
| [Maputo](east-africa/Mozambique/Maputo/) | MZ | `metro-4car` | 6 | 83 | 186 | 156 | 71% | $1.13bn | $6M | $35M |
| [Jizan](west-asia/Saudi%20Arabia/Jizan/) | SA | `light-metro-3car` | 3 | 28 | 47 | 48 | 64% | $284M | $6M | $11M |
| [Marrakech](north-africa/Morocco/Marrakech/) | MA | `metro-4car` | 6 | 79 | 191 | 159 | 58% | $1.17bn | $6M | $33M |
| [Kandahar](south-asia/Afghanistan/Kandahar/) | AF | `light-metro-3car` | 3 | 43 | 64 | 62 | 53% | $391M | $6M | $19M |
| [Tunis](north-africa/Tunisia/Tunis/) | TN | `metro-4car` | 5 | 118 | 240 | 194 | 48% | $1.47bn | $6M | $52M |
| [Meerut](south-asia/India/Meerut/) | IN | `metro-4car` | 4 | 84 | 180 | 146 | 43% | $1.10bn | $6M | $36M |
| [Jaffna](south-asia/Sri%20Lanka/Jaffna/) | LK | `light-metro-3car` | 3 | 34 | 52 | 52 | 42% | $318M | $6M | $14M |
| [Jalalabad Af](south-asia/Afghanistan/Jalalabad-Af/) | AF | `light-metro-3car` | 3 | 32 | 51 | 53 | 69% | $312M | $6M | $14M |
| [Jinja](east-africa/Uganda/Jinja/) | UG | `tram-2car` | 3 | 29 | 46 | 61 | 41% | $280M | $6M | $12M |
| [Ismailia](west-asia/Egypt/Ismailia/) | EG | `light-metro-3car` | 3 | 33 | 53 | 55 | 63% | $329M | $6M | $15M |
| [Samawah](west-asia/Iraq/Samawah/) | IQ | `light-metro-3car` | 3 | 33 | 55 | 55 | 56% | $338M | $6M | $15M |
| [Niamey](west-africa/Niger/Niamey/) | NE | `metro-4car` | 4 | 80 | 146 | 120 | 38% | $898M | $6M | $36M |
| [Mazar E Sharif](south-asia/Afghanistan/Mazar-E-Sharif/) | AF | `light-metro-3car` | 3 | 37 | 63 | 61 | 59% | $388M | $6M | $16M |
| [Kigoma](east-africa/Tanzania/Kigoma/) | TZ | `tram-2car` | 3 | 24 | 35 | 49 | 77% | $215M | $6M | $11M |
| [Kakamega](east-africa/Kenya/Kakamega/) | KE | `tram-2car` | 3 | 24 | 42 | 58 | 77% | $261M | $6M | $10M |
| [Madurai](south-asia/India/Madurai/) | IN | `metro-4car` | 6 | 104 | 222 | 183 | 59% | $1.37bn | $6M | $46M |
| [Visakhapatnam](south-asia/India/Visakhapatnam/) | IN | `metro-4car` | 6 | 110 | 240 | 196 | 52% | $1.48bn | $6M | $49M |
| [Abha](west-asia/Saudi%20Arabia/Abha/) | SA | `light-metro-3car` | 3 | 45 | 70 | 68 | 34% | $432M | $6M | $18M |
| [Medina](west-asia/Saudi%20Arabia/Medina/) | SA | `metro-4car` | 5 | 104 | 211 | 171 | 47% | $1.31bn | $6M | $44M |
| [Lucknow](south-asia/India/Lucknow/) | IN | `metro-6car` | 6 | 164 | 375 | 297 | 31% | $2.33bn | $6M | $64M |
| [Vijayawada](south-asia/India/Vijayawada/) | IN | `metro-4car` | 6 | 94 | 225 | 184 | 58% | $1.40bn | $6M | $41M |
| [Mbarara](east-africa/Uganda/Mbarara/) | UG | `light-metro-3car` | 3 | 36 | 59 | 59 | 53% | $364M | $6M | $15M |
| [Conakry](west-africa/Guinea/Conakry/) | GN | `metro-4car` | 3 | 55 | 93 | 78 | 40% | $579M | $6M | $25M |
| [Gazipur](south-asia/Bangladesh/Gazipur/) | BD | `metro-4car` | 6 | 127 | 308 | 245 | 38% | $1.92bn | $6M | $52M |
| [Chimoio](east-africa/Mozambique/Chimoio/) | MZ | `light-metro-3car` | 2 | 20 | 35 | 35 | 55% | $215M | $6M | $8M |
| [Nampula](east-africa/Mozambique/Nampula/) | MZ | `light-metro-3car` | 3 | 30 | 52 | 54 | 67% | $322M | $6M | $12M |
| [Kanpur](south-asia/India/Kanpur/) | IN | `metro-6car` | 7 | 150 | 339 | 273 | 44% | $2.11bn | $6M | $61M |
| [Damanhur](west-asia/Egypt/Damanhur/) | EG | `light-metro-3car` | 3 | 22 | 41 | 44 | 77% | $258M | $6M | $10M |
| [Damascus](west-asia/Syria/Damascus/) | SY | `metro-4car` | 6 | 113 | 233 | 192 | 45% | $1.45bn | $6M | $51M |
| [Onitsha](west-africa/Nigeria/Onitsha/) | NG | `metro-4car` | 4 | 76 | 184 | 148 | 30% | $1.15bn | $6M | $31M |
| [Nelspruit](south-africa/South%20Africa/Nelspruit/) | ZA | `tram-2car` | 3 | 22 | 39 | 53 | 68% | $246M | $6M | $10M |
| [Baqubah](west-asia/Iraq/Baqubah/) | IQ | `light-metro-3car` | 3 | 37 | 60 | 60 | 50% | $376M | $6M | $16M |
| [El Obeid](north-africa/Sudan/El-Obeid/) | SD | `light-metro-3car` | 3 | 28 | 46 | 47 | 72% | $289M | $6M | $11M |
| [East London Za](south-africa/South%20Africa/East-London-Za/) | ZA | `light-metro-3car` | 3 | 36 | 63 | 63 | 51% | $398M | $6M | $13M |
| [Ouagadougou](west-africa/Burkina%20Faso/Ouagadougou/) | BF | `metro-4car` | 6 | 138 | 264 | 213 | 37% | $1.66bn | $6M | $64M |
| [Idlib](west-asia/Syria/Idlib/) | SY | `tram-2car` | 3 | 18 | 35 | 49 | 79% | $220M | $6M | $8M |
| [Sulaymaniyah](west-asia/Iraq/Sulaymaniyah/) | IQ | `metro-4car` | 4 | 59 | 127 | 106 | 49% | $802M | $6M | $25M |
| [Meknes](north-africa/Morocco/Meknes/) | MA | `light-metro-3car` | 3 | 23 | 39 | 42 | 58% | $250M | $6M | $10M |
| [Beira](east-africa/Mozambique/Beira/) | MZ | `light-metro-3car` | 3 | 39 | 54 | 54 | 37% | $341M | $6M | $17M |
| [Zanzibar City](east-africa/Tanzania/Zanzibar-City/) | TZ | `light-metro-3car` | 3 | 32 | 56 | 56 | 70% | $357M | $6M | $12M |
| [Baghdad](west-asia/Iraq/Baghdad/) | IQ | `metro-6car` | 9 | 218 | 509 | 408 | 45% | $3.23bn | $6M | $90M |
| [Cuenca](latin-america/Ecuador/Cuenca/) | EC | `light-metro-3car` | 3 | 48 | 79 | 77 | 57% | $498M | $6M | $21M |
| [Homs](west-asia/Syria/Homs/) | SY | `light-metro-3car` | 3 | 33 | 51 | 53 | 42% | $326M | $6M | $14M |
| [Minya](west-asia/Egypt/Minya/) | EG | `light-metro-3car` | 3 | 32 | 53 | 53 | 69% | $339M | $6M | $12M |
| [Kumba](west-africa/Cameroon/Kumba/) | CM | `light-metro-3car` | 3 | 29 | 43 | 45 | 68% | $270M | $6M | $12M |
| [Mahalla](west-asia/Egypt/Mahalla/) | EG | `light-metro-3car` | 3 | 22 | 38 | 42 | 69% | $241M | $6M | $9M |
| [Dar Es Salaam](east-africa/Tanzania/Dar-Es-Salaam/) | TZ | `metro-6car` | 7 | 163 | 393 | 314 | 28% | $2.51bn | $6M | $62M |
| [Rubavu](east-africa/Rwanda/Rubavu/) | RW | `tram-2car` | 3 | 28 | 45 | 61 | 48% | $289M | $6M | $12M |
| [Nador](north-africa/Morocco/Nador/) | MA | `tram-2car` | 3 | 19 | 34 | 48 | 70% | $220M | $6M | $9M |
| [Arish](west-asia/Egypt/Arish/) | EG | `tram-2car` | 1 | 7 | 13 | 18 | 44% | $83M | $6M | $3M |
| [Mogadishu](east-africa/Somalia/Mogadishu/) | SO | `metro-4car` | 4 | 68 | 128 | 106 | 40% | $820M | $6M | $31M |
| [Agra](south-asia/India/Agra/) | IN | `metro-4car` | 5 | 98 | 191 | 156 | 39% | $1.22bn | $6M | $45M |
| [Multan](south-asia/Pakistan/Multan/) | PK | `metro-4car` | 4 | 64 | 115 | 98 | 42% | $739M | $6M | $31M |
| [Colombo](south-asia/Sri%20Lanka/Colombo/) | LK | `metro-6car` | 6 | 126 | 278 | 223 | 42% | $1.78bn | $6M | $51M |
| [Fort Portal](east-africa/Uganda/Fort-Portal/) | UG | `tram-2car` | 3 | 21 | 36 | 51 | 84% | $233M | $6M | $10M |
| [Arua](east-africa/Uganda/Arua/) | UG | `tram-2car` | 3 | 23 | 37 | 51 | 78% | $238M | $6M | $11M |
| [Luanda](east-africa/Angola/Luanda/) | AO | `metro-6car` | 9 | 170 | 390 | 317 | 64% | $2.51bn | $6M | $71M |
| [Lusaka](east-africa/Zambia/Lusaka/) | ZM | `metro-6car` | 6 | 123 | 236 | 192 | 34% | $1.52bn | $6M | $53M |
| [Kananga](central-africa/DR%20Congo/Kananga/) | CD | `metro-4car` | 2 | 18 | 38 | 34 | 73% | $247M | $6M | $8M |
| [Tanga](east-africa/Tanzania/Tanga/) | TZ | `light-metro-3car` | 3 | 27 | 48 | 50 | 72% | $312M | $6M | $12M |
| [Luxor](west-asia/Egypt/Luxor/) | EG | `light-metro-3car` | 3 | 34 | 54 | 54 | 73% | $348M | $6M | $15M |
| [Mandalay](southeast-asia/Myanmar/Mandalay/) | MM | `metro-4car` | 6 | 88 | 187 | 156 | 60% | $1.21bn | $6M | $42M |
| [Polokwane](south-africa/South%20Africa/Polokwane/) | ZA | `light-metro-3car` | 3 | 34 | 52 | 52 | 60% | $334M | $6M | $15M |
| [Uige](east-africa/Angola/Uige/) | AO | `light-metro-3car` | 1 | 8 | 13 | 14 | 67% | $84M | $6M | $4M |
| [Duhok](west-asia/Iraq/Duhok/) | IQ | `light-metro-3car` | 3 | 32 | 53 | 54 | 53% | $345M | $6M | $15M |
| [Mansoura Eg](west-asia/Egypt/Mansoura-Eg/) | EG | `light-metro-3car` | 3 | 34 | 56 | 56 | 54% | $364M | $6M | $15M |
| [Kinshasa](central-africa/DR%20Congo/Kinshasa/) | CD | `metro-6car` | 8 | 183 | 385 | 310 | 49% | $2.51bn | $7M | $82M |
| [Jeddah](west-asia/Saudi%20Arabia/Jeddah/) | SA | `metro-6car` | 8 | 202 | 406 | 326 | 45% | $2.64bn | $7M | $93M |
| [Songea](east-africa/Tanzania/Songea/) | TZ | `tram-2car` | 1 | 7 | 11 | 16 | 73% | $75M | $7M | $3M |
| [Hyderabad Pk](south-asia/Pakistan/Hyderabad-Pk/) | PK | `metro-4car` | 6 | 84 | 182 | 152 | 61% | $1.19bn | $7M | $38M |
| [Raipur](south-asia/India/Raipur/) | IN | `metro-4car` | 5 | 88 | 185 | 151 | 43% | $1.21bn | $7M | $37M |
| [Goma](central-africa/DR%20Congo/Goma/) | CD | `light-metro-3car` | 3 | 39 | 58 | 58 | 60% | $381M | $7M | $17M |
| [Mbeya](east-africa/Tanzania/Mbeya/) | TZ | `light-metro-3car` | 3 | 39 | 55 | 55 | 44% | $361M | $7M | $18M |
| [Kandy](south-asia/Sri%20Lanka/Kandy/) | LK | `light-metro-3car` | 3 | 43 | 78 | 76 | 56% | $511M | $7M | $16M |
| [Naivasha](east-africa/Kenya/Naivasha/) | KE | `tram-2car` | 3 | 20 | 33 | 48 | 86% | $216M | $7M | $9M |
| [Indore](south-asia/India/Indore/) | IN | `metro-6car` | 7 | 146 | 324 | 260 | 48% | $2.13bn | $7M | $62M |
| [Malindi](east-africa/Kenya/Malindi/) | KE | `tram-2car` | 3 | 20 | 29 | 44 | 79% | $194M | $7M | $9M |
| [Vadodara](south-asia/India/Vadodara/) | IN | `metro-4car` | 5 | 89 | 164 | 137 | 48% | $1.08bn | $7M | $43M |
| [Hoima](east-africa/Uganda/Hoima/) | UG | `tram-2car` | 3 | 19 | 31 | 45 | 84% | $206M | $7M | $9M |
| [Morogoro](east-africa/Tanzania/Morogoro/) | TZ | `light-metro-3car` | 3 | 32 | 55 | 55 | 61% | $363M | $7M | $13M |
| [Kisangani](central-africa/DR%20Congo/Kisangani/) | CD | `metro-4car` | 2 | 27 | 47 | 40 | 64% | $312M | $7M | $13M |
| [Masaka](east-africa/Uganda/Masaka/) | UG | `tram-2car` | 3 | 20 | 32 | 46 | 56% | $212M | $7M | $9M |
| [Beirut](west-asia/Lebanon/Beirut/) | LB | `metro-4car` | 6 | 83 | 159 | 134 | 70% | $1.05bn | $7M | $40M |
| [Aden](west-asia/Yemen/Aden/) | YE | `light-metro-3car` | 3 | 28 | 44 | 46 | 43% | $293M | $7M | $12M |
| [Durban](south-africa/South%20Africa/Durban/) | ZA | `metro-6car` | 9 | 172 | 401 | 325 | 79% | $2.66bn | $7M | $75M |
| [Taiz](west-asia/Yemen/Taiz/) | YE | `light-metro-3car` | 3 | 33 | 49 | 51 | 55% | $325M | $7M | $15M |
| [Bhopal](south-asia/India/Bhopal/) | IN | `metro-4car` | 6 | 107 | 206 | 169 | 52% | $1.37bn | $7M | $51M |
| [Dakar](west-africa/Senegal/Dakar/) | SN | `metro-6car` | 5 | 107 | 204 | 167 | 52% | $1.36bn | $7M | $47M |
| [Narayanganj](south-asia/Bangladesh/Narayanganj/) | BD | `light-metro-3car` | 3 | 50 | 82 | 80 | 27% | $546M | $7M | $18M |
| [Entebbe](east-africa/Uganda/Entebbe/) | UG | `tram-2car` | 3 | 28 | 43 | 59 | 70% | $288M | $7M | $13M |
| [Nacala](east-africa/Mozambique/Nacala/) | MZ | `tram-2car` | 3 | 25 | 39 | 54 | 80% | $260M | $7M | $11M |
| [Peshawar](south-asia/Pakistan/Peshawar/) | PK | `metro-4car` | 4 | 87 | 197 | 158 | 33% | $1.31bn | $7M | $35M |
| [Jos](west-africa/Nigeria/Jos/) | NG | `light-metro-3car` | 3 | 40 | 54 | 55 | 26% | $360M | $7M | $17M |
| [Bahawalpur](south-asia/Pakistan/Bahawalpur/) | PK | `light-metro-3car` | 3 | 29 | 46 | 49 | 42% | $309M | $7M | $14M |
| [Raqqa](west-asia/Syria/Raqqa/) | SY | `light-metro-3car` | 3 | 25 | 45 | 46 | 86% | $301M | $7M | $11M |
| [Karachi](south-asia/Pakistan/Karachi/) | PK | `metro-6car` | 9 | 231 | 472 | 377 | 48% | $3.17bn | $7M | $100M |
| [Bandung](southeast-asia/Indonesia/Bandung/) | ID | `metro-4car` | 6 | 126 | 257 | 208 | 41% | $1.73bn | $7M | $57M |
| [Coimbatore](south-asia/India/Coimbatore/) | IN | `metro-6car` | 5 | 121 | 268 | 214 | 31% | $1.81bn | $7M | $51M |
| [Quetta](south-asia/Pakistan/Quetta/) | PK | `metro-4car` | 5 | 78 | 140 | 120 | 54% | $947M | $7M | $39M |
| [Sidon](west-asia/Lebanon/Sidon/) | LB | `tram-2car` | 3 | 23 | 37 | 52 | 71% | $251M | $7M | $11M |
| [Lobito](east-africa/Angola/Lobito/) | AO | `light-metro-3car` | 3 | 25 | 38 | 41 | 69% | $255M | $7M | $12M |
| [Herat](south-asia/Afghanistan/Herat/) | AF | `light-metro-3car` | 3 | 43 | 65 | 64 | 36% | $438M | $7M | $19M |
| [Kisii](east-africa/Kenya/Kisii/) | KE | `tram-2car` | 3 | 17 | 30 | 43 | 67% | $200M | $7M | $8M |
| [Fez](north-africa/Morocco/Fez/) | MA | `metro-4car` | 4 | 58 | 113 | 94 | 73% | $764M | $7M | $28M |
| [Amman](west-asia/Jordan/Amman/) | JO | `metro-6car` | 8 | 172 | 354 | 286 | 51% | $2.40bn | $7M | $76M |
| [Antananarivo](east-africa/Madagascar/Antananarivo/) | MG | `metro-6car` | 7 | 155 | 339 | 272 | 42% | $2.31bn | $7M | $65M |
| [Quelimane](east-africa/Mozambique/Quelimane/) | MZ | `light-metro-3car` | 1 | 6 | 10 | 12 | 48% | $70M | $7M | $3M |
| [Chittagong](south-asia/Bangladesh/Chittagong/) | BD | `metro-6car` | 8 | 161 | 374 | 302 | 64% | $2.55bn | $7M | $71M |
| [Ramadi](west-asia/Iraq/Ramadi/) | IQ | `light-metro-3car` | 3 | 35 | 47 | 49 | 39% | $321M | $7M | $17M |
| [Garissa](east-africa/Kenya/Garissa/) | KE | `tram-2car` | 3 | 19 | 29 | 43 | 71% | $197M | $7M | $9M |
| [Oujda](north-africa/Morocco/Oujda/) | MA | `light-metro-3car` | 3 | 33 | 47 | 48 | 48% | $322M | $7M | $16M |
| [Port Sudan](north-africa/Sudan/Port-Sudan/) | SD | `light-metro-3car` | 3 | 22 | 33 | 38 | 80% | $229M | $7M | $10M |
| [Kirkuk](west-asia/Iraq/Kirkuk/) | IQ | `metro-4car` | 6 | 92 | 170 | 142 | 60% | $1.17bn | $7M | $45M |
| [Karbala](west-asia/Iraq/Karbala/) | IQ | `metro-4car` | 6 | 89 | 170 | 144 | 67% | $1.17bn | $7M | $44M |
| [Rajkot](south-asia/India/Rajkot/) | IN | `metro-4car` | 5 | 76 | 143 | 121 | 58% | $984M | $7M | $36M |
| [Fallujah](west-asia/Iraq/Fallujah/) | IQ | `light-metro-3car` | 3 | 28 | 46 | 48 | 57% | $317M | $7M | $13M |
| [Safi](north-africa/Morocco/Safi/) | MA | `light-metro-3car` | 3 | 26 | 39 | 43 | 72% | $271M | $7M | $12M |
| [Sohag](west-asia/Egypt/Sohag/) | EG | `light-metro-3car` | 3 | 32 | 60 | 60 | 68% | $417M | $7M | $13M |
| [Basra](west-asia/Iraq/Basra/) | IQ | `metro-6car` | 7 | 119 | 289 | 236 | 54% | $2.01bn | $7M | $48M |
| [Uyo](west-africa/Nigeria/Uyo/) | NG | `light-metro-3car` | 3 | 24 | 31 | 36 | 25% | $216M | $7M | $12M |
| [Barisal](south-asia/Bangladesh/Barisal/) | BD | `light-metro-3car` | 3 | 30 | 59 | 60 | 50% | $408M | $7M | $12M |
| [Yaounde](east-africa/Cameroon/Yaounde/) | CM | `metro-6car` | 8 | 136 | 267 | 219 | 43% | $1.85bn | $7M | $63M |
| [Khulna](south-asia/Bangladesh/Khulna/) | BD | `metro-4car` | 6 | 82 | 182 | 152 | 57% | $1.27bn | $7M | $37M |
| [Tabuk](west-asia/Saudi%20Arabia/Tabuk/) | SA | `light-metro-3car` | 3 | 45 | 63 | 63 | 27% | $438M | $7M | $20M |
| [Varanasi](south-asia/India/Varanasi/) | IN | `metro-4car` | 5 | 100 | 202 | 165 | 47% | $1.41bn | $7M | $43M |
| [Surabaya](southeast-asia/Indonesia/Surabaya/) | ID | `metro-6car` | 7 | 143 | 294 | 240 | 40% | $2.06bn | $7M | $61M |
| [Maroua](west-africa/Cameroon/Maroua/) | CM | `light-metro-3car` | 3 | 29 | 53 | 54 | 74% | $367M | $7M | $12M |
| [Port Said](west-asia/Egypt/Port-Said/) | EG | `light-metro-3car` | 3 | 25 | 35 | 39 | 71% | $244M | $7M | $12M |
| [Yangon](southeast-asia/Myanmar/Yangon/) | MM | `metro-6car` | 9 | 214 | 418 | 335 | 56% | $2.94bn | $7M | $102M |
| [Patna](south-asia/India/Patna/) | IN | `metro-4car` | 5 | 84 | 185 | 152 | 50% | $1.31bn | $7M | $36M |
| [Qena](west-asia/Egypt/Qena/) | EG | `light-metro-3car` | 3 | 26 | 45 | 47 | 75% | $319M | $7M | $12M |
| [Kabul](south-asia/Afghanistan/Kabul/) | AF | `metro-6car` | 7 | 137 | 261 | 215 | 53% | $1.85bn | $7M | $63M |
| [La Paz](latin-america/Bolivia/La-Paz/) | BO | `metro-4car` | 6 | 115 | 212 | 174 | 57% | $1.51bn | $7M | $55M |
| [Machakos](east-africa/Kenya/Machakos/) | KE | `tram-2car` | 3 | 16 | 27 | 40 | 76% | $188M | $7M | $8M |
| [Kafr El Sheikh](west-asia/Egypt/Kafr-El-Sheikh/) | EG | `tram-2car` | 3 | 22 | 33 | 47 | 75% | $235M | $7M | $11M |
| [Mosul](west-asia/Iraq/Mosul/) | IQ | `metro-4car` | 5 | 60 | 145 | 122 | 38% | $1.03bn | $7M | $23M |
| [Sanaa](west-asia/Yemen/Sanaa/) | YE | `metro-6car` | 9 | 126 | 261 | 218 | 78% | $1.86bn | $7M | $61M |
| [Lubumbashi](central-africa/DR%20Congo/Lubumbashi/) | CD | `metro-4car` | 4 | 75 | 130 | 107 | 34% | $925M | $7M | $39M |
| [Beni Suef](west-asia/Egypt/Beni-Suef/) | EG | `light-metro-3car` | 3 | 23 | 35 | 38 | 55% | $250M | $7M | $11M |
| [Bertoua](west-africa/Cameroon/Bertoua/) | CM | `light-metro-3car` | 3 | 20 | 29 | 34 | 77% | $206M | $7M | $10M |
| [Beni Mellal](north-africa/Morocco/Beni-Mellal/) | MA | `tram-2car` | 3 | 18 | 30 | 45 | 85% | $217M | $7M | $9M |
| [Phnom Penh](southeast-asia/Cambodia/Phnom-Penh/) | KH | `metro-4car` | 6 | 107 | 228 | 186 | 48% | $1.63bn | $7M | $47M |
| [Deir Ez Zor](west-asia/Syria/Deir-Ez-Zor/) | SY | `light-metro-3car` | 3 | 32 | 57 | 57 | 62% | $407M | $7M | $14M |
| [Kathmandu](south-asia/Nepal/Kathmandu/) | NP | `metro-4car` | 6 | 103 | 203 | 167 | 46% | $1.47bn | $7M | $51M |
| [Kano](west-africa/Nigeria/Kano/) | NG | `metro-6car` | 6 | 154 | 362 | 286 | 37% | $2.62bn | $7M | $57M |
| [Edea](west-africa/Cameroon/Edea/) | CM | `tram-2car` | 1 | 7 | 10 | 14 | 61% | $70M | $7M | $4M |
| [Diwaniyah](west-asia/Iraq/Diwaniyah/) | IQ | `light-metro-3car` | 3 | 36 | 54 | 55 | 43% | $390M | $7M | $16M |
| [Tetouan](north-africa/Morocco/Tetouan/) | MA | `light-metro-3car` | 3 | 33 | 54 | 56 | 69% | $393M | $7M | $14M |
| [Pemba Mz](east-africa/Mozambique/Pemba-Mz/) | MZ | `tram-2car` | 3 | 20 | 30 | 43 | 63% | $220M | $7M | $10M |
| [Sayun](west-asia/Yemen/Sayun/) | YE | `tram-2car` | 2 | 15 | 22 | 31 | 58% | $157M | $7M | $7M |
| [Hurghada](west-asia/Egypt/Hurghada/) | EG | `tram-2car` | 3 | 28 | 43 | 57 | 56% | $314M | $7M | $13M |
| [Hodeidah](west-asia/Yemen/Hodeidah/) | YE | `light-metro-3car` | 3 | 27 | 36 | 40 | 61% | $266M | $7M | $13M |
| [Waw](north-africa/Sudan/Waw/) | SD | `tram-2car` | 2 | 11 | 18 | 27 | 73% | $132M | $7M | $6M |
| [Xai Xai](east-africa/Mozambique/Xai-Xai/) | MZ | `tram-2car` | 2 | 12 | 18 | 27 | 43% | $133M | $7M | $6M |
| [Soyo](east-africa/Angola/Soyo/) | AO | `tram-2car` | 2 | 14 | 22 | 32 | 70% | $166M | $7M | $7M |
| [Faisalabad](south-asia/Pakistan/Faisalabad/) | PK | `metro-6car` | 5 | 93 | 166 | 137 | 52% | $1.23bn | $7M | $45M |
| [Douala](west-africa/Cameroon/Douala/) | CM | `metro-6car` | 5 | 129 | 228 | 184 | 37% | $1.69bn | $7M | $59M |
| [Kitale](east-africa/Kenya/Kitale/) | KE | `tram-2car` | 3 | 16 | 29 | 43 | 85% | $219M | $7M | $8M |
| [Benin City](west-africa/Nigeria/Benin-City/) | NG | `metro-4car` | 4 | 77 | 132 | 111 | 44% | $988M | $7M | $40M |
| [Tartus](west-asia/Syria/Tartus/) | SY | `tram-2car` | 3 | 23 | 35 | 49 | 73% | $263M | $8M | $11M |
| [Maiduguri](west-africa/Nigeria/Maiduguri/) | NG | `metro-4car` | 5 | 86 | 176 | 145 | 34% | $1.33bn | $8M | $38M |
| [Nyala](north-africa/Sudan/Nyala/) | SD | `light-metro-3car` | 3 | 29 | 47 | 48 | 61% | $352M | $8M | $11M |
| [Ibadan](west-africa/Nigeria/Ibadan/) | NG | `metro-6car` | 4 | 90 | 135 | 111 | 24% | $1.02bn | $8M | $44M |
| [Lahij](west-asia/Yemen/Lahij/) | YE | `tram-2car` | 3 | 19 | 29 | 43 | 82% | $221M | $8M | $10M |
| [Aba Ng](west-africa/Nigeria/Aba-Ng/) | NG | `light-metro-3car` | 3 | 26 | 34 | 38 | 40% | $262M | $8M | $13M |
| [Ngaoundere](west-africa/Cameroon/Ngaoundere/) | CM | `light-metro-3car` | 3 | 19 | 28 | 34 | 57% | $217M | $8M | $9M |
| [Najaf](west-asia/Iraq/Najaf/) | IQ | `metro-4car` | 6 | 91 | 172 | 144 | 60% | $1.34bn | $8M | $46M |
| [Najran](west-asia/Saudi%20Arabia/Najran/) | SA | `light-metro-3car` | 3 | 33 | 57 | 57 | 46% | $441M | $8M | $13M |
| [Iringa](east-africa/Tanzania/Iringa/) | TZ | `tram-2car` | 3 | 20 | 28 | 42 | 67% | $217M | $8M | $10M |
| [Meru Ke](east-africa/Kenya/Meru-Ke/) | KE | `tram-2car` | 2 | 12 | 22 | 32 | 52% | $176M | $8M | $5M |
| [Zarqa](west-asia/Jordan/Zarqa/) | JO | `light-metro-3car` | 3 | 57 | 83 | 80 | 48% | $672M | $8M | $24M |
| [Moshi](east-africa/Tanzania/Moshi/) | TZ | `tram-2car` | 3 | 21 | 36 | 51 | 76% | $290M | $8M | $11M |
| [Sumbawanga](east-africa/Tanzania/Sumbawanga/) | TZ | `tram-2car` | 1 | 5 | 7 | 11 | 35% | $54M | $8M | $3M |
| [Khouribga](north-africa/Morocco/Khouribga/) | MA | `tram-2car` | 2 | 11 | 15 | 23 | 57% | $123M | $8M | $6M |
| [Tabora](east-africa/Tanzania/Tabora/) | TZ | `tram-2car` | 2 | 13 | 18 | 26 | 54% | $152M | $9M | $7M |
| [Bamako](west-africa/Mali/Bamako/) | ML | `metro-4car` | 6 | 118 | 257 | 207 | 31% | $2.24bn | $9M | $47M |
| [Kut](west-asia/Iraq/Kut/) | IQ | `light-metro-3car` | 3 | 32 | 56 | 55 | 37% | $496M | $9M | $14M |
| [Nasiriyah](west-asia/Iraq/Nasiriyah/) | IQ | `light-metro-3car` | 3 | 33 | 56 | 56 | 40% | $506M | $9M | $15M |
| [Kassala](north-africa/Sudan/Kassala/) | SD | `light-metro-3car` | 3 | 20 | 34 | 39 | 76% | $312M | $9M | $9M |
| [Larkana](south-asia/Pakistan/Larkana/) | PK | `light-metro-3car` | 2 | 19 | 38 | 39 | 28% | $343M | $9M | $9M |
| [Garoua](west-africa/Cameroon/Garoua/) | CM | `light-metro-3car` | 3 | 29 | 44 | 46 | 38% | $405M | $9M | $12M |
| [Amarah](west-asia/Iraq/Amarah/) | IQ | `light-metro-3car` | 3 | 32 | 45 | 46 | 43% | $419M | $9M | $15M |
| [Tete](east-africa/Mozambique/Tete/) | MZ | `light-metro-3car` | 3 | 23 | 38 | 41 | 77% | $359M | $9M | $9M |
| [Malanje](east-africa/Angola/Malanje/) | AO | `light-metro-3car` | 2 | 12 | 15 | 19 | 57% | $142M | $9M | $7M |
| [Sheikhupura](south-asia/Pakistan/Sheikhupura/) | PK | `light-metro-3car` | 2 | 17 | 19 | 22 | 32% | $181M | $9M | $9M |
| [Jodhpur](south-asia/India/Jodhpur/) | IN | `metro-4car` | 5 | 82 | 150 | 124 | 44% | $1.44bn | $10M | $37M |
| [Nyeri](east-africa/Kenya/Nyeri/) | KE | `tram-2car` | 3 | 22 | 37 | 51 | 62% | $359M | $10M | $10M |
| [Mymensingh](south-asia/Bangladesh/Mymensingh/) | BD | `light-metro-3car` | 3 | 37 | 67 | 67 | 41% | $664M | $10M | $13M |
| [Sialkot](south-asia/Pakistan/Sialkot/) | PK | `light-metro-3car` | 3 | 37 | 59 | 59 | 43% | $649M | $11M | $16M |
| [Sukkur](south-asia/Pakistan/Sukkur/) | PK | `light-metro-3car` | 3 | 31 | 51 | 53 | 55% | $592M | $12M | $13M |
| [Biratnagar](south-asia/Nepal/Biratnagar/) | NP | `tram-2car` | 3 | 23 | 34 | 48 | 60% | $538M | $16M | $10M |
