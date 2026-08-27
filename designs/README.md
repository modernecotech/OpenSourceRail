# City Design Catalogue

This directory retains the compact machine-readable result set for all 266 cities
defined by `lib/city-batches/world-sample.toml`. These routed designs are retained
because reproducing them can require external OSM and population inputs.

Generated city READMEs contain local values and evidence only. Shared methodology
and limitations live in the
[deployment planning reference](../docs/deployment-planning-reference.md).

Every city retains its design, simulator scenario, map, engineering review layers,
validation summaries, operations asset index, acceptance report, and integrity
manifest in one city directory. Raw solver networks, GeoPackages, compressed event
bundles, and exploded manufacturing CSVs remain reproducible local outputs so the
Git repository stays usable. Mosul and Samawah remain the full acceptance references.

## Validation status

The retained
[`ring-interchange-validation.json`](ring-interchange-validation.json) report checks
all 266 cities: **266 pass and 0 require ring/topology review
or rerouting** under the current validator. A retained failed design is a
recoverable planning input, not a deployment-ready reference; Mosul and Samawah
remain the primary full-payload worked examples.

The stricter
[`station-cluster-validation.json`](station-cluster-validation.json) report records
**266 passing cities, 0 cities requiring review, and
0 station/interchange findings**.
Its hashes bind each finding set to the retained design and validator.
Basra, Mosul, and Samawah pass both catalogue validators.

The historical
[`engineering-batch-summary-aleppo-amman.json`](engineering-batch-summary-aleppo-amman.json)
is explicitly scoped to those two cities and is not catalogue-wide evidence.

