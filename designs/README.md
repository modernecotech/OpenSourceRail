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
| [Bafoussam](west-africa/Cameroon/Bafoussam/) | CM | `light-metro-3car` | 3 | 34 | 73 | 72 | 47% | $735M | $10M | $12M |
| [Huye](east-africa/Rwanda/Huye/) | RW | `tram-2car` | 3 | 28 | 46 | 61 | 23% | $479M | $10M | $10M |
| [Fayoum](west-asia/Egypt/Fayoum/) | EG | `light-metro-3car` | 3 | 36 | 69 | 67 | 72% | $727M | $11M | $14M |
| [Tanta](west-asia/Egypt/Tanta/) | EG | `light-metro-3car` | 3 | 35 | 75 | 73 | 56% | $799M | $11M | $14M |
| [Agadir](north-africa/Morocco/Agadir/) | MA | `light-metro-3car` | 3 | 44 | 83 | 80 | 65% | $887M | $11M | $17M |
| [Erbil](west-asia/Iraq/Erbil/) | IQ | `metro-4car` | 5 | 56 | 140 | 117 | 64% | $1.51bn | $11M | $21M |
| [Kisumu](east-africa/Kenya/Kisumu/) | KE | `light-metro-3car` | 3 | 42 | 75 | 74 | 31% | $816M | $11M | $14M |
| [Damietta](west-asia/Egypt/Damietta/) | EG | `light-metro-3car` | 3 | 38 | 74 | 73 | 72% | $802M | $11M | $13M |
| [Hofuf](west-asia/Saudi%20Arabia/Hofuf/) | SA | `light-metro-3car` | 3 | 46 | 78 | 77 | 50% | $852M | $11M | $18M |
| [Asyut](west-asia/Egypt/Asyut/) | EG | `light-metro-3car` | 3 | 31 | 63 | 62 | 58% | $687M | $11M | $11M |
| [Khamis Mushait](west-asia/Saudi%20Arabia/Khamis-Mushait/) | SA | `light-metro-3car` | 3 | 38 | 69 | 68 | 35% | $757M | $11M | $14M |
| [Bamenda](west-africa/Cameroon/Bamenda/) | CM | `light-metro-3car` | 3 | 31 | 54 | 55 | 59% | $594M | $11M | $12M |
| [Hail](west-asia/Saudi%20Arabia/Hail/) | SA | `light-metro-3car` | 3 | 35 | 63 | 62 | 47% | $695M | $11M | $13M |
| [Vientiane](southeast-asia/Laos/Vientiane/) | LA | `light-metro-3car` | 3 | 46 | 81 | 78 | 43% | $891M | $11M | $18M |
| [Lira](east-africa/Uganda/Lira/) | UG | `tram-2car` | 3 | 23 | 45 | 61 | 64% | $501M | $11M | $10M |
| [Arusha](east-africa/Tanzania/Arusha/) | TZ | `light-metro-3car` | 3 | 44 | 73 | 72 | 36% | $806M | $11M | $16M |
| [Nablus](west-asia/Palestine/Nablus/) | PS | `light-metro-3car` | 3 | 34 | 65 | 65 | 84% | $720M | $11M | $13M |
| [Kenitra](north-africa/Morocco/Kenitra/) | MA | `light-metro-3car` | 3 | 35 | 60 | 60 | 66% | $669M | $11M | $14M |
| [Rahim Yar Khan](south-asia/Pakistan/Rahim-Yar-Khan/) | PK | `light-metro-3car` | 3 | 24 | 46 | 47 | 37% | $514M | $11M | $10M |
| [Thika](east-africa/Kenya/Thika/) | KE | `light-metro-3car` | 3 | 38 | 76 | 74 | 63% | $844M | $11M | $13M |
| [Omdurman](north-africa/Sudan/Omdurman/) | SD | `metro-4car` | 6 | 104 | 255 | 207 | 47% | $2.85bn | $11M | $41M |
| [Sylhet](south-asia/Bangladesh/Sylhet/) | BD | `light-metro-3car` | 3 | 40 | 73 | 72 | 45% | $815M | $11M | $14M |
| [Dodoma](east-africa/Tanzania/Dodoma/) | TZ | `light-metro-3car` | 3 | 36 | 66 | 66 | 40% | $746M | $11M | $14M |
| [Al Kharj](west-asia/Saudi%20Arabia/Al-Kharj/) | SA | `light-metro-3car` | 3 | 38 | 68 | 67 | 70% | $764M | $11M | $14M |
| [Bukavu](central-africa/DR%20Congo/Bukavu/) | CD | `light-metro-3car` | 3 | 37 | 60 | 60 | 60% | $680M | $11M | $15M |
| [Hama](west-asia/Syria/Hama/) | SY | `light-metro-3car` | 3 | 31 | 55 | 55 | 53% | $625M | $11M | $13M |
| [Dammam](west-asia/Saudi%20Arabia/Dammam/) | SA | `metro-4car` | 4 | 95 | 210 | 168 | 28% | $2.37bn | $11M | $39M |
| [Shinyanga](east-africa/Tanzania/Shinyanga/) | TZ | `tram-2car` | 3 | 20 | 37 | 51 | 83% | $417M | $11M | $9M |
| [Lyon](europe/France/Lyon/) | FR | `metro-4car` | 6 | 122 | 287 | 232 | 45% | $3.26bn | $11M | $49M |
| [Hebron](west-asia/Palestine/Hebron/) | PS | `light-metro-3car` | 3 | 40 | 69 | 68 | 61% | $785M | $11M | $16M |
| [Bloemfontein](south-africa/South%20Africa/Bloemfontein/) | ZA | `light-metro-3car` | 3 | 42 | 72 | 71 | 35% | $820M | $11M | $16M |
| [Gulu](east-africa/Uganda/Gulu/) | UG | `light-metro-3car` | 3 | 36 | 64 | 63 | 50% | $726M | $11M | $15M |
| [Taif](west-asia/Saudi%20Arabia/Taif/) | SA | `light-metro-3car` | 3 | 42 | 73 | 73 | 41% | $838M | $11M | $17M |
| [Dhamar](west-asia/Yemen/Dhamar/) | YE | `tram-2car` | 3 | 18 | 32 | 46 | 76% | $369M | $11M | $8M |
| [Gaza City](west-asia/Palestine/Gaza-City/) | PS | `light-metro-3car` | 1 | 15 | 24 | 24 | 30% | $274M | $11M | $6M |
| [Lubango](east-africa/Angola/Lubango/) | AO | `light-metro-3car` | 3 | 31 | 55 | 55 | 63% | $623M | $11M | $12M |
| [Namibe](east-africa/Angola/Namibe/) | AO | `tram-2car` | 3 | 25 | 40 | 55 | 61% | $461M | $11M | $11M |
| [Galle](south-asia/Sri%20Lanka/Galle/) | LK | `light-metro-3car` | 3 | 37 | 64 | 64 | 56% | $738M | $11M | $15M |
| [Arish](west-asia/Egypt/Arish/) | EG | `tram-2car` | 1 | 7 | 13 | 18 | 44% | $148M | $11M | $3M |
| [Eldoret](east-africa/Kenya/Eldoret/) | KE | `light-metro-3car` | 3 | 39 | 65 | 64 | 46% | $752M | $12M | $16M |
| [Suez](west-asia/Egypt/Suez/) | EG | `light-metro-3car` | 3 | 32 | 59 | 60 | 65% | $679M | $12M | $12M |
| [Zagazig](west-asia/Egypt/Zagazig/) | EG | `light-metro-3car` | 3 | 30 | 56 | 57 | 59% | $649M | $12M | $13M |
| [Pokhara](south-asia/Nepal/Pokhara/) | NP | `light-metro-3car` | 3 | 44 | 82 | 80 | 52% | $951M | $12M | $18M |
| [Jinja](east-africa/Uganda/Jinja/) | UG | `tram-2car` | 3 | 29 | 46 | 61 | 41% | $526M | $12M | $12M |
| [Rangpur](south-asia/Bangladesh/Rangpur/) | BD | `light-metro-3car` | 3 | 36 | 59 | 59 | 47% | $688M | $12M | $14M |
| [Comilla](south-asia/Bangladesh/Comilla/) | BD | `light-metro-3car` | 3 | 38 | 66 | 65 | 41% | $759M | $12M | $15M |
| [Tangier](north-africa/Morocco/Tangier/) | MA | `metro-4car` | 5 | 64 | 153 | 129 | 57% | $1.77bn | $12M | $25M |
| [Nakuru](east-africa/Kenya/Nakuru/) | KE | `light-metro-3car` | 3 | 37 | 60 | 61 | 46% | $690M | $12M | $14M |
| [Tripoli Lb](west-asia/Lebanon/Tripoli-Lb/) | LB | `light-metro-3car` | 3 | 30 | 53 | 55 | 50% | $615M | $12M | $12M |
| [East London Za](south-africa/South%20Africa/East-London-Za/) | ZA | `light-metro-3car` | 3 | 36 | 63 | 63 | 51% | $734M | $12M | $13M |
| [Kampala](east-africa/Uganda/Kampala/) | UG | `metro-4car` | 4 | 99 | 201 | 160 | 24% | $2.34bn | $12M | $41M |
| [Kakamega](east-africa/Kenya/Kakamega/) | KE | `tram-2car` | 3 | 24 | 42 | 58 | 77% | $492M | $12M | $10M |
| [Port Harcourt](west-africa/Nigeria/Port-Harcourt/) | NG | `metro-4car` | 4 | 95 | 199 | 160 | 31% | $2.31bn | $12M | $39M |
| [Rajshahi](south-asia/Bangladesh/Rajshahi/) | BD | `light-metro-3car` | 3 | 30 | 50 | 52 | 30% | $581M | $12M | $12M |
| [Ibb](west-asia/Yemen/Ibb/) | YE | `light-metro-3car` | 3 | 40 | 72 | 71 | 58% | $835M | $12M | $17M |
| [Mukalla](west-asia/Yemen/Mukalla/) | YE | `light-metro-3car` | 3 | 33 | 61 | 61 | 72% | $711M | $12M | $14M |
| [Ilorin](west-africa/Nigeria/Ilorin/) | NG | `light-metro-3car` | 3 | 39 | 60 | 60 | 31% | $705M | $12M | $16M |
| [Hillah](west-asia/Iraq/Hillah/) | IQ | `light-metro-3car` | 3 | 42 | 69 | 68 | 43% | $809M | $12M | $18M |
| [Mwanza](east-africa/Tanzania/Mwanza/) | TZ | `metro-4car` | 5 | 70 | 162 | 136 | 45% | $1.90bn | $12M | $29M |
| [Rubavu](east-africa/Rwanda/Rubavu/) | RW | `tram-2car` | 3 | 28 | 45 | 61 | 48% | $533M | $12M | $12M |
| [Gazipur](south-asia/Bangladesh/Gazipur/) | BD | `metro-4car` | 6 | 127 | 308 | 245 | 38% | $3.63bn | $12M | $52M |
| [Gujranwala](south-asia/Pakistan/Gujranwala/) | PK | `metro-4car` | 4 | 72 | 160 | 130 | 39% | $1.89bn | $12M | $30M |
| [Idlib](west-asia/Syria/Idlib/) | SY | `tram-2car` | 3 | 18 | 35 | 49 | 79% | $412M | $12M | $8M |
| [Nelspruit](south-africa/South%20Africa/Nelspruit/) | ZA | `tram-2car` | 3 | 22 | 39 | 53 | 68% | $463M | $12M | $10M |
| [Songea](east-africa/Tanzania/Songea/) | TZ | `tram-2car` | 1 | 7 | 11 | 16 | 73% | $135M | $12M | $3M |
| [Mazar E Sharif](south-asia/Afghanistan/Mazar-E-Sharif/) | AF | `light-metro-3car` | 3 | 37 | 63 | 61 | 59% | $744M | $12M | $16M |
| [Aqaba](west-asia/Jordan/Aqaba/) | JO | `tram-2car` | 3 | 23 | 34 | 48 | 57% | $406M | $12M | $10M |
| [Huambo](east-africa/Angola/Huambo/) | AO | `light-metro-3car` | 3 | 31 | 53 | 55 | 72% | $624M | $12M | $13M |
| [Benguela](east-africa/Angola/Benguela/) | AO | `light-metro-3car` | 3 | 28 | 50 | 51 | 69% | $590M | $12M | $11M |
| [Kandy](south-asia/Sri%20Lanka/Kandy/) | LK | `light-metro-3car` | 3 | 43 | 78 | 76 | 56% | $923M | $12M | $16M |
| [Zanzibar City](east-africa/Tanzania/Zanzibar-City/) | TZ | `light-metro-3car` | 3 | 32 | 56 | 56 | 70% | $667M | $12M | $12M |
| [Abha](west-asia/Saudi%20Arabia/Abha/) | SA | `light-metro-3car` | 3 | 45 | 70 | 68 | 34% | $828M | $12M | $18M |
| [Onitsha](west-africa/Nigeria/Onitsha/) | NG | `metro-4car` | 4 | 76 | 184 | 148 | 30% | $2.18bn | $12M | $31M |
| [Minya](west-asia/Egypt/Minya/) | EG | `light-metro-3car` | 3 | 32 | 53 | 53 | 69% | $634M | $12M | $12M |
| [Mecca](west-asia/Saudi%20Arabia/Mecca/) | SA | `metro-4car` | 6 | 114 | 251 | 205 | 46% | $2.99bn | $12M | $49M |
| [Ranchi](south-asia/India/Ranchi/) | IN | `metro-4car` | 6 | 96 | 216 | 179 | 50% | $2.57bn | $12M | $40M |
| [Irbid](west-asia/Jordan/Irbid/) | JO | `light-metro-3car` | 3 | 33 | 56 | 56 | 42% | $669M | $12M | $15M |
| [Marrakech](north-africa/Morocco/Marrakech/) | MA | `metro-4car` | 6 | 79 | 191 | 159 | 58% | $2.28bn | $12M | $33M |
| [Chimoio](east-africa/Mozambique/Chimoio/) | MZ | `light-metro-3car` | 2 | 20 | 35 | 35 | 55% | $413M | $12M | $8M |
| [Jizan](west-asia/Saudi%20Arabia/Jizan/) | SA | `light-metro-3car` | 3 | 28 | 47 | 48 | 64% | $558M | $12M | $11M |
| [Kigali](east-africa/Rwanda/Kigali/) | RW | `metro-4car` | 4 | 86 | 171 | 139 | 34% | $2.04bn | $12M | $37M |
| [El Obeid](north-africa/Sudan/El-Obeid/) | SD | `light-metro-3car` | 3 | 28 | 46 | 47 | 72% | $552M | $12M | $11M |
| [Narayanganj](south-asia/Bangladesh/Narayanganj/) | BD | `light-metro-3car` | 3 | 50 | 82 | 80 | 27% | $983M | $12M | $18M |
| [Nampula](east-africa/Mozambique/Nampula/) | MZ | `light-metro-3car` | 3 | 30 | 52 | 54 | 67% | $621M | $12M | $12M |
| [Jaffna](south-asia/Sri%20Lanka/Jaffna/) | LK | `light-metro-3car` | 3 | 34 | 52 | 52 | 42% | $623M | $12M | $14M |
| [Latakia](west-asia/Syria/Latakia/) | SY | `light-metro-3car` | 3 | 26 | 41 | 43 | 54% | $492M | $12M | $11M |
| [Nador](north-africa/Morocco/Nador/) | MA | `tram-2car` | 3 | 19 | 34 | 48 | 70% | $413M | $12M | $9M |
| [Kigoma](east-africa/Tanzania/Kigoma/) | TZ | `tram-2car` | 3 | 24 | 35 | 49 | 77% | $421M | $12M | $11M |
| [Buraidah](west-asia/Saudi%20Arabia/Buraidah/) | SA | `light-metro-3car` | 3 | 54 | 80 | 78 | 35% | $958M | $12M | $24M |
| [Samawah](west-asia/Iraq/Samawah/) | IQ | `light-metro-3car` | 3 | 33 | 55 | 55 | 56% | $661M | $12M | $15M |
| [San Salvador](latin-america/El%20Salvador/San-Salvador/) | SV | `metro-4car` | 6 | 121 | 255 | 207 | 50% | $3.07bn | $12M | $56M |
| [Meerut](south-asia/India/Meerut/) | IN | `metro-4car` | 4 | 84 | 180 | 146 | 43% | $2.17bn | $12M | $36M |
| [Mombasa](east-africa/Kenya/Mombasa/) | KE | `metro-4car` | 6 | 95 | 201 | 167 | 52% | $2.42bn | $12M | $42M |
| [Vijayawada](south-asia/India/Vijayawada/) | IN | `metro-4car` | 6 | 94 | 225 | 184 | 58% | $2.72bn | $12M | $41M |
| [Kandahar](south-asia/Afghanistan/Kandahar/) | AF | `light-metro-3car` | 3 | 43 | 64 | 62 | 53% | $775M | $12M | $19M |
| [Medina](west-asia/Saudi%20Arabia/Medina/) | SA | `metro-4car` | 5 | 104 | 211 | 171 | 47% | $2.56bn | $12M | $44M |
| [Maputo](east-africa/Mozambique/Maputo/) | MZ | `metro-4car` | 6 | 83 | 186 | 156 | 71% | $2.25bn | $12M | $35M |
| [Mbarara](east-africa/Uganda/Mbarara/) | UG | `light-metro-3car` | 3 | 36 | 59 | 59 | 53% | $711M | $12M | $15M |
| [Davao](southeast-asia/Philippines/Davao/) | PH | `metro-4car` | 6 | 108 | 229 | 186 | 72% | $2.77bn | $12M | $50M |
| [Jalalabad Af](south-asia/Afghanistan/Jalalabad-Af/) | AF | `light-metro-3car` | 3 | 32 | 51 | 53 | 69% | $615M | $12M | $14M |
| [Cuenca](latin-america/Ecuador/Cuenca/) | EC | `light-metro-3car` | 3 | 48 | 79 | 77 | 57% | $952M | $12M | $21M |
| [Kirkuk](west-asia/Iraq/Kirkuk/) | IQ | `metro-4car` | 5 | 64 | 141 | 119 | 61% | $1.72bn | $12M | $27M |
| [Tunis](north-africa/Tunisia/Tunis/) | TN | `metro-4car` | 5 | 118 | 240 | 194 | 48% | $2.92bn | $12M | $52M |
| [Baqubah](west-asia/Iraq/Baqubah/) | IQ | `light-metro-3car` | 3 | 37 | 60 | 60 | 50% | $728M | $12M | $16M |
| [Aleppo](west-asia/Syria/Aleppo/) | SY | `metro-4car` | 5 | 89 | 176 | 145 | 46% | $2.14bn | $12M | $40M |
| [Visakhapatnam](south-asia/India/Visakhapatnam/) | IN | `metro-4car` | 6 | 110 | 240 | 196 | 52% | $2.92bn | $12M | $49M |
| [Damanhur](west-asia/Egypt/Damanhur/) | EG | `light-metro-3car` | 3 | 22 | 41 | 44 | 77% | $505M | $12M | $10M |
| [Mbuji Mayi](central-africa/DR%20Congo/Mbuji-Mayi/) | CD | `metro-4car` | 4 | 55 | 118 | 101 | 70% | $1.44bn | $12M | $25M |
| [Ismailia](west-asia/Egypt/Ismailia/) | EG | `light-metro-3car` | 3 | 33 | 53 | 55 | 63% | $652M | $12M | $15M |
| [Arua](east-africa/Uganda/Arua/) | UG | `tram-2car` | 3 | 23 | 37 | 51 | 78% | $451M | $12M | $11M |
| [Fort Portal](east-africa/Uganda/Fort-Portal/) | UG | `tram-2car` | 3 | 21 | 36 | 51 | 84% | $443M | $12M | $10M |
| [Madurai](south-asia/India/Madurai/) | IN | `metro-4car` | 6 | 104 | 222 | 183 | 59% | $2.72bn | $12M | $46M |
| [Hoima](east-africa/Uganda/Hoima/) | UG | `tram-2car` | 3 | 19 | 31 | 45 | 84% | $384M | $12M | $9M |
| [Sohag](west-asia/Egypt/Sohag/) | EG | `light-metro-3car` | 3 | 32 | 60 | 60 | 68% | $741M | $12M | $13M |
| [Peshawar](south-asia/Pakistan/Peshawar/) | PK | `metro-4car` | 4 | 87 | 197 | 158 | 33% | $2.42bn | $12M | $35M |
| [Morogoro](east-africa/Tanzania/Morogoro/) | TZ | `light-metro-3car` | 3 | 32 | 55 | 55 | 61% | $678M | $12M | $13M |
| [Sulaymaniyah](west-asia/Iraq/Sulaymaniyah/) | IQ | `metro-4car` | 4 | 48 | 117 | 99 | 67% | $1.45bn | $12M | $21M |
| [Uige](east-africa/Angola/Uige/) | AO | `light-metro-3car` | 1 | 8 | 13 | 14 | 67% | $161M | $12M | $4M |
| [Damascus](west-asia/Syria/Damascus/) | SY | `metro-4car` | 6 | 113 | 233 | 192 | 45% | $2.89bn | $12M | $51M |
| [Homs](west-asia/Syria/Homs/) | SY | `light-metro-3car` | 3 | 33 | 51 | 53 | 42% | $637M | $12M | $14M |
| [Raipur](south-asia/India/Raipur/) | IN | `metro-4car` | 5 | 88 | 185 | 151 | 43% | $2.30bn | $12M | $37M |
| [Polokwane](south-africa/South%20Africa/Polokwane/) | ZA | `light-metro-3car` | 3 | 34 | 52 | 52 | 60% | $641M | $12M | $15M |
| [Kumba](west-africa/Cameroon/Kumba/) | CM | `light-metro-3car` | 3 | 29 | 43 | 45 | 68% | $529M | $12M | $12M |
| [Entebbe](east-africa/Uganda/Entebbe/) | UG | `tram-2car` | 3 | 28 | 43 | 59 | 70% | $537M | $12M | $13M |
| [Tanga](east-africa/Tanzania/Tanga/) | TZ | `light-metro-3car` | 3 | 27 | 48 | 50 | 72% | $600M | $12M | $12M |
| [Niamey](west-africa/Niger/Niamey/) | NE | `metro-4car` | 4 | 80 | 146 | 120 | 38% | $1.82bn | $12M | $36M |
| [Meknes](north-africa/Morocco/Meknes/) | MA | `light-metro-3car` | 3 | 23 | 39 | 42 | 58% | $493M | $12M | $10M |
| [Ouagadougou](west-africa/Burkina%20Faso/Ouagadougou/) | BF | `metro-4car` | 6 | 138 | 264 | 213 | 37% | $3.30bn | $13M | $64M |
| [Mahalla](west-asia/Egypt/Mahalla/) | EG | `light-metro-3car` | 3 | 22 | 38 | 42 | 69% | $474M | $13M | $9M |
| [Naivasha](east-africa/Kenya/Naivasha/) | KE | `tram-2car` | 3 | 20 | 33 | 48 | 86% | $413M | $13M | $9M |
| [Nacala](east-africa/Mozambique/Nacala/) | MZ | `tram-2car` | 3 | 25 | 39 | 54 | 80% | $488M | $13M | $11M |
| [Beira](east-africa/Mozambique/Beira/) | MZ | `light-metro-3car` | 3 | 39 | 54 | 54 | 37% | $674M | $13M | $17M |
| [Barisal](south-asia/Bangladesh/Barisal/) | BD | `light-metro-3car` | 3 | 30 | 59 | 60 | 50% | $737M | $13M | $12M |
| [Mansoura Eg](west-asia/Egypt/Mansoura-Eg/) | EG | `light-metro-3car` | 3 | 34 | 56 | 56 | 54% | $704M | $13M | $15M |
| [Luxor](west-asia/Egypt/Luxor/) | EG | `light-metro-3car` | 3 | 34 | 54 | 54 | 73% | $678M | $13M | $15M |
| [Sidon](west-asia/Lebanon/Sidon/) | LB | `tram-2car` | 3 | 23 | 37 | 52 | 71% | $469M | $13M | $11M |
| [Masaka](east-africa/Uganda/Masaka/) | UG | `tram-2car` | 3 | 20 | 32 | 46 | 56% | $404M | $13M | $9M |
| [Malindi](east-africa/Kenya/Malindi/) | KE | `tram-2car` | 3 | 20 | 29 | 44 | 79% | $371M | $13M | $9M |
| [Goma](central-africa/DR%20Congo/Goma/) | CD | `light-metro-3car` | 3 | 39 | 58 | 58 | 60% | $734M | $13M | $17M |
| [Raqqa](west-asia/Syria/Raqqa/) | SY | `light-metro-3car` | 3 | 25 | 45 | 46 | 86% | $567M | $13M | $11M |
| [Agra](south-asia/India/Agra/) | IN | `metro-4car` | 5 | 98 | 191 | 156 | 39% | $2.42bn | $13M | $45M |
| [Aden](west-asia/Yemen/Aden/) | YE | `light-metro-3car` | 3 | 28 | 44 | 46 | 43% | $561M | $13M | $12M |
| [Hyderabad Pk](south-asia/Pakistan/Hyderabad-Pk/) | PK | `metro-4car` | 6 | 84 | 182 | 152 | 61% | $2.30bn | $13M | $38M |
| [Duhok](west-asia/Iraq/Duhok/) | IQ | `light-metro-3car` | 3 | 32 | 53 | 54 | 53% | $674M | $13M | $15M |
| [Conakry](west-africa/Guinea/Conakry/) | GN | `metro-4car` | 3 | 55 | 93 | 78 | 40% | $1.18bn | $13M | $25M |
| [Mogadishu](east-africa/Somalia/Mogadishu/) | SO | `metro-4car` | 4 | 68 | 128 | 106 | 40% | $1.63bn | $13M | $31M |
| [Maroua](west-africa/Cameroon/Maroua/) | CM | `light-metro-3car` | 3 | 29 | 53 | 54 | 74% | $669M | $13M | $12M |
| [Bandung](southeast-asia/Indonesia/Bandung/) | ID | `metro-4car` | 6 | 126 | 257 | 208 | 41% | $3.28bn | $13M | $57M |
| [Mandalay](southeast-asia/Myanmar/Mandalay/) | MM | `metro-4car` | 6 | 88 | 187 | 156 | 60% | $2.39bn | $13M | $42M |
| [Kisii](east-africa/Kenya/Kisii/) | KE | `tram-2car` | 3 | 17 | 30 | 43 | 67% | $378M | $13M | $8M |
| [Kananga](central-africa/DR%20Congo/Kananga/) | CD | `metro-4car` | 2 | 18 | 38 | 34 | 73% | $490M | $13M | $8M |
| [Jos](west-africa/Nigeria/Jos/) | NG | `light-metro-3car` | 3 | 40 | 54 | 55 | 26% | $692M | $13M | $17M |
| [Mbeya](east-africa/Tanzania/Mbeya/) | TZ | `light-metro-3car` | 3 | 39 | 55 | 55 | 44% | $707M | $13M | $18M |
| [Deir Ez Zor](west-asia/Syria/Deir-Ez-Zor/) | SY | `light-metro-3car` | 3 | 32 | 57 | 57 | 62% | $733M | $13M | $14M |
| [Herat](south-asia/Afghanistan/Herat/) | AF | `light-metro-3car` | 3 | 43 | 65 | 64 | 36% | $838M | $13M | $19M |
| [Varanasi](south-asia/India/Varanasi/) | IN | `metro-4car` | 5 | 100 | 202 | 165 | 47% | $2.62bn | $13M | $43M |
| [Taiz](west-asia/Yemen/Taiz/) | YE | `light-metro-3car` | 3 | 33 | 49 | 51 | 55% | $634M | $13M | $15M |
| [Patna](south-asia/India/Patna/) | IN | `metro-4car` | 5 | 84 | 185 | 152 | 50% | $2.40bn | $13M | $36M |
| [Bhopal](south-asia/India/Bhopal/) | IN | `metro-4car` | 6 | 107 | 206 | 169 | 52% | $2.68bn | $13M | $51M |
| [Khulna](south-asia/Bangladesh/Khulna/) | BD | `metro-4car` | 6 | 82 | 182 | 152 | 57% | $2.37bn | $13M | $37M |
| [Multan](south-asia/Pakistan/Multan/) | PK | `metro-4car` | 4 | 64 | 115 | 98 | 42% | $1.50bn | $13M | $31M |
| [Quelimane](east-africa/Mozambique/Quelimane/) | MZ | `light-metro-3car` | 1 | 6 | 10 | 12 | 48% | $134M | $13M | $3M |
| [Mosul](west-asia/Iraq/Mosul/) | IQ | `metro-4car` | 6 | 78 | 203 | 168 | 62% | $2.65bn | $13M | $32M |
| [Beirut](west-asia/Lebanon/Beirut/) | LB | `metro-4car` | 6 | 83 | 159 | 134 | 70% | $2.09bn | $13M | $40M |
| [Bahawalpur](south-asia/Pakistan/Bahawalpur/) | PK | `light-metro-3car` | 3 | 29 | 46 | 49 | 42% | $605M | $13M | $14M |
| [Fallujah](west-asia/Iraq/Fallujah/) | IQ | `light-metro-3car` | 3 | 28 | 46 | 48 | 57% | $602M | $13M | $13M |
| [Hurghada](west-asia/Egypt/Hurghada/) | EG | `tram-2car` | 3 | 28 | 43 | 57 | 56% | $562M | $13M | $13M |
| [Phnom Penh](southeast-asia/Cambodia/Phnom-Penh/) | KH | `metro-4car` | 6 | 107 | 228 | 186 | 48% | $2.99bn | $13M | $47M |
| [Kisangani](central-africa/DR%20Congo/Kisangani/) | CD | `metro-4car` | 2 | 27 | 47 | 40 | 64% | $621M | $13M | $13M |
| [Tabuk](west-asia/Saudi%20Arabia/Tabuk/) | SA | `light-metro-3car` | 3 | 45 | 63 | 63 | 27% | $827M | $13M | $20M |
| [Vadodara](south-asia/India/Vadodara/) | IN | `metro-4car` | 5 | 89 | 164 | 137 | 48% | $2.15bn | $13M | $43M |
| [Garissa](east-africa/Kenya/Garissa/) | KE | `tram-2car` | 3 | 19 | 29 | 43 | 71% | $379M | $13M | $9M |
| [Meru Ke](east-africa/Kenya/Meru-Ke/) | KE | `tram-2car` | 2 | 12 | 22 | 32 | 52% | $291M | $13M | $5M |
| [Nyala](north-africa/Sudan/Nyala/) | SD | `light-metro-3car` | 3 | 29 | 47 | 48 | 61% | $616M | $13M | $11M |
| [Edea](west-africa/Cameroon/Edea/) | CM | `tram-2car` | 1 | 7 | 10 | 14 | 61% | $127M | $13M | $4M |
| [Kafr El Sheikh](west-asia/Egypt/Kafr-El-Sheikh/) | EG | `tram-2car` | 3 | 22 | 33 | 47 | 75% | $437M | $13M | $11M |
| [Beni Mellal](north-africa/Morocco/Beni-Mellal/) | MA | `tram-2car` | 3 | 18 | 30 | 45 | 85% | $400M | $13M | $9M |
| [Qena](west-asia/Egypt/Qena/) | EG | `light-metro-3car` | 3 | 26 | 45 | 47 | 75% | $598M | $13M | $12M |
| [Tetouan](north-africa/Morocco/Tetouan/) | MA | `light-metro-3car` | 3 | 33 | 54 | 56 | 69% | $718M | $13M | $14M |
| [Fez](north-africa/Morocco/Fez/) | MA | `metro-4car` | 4 | 58 | 113 | 94 | 73% | $1.50bn | $13M | $28M |
| [Soyo](east-africa/Angola/Soyo/) | AO | `tram-2car` | 2 | 14 | 22 | 32 | 70% | $299M | $13M | $7M |
| [Oujda](north-africa/Morocco/Oujda/) | MA | `light-metro-3car` | 3 | 33 | 47 | 48 | 48% | $625M | $13M | $16M |
| [Rajkot](south-asia/India/Rajkot/) | IN | `metro-4car` | 5 | 76 | 143 | 121 | 58% | $1.91bn | $13M | $36M |
| [Kitale](east-africa/Kenya/Kitale/) | KE | `tram-2car` | 3 | 16 | 29 | 43 | 85% | $394M | $13M | $8M |
| [Waw](north-africa/Sudan/Waw/) | SD | `tram-2car` | 2 | 11 | 18 | 27 | 73% | $240M | $13M | $6M |
| [Lobito](east-africa/Angola/Lobito/) | AO | `light-metro-3car` | 3 | 25 | 38 | 41 | 69% | $508M | $13M | $12M |
| [Xai Xai](east-africa/Mozambique/Xai-Xai/) | MZ | `tram-2car` | 2 | 12 | 18 | 27 | 43% | $241M | $13M | $6M |
| [Najran](west-asia/Saudi%20Arabia/Najran/) | SA | `light-metro-3car` | 3 | 33 | 57 | 57 | 46% | $762M | $13M | $13M |
| [Pemba Mz](east-africa/Mozambique/Pemba-Mz/) | MZ | `tram-2car` | 3 | 20 | 30 | 43 | 63% | $407M | $13M | $10M |
| [Machakos](east-africa/Kenya/Machakos/) | KE | `tram-2car` | 3 | 16 | 27 | 40 | 76% | $358M | $13M | $8M |
| [Khartoum](north-africa/Sudan/Khartoum/) | SD | `metro-6car` | 5 | 152 | 363 | 287 | 22% | $4.89bn | $13M | $57M |
| [Safi](north-africa/Morocco/Safi/) | MA | `light-metro-3car` | 3 | 26 | 39 | 43 | 72% | $531M | $14M | $12M |
| [Diwaniyah](west-asia/Iraq/Diwaniyah/) | IQ | `light-metro-3car` | 3 | 36 | 54 | 55 | 43% | $726M | $14M | $16M |
| [Karbala](west-asia/Iraq/Karbala/) | IQ | `metro-4car` | 6 | 89 | 170 | 144 | 67% | $2.30bn | $14M | $44M |
| [La Paz](latin-america/Bolivia/La-Paz/) | BO | `metro-4car` | 6 | 115 | 212 | 174 | 57% | $2.88bn | $14M | $55M |
| [Nairobi](east-africa/Kenya/Nairobi/) | KE | `metro-6car` | 8 | 191 | 476 | 378 | 43% | $6.46bn | $14M | $73M |
| [Ramadi](west-asia/Iraq/Ramadi/) | IQ | `light-metro-3car` | 3 | 35 | 47 | 49 | 39% | $635M | $14M | $17M |
| [Quetta](south-asia/Pakistan/Quetta/) | PK | `metro-4car` | 5 | 78 | 140 | 120 | 54% | $1.90bn | $14M | $39M |
| [Sayun](west-asia/Yemen/Sayun/) | YE | `tram-2car` | 2 | 15 | 22 | 31 | 58% | $293M | $14M | $7M |
| [Tartus](west-asia/Syria/Tartus/) | SY | `tram-2car` | 3 | 23 | 35 | 49 | 73% | $477M | $14M | $11M |
| [Maiduguri](west-africa/Nigeria/Maiduguri/) | NG | `metro-4car` | 5 | 86 | 176 | 145 | 34% | $2.41bn | $14M | $38M |
| [Beni Suef](west-asia/Egypt/Beni-Suef/) | EG | `light-metro-3car` | 3 | 23 | 35 | 38 | 55% | $477M | $14M | $11M |
| [Port Sudan](north-africa/Sudan/Port-Sudan/) | SD | `light-metro-3car` | 3 | 22 | 33 | 38 | 80% | $456M | $14M | $10M |
| [Kathmandu](south-asia/Nepal/Kathmandu/) | NP | `metro-4car` | 6 | 103 | 203 | 167 | 46% | $2.79bn | $14M | $51M |
| [Lucknow](south-asia/India/Lucknow/) | IN | `metro-6car` | 6 | 164 | 375 | 297 | 31% | $5.18bn | $14M | $64M |
| [Port Said](west-asia/Egypt/Port-Said/) | EG | `light-metro-3car` | 3 | 25 | 35 | 39 | 71% | $483M | $14M | $12M |
| [Zarqa](west-asia/Jordan/Zarqa/) | JO | `light-metro-3car` | 3 | 57 | 83 | 80 | 48% | $1.15bn | $14M | $24M |
| [Dar Es Salaam](east-africa/Tanzania/Dar-Es-Salaam/) | TZ | `metro-6car` | 7 | 163 | 393 | 314 | 28% | $5.50bn | $14M | $62M |
| [Kanpur](south-asia/India/Kanpur/) | IN | `metro-6car` | 7 | 150 | 339 | 273 | 44% | $4.75bn | $14M | $61M |
| [Lahij](west-asia/Yemen/Lahij/) | YE | `tram-2car` | 3 | 19 | 29 | 43 | 82% | $407M | $14M | $10M |
| [Uyo](west-africa/Nigeria/Uyo/) | NG | `light-metro-3car` | 3 | 24 | 31 | 36 | 25% | $437M | $14M | $12M |
| [Lubumbashi](central-africa/DR%20Congo/Lubumbashi/) | CD | `metro-4car` | 4 | 75 | 130 | 107 | 34% | $1.82bn | $14M | $39M |
| [Baghdad](west-asia/Iraq/Baghdad/) | IQ | `metro-6car` | 9 | 218 | 509 | 408 | 45% | $7.20bn | $14M | $90M |
| [Colombo](south-asia/Sri%20Lanka/Colombo/) | LK | `metro-6car` | 6 | 126 | 278 | 223 | 42% | $3.95bn | $14M | $51M |
| [Moshi](east-africa/Tanzania/Moshi/) | TZ | `tram-2car` | 3 | 21 | 36 | 51 | 76% | $510M | $14M | $11M |
| [Bertoua](west-africa/Cameroon/Bertoua/) | CM | `light-metro-3car` | 3 | 20 | 29 | 34 | 77% | $413M | $14M | $10M |
| [Bamako](west-africa/Mali/Bamako/) | ML | `metro-4car` | 6 | 118 | 257 | 207 | 31% | $3.70bn | $14M | $47M |
| [Hodeidah](west-asia/Yemen/Hodeidah/) | YE | `light-metro-3car` | 3 | 27 | 36 | 40 | 61% | $522M | $14M | $13M |
| [Luanda](east-africa/Angola/Luanda/) | AO | `metro-6car` | 9 | 170 | 390 | 317 | 64% | $5.62bn | $14M | $71M |
| [Najaf](west-asia/Iraq/Najaf/) | IQ | `metro-4car` | 6 | 91 | 172 | 144 | 60% | $2.49bn | $14M | $46M |
| [Indore](south-asia/India/Indore/) | IN | `metro-6car` | 7 | 146 | 324 | 260 | 48% | $4.68bn | $14M | $62M |
| [Iringa](east-africa/Tanzania/Iringa/) | TZ | `tram-2car` | 3 | 20 | 28 | 42 | 67% | $404M | $15M | $10M |
| [Benin City](west-africa/Nigeria/Benin-City/) | NG | `metro-4car` | 4 | 77 | 132 | 111 | 44% | $1.92bn | $15M | $40M |
| [Kinshasa](central-africa/DR%20Congo/Kinshasa/) | CD | `metro-6car` | 8 | 183 | 385 | 310 | 49% | $5.62bn | $15M | $82M |
| [Lusaka](east-africa/Zambia/Lusaka/) | ZM | `metro-6car` | 6 | 123 | 236 | 192 | 34% | $3.45bn | $15M | $53M |
| [Coimbatore](south-asia/India/Coimbatore/) | IN | `metro-6car` | 5 | 121 | 268 | 214 | 31% | $3.93bn | $15M | $51M |
| [Durban](south-africa/South%20Africa/Durban/) | ZA | `metro-6car` | 9 | 172 | 401 | 325 | 79% | $5.89bn | $15M | $75M |
| [Kut](west-asia/Iraq/Kut/) | IQ | `light-metro-3car` | 3 | 32 | 56 | 55 | 37% | $818M | $15M | $14M |
| [Basra](west-asia/Iraq/Basra/) | IQ | `metro-6car` | 7 | 119 | 289 | 236 | 54% | $4.24bn | $15M | $48M |
| [Ngaoundere](west-africa/Cameroon/Ngaoundere/) | CM | `light-metro-3car` | 3 | 19 | 28 | 34 | 57% | $413M | $15M | $9M |
| [Antananarivo](east-africa/Madagascar/Antananarivo/) | MG | `metro-6car` | 7 | 155 | 339 | 272 | 42% | $4.99bn | $15M | $65M |
| [Karachi](south-asia/Pakistan/Karachi/) | PK | `metro-6car` | 9 | 231 | 472 | 377 | 48% | $6.95bn | $15M | $100M |
| [Kano](west-africa/Nigeria/Kano/) | NG | `metro-6car` | 6 | 154 | 362 | 286 | 37% | $5.33bn | $15M | $57M |
| [Jeddah](west-asia/Saudi%20Arabia/Jeddah/) | SA | `metro-6car` | 8 | 202 | 406 | 326 | 45% | $5.98bn | $15M | $93M |
| [Nasiriyah](west-asia/Iraq/Nasiriyah/) | IQ | `light-metro-3car` | 3 | 33 | 56 | 56 | 40% | $834M | $15M | $15M |
| [Chittagong](south-asia/Bangladesh/Chittagong/) | BD | `metro-6car` | 8 | 161 | 374 | 302 | 64% | $5.54bn | $15M | $71M |
| [Larkana](south-asia/Pakistan/Larkana/) | PK | `light-metro-3car` | 2 | 19 | 38 | 39 | 28% | $561M | $15M | $9M |
| [Dakar](west-africa/Senegal/Dakar/) | SN | `metro-6car` | 5 | 107 | 204 | 167 | 52% | $3.04bn | $15M | $47M |
| [Aba Ng](west-africa/Nigeria/Aba-Ng/) | NG | `light-metro-3car` | 3 | 26 | 34 | 38 | 40% | $507M | $15M | $13M |
| [Amman](west-asia/Jordan/Amman/) | JO | `metro-6car` | 8 | 172 | 354 | 286 | 51% | $5.28bn | $15M | $76M |
| [Mymensingh](south-asia/Bangladesh/Mymensingh/) | BD | `light-metro-3car` | 3 | 37 | 67 | 67 | 41% | $1.02bn | $15M | $13M |
| [Surabaya](southeast-asia/Indonesia/Surabaya/) | ID | `metro-6car` | 7 | 143 | 294 | 240 | 40% | $4.45bn | $15M | $61M |
| [Sumbawanga](east-africa/Tanzania/Sumbawanga/) | TZ | `tram-2car` | 1 | 5 | 7 | 11 | 35% | $99M | $15M | $3M |
| [Garoua](west-africa/Cameroon/Garoua/) | CM | `light-metro-3car` | 3 | 29 | 44 | 46 | 38% | $665M | $15M | $12M |
| [Nyeri](east-africa/Kenya/Nyeri/) | KE | `tram-2car` | 3 | 22 | 37 | 51 | 62% | $562M | $15M | $10M |
| [Tete](east-africa/Mozambique/Tete/) | MZ | `light-metro-3car` | 3 | 23 | 38 | 41 | 77% | $585M | $15M | $9M |
| [Kassala](north-africa/Sudan/Kassala/) | SD | `light-metro-3car` | 3 | 20 | 34 | 39 | 76% | $528M | $15M | $9M |
| [Yangon](southeast-asia/Myanmar/Yangon/) | MM | `metro-6car` | 9 | 214 | 418 | 335 | 56% | $6.42bn | $15M | $102M |
| [Tabora](east-africa/Tanzania/Tabora/) | TZ | `tram-2car` | 2 | 13 | 18 | 26 | 54% | $270M | $15M | $7M |
| [Yaounde](east-africa/Cameroon/Yaounde/) | CM | `metro-6car` | 8 | 136 | 267 | 219 | 43% | $4.11bn | $15M | $63M |
| [Kabul](south-asia/Afghanistan/Kabul/) | AF | `metro-6car` | 7 | 137 | 261 | 215 | 53% | $4.06bn | $16M | $63M |
| [Khouribga](north-africa/Morocco/Khouribga/) | MA | `tram-2car` | 2 | 11 | 15 | 23 | 57% | $228M | $16M | $6M |
| [Sanaa](west-asia/Yemen/Sanaa/) | YE | `metro-6car` | 9 | 126 | 261 | 218 | 78% | $4.10bn | $16M | $61M |
| [Douala](west-africa/Cameroon/Douala/) | CM | `metro-6car` | 5 | 129 | 228 | 184 | 37% | $3.60bn | $16M | $59M |
| [Amarah](west-asia/Iraq/Amarah/) | IQ | `light-metro-3car` | 3 | 32 | 45 | 46 | 43% | $707M | $16M | $15M |
| [Jodhpur](south-asia/India/Jodhpur/) | IN | `metro-4car` | 5 | 82 | 150 | 124 | 44% | $2.38bn | $16M | $37M |
| [Faisalabad](south-asia/Pakistan/Faisalabad/) | PK | `metro-6car` | 5 | 93 | 166 | 137 | 52% | $2.68bn | $16M | $45M |
| [Ibadan](west-africa/Nigeria/Ibadan/) | NG | `metro-6car` | 4 | 90 | 135 | 111 | 24% | $2.25bn | $17M | $44M |
| [Sialkot](south-asia/Pakistan/Sialkot/) | PK | `light-metro-3car` | 3 | 37 | 59 | 59 | 43% | $1.00bn | $17M | $16M |
| [Sukkur](south-asia/Pakistan/Sukkur/) | PK | `light-metro-3car` | 3 | 31 | 51 | 53 | 55% | $891M | $17M | $13M |
| [Sheikhupura](south-asia/Pakistan/Sheikhupura/) | PK | `light-metro-3car` | 2 | 17 | 19 | 22 | 32% | $334M | $17M | $9M |
| [Malanje](east-africa/Angola/Malanje/) | AO | `light-metro-3car` | 2 | 12 | 15 | 19 | 57% | $269M | $18M | $7M |
| [Biratnagar](south-asia/Nepal/Biratnagar/) | NP | `tram-2car` | 3 | 23 | 34 | 48 | 60% | $736M | $21M | $10M |
