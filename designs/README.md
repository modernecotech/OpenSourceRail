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
| [Bafoussam](west-africa/Cameroon/Bafoussam/) | CM | `light-metro-3car` | 3 | 34 | 73 | 72 | 47% | $294M | $4M | $12M |
| [Fayoum](west-asia/Egypt/Fayoum/) | EG | `light-metro-3car` | 3 | 36 | 69 | 67 | 72% | $293M | $4M | $14M |
| [Tanta](west-asia/Egypt/Tanta/) | EG | `light-metro-3car` | 3 | 35 | 75 | 73 | 56% | $327M | $4M | $14M |
| [Hofuf](west-asia/Saudi%20Arabia/Hofuf/) | SA | `light-metro-3car` | 3 | 46 | 78 | 77 | 50% | $342M | $4M | $18M |
| [Agadir](north-africa/Morocco/Agadir/) | MA | `light-metro-3car` | 3 | 44 | 83 | 80 | 65% | $363M | $4M | $17M |
| [Huye](east-africa/Rwanda/Huye/) | RW | `tram-2car` | 3 | 28 | 46 | 61 | 23% | $203M | $4M | $10M |
| [Bamenda](west-africa/Cameroon/Bamenda/) | CM | `light-metro-3car` | 3 | 31 | 54 | 55 | 59% | $239M | $4M | $12M |
| [Omdurman](north-africa/Sudan/Omdurman/) | SD | `metro-4car` | 6 | 104 | 255 | 207 | 47% | $1.13bn | $4M | $41M |
| [Arusha](east-africa/Tanzania/Arusha/) | TZ | `light-metro-3car` | 3 | 44 | 73 | 72 | 36% | $327M | $5M | $16M |
| [Dammam](west-asia/Saudi%20Arabia/Dammam/) | SA | `metro-4car` | 4 | 95 | 210 | 168 | 28% | $945M | $5M | $39M |
| [Kenitra](north-africa/Morocco/Kenitra/) | MA | `light-metro-3car` | 3 | 35 | 60 | 60 | 66% | $271M | $5M | $14M |
| [Vientiane](southeast-asia/Laos/Vientiane/) | LA | `light-metro-3car` | 3 | 46 | 81 | 78 | 43% | $366M | $5M | $18M |
| [Kisumu](east-africa/Kenya/Kisumu/) | KE | `light-metro-3car` | 3 | 42 | 75 | 74 | 31% | $342M | $5M | $14M |
| [Lyon](europe/France/Lyon/) | FR | `metro-4car` | 6 | 122 | 287 | 232 | 45% | $1.30bn | $5M | $49M |
| [Hail](west-asia/Saudi%20Arabia/Hail/) | SA | `light-metro-3car` | 3 | 35 | 63 | 62 | 47% | $287M | $5M | $13M |
| [Damietta](west-asia/Egypt/Damietta/) | EG | `light-metro-3car` | 3 | 38 | 74 | 73 | 72% | $334M | $5M | $13M |
| [Khamis Mushait](west-asia/Saudi%20Arabia/Khamis-Mushait/) | SA | `light-metro-3car` | 3 | 38 | 69 | 68 | 35% | $314M | $5M | $14M |
| [Nablus](west-asia/Palestine/Nablus/) | PS | `light-metro-3car` | 3 | 34 | 65 | 65 | 84% | $295M | $5M | $13M |
| [Bukavu](central-africa/DR%20Congo/Bukavu/) | CD | `light-metro-3car` | 3 | 37 | 60 | 60 | 60% | $276M | $5M | $15M |
| [Asyut](west-asia/Egypt/Asyut/) | EG | `light-metro-3car` | 3 | 31 | 63 | 62 | 58% | $289M | $5M | $11M |
| [Rahim Yar Khan](south-asia/Pakistan/Rahim-Yar-Khan/) | PK | `light-metro-3car` | 3 | 24 | 46 | 47 | 37% | $213M | $5M | $10M |
| [Tangier](north-africa/Morocco/Tangier/) | MA | `metro-4car` | 5 | 64 | 153 | 129 | 57% | $711M | $5M | $25M |
| [Port Harcourt](west-africa/Nigeria/Port-Harcourt/) | NG | `metro-4car` | 4 | 95 | 199 | 160 | 31% | $925M | $5M | $39M |
| [Hebron](west-asia/Palestine/Hebron/) | PS | `light-metro-3car` | 3 | 40 | 69 | 68 | 61% | $322M | $5M | $16M |
| [Kampala](east-africa/Uganda/Kampala/) | UG | `metro-4car` | 4 | 99 | 201 | 160 | 24% | $938M | $5M | $41M |
| [Dodoma](east-africa/Tanzania/Dodoma/) | TZ | `light-metro-3car` | 3 | 36 | 66 | 66 | 40% | $309M | $5M | $14M |
| [Mwanza](east-africa/Tanzania/Mwanza/) | TZ | `metro-4car` | 5 | 70 | 162 | 136 | 45% | $756M | $5M | $29M |
| [Hama](west-asia/Syria/Hama/) | SY | `light-metro-3car` | 3 | 31 | 55 | 55 | 53% | $259M | $5M | $13M |
| [Gulu](east-africa/Uganda/Gulu/) | UG | `light-metro-3car` | 3 | 36 | 64 | 63 | 50% | $299M | $5M | $15M |
| [Al Kharj](west-asia/Saudi%20Arabia/Al-Kharj/) | SA | `light-metro-3car` | 3 | 38 | 68 | 67 | 70% | $318M | $5M | $14M |
| [Taif](west-asia/Saudi%20Arabia/Taif/) | SA | `light-metro-3car` | 3 | 42 | 73 | 73 | 41% | $345M | $5M | $17M |
| [Galle](south-asia/Sri%20Lanka/Galle/) | LK | `light-metro-3car` | 3 | 37 | 64 | 64 | 56% | $303M | $5M | $15M |
| [Sylhet](south-asia/Bangladesh/Sylhet/) | BD | `light-metro-3car` | 3 | 40 | 73 | 72 | 45% | $343M | $5M | $14M |
| [Bloemfontein](south-africa/South%20Africa/Bloemfontein/) | ZA | `light-metro-3car` | 3 | 42 | 72 | 71 | 35% | $341M | $5M | $16M |
| [Eldoret](east-africa/Kenya/Eldoret/) | KE | `light-metro-3car` | 3 | 39 | 65 | 64 | 46% | $310M | $5M | $16M |
| [Rajshahi](south-asia/Bangladesh/Rajshahi/) | BD | `light-metro-3car` | 3 | 30 | 50 | 52 | 30% | $237M | $5M | $12M |
| [Lira](east-africa/Uganda/Lira/) | UG | `tram-2car` | 3 | 23 | 45 | 61 | 64% | $216M | $5M | $10M |
| [Nakuru](east-africa/Kenya/Nakuru/) | KE | `light-metro-3car` | 3 | 37 | 60 | 61 | 46% | $284M | $5M | $14M |
| [Thika](east-africa/Kenya/Thika/) | KE | `light-metro-3car` | 3 | 38 | 76 | 74 | 63% | $361M | $5M | $13M |
| [Gaza City](west-asia/Palestine/Gaza-City/) | PS | `light-metro-3car` | 1 | 15 | 24 | 24 | 30% | $114M | $5M | $6M |
| [Tripoli Lb](west-asia/Lebanon/Tripoli-Lb/) | LB | `light-metro-3car` | 3 | 30 | 53 | 55 | 50% | $253M | $5M | $12M |
| [Zagazig](west-asia/Egypt/Zagazig/) | EG | `light-metro-3car` | 3 | 30 | 56 | 57 | 59% | $269M | $5M | $13M |
| [Lubango](east-africa/Angola/Lubango/) | AO | `light-metro-3car` | 3 | 31 | 55 | 55 | 63% | $261M | $5M | $12M |
| [Rangpur](south-asia/Bangladesh/Rangpur/) | BD | `light-metro-3car` | 3 | 36 | 59 | 59 | 47% | $285M | $5M | $14M |
| [Kigali](east-africa/Rwanda/Kigali/) | RW | `metro-4car` | 4 | 86 | 171 | 139 | 34% | $819M | $5M | $37M |
| [Gujranwala](south-asia/Pakistan/Gujranwala/) | PK | `metro-4car` | 4 | 72 | 160 | 130 | 39% | $771M | $5M | $30M |
| [Mombasa](east-africa/Kenya/Mombasa/) | KE | `metro-4car` | 6 | 95 | 201 | 167 | 52% | $967M | $5M | $42M |
| [Erbil](west-asia/Iraq/Erbil/) | IQ | `metro-4car` | 6 | 97 | 199 | 166 | 42% | $961M | $5M | $45M |
| [Mecca](west-asia/Saudi%20Arabia/Mecca/) | SA | `metro-4car` | 6 | 114 | 251 | 205 | 46% | $1.21bn | $5M | $49M |
| [Ibb](west-asia/Yemen/Ibb/) | YE | `light-metro-3car` | 3 | 40 | 72 | 71 | 58% | $345M | $5M | $17M |
| [Ranchi](south-asia/India/Ranchi/) | IN | `metro-4car` | 6 | 96 | 216 | 179 | 50% | $1.04bn | $5M | $40M |
| [Dhamar](west-asia/Yemen/Dhamar/) | YE | `tram-2car` | 3 | 18 | 32 | 46 | 76% | $156M | $5M | $8M |
| [Khartoum](north-africa/Sudan/Khartoum/) | SD | `metro-6car` | 5 | 152 | 363 | 287 | 22% | $1.75bn | $5M | $57M |
| [Aleppo](west-asia/Syria/Aleppo/) | SY | `metro-4car` | 5 | 89 | 176 | 145 | 46% | $850M | $5M | $40M |
| [Hillah](west-asia/Iraq/Hillah/) | IQ | `light-metro-3car` | 3 | 42 | 69 | 68 | 43% | $334M | $5M | $18M |
| [Davao](southeast-asia/Philippines/Davao/) | PH | `metro-4car` | 6 | 108 | 229 | 186 | 72% | $1.11bn | $5M | $50M |
| [Ilorin](west-africa/Nigeria/Ilorin/) | NG | `light-metro-3car` | 3 | 39 | 60 | 60 | 31% | $292M | $5M | $16M |
| [Pokhara](south-asia/Nepal/Pokhara/) | NP | `light-metro-3car` | 3 | 44 | 82 | 80 | 52% | $399M | $5M | $18M |
| [Namibe](east-africa/Angola/Namibe/) | AO | `tram-2car` | 3 | 25 | 40 | 55 | 61% | $195M | $5M | $11M |
| [Mukalla](west-asia/Yemen/Mukalla/) | YE | `light-metro-3car` | 3 | 33 | 61 | 61 | 72% | $296M | $5M | $14M |
| [Mbuji Mayi](central-africa/DR%20Congo/Mbuji-Mayi/) | CD | `metro-4car` | 4 | 55 | 118 | 101 | 70% | $576M | $5M | $25M |
| [San Salvador](latin-america/El%20Salvador/San-Salvador/) | SV | `metro-4car` | 6 | 121 | 255 | 207 | 50% | $1.24bn | $5M | $56M |
| [Comilla](south-asia/Bangladesh/Comilla/) | BD | `light-metro-3car` | 3 | 38 | 66 | 65 | 41% | $320M | $5M | $15M |
| [Marrakech](north-africa/Morocco/Marrakech/) | MA | `metro-4car` | 6 | 79 | 191 | 159 | 58% | $934M | $5M | $33M |
| [Maputo](east-africa/Mozambique/Maputo/) | MZ | `metro-4car` | 6 | 83 | 186 | 156 | 71% | $908M | $5M | $35M |
| [Suez](west-asia/Egypt/Suez/) | EG | `light-metro-3car` | 3 | 32 | 59 | 60 | 65% | $288M | $5M | $12M |
| [Nairobi](east-africa/Kenya/Nairobi/) | KE | `metro-6car` | 8 | 191 | 476 | 378 | 43% | $2.33bn | $5M | $73M |
| [Huambo](east-africa/Angola/Huambo/) | AO | `light-metro-3car` | 3 | 31 | 53 | 55 | 72% | $258M | $5M | $13M |
| [Shinyanga](east-africa/Tanzania/Shinyanga/) | TZ | `tram-2car` | 3 | 20 | 37 | 51 | 83% | $180M | $5M | $9M |
| [Meerut](south-asia/India/Meerut/) | IN | `metro-4car` | 4 | 84 | 180 | 146 | 43% | $882M | $5M | $36M |
| [Latakia](west-asia/Syria/Latakia/) | SY | `light-metro-3car` | 3 | 26 | 41 | 43 | 54% | $201M | $5M | $11M |
| [Buraidah](west-asia/Saudi%20Arabia/Buraidah/) | SA | `light-metro-3car` | 3 | 54 | 80 | 78 | 35% | $392M | $5M | $24M |
| [Tunis](north-africa/Tunisia/Tunis/) | TN | `metro-4car` | 5 | 118 | 240 | 194 | 48% | $1.18bn | $5M | $52M |
| [Benguela](east-africa/Angola/Benguela/) | AO | `light-metro-3car` | 3 | 28 | 50 | 51 | 69% | $246M | $5M | $11M |
| [Irbid](west-asia/Jordan/Irbid/) | JO | `light-metro-3car` | 3 | 33 | 56 | 56 | 42% | $277M | $5M | $15M |
| [Gazipur](south-asia/Bangladesh/Gazipur/) | BD | `metro-4car` | 6 | 127 | 308 | 245 | 38% | $1.52bn | $5M | $52M |
| [Visakhapatnam](south-asia/India/Visakhapatnam/) | IN | `metro-4car` | 6 | 110 | 240 | 196 | 52% | $1.19bn | $5M | $49M |
| [Jizan](west-asia/Saudi%20Arabia/Jizan/) | SA | `light-metro-3car` | 3 | 28 | 47 | 48 | 64% | $232M | $5M | $11M |
| [Onitsha](west-africa/Nigeria/Onitsha/) | NG | `metro-4car` | 4 | 76 | 184 | 148 | 30% | $912M | $5M | $31M |
| [Vijayawada](south-asia/India/Vijayawada/) | IN | `metro-4car` | 6 | 94 | 225 | 184 | 58% | $1.12bn | $5M | $41M |
| [Madurai](south-asia/India/Madurai/) | IN | `metro-4car` | 6 | 104 | 222 | 183 | 59% | $1.11bn | $5M | $46M |
| [Niamey](west-africa/Niger/Niamey/) | NE | `metro-4car` | 4 | 80 | 146 | 120 | 38% | $729M | $5M | $36M |
| [Medina](west-asia/Saudi%20Arabia/Medina/) | SA | `metro-4car` | 5 | 104 | 211 | 171 | 47% | $1.06bn | $5M | $44M |
| [Kandahar](south-asia/Afghanistan/Kandahar/) | AF | `light-metro-3car` | 3 | 43 | 64 | 62 | 53% | $320M | $5M | $19M |
| [Aqaba](west-asia/Jordan/Aqaba/) | JO | `tram-2car` | 3 | 23 | 34 | 48 | 57% | $172M | $5M | $10M |
| [Mazar E Sharif](south-asia/Afghanistan/Mazar-E-Sharif/) | AF | `light-metro-3car` | 3 | 37 | 63 | 61 | 59% | $315M | $5M | $16M |
| [Jaffna](south-asia/Sri%20Lanka/Jaffna/) | LK | `light-metro-3car` | 3 | 34 | 52 | 52 | 42% | $260M | $5M | $14M |
| [Jinja](east-africa/Uganda/Jinja/) | UG | `tram-2car` | 3 | 29 | 46 | 61 | 41% | $228M | $5M | $12M |
| [Lucknow](south-asia/India/Lucknow/) | IN | `metro-6car` | 6 | 164 | 375 | 297 | 31% | $1.88bn | $5M | $64M |
| [Kakamega](east-africa/Kenya/Kakamega/) | KE | `tram-2car` | 3 | 24 | 42 | 58 | 77% | $213M | $5M | $10M |
| [Abha](west-asia/Saudi%20Arabia/Abha/) | SA | `light-metro-3car` | 3 | 45 | 70 | 68 | 34% | $351M | $5M | $18M |
| [Samawah](west-asia/Iraq/Samawah/) | IQ | `light-metro-3car` | 3 | 33 | 55 | 55 | 56% | $276M | $5M | $15M |
| [East London Za](south-africa/South%20Africa/East-London-Za/) | ZA | `light-metro-3car` | 3 | 36 | 63 | 63 | 51% | $318M | $5M | $13M |
| [Jalalabad Af](south-asia/Afghanistan/Jalalabad-Af/) | AF | `light-metro-3car` | 3 | 32 | 51 | 53 | 69% | $255M | $5M | $14M |
| [Ismailia](west-asia/Egypt/Ismailia/) | EG | `light-metro-3car` | 3 | 33 | 53 | 55 | 63% | $269M | $5M | $15M |
| [Damascus](west-asia/Syria/Damascus/) | SY | `metro-4car` | 6 | 113 | 233 | 192 | 45% | $1.18bn | $5M | $51M |
| [Mbarara](east-africa/Uganda/Mbarara/) | UG | `light-metro-3car` | 3 | 36 | 59 | 59 | 53% | $297M | $5M | $15M |
| [Kanpur](south-asia/India/Kanpur/) | IN | `metro-6car` | 7 | 150 | 339 | 273 | 44% | $1.71bn | $5M | $61M |
| [Sulaymaniyah](west-asia/Iraq/Sulaymaniyah/) | IQ | `metro-4car` | 4 | 59 | 127 | 106 | 49% | $643M | $5M | $25M |
| [Nampula](east-africa/Mozambique/Nampula/) | MZ | `light-metro-3car` | 3 | 30 | 52 | 54 | 67% | $262M | $5M | $12M |
| [Conakry](west-africa/Guinea/Conakry/) | GN | `metro-4car` | 3 | 55 | 93 | 78 | 40% | $473M | $5M | $25M |
| [Chimoio](east-africa/Mozambique/Chimoio/) | MZ | `light-metro-3car` | 2 | 20 | 35 | 35 | 55% | $176M | $5M | $8M |
| [Ouagadougou](west-africa/Burkina%20Faso/Ouagadougou/) | BF | `metro-4car` | 6 | 138 | 264 | 213 | 37% | $1.34bn | $5M | $64M |
| [Kigoma](east-africa/Tanzania/Kigoma/) | TZ | `tram-2car` | 3 | 24 | 35 | 49 | 77% | $178M | $5M | $11M |
| [Damanhur](west-asia/Egypt/Damanhur/) | EG | `light-metro-3car` | 3 | 22 | 41 | 44 | 77% | $211M | $5M | $10M |
| [Baqubah](west-asia/Iraq/Baqubah/) | IQ | `light-metro-3car` | 3 | 37 | 60 | 60 | 50% | $306M | $5M | $16M |
| [Minya](west-asia/Egypt/Minya/) | EG | `light-metro-3car` | 3 | 32 | 53 | 53 | 69% | $273M | $5M | $12M |
| [El Obeid](north-africa/Sudan/El-Obeid/) | SD | `light-metro-3car` | 3 | 28 | 46 | 47 | 72% | $236M | $5M | $11M |
| [Nelspruit](south-africa/South%20Africa/Nelspruit/) | ZA | `tram-2car` | 3 | 22 | 39 | 53 | 68% | $201M | $5M | $10M |
| [Dar Es Salaam](east-africa/Tanzania/Dar-Es-Salaam/) | TZ | `metro-6car` | 7 | 163 | 393 | 314 | 28% | $2.02bn | $5M | $62M |
| [Idlib](west-asia/Syria/Idlib/) | SY | `tram-2car` | 3 | 18 | 35 | 49 | 79% | $180M | $5M | $8M |
| [Baghdad](west-asia/Iraq/Baghdad/) | IQ | `metro-6car` | 9 | 218 | 509 | 408 | 45% | $2.62bn | $5M | $90M |
| [Zanzibar City](east-africa/Tanzania/Zanzibar-City/) | TZ | `light-metro-3car` | 3 | 32 | 56 | 56 | 70% | $290M | $5M | $12M |
| [Cuenca](latin-america/Ecuador/Cuenca/) | EC | `light-metro-3car` | 3 | 48 | 79 | 77 | 57% | $406M | $5M | $21M |
| [Agra](south-asia/India/Agra/) | IN | `metro-4car` | 5 | 98 | 191 | 156 | 39% | $989M | $5M | $45M |
| [Homs](west-asia/Syria/Homs/) | SY | `light-metro-3car` | 3 | 33 | 51 | 53 | 42% | $267M | $5M | $14M |
| [Meknes](north-africa/Morocco/Meknes/) | MA | `light-metro-3car` | 3 | 23 | 39 | 42 | 58% | $205M | $5M | $10M |
| [Colombo](south-asia/Sri%20Lanka/Colombo/) | LK | `metro-6car` | 6 | 126 | 278 | 223 | 42% | $1.45bn | $5M | $51M |
| [Rubavu](east-africa/Rwanda/Rubavu/) | RW | `tram-2car` | 3 | 28 | 45 | 61 | 48% | $236M | $5M | $12M |
| [Mogadishu](east-africa/Somalia/Mogadishu/) | SO | `metro-4car` | 4 | 68 | 128 | 106 | 40% | $668M | $5M | $31M |
| [Kumba](west-africa/Cameroon/Kumba/) | CM | `light-metro-3car` | 3 | 29 | 43 | 45 | 68% | $222M | $5M | $12M |
| [Beira](east-africa/Mozambique/Beira/) | MZ | `light-metro-3car` | 3 | 39 | 54 | 54 | 37% | $281M | $5M | $17M |
| [Mahalla](west-asia/Egypt/Mahalla/) | EG | `light-metro-3car` | 3 | 22 | 38 | 42 | 69% | $198M | $5M | $9M |
| [Kandy](south-asia/Sri%20Lanka/Kandy/) | LK | `light-metro-3car` | 3 | 43 | 78 | 76 | 56% | $408M | $5M | $16M |
| [Multan](south-asia/Pakistan/Multan/) | PK | `metro-4car` | 4 | 64 | 115 | 98 | 42% | $604M | $5M | $31M |
| [Mandalay](southeast-asia/Myanmar/Mandalay/) | MM | `metro-4car` | 6 | 88 | 187 | 156 | 60% | $981M | $5M | $42M |
| [Raipur](south-asia/India/Raipur/) | IN | `metro-4car` | 5 | 88 | 185 | 151 | 43% | $972M | $5M | $37M |
| [Luanda](east-africa/Angola/Luanda/) | AO | `metro-6car` | 9 | 170 | 390 | 317 | 64% | $2.05bn | $5M | $71M |
| [Nador](north-africa/Morocco/Nador/) | MA | `tram-2car` | 3 | 19 | 34 | 48 | 70% | $180M | $5M | $9M |
| [Kananga](central-africa/DR%20Congo/Kananga/) | CD | `metro-4car` | 2 | 18 | 38 | 34 | 73% | $202M | $5M | $8M |
| [Hyderabad Pk](south-asia/Pakistan/Hyderabad-Pk/) | PK | `metro-4car` | 6 | 84 | 182 | 152 | 61% | $960M | $5M | $38M |
| [Fort Portal](east-africa/Uganda/Fort-Portal/) | UG | `tram-2car` | 3 | 21 | 36 | 51 | 84% | $192M | $5M | $10M |
| [Tanga](east-africa/Tanzania/Tanga/) | TZ | `light-metro-3car` | 3 | 27 | 48 | 50 | 72% | $255M | $5M | $12M |
| [Arish](west-asia/Egypt/Arish/) | EG | `tram-2car` | 1 | 7 | 13 | 18 | 44% | $68M | $5M | $3M |
| [Arua](east-africa/Uganda/Arua/) | UG | `tram-2car` | 3 | 23 | 37 | 51 | 78% | $196M | $5M | $11M |
| [Lusaka](east-africa/Zambia/Lusaka/) | ZM | `metro-6car` | 6 | 123 | 236 | 192 | 34% | $1.25bn | $5M | $53M |
| [Peshawar](south-asia/Pakistan/Peshawar/) | PK | `metro-4car` | 4 | 87 | 197 | 158 | 33% | $1.04bn | $5M | $35M |
| [Luxor](west-asia/Egypt/Luxor/) | EG | `light-metro-3car` | 3 | 34 | 54 | 54 | 73% | $286M | $5M | $15M |
| [Mansoura Eg](west-asia/Egypt/Mansoura-Eg/) | EG | `light-metro-3car` | 3 | 34 | 56 | 56 | 54% | $298M | $5M | $15M |
| [Narayanganj](south-asia/Bangladesh/Narayanganj/) | BD | `light-metro-3car` | 3 | 50 | 82 | 80 | 27% | $435M | $5M | $18M |
| [Polokwane](south-africa/South%20Africa/Polokwane/) | ZA | `light-metro-3car` | 3 | 34 | 52 | 52 | 60% | $275M | $5M | $15M |
| [Duhok](west-asia/Iraq/Duhok/) | IQ | `light-metro-3car` | 3 | 32 | 53 | 54 | 53% | $283M | $5M | $15M |
| [Kinshasa](central-africa/DR%20Congo/Kinshasa/) | CD | `metro-6car` | 8 | 183 | 385 | 310 | 49% | $2.05bn | $5M | $82M |
| [Morogoro](east-africa/Tanzania/Morogoro/) | TZ | `light-metro-3car` | 3 | 32 | 55 | 55 | 61% | $294M | $5M | $13M |
| [Jeddah](west-asia/Saudi%20Arabia/Jeddah/) | SA | `metro-6car` | 8 | 202 | 406 | 326 | 45% | $2.17bn | $5M | $93M |
| [Indore](south-asia/India/Indore/) | IN | `metro-6car` | 7 | 146 | 324 | 260 | 48% | $1.74bn | $5M | $62M |
| [Vadodara](south-asia/India/Vadodara/) | IN | `metro-4car` | 5 | 89 | 164 | 137 | 48% | $879M | $5M | $43M |
| [Beirut](west-asia/Lebanon/Beirut/) | LB | `metro-4car` | 6 | 83 | 159 | 134 | 70% | $860M | $5M | $40M |
| [Bhopal](south-asia/India/Bhopal/) | IN | `metro-4car` | 6 | 107 | 206 | 169 | 52% | $1.11bn | $5M | $51M |
| [Durban](south-africa/South%20Africa/Durban/) | ZA | `metro-6car` | 9 | 172 | 401 | 325 | 79% | $2.17bn | $5M | $75M |
| [Goma](central-africa/DR%20Congo/Goma/) | CD | `light-metro-3car` | 3 | 39 | 58 | 58 | 60% | $314M | $5M | $17M |
| [Bandung](southeast-asia/Indonesia/Bandung/) | ID | `metro-4car` | 6 | 126 | 257 | 208 | 41% | $1.39bn | $5M | $57M |
| [Kisangani](central-africa/DR%20Congo/Kisangani/) | CD | `metro-4car` | 2 | 27 | 47 | 40 | 64% | $256M | $5M | $13M |
| [Naivasha](east-africa/Kenya/Naivasha/) | KE | `tram-2car` | 3 | 20 | 33 | 48 | 86% | $179M | $5M | $9M |
| [Uige](east-africa/Angola/Uige/) | AO | `light-metro-3car` | 1 | 8 | 13 | 14 | 67% | $70M | $5M | $4M |
| [Mbeya](east-africa/Tanzania/Mbeya/) | TZ | `light-metro-3car` | 3 | 39 | 55 | 55 | 44% | $298M | $5M | $18M |
| [Malindi](east-africa/Kenya/Malindi/) | KE | `tram-2car` | 3 | 20 | 29 | 44 | 79% | $160M | $5M | $9M |
| [Hoima](east-africa/Uganda/Hoima/) | UG | `tram-2car` | 3 | 19 | 31 | 45 | 84% | $170M | $5M | $9M |
| [Aden](west-asia/Yemen/Aden/) | YE | `light-metro-3car` | 3 | 28 | 44 | 46 | 43% | $241M | $5M | $12M |
| [Dakar](west-africa/Senegal/Dakar/) | SN | `metro-6car` | 5 | 107 | 204 | 167 | 52% | $1.11bn | $5M | $47M |
| [Songea](east-africa/Tanzania/Songea/) | TZ | `tram-2car` | 1 | 7 | 11 | 16 | 73% | $63M | $5M | $3M |
| [Masaka](east-africa/Uganda/Masaka/) | UG | `tram-2car` | 3 | 20 | 32 | 46 | 56% | $175M | $5M | $9M |
| [Taiz](west-asia/Yemen/Taiz/) | YE | `light-metro-3car` | 3 | 33 | 49 | 51 | 55% | $268M | $5M | $15M |
| [Coimbatore](south-asia/India/Coimbatore/) | IN | `metro-6car` | 5 | 121 | 268 | 214 | 31% | $1.47bn | $5M | $51M |
| [Karachi](south-asia/Pakistan/Karachi/) | PK | `metro-6car` | 9 | 231 | 472 | 377 | 48% | $2.59bn | $5M | $100M |
| [Raqqa](west-asia/Syria/Raqqa/) | SY | `light-metro-3car` | 3 | 25 | 45 | 46 | 86% | $246M | $5M | $11M |
| [Jos](west-africa/Nigeria/Jos/) | NG | `light-metro-3car` | 3 | 40 | 54 | 55 | 26% | $296M | $5M | $17M |
| [Entebbe](east-africa/Uganda/Entebbe/) | UG | `tram-2car` | 3 | 28 | 43 | 59 | 70% | $237M | $5M | $13M |
| [Nacala](east-africa/Mozambique/Nacala/) | MZ | `tram-2car` | 3 | 25 | 39 | 54 | 80% | $215M | $6M | $11M |
| [Bahawalpur](south-asia/Pakistan/Bahawalpur/) | PK | `light-metro-3car` | 3 | 29 | 46 | 49 | 42% | $256M | $6M | $14M |
| [Antananarivo](east-africa/Madagascar/Antananarivo/) | MG | `metro-6car` | 7 | 155 | 339 | 272 | 42% | $1.88bn | $6M | $65M |
| [Fez](north-africa/Morocco/Fez/) | MA | `metro-4car` | 4 | 58 | 113 | 94 | 73% | $623M | $6M | $28M |
| [Quetta](south-asia/Pakistan/Quetta/) | PK | `metro-4car` | 5 | 78 | 140 | 120 | 54% | $776M | $6M | $39M |
| [Amman](west-asia/Jordan/Amman/) | JO | `metro-6car` | 8 | 172 | 354 | 286 | 51% | $1.96bn | $6M | $76M |
| [Chittagong](south-asia/Bangladesh/Chittagong/) | BD | `metro-6car` | 8 | 161 | 374 | 302 | 64% | $2.08bn | $6M | $71M |
| [Sohag](west-asia/Egypt/Sohag/) | EG | `light-metro-3car` | 3 | 32 | 60 | 60 | 68% | $335M | $6M | $13M |
| [Herat](south-asia/Afghanistan/Herat/) | AF | `light-metro-3car` | 3 | 43 | 65 | 64 | 36% | $361M | $6M | $19M |
| [Varanasi](south-asia/India/Varanasi/) | IN | `metro-4car` | 5 | 100 | 202 | 165 | 47% | $1.13bn | $6M | $43M |
| [Barisal](south-asia/Bangladesh/Barisal/) | BD | `light-metro-3car` | 3 | 30 | 59 | 60 | 50% | $328M | $6M | $12M |
| [Rajkot](south-asia/India/Rajkot/) | IN | `metro-4car` | 5 | 76 | 143 | 121 | 58% | $798M | $6M | $36M |
| [Khulna](south-asia/Bangladesh/Khulna/) | BD | `metro-4car` | 6 | 82 | 182 | 152 | 57% | $1.02bn | $6M | $37M |
| [Sidon](west-asia/Lebanon/Sidon/) | LB | `tram-2car` | 3 | 23 | 37 | 52 | 71% | $208M | $6M | $11M |
| [Basra](west-asia/Iraq/Basra/) | IQ | `metro-6car` | 7 | 119 | 289 | 236 | 54% | $1.62bn | $6M | $48M |
| [Kisii](east-africa/Kenya/Kisii/) | KE | `tram-2car` | 3 | 17 | 30 | 43 | 67% | $166M | $6M | $8M |
| [Lobito](east-africa/Angola/Lobito/) | AO | `light-metro-3car` | 3 | 25 | 38 | 41 | 69% | $212M | $6M | $12M |
| [Kirkuk](west-asia/Iraq/Kirkuk/) | IQ | `metro-4car` | 6 | 92 | 170 | 142 | 60% | $955M | $6M | $45M |
| [Karbala](west-asia/Iraq/Karbala/) | IQ | `metro-4car` | 6 | 89 | 170 | 144 | 67% | $957M | $6M | $44M |
| [Patna](south-asia/India/Patna/) | IN | `metro-4car` | 5 | 84 | 185 | 152 | 50% | $1.04bn | $6M | $36M |
| [Mosul](west-asia/Iraq/Mosul/) | IQ | `metro-4car` | 5 | 60 | 145 | 122 | 38% | $818M | $6M | $23M |
| [Maroua](west-africa/Cameroon/Maroua/) | CM | `light-metro-3car` | 3 | 29 | 53 | 54 | 74% | $298M | $6M | $12M |
| [Fallujah](west-asia/Iraq/Fallujah/) | IQ | `light-metro-3car` | 3 | 28 | 46 | 48 | 57% | $261M | $6M | $13M |
| [Tabuk](west-asia/Saudi%20Arabia/Tabuk/) | SA | `light-metro-3car` | 3 | 45 | 63 | 63 | 27% | $358M | $6M | $20M |
| [Ramadi](west-asia/Iraq/Ramadi/) | IQ | `light-metro-3car` | 3 | 35 | 47 | 49 | 39% | $267M | $6M | $17M |
| [Oujda](north-africa/Morocco/Oujda/) | MA | `light-metro-3car` | 3 | 33 | 47 | 48 | 48% | $267M | $6M | $16M |
| [Surabaya](southeast-asia/Indonesia/Surabaya/) | ID | `metro-6car` | 7 | 143 | 294 | 240 | 40% | $1.68bn | $6M | $61M |
| [Port Sudan](north-africa/Sudan/Port-Sudan/) | SD | `light-metro-3car` | 3 | 22 | 33 | 38 | 80% | $191M | $6M | $10M |
| [Garissa](east-africa/Kenya/Garissa/) | KE | `tram-2car` | 3 | 19 | 29 | 43 | 71% | $165M | $6M | $9M |
| [Phnom Penh](southeast-asia/Cambodia/Phnom-Penh/) | KH | `metro-4car` | 6 | 107 | 228 | 186 | 48% | $1.31bn | $6M | $47M |
| [Yaounde](east-africa/Cameroon/Yaounde/) | CM | `metro-6car` | 8 | 136 | 267 | 219 | 43% | $1.53bn | $6M | $63M |
| [Safi](north-africa/Morocco/Safi/) | MA | `light-metro-3car` | 3 | 26 | 39 | 43 | 72% | $226M | $6M | $12M |
| [La Paz](latin-america/Bolivia/La-Paz/) | BO | `metro-4car` | 6 | 115 | 212 | 174 | 57% | $1.22bn | $6M | $55M |
| [Quelimane](east-africa/Mozambique/Quelimane/) | MZ | `light-metro-3car` | 1 | 6 | 10 | 12 | 48% | $59M | $6M | $3M |
| [Yangon](southeast-asia/Myanmar/Yangon/) | MM | `metro-6car` | 9 | 214 | 418 | 335 | 56% | $2.41bn | $6M | $102M |
| [Qena](west-asia/Egypt/Qena/) | EG | `light-metro-3car` | 3 | 26 | 45 | 47 | 75% | $261M | $6M | $12M |
| [Kano](west-africa/Nigeria/Kano/) | NG | `metro-6car` | 6 | 154 | 362 | 286 | 37% | $2.10bn | $6M | $57M |
| [Deir Ez Zor](west-asia/Syria/Deir-Ez-Zor/) | SY | `light-metro-3car` | 3 | 32 | 57 | 57 | 62% | $329M | $6M | $14M |
| [Port Said](west-asia/Egypt/Port-Said/) | EG | `light-metro-3car` | 3 | 25 | 35 | 39 | 71% | $204M | $6M | $12M |
| [Kabul](south-asia/Afghanistan/Kabul/) | AF | `metro-6car` | 7 | 137 | 261 | 215 | 53% | $1.52bn | $6M | $63M |
| [Uyo](west-africa/Nigeria/Uyo/) | NG | `light-metro-3car` | 3 | 24 | 31 | 36 | 25% | $182M | $6M | $12M |
| [Lubumbashi](central-africa/DR%20Congo/Lubumbashi/) | CD | `metro-4car` | 4 | 75 | 130 | 107 | 34% | $762M | $6M | $39M |
| [Kathmandu](south-asia/Nepal/Kathmandu/) | NP | `metro-4car` | 6 | 103 | 203 | 167 | 46% | $1.19bn | $6M | $51M |
| [Sanaa](west-asia/Yemen/Sanaa/) | YE | `metro-6car` | 9 | 126 | 261 | 218 | 78% | $1.54bn | $6M | $61M |
| [Tetouan](north-africa/Morocco/Tetouan/) | MA | `light-metro-3car` | 3 | 33 | 54 | 56 | 69% | $319M | $6M | $14M |
| [Kafr El Sheikh](west-asia/Egypt/Kafr-El-Sheikh/) | EG | `tram-2car` | 3 | 22 | 33 | 47 | 75% | $195M | $6M | $11M |
| [Machakos](east-africa/Kenya/Machakos/) | KE | `tram-2car` | 3 | 16 | 27 | 40 | 76% | $157M | $6M | $8M |
| [Diwaniyah](west-asia/Iraq/Diwaniyah/) | IQ | `light-metro-3car` | 3 | 36 | 54 | 55 | 43% | $320M | $6M | $16M |
| [Beni Mellal](north-africa/Morocco/Beni-Mellal/) | MA | `tram-2car` | 3 | 18 | 30 | 45 | 85% | $180M | $6M | $9M |
| [Beni Suef](west-asia/Egypt/Beni-Suef/) | EG | `light-metro-3car` | 3 | 23 | 35 | 38 | 55% | $208M | $6M | $11M |
| [Bertoua](west-africa/Cameroon/Bertoua/) | CM | `light-metro-3car` | 3 | 20 | 29 | 34 | 77% | $173M | $6M | $10M |
| [Nyala](north-africa/Sudan/Nyala/) | SD | `light-metro-3car` | 3 | 29 | 47 | 48 | 61% | $282M | $6M | $11M |
| [Maiduguri](west-africa/Nigeria/Maiduguri/) | NG | `metro-4car` | 5 | 86 | 176 | 145 | 34% | $1.07bn | $6M | $38M |
| [Douala](west-africa/Cameroon/Douala/) | CM | `metro-6car` | 5 | 129 | 228 | 184 | 37% | $1.38bn | $6M | $59M |
| [Hurghada](west-asia/Egypt/Hurghada/) | EG | `tram-2car` | 3 | 28 | 43 | 57 | 56% | $260M | $6M | $13M |
| [Pemba Mz](east-africa/Mozambique/Pemba-Mz/) | MZ | `tram-2car` | 3 | 20 | 30 | 43 | 63% | $184M | $6M | $10M |
| [Sayun](west-asia/Yemen/Sayun/) | YE | `tram-2car` | 2 | 15 | 22 | 31 | 58% | $132M | $6M | $7M |
| [Faisalabad](south-asia/Pakistan/Faisalabad/) | PK | `metro-6car` | 5 | 93 | 166 | 137 | 52% | $1.02bn | $6M | $45M |
| [Benin City](west-africa/Nigeria/Benin-City/) | NG | `metro-4car` | 4 | 77 | 132 | 111 | 44% | $812M | $6M | $40M |
| [Kitale](east-africa/Kenya/Kitale/) | KE | `tram-2car` | 3 | 16 | 29 | 43 | 85% | $180M | $6M | $8M |
| [Edea](west-africa/Cameroon/Edea/) | CM | `tram-2car` | 1 | 7 | 10 | 14 | 61% | $59M | $6M | $4M |
| [Hodeidah](west-asia/Yemen/Hodeidah/) | YE | `light-metro-3car` | 3 | 27 | 36 | 40 | 61% | $223M | $6M | $13M |
| [Soyo](east-africa/Angola/Soyo/) | AO | `tram-2car` | 2 | 14 | 22 | 32 | 70% | $139M | $6M | $7M |
| [Waw](north-africa/Sudan/Waw/) | SD | `tram-2car` | 2 | 11 | 18 | 27 | 73% | $111M | $6M | $6M |
| [Xai Xai](east-africa/Mozambique/Xai-Xai/) | MZ | `tram-2car` | 2 | 12 | 18 | 27 | 43% | $111M | $6M | $6M |
| [Najran](west-asia/Saudi%20Arabia/Najran/) | SA | `light-metro-3car` | 3 | 33 | 57 | 57 | 46% | $354M | $6M | $13M |
| [Tartus](west-asia/Syria/Tartus/) | SY | `tram-2car` | 3 | 23 | 35 | 49 | 73% | $219M | $6M | $11M |
| [Najaf](west-asia/Iraq/Najaf/) | IQ | `metro-4car` | 6 | 91 | 172 | 144 | 60% | $1.09bn | $6M | $46M |
| [Ibadan](west-africa/Nigeria/Ibadan/) | NG | `metro-6car` | 4 | 90 | 135 | 111 | 24% | $857M | $6M | $44M |
| [Lahij](west-asia/Yemen/Lahij/) | YE | `tram-2car` | 3 | 19 | 29 | 43 | 82% | $186M | $6M | $10M |
| [Ngaoundere](west-africa/Cameroon/Ngaoundere/) | CM | `light-metro-3car` | 3 | 19 | 28 | 34 | 57% | $182M | $6M | $9M |
| [Meru Ke](east-africa/Kenya/Meru-Ke/) | KE | `tram-2car` | 2 | 12 | 22 | 32 | 52% | $142M | $6M | $5M |
| [Aba Ng](west-africa/Nigeria/Aba-Ng/) | NG | `light-metro-3car` | 3 | 26 | 34 | 38 | 40% | $220M | $6M | $13M |
| [Zarqa](west-asia/Jordan/Zarqa/) | JO | `light-metro-3car` | 3 | 57 | 83 | 80 | 48% | $540M | $6M | $24M |
| [Iringa](east-africa/Tanzania/Iringa/) | TZ | `tram-2car` | 3 | 20 | 28 | 42 | 67% | $183M | $7M | $10M |
| [Moshi](east-africa/Tanzania/Moshi/) | TZ | `tram-2car` | 3 | 21 | 36 | 51 | 76% | $238M | $7M | $11M |
| [Bamako](west-africa/Mali/Bamako/) | ML | `metro-4car` | 6 | 118 | 257 | 207 | 31% | $1.77bn | $7M | $47M |
| [Kut](west-asia/Iraq/Kut/) | IQ | `light-metro-3car` | 3 | 32 | 56 | 55 | 37% | $398M | $7M | $14M |
| [Khouribga](north-africa/Morocco/Khouribga/) | MA | `tram-2car` | 2 | 11 | 15 | 23 | 57% | $105M | $7M | $6M |
| [Nasiriyah](west-asia/Iraq/Nasiriyah/) | IQ | `light-metro-3car` | 3 | 33 | 56 | 56 | 40% | $407M | $7M | $15M |
| [Sumbawanga](east-africa/Tanzania/Sumbawanga/) | TZ | `tram-2car` | 1 | 5 | 7 | 11 | 35% | $47M | $7M | $3M |
| [Larkana](south-asia/Pakistan/Larkana/) | PK | `light-metro-3car` | 2 | 19 | 38 | 39 | 28% | $275M | $7M | $9M |
| [Kassala](north-africa/Sudan/Kassala/) | SD | `light-metro-3car` | 3 | 20 | 34 | 39 | 76% | $252M | $7M | $9M |
| [Tabora](east-africa/Tanzania/Tabora/) | TZ | `tram-2car` | 2 | 13 | 18 | 26 | 54% | $129M | $7M | $7M |
| [Garoua](west-africa/Cameroon/Garoua/) | CM | `light-metro-3car` | 3 | 29 | 44 | 46 | 38% | $326M | $7M | $12M |
| [Tete](east-africa/Mozambique/Tete/) | MZ | `light-metro-3car` | 3 | 23 | 38 | 41 | 77% | $289M | $8M | $9M |
| [Amarah](west-asia/Iraq/Amarah/) | IQ | `light-metro-3car` | 3 | 32 | 45 | 46 | 43% | $341M | $8M | $15M |
| [Jodhpur](south-asia/India/Jodhpur/) | IN | `metro-4car` | 5 | 82 | 150 | 124 | 44% | $1.15bn | $8M | $37M |
| [Mymensingh](south-asia/Bangladesh/Mymensingh/) | BD | `light-metro-3car` | 3 | 37 | 67 | 67 | 41% | $524M | $8M | $13M |
| [Nyeri](east-africa/Kenya/Nyeri/) | KE | `tram-2car` | 3 | 22 | 37 | 51 | 62% | $289M | $8M | $10M |
| [Sheikhupura](south-asia/Pakistan/Sheikhupura/) | PK | `light-metro-3car` | 2 | 17 | 19 | 22 | 32% | $156M | $8M | $9M |
| [Malanje](east-africa/Angola/Malanje/) | AO | `light-metro-3car` | 2 | 12 | 15 | 19 | 57% | $122M | $8M | $7M |
| [Sialkot](south-asia/Pakistan/Sialkot/) | PK | `light-metro-3car` | 3 | 37 | 59 | 59 | 43% | $519M | $9M | $16M |
| [Sukkur](south-asia/Pakistan/Sukkur/) | PK | `light-metro-3car` | 3 | 31 | 51 | 53 | 55% | $471M | $9M | $13M |
| [Biratnagar](south-asia/Nepal/Biratnagar/) | NP | `tram-2car` | 3 | 23 | 34 | 48 | 60% | $428M | $13M | $10M |
