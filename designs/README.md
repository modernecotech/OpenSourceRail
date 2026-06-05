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
| [Tanta](west-asia/Egypt/Tanta/) | EG | `light-metro-3car` | 3 | 35 | 75 | 73 | 56% | $406M | $5M | $14M |
| [Hofuf](west-asia/Saudi%20Arabia/Hofuf/) | SA | `light-metro-3car` | 3 | 46 | 78 | 77 | 50% | $425M | $5M | $18M |
| [Agadir](north-africa/Morocco/Agadir/) | MA | `light-metro-3car` | 3 | 44 | 83 | 80 | 65% | $450M | $5M | $17M |
| [Omdurman](north-africa/Sudan/Omdurman/) | SD | `metro-4car` | 6 | 104 | 255 | 207 | 47% | $1.39bn | $5M | $41M |
| [Bamenda](west-africa/Cameroon/Bamenda/) | CM | `light-metro-3car` | 3 | 31 | 54 | 55 | 59% | $297M | $5M | $12M |
| [Huye](east-africa/Rwanda/Huye/) | RW | `tram-2car` | 3 | 28 | 46 | 61 | 23% | $251M | $5M | $10M |
| [Kisumu](east-africa/Kenya/Kisumu/) | KE | `light-metro-3car` | 3 | 42 | 75 | 74 | 31% | $418M | $6M | $14M |
| [Dammam](west-asia/Saudi%20Arabia/Dammam/) | SA | `metro-4car` | 4 | 95 | 210 | 168 | 28% | $1.16bn | $6M | $39M |
| [Arusha](east-africa/Tanzania/Arusha/) | TZ | `light-metro-3car` | 3 | 44 | 73 | 72 | 36% | $403M | $6M | $16M |
| [Lyon](europe/France/Lyon/) | FR | `metro-4car` | 6 | 122 | 287 | 232 | 45% | $1.59bn | $6M | $49M |
| [Khamis Mushait](west-asia/Saudi%20Arabia/Khamis-Mushait/) | SA | `light-metro-3car` | 3 | 38 | 69 | 68 | 35% | $385M | $6M | $14M |
| [Kenitra](north-africa/Morocco/Kenitra/) | MA | `light-metro-3car` | 3 | 35 | 60 | 60 | 66% | $335M | $6M | $14M |
| [Vientiane](southeast-asia/Laos/Vientiane/) | LA | `light-metro-3car` | 3 | 46 | 81 | 78 | 43% | $451M | $6M | $18M |
| [Damietta](west-asia/Egypt/Damietta/) | EG | `light-metro-3car` | 3 | 38 | 74 | 73 | 72% | $410M | $6M | $13M |
| [Hail](west-asia/Saudi%20Arabia/Hail/) | SA | `light-metro-3car` | 3 | 35 | 63 | 62 | 47% | $353M | $6M | $13M |
| [Bukavu](central-africa/DR%20Congo/Bukavu/) | CD | `light-metro-3car` | 3 | 37 | 60 | 60 | 60% | $337M | $6M | $15M |
| [Nablus](west-asia/Palestine/Nablus/) | PS | `light-metro-3car` | 3 | 34 | 65 | 65 | 84% | $363M | $6M | $13M |
| [Asyut](west-asia/Egypt/Asyut/) | EG | `light-metro-3car` | 3 | 31 | 63 | 62 | 58% | $353M | $6M | $11M |
| [Tangier](north-africa/Morocco/Tangier/) | MA | `metro-4car` | 5 | 64 | 153 | 129 | 57% | $867M | $6M | $25M |
| [Port Harcourt](west-africa/Nigeria/Port-Harcourt/) | NG | `metro-4car` | 4 | 95 | 199 | 160 | 31% | $1.13bn | $6M | $39M |
| [Rahim Yar Khan](south-asia/Pakistan/Rahim-Yar-Khan/) | PK | `light-metro-3car` | 3 | 24 | 46 | 47 | 37% | $261M | $6M | $10M |
| [Kampala](east-africa/Uganda/Kampala/) | UG | `metro-4car` | 4 | 99 | 201 | 160 | 24% | $1.14bn | $6M | $41M |
| [Sylhet](south-asia/Bangladesh/Sylhet/) | BD | `light-metro-3car` | 3 | 40 | 73 | 72 | 45% | $414M | $6M | $14M |
| [Mwanza](east-africa/Tanzania/Mwanza/) | TZ | `metro-4car` | 5 | 70 | 162 | 136 | 45% | $920M | $6M | $29M |
| [Dodoma](east-africa/Tanzania/Dodoma/) | TZ | `light-metro-3car` | 3 | 36 | 66 | 66 | 40% | $378M | $6M | $14M |
| [Hebron](west-asia/Palestine/Hebron/) | PS | `light-metro-3car` | 3 | 40 | 69 | 68 | 61% | $394M | $6M | $16M |
| [Hama](west-asia/Syria/Hama/) | SY | `light-metro-3car` | 3 | 31 | 55 | 55 | 53% | $316M | $6M | $13M |
| [Taif](west-asia/Saudi%20Arabia/Taif/) | SA | `light-metro-3car` | 3 | 42 | 73 | 73 | 41% | $421M | $6M | $17M |
| [Al Kharj](west-asia/Saudi%20Arabia/Al-Kharj/) | SA | `light-metro-3car` | 3 | 38 | 68 | 67 | 70% | $388M | $6M | $14M |
| [Gulu](east-africa/Uganda/Gulu/) | UG | `light-metro-3car` | 3 | 36 | 64 | 63 | 50% | $366M | $6M | $15M |
| [Galle](south-asia/Sri%20Lanka/Galle/) | LK | `light-metro-3car` | 3 | 37 | 64 | 64 | 56% | $370M | $6M | $15M |
| [Thika](east-africa/Kenya/Thika/) | KE | `light-metro-3car` | 3 | 38 | 76 | 74 | 63% | $435M | $6M | $13M |
| [Bloemfontein](south-africa/South%20Africa/Bloemfontein/) | ZA | `light-metro-3car` | 3 | 42 | 72 | 71 | 35% | $416M | $6M | $16M |
| [Rajshahi](south-asia/Bangladesh/Rajshahi/) | BD | `light-metro-3car` | 3 | 30 | 50 | 52 | 30% | $288M | $6M | $12M |
| [Eldoret](east-africa/Kenya/Eldoret/) | KE | `light-metro-3car` | 3 | 39 | 65 | 64 | 46% | $378M | $6M | $16M |
| [Lira](east-africa/Uganda/Lira/) | UG | `tram-2car` | 3 | 23 | 45 | 61 | 64% | $263M | $6M | $10M |
| [Lubango](east-africa/Angola/Lubango/) | AO | `light-metro-3car` | 3 | 31 | 55 | 55 | 63% | $317M | $6M | $12M |
| [Gujranwala](south-asia/Pakistan/Gujranwala/) | PK | `metro-4car` | 4 | 72 | 160 | 130 | 39% | $931M | $6M | $30M |
| [Nakuru](east-africa/Kenya/Nakuru/) | KE | `light-metro-3car` | 3 | 37 | 60 | 61 | 46% | $347M | $6M | $14M |
| [Tripoli Lb](west-asia/Lebanon/Tripoli-Lb/) | LB | `light-metro-3car` | 3 | 30 | 53 | 55 | 50% | $309M | $6M | $12M |
| [Gaza City](west-asia/Palestine/Gaza-City/) | PS | `light-metro-3car` | 1 | 15 | 24 | 24 | 30% | $139M | $6M | $6M |
| [Zagazig](west-asia/Egypt/Zagazig/) | EG | `light-metro-3car` | 3 | 30 | 56 | 57 | 59% | $327M | $6M | $13M |
| [Kigali](east-africa/Rwanda/Kigali/) | RW | `metro-4car` | 4 | 86 | 171 | 139 | 34% | $993M | $6M | $37M |
| [Ranchi](south-asia/India/Ranchi/) | IN | `metro-4car` | 6 | 96 | 216 | 179 | 50% | $1.26bn | $6M | $40M |
| [Mecca](west-asia/Saudi%20Arabia/Mecca/) | SA | `metro-4car` | 6 | 114 | 251 | 205 | 46% | $1.47bn | $6M | $49M |
| [Rangpur](south-asia/Bangladesh/Rangpur/) | BD | `light-metro-3car` | 3 | 36 | 59 | 59 | 47% | $347M | $6M | $14M |
| [Mombasa](east-africa/Kenya/Mombasa/) | KE | `metro-4car` | 6 | 95 | 201 | 167 | 52% | $1.17bn | $6M | $42M |
| [Khartoum](north-africa/Sudan/Khartoum/) | SD | `metro-6car` | 5 | 152 | 363 | 287 | 22% | $2.12bn | $6M | $57M |
| [Pokhara](south-asia/Nepal/Pokhara/) | NP | `light-metro-3car` | 3 | 44 | 82 | 80 | 52% | $481M | $6M | $18M |
| [Erbil](west-asia/Iraq/Erbil/) | IQ | `metro-4car` | 6 | 97 | 199 | 166 | 42% | $1.17bn | $6M | $45M |
| [Davao](southeast-asia/Philippines/Davao/) | PH | `metro-4car` | 6 | 108 | 229 | 186 | 72% | $1.34bn | $6M | $50M |
| [Ibb](west-asia/Yemen/Ibb/) | YE | `light-metro-3car` | 3 | 40 | 72 | 71 | 58% | $419M | $6M | $17M |
| [Aleppo](west-asia/Syria/Aleppo/) | SY | `metro-4car` | 5 | 89 | 176 | 145 | 46% | $1.03bn | $6M | $40M |
| [Marrakech](north-africa/Morocco/Marrakech/) | MA | `metro-4car` | 6 | 79 | 191 | 159 | 58% | $1.12bn | $6M | $33M |
| [Dhamar](west-asia/Yemen/Dhamar/) | YE | `tram-2car` | 3 | 18 | 32 | 46 | 76% | $190M | $6M | $8M |
| [Ilorin](west-africa/Nigeria/Ilorin/) | NG | `light-metro-3car` | 3 | 39 | 60 | 60 | 31% | $354M | $6M | $16M |
| [Hillah](west-asia/Iraq/Hillah/) | IQ | `light-metro-3car` | 3 | 42 | 69 | 68 | 43% | $406M | $6M | $18M |
| [San Salvador](latin-america/El%20Salvador/San-Salvador/) | SV | `metro-4car` | 6 | 121 | 255 | 207 | 50% | $1.50bn | $6M | $56M |
| [Gazipur](south-asia/Bangladesh/Gazipur/) | BD | `metro-4car` | 6 | 127 | 308 | 245 | 38% | $1.81bn | $6M | $52M |
| [Mukalla](west-asia/Yemen/Mukalla/) | YE | `light-metro-3car` | 3 | 33 | 61 | 61 | 72% | $358M | $6M | $14M |
| [Maputo](east-africa/Mozambique/Maputo/) | MZ | `metro-4car` | 6 | 83 | 186 | 156 | 71% | $1.09bn | $6M | $35M |
| [Mbuji Mayi](central-africa/DR%20Congo/Mbuji-Mayi/) | CD | `metro-4car` | 4 | 55 | 118 | 101 | 70% | $696M | $6M | $25M |
| [Comilla](south-asia/Bangladesh/Comilla/) | BD | `light-metro-3car` | 3 | 38 | 66 | 65 | 41% | $387M | $6M | $15M |
| [Nairobi](east-africa/Kenya/Nairobi/) | KE | `metro-6car` | 8 | 191 | 476 | 378 | 43% | $2.81bn | $6M | $73M |
| [Meerut](south-asia/India/Meerut/) | IN | `metro-4car` | 4 | 84 | 180 | 146 | 43% | $1.06bn | $6M | $36M |
| [Suez](west-asia/Egypt/Suez/) | EG | `light-metro-3car` | 3 | 32 | 59 | 60 | 65% | $348M | $6M | $12M |
| [Namibe](east-africa/Angola/Namibe/) | AO | `tram-2car` | 3 | 25 | 40 | 55 | 61% | $238M | $6M | $11M |
| [Huambo](east-africa/Angola/Huambo/) | AO | `light-metro-3car` | 3 | 31 | 53 | 55 | 72% | $312M | $6M | $13M |
| [Onitsha](west-africa/Nigeria/Onitsha/) | NG | `metro-4car` | 4 | 76 | 184 | 148 | 30% | $1.09bn | $6M | $31M |
| [Shinyanga](east-africa/Tanzania/Shinyanga/) | TZ | `tram-2car` | 3 | 20 | 37 | 51 | 83% | $218M | $6M | $9M |
| [Tunis](north-africa/Tunisia/Tunis/) | TN | `metro-4car` | 5 | 118 | 240 | 194 | 48% | $1.43bn | $6M | $52M |
| [Visakhapatnam](south-asia/India/Visakhapatnam/) | IN | `metro-4car` | 6 | 110 | 240 | 196 | 52% | $1.42bn | $6M | $49M |
| [Vijayawada](south-asia/India/Vijayawada/) | IN | `metro-4car` | 6 | 94 | 225 | 184 | 58% | $1.34bn | $6M | $41M |
| [Benguela](east-africa/Angola/Benguela/) | AO | `light-metro-3car` | 3 | 28 | 50 | 51 | 69% | $297M | $6M | $11M |
| [Madurai](south-asia/India/Madurai/) | IN | `metro-4car` | 6 | 104 | 222 | 183 | 59% | $1.33bn | $6M | $46M |
| [Buraidah](west-asia/Saudi%20Arabia/Buraidah/) | SA | `light-metro-3car` | 3 | 54 | 80 | 78 | 35% | $475M | $6M | $24M |
| [Latakia](west-asia/Syria/Latakia/) | SY | `light-metro-3car` | 3 | 26 | 41 | 43 | 54% | $245M | $6M | $11M |
| [Irbid](west-asia/Jordan/Irbid/) | JO | `light-metro-3car` | 3 | 33 | 56 | 56 | 42% | $335M | $6M | $15M |
| [Medina](west-asia/Saudi%20Arabia/Medina/) | SA | `metro-4car` | 5 | 104 | 211 | 171 | 47% | $1.27bn | $6M | $44M |
| [East London Za](south-africa/South%20Africa/East-London-Za/) | ZA | `light-metro-3car` | 3 | 36 | 63 | 63 | 51% | $380M | $6M | $13M |
| [Jizan](west-asia/Saudi%20Arabia/Jizan/) | SA | `light-metro-3car` | 3 | 28 | 47 | 48 | 64% | $280M | $6M | $11M |
| [Niamey](west-africa/Niger/Niamey/) | NE | `metro-4car` | 4 | 80 | 146 | 120 | 38% | $878M | $6M | $36M |
| [Lucknow](south-asia/India/Lucknow/) | IN | `metro-6car` | 6 | 164 | 375 | 297 | 31% | $2.26bn | $6M | $64M |
| [Mazar E Sharif](south-asia/Afghanistan/Mazar-E-Sharif/) | AF | `light-metro-3car` | 3 | 37 | 63 | 61 | 59% | $379M | $6M | $16M |
| [Sulaymaniyah](west-asia/Iraq/Sulaymaniyah/) | IQ | `metro-4car` | 4 | 59 | 127 | 106 | 49% | $766M | $6M | $25M |
| [Damascus](west-asia/Syria/Damascus/) | SY | `metro-4car` | 6 | 113 | 233 | 192 | 45% | $1.41bn | $6M | $51M |
| [Abha](west-asia/Saudi%20Arabia/Abha/) | SA | `light-metro-3car` | 3 | 45 | 70 | 68 | 34% | $421M | $6M | $18M |
| [Jinja](east-africa/Uganda/Jinja/) | UG | `tram-2car` | 3 | 29 | 46 | 61 | 41% | $275M | $6M | $12M |
| [Kakamega](east-africa/Kenya/Kakamega/) | KE | `tram-2car` | 3 | 24 | 42 | 58 | 77% | $256M | $6M | $10M |
| [Jaffna](south-asia/Sri%20Lanka/Jaffna/) | LK | `light-metro-3car` | 3 | 34 | 52 | 52 | 42% | $313M | $6M | $14M |
| [Kandahar](south-asia/Afghanistan/Kandahar/) | AF | `light-metro-3car` | 3 | 43 | 64 | 62 | 53% | $387M | $6M | $19M |
| [Jalalabad Af](south-asia/Afghanistan/Jalalabad-Af/) | AF | `light-metro-3car` | 3 | 32 | 51 | 53 | 69% | $307M | $6M | $14M |
| [Samawah](west-asia/Iraq/Samawah/) | IQ | `light-metro-3car` | 3 | 33 | 55 | 55 | 56% | $333M | $6M | $15M |
| [Aqaba](west-asia/Jordan/Aqaba/) | JO | `tram-2car` | 3 | 23 | 34 | 48 | 57% | $208M | $6M | $10M |
| [Kanpur](south-asia/India/Kanpur/) | IN | `metro-6car` | 7 | 150 | 339 | 273 | 44% | $2.06bn | $6M | $61M |
| [Mbarara](east-africa/Uganda/Mbarara/) | UG | `light-metro-3car` | 3 | 36 | 59 | 59 | 53% | $356M | $6M | $15M |
| [Ismailia](west-asia/Egypt/Ismailia/) | EG | `light-metro-3car` | 3 | 33 | 53 | 55 | 63% | $325M | $6M | $15M |
| [Nampula](east-africa/Mozambique/Nampula/) | MZ | `light-metro-3car` | 3 | 30 | 52 | 54 | 67% | $315M | $6M | $12M |
| [Conakry](west-africa/Guinea/Conakry/) | GN | `metro-4car` | 3 | 55 | 93 | 78 | 40% | $567M | $6M | $25M |
| [Ouagadougou](west-africa/Burkina%20Faso/Ouagadougou/) | BF | `metro-4car` | 6 | 138 | 264 | 213 | 37% | $1.61bn | $6M | $64M |
| [Minya](west-asia/Egypt/Minya/) | EG | `light-metro-3car` | 3 | 32 | 53 | 53 | 69% | $325M | $6M | $12M |
| [Chimoio](east-africa/Mozambique/Chimoio/) | MZ | `light-metro-3car` | 2 | 20 | 35 | 35 | 55% | $211M | $6M | $8M |
| [Baqubah](west-asia/Iraq/Baqubah/) | IQ | `light-metro-3car` | 3 | 37 | 60 | 60 | 50% | $366M | $6M | $16M |
| [Dar Es Salaam](east-africa/Tanzania/Dar-Es-Salaam/) | TZ | `metro-6car` | 7 | 163 | 393 | 314 | 28% | $2.40bn | $6M | $62M |
| [Damanhur](west-asia/Egypt/Damanhur/) | EG | `light-metro-3car` | 3 | 22 | 41 | 44 | 77% | $254M | $6M | $10M |
| [Zanzibar City](east-africa/Tanzania/Zanzibar-City/) | TZ | `light-metro-3car` | 3 | 32 | 56 | 56 | 70% | $346M | $6M | $12M |
| [El Obeid](north-africa/Sudan/El-Obeid/) | SD | `light-metro-3car` | 3 | 28 | 46 | 47 | 72% | $283M | $6M | $11M |
| [Baghdad](west-asia/Iraq/Baghdad/) | IQ | `metro-6car` | 9 | 218 | 509 | 408 | 45% | $3.13bn | $6M | $90M |
| [Cuenca](latin-america/Ecuador/Cuenca/) | EC | `light-metro-3car` | 3 | 48 | 79 | 77 | 57% | $483M | $6M | $21M |
| [Kigoma](east-africa/Tanzania/Kigoma/) | TZ | `tram-2car` | 3 | 24 | 35 | 49 | 77% | $215M | $6M | $11M |
| [Kandy](south-asia/Sri%20Lanka/Kandy/) | LK | `light-metro-3car` | 3 | 43 | 78 | 76 | 56% | $480M | $6M | $16M |
| [Nelspruit](south-africa/South%20Africa/Nelspruit/) | ZA | `tram-2car` | 3 | 22 | 39 | 53 | 68% | $242M | $6M | $10M |
| [Agra](south-asia/India/Agra/) | IN | `metro-4car` | 5 | 98 | 191 | 156 | 39% | $1.18bn | $6M | $45M |
| [Idlib](west-asia/Syria/Idlib/) | SY | `tram-2car` | 3 | 18 | 35 | 49 | 79% | $216M | $6M | $8M |
| [Mogadishu](east-africa/Somalia/Mogadishu/) | SO | `metro-4car` | 4 | 68 | 128 | 106 | 40% | $793M | $6M | $31M |
| [Raipur](south-asia/India/Raipur/) | IN | `metro-4car` | 5 | 88 | 185 | 151 | 43% | $1.15bn | $6M | $37M |
| [Colombo](south-asia/Sri%20Lanka/Colombo/) | LK | `metro-6car` | 6 | 126 | 278 | 223 | 42% | $1.72bn | $6M | $51M |
| [Narayanganj](south-asia/Bangladesh/Narayanganj/) | BD | `light-metro-3car` | 3 | 50 | 82 | 80 | 27% | $507M | $6M | $18M |
| [Peshawar](south-asia/Pakistan/Peshawar/) | PK | `metro-4car` | 4 | 87 | 197 | 158 | 33% | $1.22bn | $6M | $35M |
| [Rubavu](east-africa/Rwanda/Rubavu/) | RW | `tram-2car` | 3 | 28 | 45 | 61 | 48% | $282M | $6M | $12M |
| [Mandalay](southeast-asia/Myanmar/Mandalay/) | MM | `metro-4car` | 6 | 88 | 187 | 156 | 60% | $1.16bn | $6M | $42M |
| [Homs](west-asia/Syria/Homs/) | SY | `light-metro-3car` | 3 | 33 | 51 | 53 | 42% | $320M | $6M | $14M |
| [Hyderabad Pk](south-asia/Pakistan/Hyderabad-Pk/) | PK | `metro-4car` | 6 | 84 | 182 | 152 | 61% | $1.13bn | $6M | $38M |
| [Meknes](north-africa/Morocco/Meknes/) | MA | `light-metro-3car` | 3 | 23 | 39 | 42 | 58% | $246M | $6M | $10M |
| [Kumba](west-africa/Cameroon/Kumba/) | CM | `light-metro-3car` | 3 | 29 | 43 | 45 | 68% | $266M | $6M | $12M |
| [Multan](south-asia/Pakistan/Multan/) | PK | `metro-4car` | 4 | 64 | 115 | 98 | 42% | $722M | $6M | $31M |
| [Luanda](east-africa/Angola/Luanda/) | AO | `metro-6car` | 9 | 170 | 390 | 317 | 64% | $2.44bn | $6M | $71M |
| [Mahalla](west-asia/Egypt/Mahalla/) | EG | `light-metro-3car` | 3 | 22 | 38 | 42 | 69% | $237M | $6M | $9M |
| [Beira](east-africa/Mozambique/Beira/) | MZ | `light-metro-3car` | 3 | 39 | 54 | 54 | 37% | $337M | $6M | $17M |
| [Nador](north-africa/Morocco/Nador/) | MA | `tram-2car` | 3 | 19 | 34 | 48 | 70% | $216M | $6M | $9M |
| [Kananga](central-africa/DR%20Congo/Kananga/) | CD | `metro-4car` | 2 | 18 | 38 | 34 | 73% | $240M | $6M | $8M |
| [Morogoro](east-africa/Tanzania/Morogoro/) | TZ | `light-metro-3car` | 3 | 32 | 55 | 55 | 61% | $346M | $6M | $13M |
| [Tanga](east-africa/Tanzania/Tanga/) | TZ | `light-metro-3car` | 3 | 27 | 48 | 50 | 72% | $304M | $6M | $12M |
| [Lusaka](east-africa/Zambia/Lusaka/) | ZM | `metro-6car` | 6 | 123 | 236 | 192 | 34% | $1.49bn | $6M | $53M |
| [Kinshasa](central-africa/DR%20Congo/Kinshasa/) | CD | `metro-6car` | 8 | 183 | 385 | 310 | 49% | $2.43bn | $6M | $82M |
| [Fort Portal](east-africa/Uganda/Fort-Portal/) | UG | `tram-2car` | 3 | 21 | 36 | 51 | 84% | $230M | $6M | $10M |
| [Mansoura Eg](west-asia/Egypt/Mansoura-Eg/) | EG | `light-metro-3car` | 3 | 34 | 56 | 56 | 54% | $355M | $6M | $15M |
| [Luxor](west-asia/Egypt/Luxor/) | EG | `light-metro-3car` | 3 | 34 | 54 | 54 | 73% | $340M | $6M | $15M |
| [Bandung](southeast-asia/Indonesia/Bandung/) | ID | `metro-4car` | 6 | 126 | 257 | 208 | 41% | $1.63bn | $6M | $57M |
| [Arua](east-africa/Uganda/Arua/) | UG | `tram-2car` | 3 | 23 | 37 | 51 | 78% | $234M | $6M | $11M |
| [Arish](west-asia/Egypt/Arish/) | EG | `tram-2car` | 1 | 7 | 13 | 18 | 44% | $82M | $6M | $3M |
| [Polokwane](south-africa/South%20Africa/Polokwane/) | ZA | `light-metro-3car` | 3 | 34 | 52 | 52 | 60% | $327M | $6M | $15M |
| [Indore](south-asia/India/Indore/) | IN | `metro-6car` | 7 | 146 | 324 | 260 | 48% | $2.05bn | $6M | $62M |
| [Duhok](west-asia/Iraq/Duhok/) | IQ | `light-metro-3car` | 3 | 32 | 53 | 54 | 53% | $338M | $6M | $15M |
| [Jeddah](west-asia/Saudi%20Arabia/Jeddah/) | SA | `metro-6car` | 8 | 202 | 406 | 326 | 45% | $2.58bn | $6M | $93M |
| [Vadodara](south-asia/India/Vadodara/) | IN | `metro-4car` | 5 | 89 | 164 | 137 | 48% | $1.04bn | $6M | $43M |
| [Beirut](west-asia/Lebanon/Beirut/) | LB | `metro-4car` | 6 | 83 | 159 | 134 | 70% | $1.02bn | $6M | $40M |
| [Bhopal](south-asia/India/Bhopal/) | IN | `metro-4car` | 6 | 107 | 206 | 169 | 52% | $1.31bn | $6M | $51M |
| [Durban](south-africa/South%20Africa/Durban/) | ZA | `metro-6car` | 9 | 172 | 401 | 325 | 79% | $2.56bn | $6M | $75M |
| [Goma](central-africa/DR%20Congo/Goma/) | CD | `light-metro-3car` | 3 | 39 | 58 | 58 | 60% | $371M | $6M | $17M |
| [Kisangani](central-africa/DR%20Congo/Kisangani/) | CD | `metro-4car` | 2 | 27 | 47 | 40 | 64% | $303M | $6M | $13M |
| [Hoima](east-africa/Uganda/Hoima/) | UG | `tram-2car` | 3 | 19 | 31 | 45 | 84% | $202M | $6M | $9M |
| [Naivasha](east-africa/Kenya/Naivasha/) | KE | `tram-2car` | 3 | 20 | 33 | 48 | 86% | $212M | $6M | $9M |
| [Mbeya](east-africa/Tanzania/Mbeya/) | TZ | `light-metro-3car` | 3 | 39 | 55 | 55 | 44% | $354M | $6M | $18M |
| [Coimbatore](south-asia/India/Coimbatore/) | IN | `metro-6car` | 5 | 121 | 268 | 214 | 31% | $1.73bn | $6M | $51M |
| [Aden](west-asia/Yemen/Aden/) | YE | `light-metro-3car` | 3 | 28 | 44 | 46 | 43% | $286M | $6M | $12M |
| [Malindi](east-africa/Kenya/Malindi/) | KE | `tram-2car` | 3 | 20 | 29 | 44 | 79% | $190M | $6M | $9M |
| [Dakar](west-africa/Senegal/Dakar/) | SN | `metro-6car` | 5 | 107 | 204 | 167 | 52% | $1.32bn | $6M | $47M |
| [Karachi](south-asia/Pakistan/Karachi/) | PK | `metro-6car` | 9 | 231 | 472 | 377 | 48% | $3.06bn | $6M | $100M |
| [Barisal](south-asia/Bangladesh/Barisal/) | BD | `light-metro-3car` | 3 | 30 | 59 | 60 | 50% | $380M | $6M | $12M |
| [Sohag](west-asia/Egypt/Sohag/) | EG | `light-metro-3car` | 3 | 32 | 60 | 60 | 68% | $391M | $6M | $13M |
| [Raqqa](west-asia/Syria/Raqqa/) | SY | `light-metro-3car` | 3 | 25 | 45 | 46 | 86% | $291M | $6M | $11M |
| [Uige](east-africa/Angola/Uige/) | AO | `light-metro-3car` | 1 | 8 | 13 | 14 | 67% | $84M | $6M | $4M |
| [Khulna](south-asia/Bangladesh/Khulna/) | BD | `metro-4car` | 6 | 82 | 182 | 152 | 57% | $1.18bn | $6M | $37M |
| [Varanasi](south-asia/India/Varanasi/) | IN | `metro-4car` | 5 | 100 | 202 | 165 | 47% | $1.31bn | $6M | $43M |
| [Jos](west-africa/Nigeria/Jos/) | NG | `light-metro-3car` | 3 | 40 | 54 | 55 | 26% | $349M | $6M | $17M |
| [Antananarivo](east-africa/Madagascar/Antananarivo/) | MG | `metro-6car` | 7 | 155 | 339 | 272 | 42% | $2.20bn | $6M | $65M |
| [Taiz](west-asia/Yemen/Taiz/) | YE | `light-metro-3car` | 3 | 33 | 49 | 51 | 55% | $318M | $6M | $15M |
| [Entebbe](east-africa/Uganda/Entebbe/) | UG | `tram-2car` | 3 | 28 | 43 | 59 | 70% | $281M | $7M | $13M |
| [Masaka](east-africa/Uganda/Masaka/) | UG | `tram-2car` | 3 | 20 | 32 | 46 | 56% | $208M | $7M | $9M |
| [Chittagong](south-asia/Bangladesh/Chittagong/) | BD | `metro-6car` | 8 | 161 | 374 | 302 | 64% | $2.43bn | $7M | $71M |
| [Fez](north-africa/Morocco/Fez/) | MA | `metro-4car` | 4 | 58 | 113 | 94 | 73% | $733M | $7M | $28M |
| [Amman](west-asia/Jordan/Amman/) | JO | `metro-6car` | 8 | 172 | 354 | 286 | 51% | $2.31bn | $7M | $76M |
| [Patna](south-asia/India/Patna/) | IN | `metro-4car` | 5 | 84 | 185 | 152 | 50% | $1.21bn | $7M | $36M |
| [Basra](west-asia/Iraq/Basra/) | IQ | `metro-6car` | 7 | 119 | 289 | 236 | 54% | $1.89bn | $7M | $48M |
| [Mosul](west-asia/Iraq/Mosul/) | IQ | `metro-4car` | 5 | 60 | 145 | 122 | 38% | $943M | $7M | $23M |
| [Quetta](south-asia/Pakistan/Quetta/) | PK | `metro-4car` | 5 | 78 | 140 | 120 | 54% | $915M | $7M | $39M |
| [Rajkot](south-asia/India/Rajkot/) | IN | `metro-4car` | 5 | 76 | 143 | 121 | 58% | $933M | $7M | $36M |
| [Nacala](east-africa/Mozambique/Nacala/) | MZ | `tram-2car` | 3 | 25 | 39 | 54 | 80% | $255M | $7M | $11M |
| [Songea](east-africa/Tanzania/Songea/) | TZ | `tram-2car` | 1 | 7 | 11 | 16 | 73% | $75M | $7M | $3M |
| [Herat](south-asia/Afghanistan/Herat/) | AF | `light-metro-3car` | 3 | 43 | 65 | 64 | 36% | $424M | $7M | $19M |
| [Bahawalpur](south-asia/Pakistan/Bahawalpur/) | PK | `light-metro-3car` | 3 | 29 | 46 | 49 | 42% | $303M | $7M | $14M |
| [Maroua](west-africa/Cameroon/Maroua/) | CM | `light-metro-3car` | 3 | 29 | 53 | 54 | 74% | $346M | $7M | $12M |
| [Kirkuk](west-asia/Iraq/Kirkuk/) | IQ | `metro-4car` | 6 | 92 | 170 | 142 | 60% | $1.12bn | $7M | $45M |
| [Sidon](west-asia/Lebanon/Sidon/) | LB | `tram-2car` | 3 | 23 | 37 | 52 | 71% | $246M | $7M | $11M |
| [Karbala](west-asia/Iraq/Karbala/) | IQ | `metro-4car` | 6 | 89 | 170 | 144 | 67% | $1.12bn | $7M | $44M |
| [Phnom Penh](southeast-asia/Cambodia/Phnom-Penh/) | KH | `metro-4car` | 6 | 107 | 228 | 186 | 48% | $1.50bn | $7M | $47M |
| [Surabaya](southeast-asia/Indonesia/Surabaya/) | ID | `metro-6car` | 7 | 143 | 294 | 240 | 40% | $1.95bn | $7M | $61M |
| [Kisii](east-africa/Kenya/Kisii/) | KE | `tram-2car` | 3 | 17 | 30 | 43 | 67% | $196M | $7M | $8M |
| [Lobito](east-africa/Angola/Lobito/) | AO | `light-metro-3car` | 3 | 25 | 38 | 41 | 69% | $251M | $7M | $12M |
| [Tabuk](west-asia/Saudi%20Arabia/Tabuk/) | SA | `light-metro-3car` | 3 | 45 | 63 | 63 | 27% | $418M | $7M | $20M |
| [Fallujah](west-asia/Iraq/Fallujah/) | IQ | `light-metro-3car` | 3 | 28 | 46 | 48 | 57% | $306M | $7M | $13M |
| [Kano](west-africa/Nigeria/Kano/) | NG | `metro-6car` | 6 | 154 | 362 | 286 | 37% | $2.41bn | $7M | $57M |
| [Deir Ez Zor](west-asia/Syria/Deir-Ez-Zor/) | SY | `light-metro-3car` | 3 | 32 | 57 | 57 | 62% | $380M | $7M | $14M |
| [La Paz](latin-america/Bolivia/La-Paz/) | BO | `metro-4car` | 6 | 115 | 212 | 174 | 57% | $1.42bn | $7M | $55M |
| [Yaounde](east-africa/Cameroon/Yaounde/) | CM | `metro-6car` | 8 | 136 | 267 | 219 | 43% | $1.79bn | $7M | $63M |
| [Oujda](north-africa/Morocco/Oujda/) | MA | `light-metro-3car` | 3 | 33 | 47 | 48 | 48% | $315M | $7M | $16M |
| [Ramadi](west-asia/Iraq/Ramadi/) | IQ | `light-metro-3car` | 3 | 35 | 47 | 49 | 39% | $315M | $7M | $17M |
| [Garissa](east-africa/Kenya/Garissa/) | KE | `tram-2car` | 3 | 19 | 29 | 43 | 71% | $194M | $7M | $9M |
| [Yangon](southeast-asia/Myanmar/Yangon/) | MM | `metro-6car` | 9 | 214 | 418 | 335 | 56% | $2.81bn | $7M | $102M |
| [Port Sudan](north-africa/Sudan/Port-Sudan/) | SD | `light-metro-3car` | 3 | 22 | 33 | 38 | 80% | $225M | $7M | $10M |
| [Qena](west-asia/Egypt/Qena/) | EG | `light-metro-3car` | 3 | 26 | 45 | 47 | 75% | $305M | $7M | $12M |
| [Safi](north-africa/Morocco/Safi/) | MA | `light-metro-3car` | 3 | 26 | 39 | 43 | 72% | $266M | $7M | $12M |
| [Kathmandu](south-asia/Nepal/Kathmandu/) | NP | `metro-4car` | 6 | 103 | 203 | 167 | 46% | $1.37bn | $7M | $51M |
| [Kabul](south-asia/Afghanistan/Kabul/) | AF | `metro-6car` | 7 | 137 | 261 | 215 | 53% | $1.77bn | $7M | $63M |
| [Tetouan](north-africa/Morocco/Tetouan/) | MA | `light-metro-3car` | 3 | 33 | 54 | 56 | 69% | $368M | $7M | $14M |
| [Quelimane](east-africa/Mozambique/Quelimane/) | MZ | `light-metro-3car` | 1 | 6 | 10 | 12 | 48% | $70M | $7M | $3M |
| [Lubumbashi](central-africa/DR%20Congo/Lubumbashi/) | CD | `metro-4car` | 4 | 75 | 130 | 107 | 34% | $887M | $7M | $39M |
| [Port Said](west-asia/Egypt/Port-Said/) | EG | `light-metro-3car` | 3 | 25 | 35 | 39 | 71% | $240M | $7M | $12M |
| [Sanaa](west-asia/Yemen/Sanaa/) | YE | `metro-6car` | 9 | 126 | 261 | 218 | 78% | $1.79bn | $7M | $61M |
| [Uyo](west-africa/Nigeria/Uyo/) | NG | `light-metro-3car` | 3 | 24 | 31 | 36 | 25% | $214M | $7M | $12M |
| [Diwaniyah](west-asia/Iraq/Diwaniyah/) | IQ | `light-metro-3car` | 3 | 36 | 54 | 55 | 43% | $370M | $7M | $16M |
| [Nyala](north-africa/Sudan/Nyala/) | SD | `light-metro-3car` | 3 | 29 | 47 | 48 | 61% | $322M | $7M | $11M |
| [Maiduguri](west-africa/Nigeria/Maiduguri/) | NG | `metro-4car` | 5 | 86 | 176 | 145 | 34% | $1.22bn | $7M | $38M |
| [Kafr El Sheikh](west-asia/Egypt/Kafr-El-Sheikh/) | EG | `tram-2car` | 3 | 22 | 33 | 47 | 75% | $228M | $7M | $11M |
| [Machakos](east-africa/Kenya/Machakos/) | KE | `tram-2car` | 3 | 16 | 27 | 40 | 76% | $184M | $7M | $8M |
| [Beni Mellal](north-africa/Morocco/Beni-Mellal/) | MA | `tram-2car` | 3 | 18 | 30 | 45 | 85% | $210M | $7M | $9M |
| [Beni Suef](west-asia/Egypt/Beni-Suef/) | EG | `light-metro-3car` | 3 | 23 | 35 | 38 | 55% | $243M | $7M | $11M |
| [Douala](west-africa/Cameroon/Douala/) | CM | `metro-6car` | 5 | 129 | 228 | 184 | 37% | $1.59bn | $7M | $59M |
| [Bertoua](west-africa/Cameroon/Bertoua/) | CM | `light-metro-3car` | 3 | 20 | 29 | 34 | 77% | $203M | $7M | $10M |
| [Hurghada](west-asia/Egypt/Hurghada/) | EG | `tram-2car` | 3 | 28 | 43 | 57 | 56% | $302M | $7M | $13M |
| [Benin City](west-africa/Nigeria/Benin-City/) | NG | `metro-4car` | 4 | 77 | 132 | 111 | 44% | $934M | $7M | $40M |
| [Pemba Mz](east-africa/Mozambique/Pemba-Mz/) | MZ | `tram-2car` | 3 | 20 | 30 | 43 | 63% | $213M | $7M | $10M |
| [Kitale](east-africa/Kenya/Kitale/) | KE | `tram-2car` | 3 | 16 | 29 | 43 | 85% | $208M | $7M | $8M |
| [Faisalabad](south-asia/Pakistan/Faisalabad/) | PK | `metro-6car` | 5 | 93 | 166 | 137 | 52% | $1.18bn | $7M | $45M |
| [Najran](west-asia/Saudi%20Arabia/Najran/) | SA | `light-metro-3car` | 3 | 33 | 57 | 57 | 46% | $402M | $7M | $13M |
| [Sayun](west-asia/Yemen/Sayun/) | YE | `tram-2car` | 2 | 15 | 22 | 31 | 58% | $153M | $7M | $7M |
| [Soyo](east-africa/Angola/Soyo/) | AO | `tram-2car` | 2 | 14 | 22 | 32 | 70% | $161M | $7M | $7M |
| [Najaf](west-asia/Iraq/Najaf/) | IQ | `metro-4car` | 6 | 91 | 172 | 144 | 60% | $1.24bn | $7M | $46M |
| [Waw](north-africa/Sudan/Waw/) | SD | `tram-2car` | 2 | 11 | 18 | 27 | 73% | $128M | $7M | $6M |
| [Hodeidah](west-asia/Yemen/Hodeidah/) | YE | `light-metro-3car` | 3 | 27 | 36 | 40 | 61% | $260M | $7M | $13M |
| [Xai Xai](east-africa/Mozambique/Xai-Xai/) | MZ | `tram-2car` | 2 | 12 | 18 | 27 | 43% | $129M | $7M | $6M |
| [Edea](west-africa/Cameroon/Edea/) | CM | `tram-2car` | 1 | 7 | 10 | 14 | 61% | $70M | $7M | $4M |
| [Tartus](west-asia/Syria/Tartus/) | SY | `tram-2car` | 3 | 23 | 35 | 49 | 73% | $253M | $7M | $11M |
| [Ibadan](west-africa/Nigeria/Ibadan/) | NG | `metro-6car` | 4 | 90 | 135 | 111 | 24% | $985M | $7M | $44M |
| [Meru Ke](east-africa/Kenya/Meru-Ke/) | KE | `tram-2car` | 2 | 12 | 22 | 32 | 52% | $161M | $7M | $5M |
| [Zarqa](west-asia/Jordan/Zarqa/) | JO | `light-metro-3car` | 3 | 57 | 83 | 80 | 48% | $608M | $7M | $24M |
| [Lahij](west-asia/Yemen/Lahij/) | YE | `tram-2car` | 3 | 19 | 29 | 43 | 82% | $214M | $7M | $10M |
| [Ngaoundere](west-africa/Cameroon/Ngaoundere/) | CM | `light-metro-3car` | 3 | 19 | 28 | 34 | 57% | $208M | $7M | $9M |
| [Aba Ng](west-africa/Nigeria/Aba-Ng/) | NG | `light-metro-3car` | 3 | 26 | 34 | 38 | 40% | $253M | $7M | $13M |
| [Moshi](east-africa/Tanzania/Moshi/) | TZ | `tram-2car` | 3 | 21 | 36 | 51 | 76% | $269M | $8M | $11M |
| [Iringa](east-africa/Tanzania/Iringa/) | TZ | `tram-2car` | 3 | 20 | 28 | 42 | 67% | $209M | $8M | $10M |
| [Bamako](west-africa/Mali/Bamako/) | ML | `metro-4car` | 6 | 118 | 257 | 207 | 31% | $1.95bn | $8M | $47M |
| [Kut](west-asia/Iraq/Kut/) | IQ | `light-metro-3car` | 3 | 32 | 56 | 55 | 37% | $438M | $8M | $14M |
| [Nasiriyah](west-asia/Iraq/Nasiriyah/) | IQ | `light-metro-3car` | 3 | 33 | 56 | 56 | 40% | $447M | $8M | $15M |
| [Larkana](south-asia/Pakistan/Larkana/) | PK | `light-metro-3car` | 2 | 19 | 38 | 39 | 28% | $302M | $8M | $9M |
| [Kassala](north-africa/Sudan/Kassala/) | SD | `light-metro-3car` | 3 | 20 | 34 | 39 | 76% | $278M | $8M | $9M |
| [Garoua](west-africa/Cameroon/Garoua/) | CM | `light-metro-3car` | 3 | 29 | 44 | 46 | 38% | $355M | $8M | $12M |
| [Khouribga](north-africa/Morocco/Khouribga/) | MA | `tram-2car` | 2 | 11 | 15 | 23 | 57% | $119M | $8M | $6M |
| [Tete](east-africa/Mozambique/Tete/) | MZ | `light-metro-3car` | 3 | 23 | 38 | 41 | 77% | $315M | $8M | $9M |
| [Tabora](east-africa/Tanzania/Tabora/) | TZ | `tram-2car` | 2 | 13 | 18 | 26 | 54% | $145M | $8M | $7M |
| [Jodhpur](south-asia/India/Jodhpur/) | IN | `metro-4car` | 5 | 82 | 150 | 124 | 44% | $1.24bn | $8M | $37M |
| [Sumbawanga](east-africa/Tanzania/Sumbawanga/) | TZ | `tram-2car` | 1 | 5 | 7 | 11 | 35% | $54M | $8M | $3M |
| [Mymensingh](south-asia/Bangladesh/Mymensingh/) | BD | `light-metro-3car` | 3 | 37 | 67 | 67 | 41% | $562M | $8M | $13M |
| [Amarah](west-asia/Iraq/Amarah/) | IQ | `light-metro-3car` | 3 | 32 | 45 | 46 | 43% | $374M | $8M | $15M |
| [Nyeri](east-africa/Kenya/Nyeri/) | KE | `tram-2car` | 3 | 22 | 37 | 51 | 62% | $313M | $9M | $10M |
| [Sheikhupura](south-asia/Pakistan/Sheikhupura/) | PK | `light-metro-3car` | 2 | 17 | 19 | 22 | 32% | $173M | $9M | $9M |
| [Malanje](east-africa/Angola/Malanje/) | AO | `light-metro-3car` | 2 | 12 | 15 | 19 | 57% | $136M | $9M | $7M |
| [Sialkot](south-asia/Pakistan/Sialkot/) | PK | `light-metro-3car` | 3 | 37 | 59 | 59 | 43% | $549M | $9M | $16M |
| [Sukkur](south-asia/Pakistan/Sukkur/) | PK | `light-metro-3car` | 3 | 31 | 51 | 53 | 55% | $492M | $10M | $13M |
| [Biratnagar](south-asia/Nepal/Biratnagar/) | NP | `tram-2car` | 3 | 23 | 34 | 48 | 60% | $428M | $13M | $10M |