| City | Train family | Lines | Stations | Route km | Fleet | High-demand coverage |
|---|---|---:|---:|---:|---:|---:|
| [Bukavu](central-africa/DR Congo/Bukavu/) | `light-metro-3car` | 3 | 23 | 61.4 | 130 | 56% |
| [Goma](central-africa/DR Congo/Goma/) | `light-metro-3car` | 3 | 24 | 59.9 | 125 | 53% |
| [Kananga](central-africa/DR Congo/Kananga/) | `metro-4car` | 2 | 14 | 38.1 | 36 | 73% |
| [Kinshasa](central-africa/DR Congo/Kinshasa/) | `metro-6car` | 9 | 147 | 402.1 | 643 | 57% |
| [Kisangani](central-africa/DR Congo/Kisangani/) | `metro-4car` | 2 | 18 | 47.5 | 50 | 64% |
| [Lubumbashi](central-africa/DR Congo/Lubumbashi/) | `metro-4car` | 5 | 41 | 130.0 | 161 | 51% |
| [Mbuji-Mayi](central-africa/DR Congo/Mbuji-Mayi/) | `metro-4car` | 4 | 42 | 118.8 | 135 | 71% |
| [Benguela](east-africa/Angola/Benguela/) | `light-metro-3car` | 3 | 18 | 50.5 | 110 | 69% |
| [Huambo](east-africa/Angola/Huambo/) | `light-metro-3car` | 3 | 21 | 52.4 | 112 | 71% |
| [Lobito](east-africa/Angola/Lobito/) | `light-metro-3car` | 3 | 15 | 38.1 | 83 | 72% |
| [Luanda](east-africa/Angola/Luanda/) | `metro-6car` | 9 | 127 | 390.4 | 622 | 64% |
| [Lubango](east-africa/Angola/Lubango/) | `light-metro-3car` | 3 | 22 | 53.8 | 119 | 63% |
| [Malanje](east-africa/Angola/Malanje/) | `light-metro-3car` | 2 | 8 | 15.0 | 34 | 57% |
| [Namibe](east-africa/Angola/Namibe/) | `tram-2car` | 3 | 19 | 40.8 | 84 | 64% |
| [Soyo](east-africa/Angola/Soyo/) | `tram-2car` | 3 | 14 | 29.4 | 63 | 81% |
| [Uige](east-africa/Angola/Uige/) | `light-metro-3car` | 1 | 6 | 12.0 | 27 | 47% |
| [Eldoret](east-africa/Kenya/Eldoret/) | `light-metro-3car` | 3 | 20 | 59.0 | 163 | 79% |
| [Garissa](east-africa/Kenya/Garissa/) | `tram-2car` | 3 | 13 | 25.4 | 57 | 70% |
| [Kakamega](east-africa/Kenya/Kakamega/) | `tram-2car` | 3 | 17 | 42.2 | 83 | 77% |
| [Kisii](east-africa/Kenya/Kisii/) | `tram-2car` | 3 | 12 | 24.3 | 52 | 90% |
| [Kisumu](east-africa/Kenya/Kisumu/) | `light-metro-3car` | 3 | 21 | 53.5 | 115 | 69% |
| [Kitale](east-africa/Kenya/Kitale/) | `tram-2car` | 3 | 15 | 39.9 | 84 | 78% |
| [Machakos](east-africa/Kenya/Machakos/) | `tram-2car` | 3 | 14 | 28.9 | 63 | 76% |
| [Malindi](east-africa/Kenya/Malindi/) | `tram-2car` | 3 | 14 | 29.4 | 61 | 79% |
| [Meru-Ke](east-africa/Kenya/Meru-Ke/) | `tram-2car` | 3 | 11 | 28.0 | 61 | 78% |
| [Mombasa](east-africa/Kenya/Mombasa/) | `metro-4car` | 6 | 58 | 156.7 | 190 | 59% |
| [Nairobi](east-africa/Kenya/Nairobi/) | `metro-6car` | 9 | 151 | 505.8 | 790 | 54% |
| [Naivasha](east-africa/Kenya/Naivasha/) | `tram-2car` | 3 | 14 | 39.0 | 79 | 82% |
| [Nakuru](east-africa/Kenya/Nakuru/) | `light-metro-3car` | 3 | 19 | 54.3 | 116 | 47% |
| [Nyeri](east-africa/Kenya/Nyeri/) | `tram-2car` | 3 | 16 | 36.7 | 76 | 62% |
| [Thika](east-africa/Kenya/Thika/) | `light-metro-3car` | 3 | 28 | 75.5 | 161 | 62% |
| [Antananarivo](east-africa/Madagascar/Antananarivo/) | `metro-6car` | 9 | 101 | 324.5 | 504 | 82% |
| [Beira](east-africa/Mozambique/Beira/) | `light-metro-3car` | 3 | 18 | 44.8 | 96 | 34% |
| [Chimoio](east-africa/Mozambique/Chimoio/) | `light-metro-3car` | 2 | 12 | 34.1 | 82 | 56% |
| [Lichinga](east-africa/Mozambique/Lichinga/) | `tram-2car` | 2 | 8 | 14.9 | 34 | 80% |
| [Maputo](east-africa/Mozambique/Maputo/) | `metro-4car` | 6 | 64 | 174.4 | 214 | 69% |
| [Nacala](east-africa/Mozambique/Nacala/) | `tram-2car` | 3 | 17 | 39.0 | 81 | 80% |
| [Nampula](east-africa/Mozambique/Nampula/) | `light-metro-3car` | 3 | 17 | 51.7 | 122 | 66% |
| [Pemba-Mz](east-africa/Mozambique/Pemba-Mz/) | `tram-2car` | 3 | 15 | 32.4 | 69 | 64% |
| [Quelimane](east-africa/Mozambique/Quelimane/) | `light-metro-3car` | 1 | 5 | 10.3 | 23 | 48% |
| [Tete](east-africa/Mozambique/Tete/) | `light-metro-3car` | 3 | 13 | 37.9 | 81 | 77% |
| [Xai-Xai](east-africa/Mozambique/Xai-Xai/) | `tram-2car` | 3 | 11 | 22.2 | 47 | 56% |
| [Huye](east-africa/Rwanda/Huye/) | `tram-2car` | 3 | 17 | 44.6 | 92 | 68% |
| [Kigali](east-africa/Rwanda/Kigali/) | `metro-4car` | 6 | 68 | 183.2 | 227 | 69% |
| [Rubavu](east-africa/Rwanda/Rubavu/) | `tram-2car` | 3 | 19 | 46.1 | 91 | 57% |
| [Mogadishu](east-africa/Somalia/Mogadishu/) | `metro-4car` | 4 | 48 | 120.7 | 149 | 56% |
| [Arusha](east-africa/Tanzania/Arusha/) | `light-metro-3car` | 3 | 21 | 63.9 | 153 | 61% |
| [Dar-Es-Salaam](east-africa/Tanzania/Dar-Es-Salaam/) | `metro-6car` | 9 | 132 | 443.7 | 709 | 57% |
| [Dodoma](east-africa/Tanzania/Dodoma/) | `light-metro-3car` | 3 | 22 | 52.2 | 113 | 58% |
| [Iringa](east-africa/Tanzania/Iringa/) | `tram-2car` | 3 | 14 | 27.1 | 58 | 73% |
| [Kigoma](east-africa/Tanzania/Kigoma/) | `tram-2car` | 3 | 17 | 35.9 | 76 | 77% |
| [Mbeya](east-africa/Tanzania/Mbeya/) | `light-metro-3car` | 3 | 21 | 53.0 | 112 | 63% |
| [Morogoro](east-africa/Tanzania/Morogoro/) | `light-metro-3car` | 3 | 24 | 55.1 | 120 | 61% |
| [Moshi](east-africa/Tanzania/Moshi/) | `tram-2car` | 3 | 14 | 36.1 | 73 | 76% |
| [Mwanza](east-africa/Tanzania/Mwanza/) | `metro-4car` | 6 | 62 | 175.9 | 219 | 76% |
| [Shinyanga](east-africa/Tanzania/Shinyanga/) | `tram-2car` | 3 | 14 | 36.8 | 76 | 83% |
| [Songea](east-africa/Tanzania/Songea/) | `tram-2car` | 2 | 7 | 16.8 | 37 | 80% |
| [Sumbawanga](east-africa/Tanzania/Sumbawanga/) | `tram-2car` | 3 | 10 | 15.7 | 40 | 77% |
| [Tabora](east-africa/Tanzania/Tabora/) | `tram-2car` | 3 | 10 | 21.1 | 49 | 65% |
| [Tanga](east-africa/Tanzania/Tanga/) | `light-metro-3car` | 3 | 20 | 50.1 | 108 | 52% |
| [Zanzibar-City](east-africa/Tanzania/Zanzibar-City/) | `light-metro-3car` | 3 | 22 | 61.9 | 134 | 72% |
| [Arua](east-africa/Uganda/Arua/) | `tram-2car` | 3 | 16 | 37.7 | 77 | 79% |
| [Entebbe](east-africa/Uganda/Entebbe/) | `tram-2car` | 3 | 17 | 38.9 | 78 | 76% |
| [Fort-Portal](east-africa/Uganda/Fort-Portal/) | `tram-2car` | 3 | 15 | 36.3 | 76 | 84% |
| [Gulu](east-africa/Uganda/Gulu/) | `light-metro-3car` | 3 | 18 | 60.1 | 139 | 68% |
| [Hoima](east-africa/Uganda/Hoima/) | `tram-2car` | 3 | 11 | 29.1 | 61 | 81% |
| [Jinja](east-africa/Uganda/Jinja/) | `tram-2car` | 3 | 17 | 42.1 | 87 | 71% |
| [Kampala](east-africa/Uganda/Kampala/) | `metro-4car` | 6 | 70 | 221.6 | 274 | 69% |
| [Lira](east-africa/Uganda/Lira/) | `tram-2car` | 3 | 16 | 45.3 | 92 | 64% |
| [Masaka](east-africa/Uganda/Masaka/) | `tram-2car` | 3 | 16 | 32.1 | 69 | 56% |
| [Mbale](east-africa/Uganda/Mbale/) | `tram-2car` | 3 | 13 | 34.1 | 71 | 85% |
| [Mbarara](east-africa/Uganda/Mbarara/) | `light-metro-3car` | 3 | 22 | 53.0 | 113 | 78% |
| [Soroti](east-africa/Uganda/Soroti/) | `tram-2car` | 2 | 6 | 7.9 | 23 | 69% |
| [Lusaka](east-africa/Zambia/Lusaka/) | `metro-6car` | 8 | 95 | 279.5 | 418 | 58% |
| [Lyon](europe/France/Lyon/) | `metro-4car` | 6 | 85 | 269.8 | 347 | 54% |
| [La-Paz](latin-america/Bolivia/La-Paz/) | `metro-4car` | 6 | 79 | 223.9 | 285 | 61% |
| [Cuenca](latin-america/Ecuador/Cuenca/) | `light-metro-3car` | 3 | 24 | 70.9 | 169 | 64% |
| [San-Salvador](latin-america/El Salvador/San-Salvador/) | `metro-4car` | 6 | 81 | 256.6 | 308 | 61% |
| [Agadir](north-africa/Morocco/Agadir/) | `light-metro-3car` | 3 | 30 | 81.5 | 172 | 61% |
| [Beni-Mellal](north-africa/Morocco/Beni-Mellal/) | `tram-2car` | 3 | 14 | 30.2 | 66 | 85% |
| [Fez](north-africa/Morocco/Fez/) | `metro-4car` | 4 | 45 | 114.4 | 128 | 73% |
| [Kenitra](north-africa/Morocco/Kenitra/) | `light-metro-3car` | 3 | 24 | 60.1 | 130 | 66% |
| [Khouribga](north-africa/Morocco/Khouribga/) | `tram-2car` | 3 | 11 | 18.8 | 46 | 82% |
| [Marrakech](north-africa/Morocco/Marrakech/) | `metro-4car` | 6 | 57 | 194.1 | 255 | 59% |
| [Meknes](north-africa/Morocco/Meknes/) | `light-metro-3car` | 3 | 17 | 39.4 | 89 | 58% |
| [Nador](north-africa/Morocco/Nador/) | `tram-2car` | 3 | 16 | 34.3 | 72 | 70% |
| [Oujda](north-africa/Morocco/Oujda/) | `light-metro-3car` | 3 | 18 | 37.5 | 81 | 43% |
| [Safi](north-africa/Morocco/Safi/) | `light-metro-3car` | 3 | 19 | 39.3 | 86 | 72% |
| [Tangier](north-africa/Morocco/Tangier/) | `metro-4car` | 5 | 52 | 156.6 | 181 | 58% |
| [Tetouan](north-africa/Morocco/Tetouan/) | `light-metro-3car` | 3 | 19 | 54.1 | 115 | 69% |
| [El-Obeid](north-africa/Sudan/El-Obeid/) | `light-metro-3car` | 3 | 19 | 47.2 | 102 | 70% |
| [Kassala](north-africa/Sudan/Kassala/) | `light-metro-3car` | 3 | 11 | 23.5 | 52 | 81% |
| [Khartoum](north-africa/Sudan/Khartoum/) | `metro-6car` | 9 | 137 | 417.0 | 637 | 58% |
| [Nyala](north-africa/Sudan/Nyala/) | `light-metro-3car` | 3 | 20 | 46.7 | 99 | 61% |
| [Omdurman](north-africa/Sudan/Omdurman/) | `metro-4car` | 6 | 85 | 256.1 | 312 | 53% |
| [Port-Sudan](north-africa/Sudan/Port-Sudan/) | `light-metro-3car` | 3 | 15 | 33.9 | 76 | 80% |
| [Waw](north-africa/Sudan/Waw/) | `tram-2car` | 3 | 9 | 18.3 | 41 | 75% |
| [Tunis](north-africa/Tunisia/Tunis/) | `metro-4car` | 5 | 73 | 221.1 | 255 | 60% |
| [Bloemfontein](south-africa/South Africa/Bloemfontein/) | `light-metro-3car` | 3 | 26 | 72.1 | 151 | 35% |
| [Durban](south-africa/South Africa/Durban/) | `metro-6car` | 9 | 139 | 401.0 | 616 | 80% |
| [East-London-Za](south-africa/South Africa/East-London-Za/) | `light-metro-3car` | 3 | 23 | 67.5 | 139 | 42% |
| [Nelspruit](south-africa/South Africa/Nelspruit/) | `tram-2car` | 3 | 16 | 38.7 | 80 | 72% |
| [Polokwane](south-africa/South Africa/Polokwane/) | `light-metro-3car` | 3 | 20 | 51.3 | 110 | 62% |
| [Herat](south-asia/Afghanistan/Herat/) | `light-metro-3car` | 3 | 19 | 49.5 | 108 | 57% |
| [Jalalabad-Af](south-asia/Afghanistan/Jalalabad-Af/) | `light-metro-3car` | 3 | 16 | 47.0 | 112 | 57% |
| [Kabul](south-asia/Afghanistan/Kabul/) | `metro-6car` | 7 | 80 | 228.8 | 350 | 59% |
| [Kandahar](south-asia/Afghanistan/Kandahar/) | `light-metro-3car` | 3 | 21 | 52.9 | 113 | 68% |
| [Mazar-E-Sharif](south-asia/Afghanistan/Mazar-E-Sharif/) | `light-metro-3car` | 3 | 22 | 64.1 | 139 | 82% |
| [Barisal](south-asia/Bangladesh/Barisal/) | `light-metro-3car` | 3 | 23 | 61.2 | 130 | 56% |
| [Chittagong](south-asia/Bangladesh/Chittagong/) | `metro-6car` | 8 | 103 | 323.8 | 517 | 72% |
| [Comilla](south-asia/Bangladesh/Comilla/) | `light-metro-3car` | 3 | 21 | 55.5 | 114 | 68% |
| [Gazipur](south-asia/Bangladesh/Gazipur/) | `metro-4car` | 6 | 89 | 264.5 | 338 | 46% |
| [Khulna](south-asia/Bangladesh/Khulna/) | `metro-4car` | 6 | 68 | 196.4 | 252 | 51% |
| [Mymensingh](south-asia/Bangladesh/Mymensingh/) | `light-metro-3car` | 3 | 17 | 42.3 | 92 | 43% |
| [Narayanganj](south-asia/Bangladesh/Narayanganj/) | `light-metro-3car` | 3 | 28 | 75.3 | 157 | 50% |
| [Rajshahi](south-asia/Bangladesh/Rajshahi/) | `light-metro-3car` | 3 | 18 | 42.4 | 93 | 66% |
| [Rangpur](south-asia/Bangladesh/Rangpur/) | `light-metro-3car` | 3 | 18 | 46.0 | 99 | 49% |
| [Sylhet](south-asia/Bangladesh/Sylhet/) | `light-metro-3car` | 3 | 21 | 49.6 | 109 | 75% |
| [Agra](south-asia/India/Agra/) | `metro-4car` | 5 | 58 | 160.2 | 187 | 58% |
| [Bhopal](south-asia/India/Bhopal/) | `metro-4car` | 6 | 72 | 194.6 | 245 | 59% |
| [Coimbatore](south-asia/India/Coimbatore/) | `metro-6car` | 9 | 111 | 342.0 | 540 | 74% |
| [Indore](south-asia/India/Indore/) | `metro-6car` | 8 | 111 | 369.4 | 571 | 56% |
| [Jodhpur](south-asia/India/Jodhpur/) | `metro-4car` | 5 | 52 | 150.2 | 175 | 53% |
| [Kanpur](south-asia/India/Kanpur/) | `metro-6car` | 8 | 113 | 352.5 | 533 | 59% |
| [Lucknow](south-asia/India/Lucknow/) | `metro-6car` | 8 | 117 | 367.8 | 556 | 51% |
| [Madurai](south-asia/India/Madurai/) | `metro-4car` | 6 | 69 | 224.3 | 268 | 73% |
| [Meerut](south-asia/India/Meerut/) | `metro-4car` | 4 | 47 | 145.4 | 158 | 69% |
| [Patna](south-asia/India/Patna/) | `metro-4car` | 6 | 62 | 171.3 | 215 | 65% |
| [Raipur](south-asia/India/Raipur/) | `metro-4car` | 6 | 53 | 155.7 | 212 | 52% |
| [Rajkot](south-asia/India/Rajkot/) | `metro-4car` | 5 | 47 | 133.9 | 162 | 82% |
| [Ranchi](south-asia/India/Ranchi/) | `metro-4car` | 6 | 77 | 221.5 | 260 | 49% |
| [Vadodara](south-asia/India/Vadodara/) | `metro-4car` | 6 | 61 | 150.2 | 207 | 66% |
| [Varanasi](south-asia/India/Varanasi/) | `metro-4car` | 6 | 64 | 201.4 | 243 | 49% |
| [Vijayawada](south-asia/India/Vijayawada/) | `metro-4car` | 6 | 67 | 228.3 | 266 | 83% |
| [Visakhapatnam](south-asia/India/Visakhapatnam/) | `metro-4car` | 6 | 76 | 236.8 | 286 | 50% |
| [Biratnagar](south-asia/Nepal/Biratnagar/) | `tram-2car` | 3 | 14 | 31.8 | 67 | 75% |
| [Kathmandu](south-asia/Nepal/Kathmandu/) | `metro-4car` | 6 | 68 | 197.3 | 244 | 54% |
| [Pokhara](south-asia/Nepal/Pokhara/) | `light-metro-3car` | 3 | 25 | 81.2 | 172 | 41% |
| [Bahawalpur](south-asia/Pakistan/Bahawalpur/) | `light-metro-3car` | 3 | 18 | 44.8 | 100 | 58% |
| [Faisalabad](south-asia/Pakistan/Faisalabad/) | `metro-6car` | 6 | 60 | 169.7 | 252 | 80% |
| [Gujranwala](south-asia/Pakistan/Gujranwala/) | `metro-4car` | 5 | 55 | 187.2 | 218 | 65% |
| [Hyderabad-Pk](south-asia/Pakistan/Hyderabad-Pk/) | `metro-4car` | 6 | 58 | 180.0 | 216 | 66% |
| [Karachi](south-asia/Pakistan/Karachi/) | `metro-6car` | 9 | 145 | 459.6 | 707 | 64% |
| [Larkana](south-asia/Pakistan/Larkana/) | `light-metro-3car` | 2 | 15 | 37.0 | 79 | 49% |
| [Multan](south-asia/Pakistan/Multan/) | `metro-4car` | 5 | 48 | 118.6 | 149 | 69% |
| [Peshawar](south-asia/Pakistan/Peshawar/) | `metro-4car` | 5 | 63 | 186.7 | 221 | 64% |
| [Quetta](south-asia/Pakistan/Quetta/) | `metro-4car` | 4 | 41 | 120.7 | 127 | 50% |
| [Rahim-Yar-Khan](south-asia/Pakistan/Rahim-Yar-Khan/) | `light-metro-3car` | 3 | 18 | 53.6 | 129 | 76% |
| [Sheikhupura](south-asia/Pakistan/Sheikhupura/) | `light-metro-3car` | 2 | 9 | 16.6 | 37 | 77% |
| [Sialkot](south-asia/Pakistan/Sialkot/) | `light-metro-3car` | 3 | 21 | 55.4 | 134 | 46% |
| [Sukkur](south-asia/Pakistan/Sukkur/) | `light-metro-3car` | 3 | 15 | 43.7 | 92 | 72% |
| [Colombo](south-asia/Sri Lanka/Colombo/) | `metro-6car` | 9 | 106 | 320.9 | 497 | 68% |
| [Galle](south-asia/Sri Lanka/Galle/) | `light-metro-3car` | 3 | 23 | 63.7 | 177 | 54% |
| [Jaffna](south-asia/Sri Lanka/Jaffna/) | `light-metro-3car` | 3 | 21 | 53.4 | 131 | 70% |
| [Kandy](south-asia/Sri Lanka/Kandy/) | `light-metro-3car` | 3 | 23 | 75.4 | 178 | 57% |
| [Phnom-Penh](southeast-asia/Cambodia/Phnom-Penh/) | `metro-4car` | 6 | 80 | 238.4 | 293 | 75% |
| [Bandung](southeast-asia/Indonesia/Bandung/) | `metro-4car` | 6 | 89 | 245.6 | 312 | 60% |
| [Surabaya](southeast-asia/Indonesia/Surabaya/) | `metro-6car` | 9 | 102 | 293.8 | 470 | 74% |
| [Vientiane](southeast-asia/Laos/Vientiane/) | `light-metro-3car` | 3 | 27 | 74.4 | 155 | 50% |
| [Mandalay](southeast-asia/Myanmar/Mandalay/) | `metro-4car` | 6 | 75 | 221.9 | 276 | 67% |
| [Yangon](southeast-asia/Myanmar/Yangon/) | `metro-6car` | 9 | 141 | 418.1 | 661 | 58% |
| [Davao](southeast-asia/Philippines/Davao/) | `metro-4car` | 6 | 99 | 280.2 | 329 | 39% |
| [Ouagadougou](west-africa/Burkina Faso/Ouagadougou/) | `metro-4car` | 6 | 77 | 221.6 | 271 | 60% |
| [Bafoussam](west-africa/Cameroon/Bafoussam/) | `light-metro-3car` | 3 | 27 | 73.5 | 158 | 47% |
| [Bamenda](west-africa/Cameroon/Bamenda/) | `light-metro-3car` | 3 | 22 | 52.5 | 111 | 54% |
| [Bertoua](west-africa/Cameroon/Bertoua/) | `light-metro-3car` | 3 | 12 | 29.4 | 63 | 78% |
| [Douala](west-africa/Cameroon/Douala/) | `metro-6car` | 5 | 78 | 207.5 | 322 | 56% |
| [Edea](west-africa/Cameroon/Edea/) | `tram-2car` | 1 | 5 | 9.6 | 20 | 61% |
| [Garoua](west-africa/Cameroon/Garoua/) | `light-metro-3car` | 3 | 14 | 33.0 | 73 | 66% |
| [Kumba](west-africa/Cameroon/Kumba/) | `light-metro-3car` | 3 | 15 | 42.5 | 90 | 68% |
| [Maroua](west-africa/Cameroon/Maroua/) | `light-metro-3car` | 3 | 21 | 52.5 | 113 | 74% |
| [Ngaoundere](west-africa/Cameroon/Ngaoundere/) | `light-metro-3car` | 3 | 15 | 29.4 | 64 | 85% |
| [Yaounde](west-africa/Cameroon/Yaounde/) | `metro-6car` | 5 | 72 | 220.2 | 312 | 56% |
| [Conakry](west-africa/Guinea/Conakry/) | `metro-4car` | 3 | 26 | 82.0 | 84 | 81% |
| [Bamako](west-africa/Mali/Bamako/) | `metro-4car` | 6 | 69 | 212.5 | 255 | 56% |
| [Niamey](west-africa/Niger/Niamey/) | `metro-4car` | 6 | 54 | 157.6 | 186 | 68% |
| [Aba-Ng](west-africa/Nigeria/Aba-Ng/) | `light-metro-3car` | 3 | 13 | 31.9 | 70 | 68% |
| [Benin-City](west-africa/Nigeria/Benin-City/) | `metro-4car` | 5 | 49 | 122.7 | 171 | 77% |
| [Ibadan](west-africa/Nigeria/Ibadan/) | `metro-6car` | 5 | 55 | 135.3 | 222 | 38% |
| [Ilorin](west-africa/Nigeria/Ilorin/) | `light-metro-3car` | 3 | 26 | 56.8 | 124 | 55% |
| [Jos](west-africa/Nigeria/Jos/) | `light-metro-3car` | 3 | 20 | 45.9 | 102 | 43% |
| [Kano](west-africa/Nigeria/Kano/) | `metro-6car` | 9 | 142 | 434.4 | 686 | 58% |
| [Maiduguri](west-africa/Nigeria/Maiduguri/) | `metro-4car` | 5 | 58 | 168.4 | 197 | 49% |
| [Onitsha](west-africa/Nigeria/Onitsha/) | `metro-4car` | 5 | 63 | 188.6 | 198 | 79% |
| [Port-Harcourt](west-africa/Nigeria/Port-Harcourt/) | `metro-4car` | 5 | 69 | 193.8 | 232 | 48% |
| [Uyo](west-africa/Nigeria/Uyo/) | `light-metro-3car` | 3 | 14 | 34.0 | 76 | 70% |
| [Dakar](west-africa/Senegal/Dakar/) | `metro-6car` | 6 | 82 | 222.2 | 330 | 63% |
| [Arish](west-asia/Egypt/Arish/) | `tram-2car` | 2 | 8 | 17.3 | 38 | 62% |
| [Asyut](west-asia/Egypt/Asyut/) | `light-metro-3car` | 3 | 19 | 51.7 | 162 | 70% |
| [Beni-Suef](west-asia/Egypt/Beni-Suef/) | `light-metro-3car` | 3 | 17 | 40.0 | 87 | 49% |
| [Damanhur](west-asia/Egypt/Damanhur/) | `light-metro-3car` | 3 | 18 | 47.4 | 103 | 86% |
| [Damietta](west-asia/Egypt/Damietta/) | `light-metro-3car` | 3 | 24 | 73.5 | 156 | 72% |
| [Fayoum](west-asia/Egypt/Fayoum/) | `light-metro-3car` | 3 | 23 | 68.8 | 190 | 71% |
| [Hurghada](west-asia/Egypt/Hurghada/) | `tram-2car` | 3 | 17 | 39.0 | 80 | 58% |
| [Ismailia](west-asia/Egypt/Ismailia/) | `light-metro-3car` | 3 | 22 | 47.7 | 119 | 63% |
| [Kafr-El-Sheikh](west-asia/Egypt/Kafr-El-Sheikh/) | `tram-2car` | 3 | 11 | 31.6 | 65 | 81% |
| [Luxor](west-asia/Egypt/Luxor/) | `light-metro-3car` | 3 | 19 | 50.7 | 111 | 73% |
| [Mahalla](west-asia/Egypt/Mahalla/) | `light-metro-3car` | 3 | 16 | 38.3 | 84 | 68% |
| [Mansoura-Eg](west-asia/Egypt/Mansoura-Eg/) | `light-metro-3car` | 3 | 19 | 51.6 | 109 | 71% |
| [Minya](west-asia/Egypt/Minya/) | `light-metro-3car` | 3 | 23 | 53.2 | 114 | 69% |
| [Port-Said](west-asia/Egypt/Port-Said/) | `light-metro-3car` | 3 | 15 | 29.2 | 64 | 66% |
| [Qena](west-asia/Egypt/Qena/) | `light-metro-3car` | 3 | 15 | 49.3 | 117 | 82% |
| [Sohag](west-asia/Egypt/Sohag/) | `light-metro-3car` | 3 | 17 | 44.4 | 98 | 77% |
| [Suez](west-asia/Egypt/Suez/) | `light-metro-3car` | 3 | 23 | 60.6 | 129 | 57% |
| [Tanta](west-asia/Egypt/Tanta/) | `light-metro-3car` | 3 | 25 | 74.9 | 176 | 56% |
| [Zagazig](west-asia/Egypt/Zagazig/) | `light-metro-3car` | 3 | 18 | 42.9 | 92 | 63% |
| [Amarah](west-asia/Iraq/Amarah/) | `light-metro-3car` | 3 | 18 | 46.6 | 101 | 57% |
| [Baghdad](west-asia/Iraq/Baghdad/) | `metro-6car` | 9 | 155 | 501.3 | 784 | 86% |
| [Baqubah](west-asia/Iraq/Baqubah/) | `light-metro-3car` | 3 | 22 | 60.9 | 130 | 60% |
| [Basra](west-asia/Iraq/Basra/) | `metro-6car` | 7 | 92 | 305.4 | 450 | 82% |
| [Diwaniyah](west-asia/Iraq/Diwaniyah/) | `light-metro-3car` | 3 | 19 | 49.8 | 106 | 50% |
| [Duhok](west-asia/Iraq/Duhok/) | `light-metro-3car` | 3 | 22 | 57.3 | 122 | 60% |
| [Erbil](west-asia/Iraq/Erbil/) | `metro-4car` | 5 | 45 | 138.1 | 212 | 62% |
| [Fallujah](west-asia/Iraq/Fallujah/) | `light-metro-3car` | 3 | 21 | 55.8 | 122 | 70% |
| [Hillah](west-asia/Iraq/Hillah/) | `light-metro-3car` | 3 | 24 | 57.9 | 125 | 66% |
| [Karbala](west-asia/Iraq/Karbala/) | `metro-4car` | 6 | 56 | 168.5 | 198 | 60% |
| [Kirkuk](west-asia/Iraq/Kirkuk/) | `metro-4car` | 5 | 52 | 143.9 | 179 | 61% |
| [Kut](west-asia/Iraq/Kut/) | `light-metro-3car` | 3 | 17 | 46.4 | 101 | 60% |
| [Mosul](west-asia/Iraq/Mosul/) | `metro-4car` | 6 | 69 | 207.3 | 256 | 62% |
| [Najaf](west-asia/Iraq/Najaf/) | `metro-4car` | 6 | 59 | 165.1 | 229 | 52% |
| [Nasiriyah](west-asia/Iraq/Nasiriyah/) | `light-metro-3car` | 3 | 20 | 51.1 | 147 | 59% |
| [Ramadi](west-asia/Iraq/Ramadi/) | `light-metro-3car` | 3 | 22 | 48.0 | 104 | 70% |
| [Samawah](west-asia/Iraq/Samawah/) | `light-metro-3car` | 3 | 21 | 50.4 | 108 | 59% |
| [Sulaymaniyah](west-asia/Iraq/Sulaymaniyah/) | `metro-4car` | 4 | 45 | 119.8 | 129 | 67% |
| [Amman](west-asia/Jordan/Amman/) | `metro-6car` | 9 | 120 | 358.4 | 555 | 67% |
| [Aqaba](west-asia/Jordan/Aqaba/) | `tram-2car` | 3 | 16 | 34.6 | 71 | 63% |
| [Irbid](west-asia/Jordan/Irbid/) | `light-metro-3car` | 3 | 21 | 48.7 | 107 | 65% |
| [Zarqa](west-asia/Jordan/Zarqa/) | `light-metro-3car` | 3 | 24 | 72.5 | 227 | 56% |
| [Beirut](west-asia/Lebanon/Beirut/) | `metro-4car` | 6 | 50 | 142.6 | 189 | 60% |
| [Sidon](west-asia/Lebanon/Sidon/) | `tram-2car` | 3 | 16 | 37.8 | 79 | 85% |
| [Tripoli-Lb](west-asia/Lebanon/Tripoli-Lb/) | `light-metro-3car` | 3 | 20 | 45.6 | 99 | 57% |
| [Gaza-City](west-asia/Palestine/Gaza-City/) | `light-metro-3car` | 3 | 15 | 38.8 | 84 | 62% |
| [Hebron](west-asia/Palestine/Hebron/) | `light-metro-3car` | 3 | 22 | 60.3 | 127 | 73% |
| [Nablus](west-asia/Palestine/Nablus/) | `light-metro-3car` | 3 | 24 | 71.7 | 174 | 71% |
| [Abha](west-asia/Saudi Arabia/Abha/) | `light-metro-3car` | 3 | 21 | 59.1 | 126 | 29% |
| [Al-Kharj](west-asia/Saudi Arabia/Al-Kharj/) | `light-metro-3car` | 3 | 27 | 67.7 | 143 | 70% |
| [Buraidah](west-asia/Saudi Arabia/Buraidah/) | `light-metro-3car` | 3 | 27 | 69.2 | 146 | 46% |
| [Dammam](west-asia/Saudi Arabia/Dammam/) | `metro-4car` | 6 | 97 | 272.9 | 325 | 49% |
| [Hail](west-asia/Saudi Arabia/Hail/) | `light-metro-3car` | 3 | 23 | 63.1 | 133 | 47% |
| [Hofuf](west-asia/Saudi Arabia/Hofuf/) | `light-metro-3car` | 3 | 26 | 77.9 | 163 | 49% |
| [Jeddah](west-asia/Saudi Arabia/Jeddah/) | `metro-6car` | 9 | 127 | 375.4 | 592 | 69% |
| [Jizan](west-asia/Saudi Arabia/Jizan/) | `light-metro-3car` | 3 | 17 | 47.9 | 102 | 68% |
| [Khamis-Mushait](west-asia/Saudi Arabia/Khamis-Mushait/) | `light-metro-3car` | 3 | 26 | 81.2 | 217 | 45% |
| [Mecca](west-asia/Saudi Arabia/Mecca/) | `metro-4car` | 6 | 77 | 223.1 | 271 | 46% |
| [Medina](west-asia/Saudi Arabia/Medina/) | `metro-4car` | 6 | 57 | 179.8 | 212 | 51% |
| [Najran](west-asia/Saudi Arabia/Najran/) | `light-metro-3car` | 3 | 20 | 56.7 | 120 | 46% |
| [Tabuk](west-asia/Saudi Arabia/Tabuk/) | `light-metro-3car` | 3 | 26 | 63.0 | 134 | 46% |
| [Taif](west-asia/Saudi Arabia/Taif/) | `light-metro-3car` | 3 | 22 | 59.5 | 125 | 69% |
| [Aleppo](west-asia/Syria/Aleppo/) | `metro-4car` | 6 | 62 | 183.9 | 219 | 61% |
| [Damascus](west-asia/Syria/Damascus/) | `metro-4car` | 6 | 64 | 197.9 | 236 | 77% |
| [Deir-Ez-Zor](west-asia/Syria/Deir-Ez-Zor/) | `light-metro-3car` | 3 | 18 | 51.4 | 143 | 65% |
| [Hama](west-asia/Syria/Hama/) | `light-metro-3car` | 3 | 21 | 51.4 | 114 | 64% |
| [Homs](west-asia/Syria/Homs/) | `light-metro-3car` | 3 | 18 | 40.0 | 87 | 48% |
| [Idlib](west-asia/Syria/Idlib/) | `tram-2car` | 3 | 13 | 32.0 | 67 | 75% |
| [Latakia](west-asia/Syria/Latakia/) | `light-metro-3car` | 3 | 17 | 42.8 | 93 | 57% |
| [Raqqa](west-asia/Syria/Raqqa/) | `light-metro-3car` | 3 | 18 | 48.7 | 105 | 86% |
| [Tartus](west-asia/Syria/Tartus/) | `tram-2car` | 3 | 13 | 27.8 | 60 | 83% |
| [Aden](west-asia/Yemen/Aden/) | `light-metro-3car` | 3 | 17 | 45.8 | 97 | 72% |
| [Dhamar](west-asia/Yemen/Dhamar/) | `tram-2car` | 3 | 13 | 29.1 | 63 | 72% |
| [Hodeidah](west-asia/Yemen/Hodeidah/) | `light-metro-3car` | 3 | 15 | 30.7 | 71 | 66% |
| [Ibb](west-asia/Yemen/Ibb/) | `light-metro-3car` | 3 | 18 | 49.9 | 106 | 74% |
| [Lahij](west-asia/Yemen/Lahij/) | `tram-2car` | 3 | 14 | 28.9 | 59 | 82% |
| [Mukalla](west-asia/Yemen/Mukalla/) | `light-metro-3car` | 3 | 22 | 61.6 | 152 | 63% |
| [Sanaa](west-asia/Yemen/Sanaa/) | `metro-6car` | 7 | 75 | 233.1 | 358 | 73% |
| [Sayun](west-asia/Yemen/Sayun/) | `tram-2car` | 3 | 11 | 24.4 | 54 | 79% |
| [Taiz](west-asia/Yemen/Taiz/) | `light-metro-3car` | 3 | 18 | 42.8 | 94 | 65% |

```bash
scripts/regenerate-city.sh samawah
```

The command refreshes the full package in the canonical `designs/` tree.
