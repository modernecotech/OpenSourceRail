# City Design Catalogue

This directory retains the compact machine-readable result set for all 266 cities
defined by `lib/city-batches/world-sample.toml`. These routed designs are retained
because reproducing them can require external OSM and population inputs.

Every city retains its design, simulator scenario, map, engineering review layers,
validation summaries, operations asset index, acceptance report, and integrity
manifest in one city directory. Raw solver networks, GeoPackages, compressed event
bundles, and exploded manufacturing CSVs remain reproducible local outputs so the
Git repository stays usable. Mosul and Samawah remain the full acceptance references.

## Recovery and validation status

The catalogue was recovered from the last complete tracked routed snapshots after
the cleanup commit removed them. Simulator scenarios have been regenerated with the
current generator and current rolling-stock architecture. The retained
[`ring-interchange-validation.json`](ring-interchange-validation.json) report checks
all 266 cities: **266 pass and 0 require ring/topology review
or rerouting** under the current validator. A retained failed design is a
recoverable planning input, not a deployment-ready reference; Mosul and Samawah
remain the primary full-payload worked examples.

The stricter
[`station-cluster-validation.json`](station-cluster-validation.json) report records
**266 passing cities and 0 cities with
0 inherited station/interchange
findings**. Its hashes bind each finding set to the retained design and validator.
Basra, Mosul, and Samawah pass both catalogue validators.

The historical
[`engineering-batch-summary-aleppo-amman.json`](engineering-batch-summary-aleppo-amman.json)
is explicitly scoped to those two cities and is not catalogue-wide evidence.

| City | Train family | Lines | Stations | Route km | Fleet | High-demand coverage |
|---|---|---:|---:|---:|---:|---:|
| [Bukavu](central-africa/DR Congo/Bukavu/) | `light-metro-3car` | 3 | 37 | 61.4 | 157 | 56% |
| [Goma](central-africa/DR Congo/Goma/) | `light-metro-3car` | 3 | 39 | 59.9 | 152 | 53% |
| [Kananga](central-africa/DR Congo/Kananga/) | `metro-4car` | 2 | 25 | 38.1 | 52 | 73% |
| [Kinshasa](central-africa/DR Congo/Kinshasa/) | `metro-6car` | 9 | 268 | 402.1 | 862 | 57% |
| [Kisangani](central-africa/DR Congo/Kisangani/) | `metro-4car` | 2 | 32 | 47.5 | 71 | 64% |
| [Lubumbashi](central-africa/DR Congo/Lubumbashi/) | `metro-4car` | 5 | 76 | 130.0 | 217 | 51% |
| [Mbuji-Mayi](central-africa/DR Congo/Mbuji-Mayi/) | `metro-4car` | 4 | 72 | 118.8 | 187 | 71% |
| [Benguela](east-africa/Angola/Benguela/) | `light-metro-3car` | 3 | 30 | 50.5 | 131 | 69% |
| [Huambo](east-africa/Angola/Huambo/) | `light-metro-3car` | 3 | 32 | 52.4 | 132 | 71% |
| [Lobito](east-africa/Angola/Lobito/) | `light-metro-3car` | 3 | 26 | 38.1 | 97 | 72% |
| [Luanda](east-africa/Angola/Luanda/) | `metro-6car` | 9 | 229 | 390.4 | 824 | 64% |
| [Lubango](east-africa/Angola/Lubango/) | `light-metro-3car` | 3 | 31 | 53.8 | 134 | 63% |
| [Malanje](east-africa/Angola/Malanje/) | `light-metro-3car` | 2 | 11 | 15.0 | 43 | 57% |
| [Namibe](east-africa/Angola/Namibe/) | `tram-2car` | 3 | 26 | 40.8 | 122 | 64% |
| [Soyo](east-africa/Angola/Soyo/) | `tram-2car` | 3 | 20 | 29.4 | 91 | 81% |
| [Uige](east-africa/Angola/Uige/) | `light-metro-3car` | 1 | 7 | 12.0 | 31 | 47% |
| [Eldoret](east-africa/Kenya/Eldoret/) | `light-metro-3car` | 3 | 32 | 59.0 | 154 | 79% |
| [Garissa](east-africa/Kenya/Garissa/) | `tram-2car` | 3 | 17 | 25.4 | 80 | 70% |
| [Kakamega](east-africa/Kenya/Kakamega/) | `tram-2car` | 3 | 26 | 42.2 | 125 | 77% |
| [Kisii](east-africa/Kenya/Kisii/) | `tram-2car` | 3 | 17 | 24.3 | 77 | 90% |
| [Kisumu](east-africa/Kenya/Kisumu/) | `light-metro-3car` | 3 | 34 | 53.5 | 136 | 69% |
| [Kitale](east-africa/Kenya/Kitale/) | `tram-2car` | 3 | 21 | 39.9 | 117 | 78% |
| [Machakos](east-africa/Kenya/Machakos/) | `tram-2car` | 3 | 19 | 28.9 | 89 | 76% |
| [Malindi](east-africa/Kenya/Malindi/) | `tram-2car` | 3 | 20 | 29.4 | 91 | 79% |
| [Meru-Ke](east-africa/Kenya/Meru-Ke/) | `tram-2car` | 3 | 19 | 28.0 | 86 | 78% |
| [Mombasa](east-africa/Kenya/Mombasa/) | `metro-4car` | 6 | 96 | 156.7 | 258 | 59% |
| [Nairobi](east-africa/Kenya/Nairobi/) | `metro-6car` | 9 | 265 | 505.8 | 1006 | 54% |
| [Naivasha](east-africa/Kenya/Naivasha/) | `tram-2car` | 3 | 22 | 39.0 | 113 | 82% |
| [Nakuru](east-africa/Kenya/Nakuru/) | `light-metro-3car` | 3 | 31 | 54.3 | 141 | 47% |
| [Nyeri](east-africa/Kenya/Nyeri/) | `tram-2car` | 3 | 23 | 36.7 | 109 | 62% |
| [Thika](east-africa/Kenya/Thika/) | `light-metro-3car` | 3 | 41 | 75.5 | 189 | 62% |
| [Antananarivo](east-africa/Madagascar/Antananarivo/) | `metro-6car` | 9 | 178 | 324.5 | 665 | 82% |
| [Beira](east-africa/Mozambique/Beira/) | `light-metro-3car` | 3 | 28 | 44.8 | 113 | 34% |
| [Chimoio](east-africa/Mozambique/Chimoio/) | `light-metro-3car` | 2 | 20 | 34.1 | 88 | 56% |
| [Lichinga](east-africa/Mozambique/Lichinga/) | `tram-2car` | 2 | 12 | 14.9 | 49 | 80% |
| [Maputo](east-africa/Mozambique/Maputo/) | `metro-4car` | 6 | 110 | 174.4 | 300 | 69% |
| [Nacala](east-africa/Mozambique/Nacala/) | `tram-2car` | 3 | 25 | 39.0 | 116 | 80% |
| [Nampula](east-africa/Mozambique/Nampula/) | `light-metro-3car` | 3 | 30 | 51.7 | 133 | 66% |
| [Pemba-Mz](east-africa/Mozambique/Pemba-Mz/) | `tram-2car` | 3 | 20 | 32.4 | 97 | 64% |
| [Quelimane](east-africa/Mozambique/Quelimane/) | `light-metro-3car` | 1 | 7 | 10.3 | 26 | 48% |
| [Tete](east-africa/Mozambique/Tete/) | `light-metro-3car` | 3 | 23 | 37.9 | 101 | 77% |
| [Xai-Xai](east-africa/Mozambique/Xai-Xai/) | `tram-2car` | 3 | 16 | 22.2 | 73 | 56% |
| [Huye](east-africa/Rwanda/Huye/) | `tram-2car` | 3 | 24 | 44.6 | 130 | 68% |
| [Kigali](east-africa/Rwanda/Kigali/) | `metro-4car` | 6 | 120 | 183.2 | 315 | 69% |
| [Rubavu](east-africa/Rwanda/Rubavu/) | `tram-2car` | 3 | 31 | 46.1 | 135 | 57% |
| [Mogadishu](east-africa/Somalia/Mogadishu/) | `metro-4car` | 4 | 76 | 120.7 | 201 | 56% |
| [Arusha](east-africa/Tanzania/Arusha/) | `light-metro-3car` | 3 | 39 | 63.9 | 159 | 61% |
| [Dar-Es-Salaam](east-africa/Tanzania/Dar-Es-Salaam/) | `metro-6car` | 9 | 234 | 443.7 | 901 | 57% |
| [Dodoma](east-africa/Tanzania/Dodoma/) | `light-metro-3car` | 3 | 33 | 52.2 | 133 | 58% |
| [Iringa](east-africa/Tanzania/Iringa/) | `tram-2car` | 3 | 20 | 27.1 | 85 | 73% |
| [Kigoma](east-africa/Tanzania/Kigoma/) | `tram-2car` | 3 | 23 | 35.9 | 108 | 77% |
| [Mbeya](east-africa/Tanzania/Mbeya/) | `light-metro-3car` | 3 | 34 | 53.0 | 133 | 63% |
| [Morogoro](east-africa/Tanzania/Morogoro/) | `light-metro-3car` | 3 | 33 | 55.1 | 137 | 61% |
| [Moshi](east-africa/Tanzania/Moshi/) | `tram-2car` | 3 | 24 | 36.1 | 110 | 76% |
| [Mwanza](east-africa/Tanzania/Mwanza/) | `metro-4car` | 6 | 113 | 175.9 | 305 | 76% |
| [Shinyanga](east-africa/Tanzania/Shinyanga/) | `tram-2car` | 3 | 21 | 36.8 | 111 | 83% |
| [Songea](east-africa/Tanzania/Songea/) | `tram-2car` | 2 | 12 | 16.8 | 52 | 80% |
| [Sumbawanga](east-africa/Tanzania/Sumbawanga/) | `tram-2car` | 3 | 13 | 15.7 | 56 | 77% |
| [Tabora](east-africa/Tanzania/Tabora/) | `tram-2car` | 3 | 16 | 21.1 | 69 | 65% |
| [Tanga](east-africa/Tanzania/Tanga/) | `light-metro-3car` | 3 | 31 | 50.1 | 127 | 52% |
| [Zanzibar-City](east-africa/Tanzania/Zanzibar-City/) | `light-metro-3car` | 3 | 37 | 61.9 | 155 | 72% |
| [Arua](east-africa/Uganda/Arua/) | `tram-2car` | 3 | 24 | 37.7 | 113 | 79% |
| [Entebbe](east-africa/Uganda/Entebbe/) | `tram-2car` | 3 | 27 | 38.9 | 119 | 76% |
| [Fort-Portal](east-africa/Uganda/Fort-Portal/) | `tram-2car` | 3 | 24 | 36.3 | 108 | 84% |
| [Gulu](east-africa/Uganda/Gulu/) | `light-metro-3car` | 3 | 33 | 60.1 | 158 | 68% |
| [Hoima](east-africa/Uganda/Hoima/) | `tram-2car` | 3 | 17 | 29.1 | 90 | 81% |
| [Jinja](east-africa/Uganda/Jinja/) | `tram-2car` | 3 | 27 | 42.1 | 126 | 71% |
| [Kampala](east-africa/Uganda/Kampala/) | `metro-4car` | 6 | 127 | 221.6 | 372 | 69% |
| [Lira](east-africa/Uganda/Lira/) | `tram-2car` | 3 | 26 | 45.3 | 128 | 64% |
| [Masaka](east-africa/Uganda/Masaka/) | `tram-2car` | 3 | 22 | 32.1 | 97 | 56% |
| [Mbale](east-africa/Uganda/Mbale/) | `tram-2car` | 3 | 22 | 34.1 | 102 | 85% |
| [Mbarara](east-africa/Uganda/Mbarara/) | `light-metro-3car` | 3 | 29 | 53.0 | 134 | 78% |
| [Soroti](east-africa/Uganda/Soroti/) | `tram-2car` | 2 | 8 | 7.9 | 31 | 69% |
| [Lusaka](east-africa/Zambia/Lusaka/) | `metro-6car` | 8 | 167 | 279.5 | 570 | 58% |
| [Lyon](europe/France/Lyon/) | `metro-4car` | 6 | 150 | 269.8 | 453 | 54% |
| [La-Paz](latin-america/Bolivia/La-Paz/) | `metro-4car` | 6 | 139 | 223.9 | 389 | 61% |
| [Cuenca](latin-america/Ecuador/Cuenca/) | `light-metro-3car` | 3 | 38 | 70.9 | 180 | 64% |
| [San-Salvador](latin-america/El Salvador/San-Salvador/) | `metro-4car` | 6 | 157 | 256.6 | 434 | 61% |
| [Agadir](north-africa/Morocco/Agadir/) | `light-metro-3car` | 3 | 49 | 81.5 | 199 | 61% |
| [Beni-Mellal](north-africa/Morocco/Beni-Mellal/) | `tram-2car` | 3 | 18 | 30.2 | 93 | 85% |
| [Fez](north-africa/Morocco/Fez/) | `metro-4car` | 4 | 76 | 114.4 | 177 | 73% |
| [Kenitra](north-africa/Morocco/Kenitra/) | `light-metro-3car` | 3 | 35 | 60.1 | 154 | 66% |
| [Khouribga](north-africa/Morocco/Khouribga/) | `tram-2car` | 3 | 14 | 18.8 | 63 | 82% |
| [Marrakech](north-africa/Morocco/Marrakech/) | `metro-4car` | 6 | 104 | 194.1 | 334 | 59% |
| [Meknes](north-africa/Morocco/Meknes/) | `light-metro-3car` | 3 | 26 | 39.4 | 101 | 58% |
| [Nador](north-africa/Morocco/Nador/) | `tram-2car` | 3 | 21 | 34.3 | 102 | 70% |
| [Oujda](north-africa/Morocco/Oujda/) | `light-metro-3car` | 3 | 26 | 37.5 | 91 | 43% |
| [Safi](north-africa/Morocco/Safi/) | `light-metro-3car` | 3 | 27 | 39.3 | 99 | 72% |
| [Tangier](north-africa/Morocco/Tangier/) | `metro-4car` | 5 | 93 | 156.6 | 247 | 58% |
| [Tetouan](north-africa/Morocco/Tetouan/) | `light-metro-3car` | 3 | 32 | 54.1 | 135 | 69% |
| [El-Obeid](north-africa/Sudan/El-Obeid/) | `light-metro-3car` | 3 | 28 | 47.2 | 120 | 70% |
| [Kassala](north-africa/Sudan/Kassala/) | `light-metro-3car` | 3 | 18 | 23.5 | 63 | 81% |
| [Khartoum](north-africa/Sudan/Khartoum/) | `metro-6car` | 9 | 240 | 417.0 | 852 | 58% |
| [Nyala](north-africa/Sudan/Nyala/) | `light-metro-3car` | 3 | 29 | 46.7 | 120 | 61% |
| [Omdurman](north-africa/Sudan/Omdurman/) | `metro-4car` | 6 | 153 | 256.1 | 424 | 53% |
| [Port-Sudan](north-africa/Sudan/Port-Sudan/) | `light-metro-3car` | 3 | 22 | 33.9 | 92 | 80% |
| [Waw](north-africa/Sudan/Waw/) | `tram-2car` | 3 | 14 | 18.3 | 62 | 75% |
| [Tunis](north-africa/Tunisia/Tunis/) | `metro-4car` | 5 | 136 | 221.1 | 359 | 60% |
| [Bloemfontein](south-africa/South Africa/Bloemfontein/) | `light-metro-3car` | 3 | 42 | 72.1 | 177 | 35% |
| [Durban](south-africa/South Africa/Durban/) | `metro-6car` | 9 | 246 | 401.0 | 837 | 80% |
| [East-London-Za](south-africa/South Africa/East-London-Za/) | `light-metro-3car` | 3 | 39 | 67.5 | 172 | 42% |
| [Nelspruit](south-africa/South Africa/Nelspruit/) | `tram-2car` | 3 | 25 | 38.7 | 115 | 72% |
| [Polokwane](south-africa/South Africa/Polokwane/) | `light-metro-3car` | 3 | 31 | 51.3 | 132 | 62% |
| [Herat](south-asia/Afghanistan/Herat/) | `light-metro-3car` | 3 | 30 | 49.5 | 126 | 57% |
| [Jalalabad-Af](south-asia/Afghanistan/Jalalabad-Af/) | `light-metro-3car` | 3 | 26 | 47.0 | 120 | 57% |
| [Kabul](south-asia/Afghanistan/Kabul/) | `metro-6car` | 7 | 144 | 228.8 | 474 | 59% |
| [Kandahar](south-asia/Afghanistan/Kandahar/) | `light-metro-3car` | 3 | 33 | 52.9 | 136 | 68% |
| [Mazar-E-Sharif](south-asia/Afghanistan/Mazar-E-Sharif/) | `light-metro-3car` | 3 | 34 | 64.1 | 164 | 82% |
| [Barisal](south-asia/Bangladesh/Barisal/) | `light-metro-3car` | 3 | 33 | 61.2 | 156 | 56% |
| [Chittagong](south-asia/Bangladesh/Chittagong/) | `metro-6car` | 8 | 182 | 323.8 | 660 | 72% |
| [Comilla](south-asia/Bangladesh/Comilla/) | `light-metro-3car` | 3 | 35 | 55.5 | 142 | 68% |
| [Gazipur](south-asia/Bangladesh/Gazipur/) | `metro-4car` | 6 | 149 | 264.5 | 462 | 46% |
| [Khulna](south-asia/Bangladesh/Khulna/) | `metro-4car` | 6 | 120 | 196.4 | 338 | 51% |
| [Mymensingh](south-asia/Bangladesh/Mymensingh/) | `light-metro-3car` | 3 | 25 | 42.3 | 109 | 43% |
| [Narayanganj](south-asia/Bangladesh/Narayanganj/) | `light-metro-3car` | 3 | 45 | 75.3 | 187 | 50% |
| [Rajshahi](south-asia/Bangladesh/Rajshahi/) | `light-metro-3car` | 3 | 26 | 42.4 | 110 | 66% |
| [Rangpur](south-asia/Bangladesh/Rangpur/) | `light-metro-3car` | 3 | 26 | 46.0 | 122 | 49% |
| [Sylhet](south-asia/Bangladesh/Sylhet/) | `light-metro-3car` | 3 | 30 | 49.6 | 125 | 75% |
| [Agra](south-asia/India/Agra/) | `metro-4car` | 5 | 98 | 160.2 | 259 | 58% |
| [Bhopal](south-asia/India/Bhopal/) | `metro-4car` | 6 | 123 | 194.6 | 336 | 59% |
| [Coimbatore](south-asia/India/Coimbatore/) | `metro-6car` | 9 | 187 | 342.0 | 698 | 74% |
| [Indore](south-asia/India/Indore/) | `metro-6car` | 8 | 198 | 369.4 | 718 | 56% |
| [Jodhpur](south-asia/India/Jodhpur/) | `metro-4car` | 5 | 94 | 150.2 | 250 | 53% |
| [Kanpur](south-asia/India/Kanpur/) | `metro-6car` | 8 | 203 | 352.5 | 694 | 59% |
| [Lucknow](south-asia/India/Lucknow/) | `metro-6car` | 8 | 205 | 367.8 | 724 | 51% |
| [Madurai](south-asia/India/Madurai/) | `metro-4car` | 6 | 121 | 224.3 | 359 | 73% |
| [Meerut](south-asia/India/Meerut/) | `metro-4car` | 4 | 86 | 145.4 | 224 | 69% |
| [Patna](south-asia/India/Patna/) | `metro-4car` | 6 | 106 | 171.3 | 291 | 65% |
| [Raipur](south-asia/India/Raipur/) | `metro-4car` | 6 | 85 | 155.7 | 288 | 52% |
| [Rajkot](south-asia/India/Rajkot/) | `metro-4car` | 5 | 79 | 133.9 | 210 | 82% |
| [Ranchi](south-asia/India/Ranchi/) | `metro-4car` | 6 | 128 | 221.5 | 360 | 49% |
| [Vadodara](south-asia/India/Vadodara/) | `metro-4car` | 6 | 108 | 150.2 | 279 | 66% |
| [Varanasi](south-asia/India/Varanasi/) | `metro-4car` | 6 | 110 | 201.4 | 326 | 49% |
| [Vijayawada](south-asia/India/Vijayawada/) | `metro-4car` | 6 | 119 | 228.3 | 361 | 83% |
| [Visakhapatnam](south-asia/India/Visakhapatnam/) | `metro-4car` | 6 | 139 | 236.8 | 399 | 50% |
| [Biratnagar](south-asia/Nepal/Biratnagar/) | `tram-2car` | 3 | 21 | 31.8 | 96 | 75% |
| [Kathmandu](south-asia/Nepal/Kathmandu/) | `metro-4car` | 6 | 130 | 197.3 | 347 | 54% |
| [Pokhara](south-asia/Nepal/Pokhara/) | `light-metro-3car` | 3 | 46 | 81.2 | 203 | 41% |
| [Bahawalpur](south-asia/Pakistan/Bahawalpur/) | `light-metro-3car` | 3 | 27 | 44.8 | 120 | 58% |
| [Faisalabad](south-asia/Pakistan/Faisalabad/) | `metro-6car` | 6 | 117 | 169.7 | 361 | 80% |
| [Gujranwala](south-asia/Pakistan/Gujranwala/) | `metro-4car` | 5 | 104 | 187.2 | 298 | 65% |
| [Hyderabad-Pk](south-asia/Pakistan/Hyderabad-Pk/) | `metro-4car` | 6 | 111 | 180.0 | 304 | 66% |
| [Karachi](south-asia/Pakistan/Karachi/) | `metro-6car` | 9 | 255 | 459.6 | 925 | 64% |
| [Larkana](south-asia/Pakistan/Larkana/) | `light-metro-3car` | 2 | 20 | 37.0 | 96 | 49% |
| [Multan](south-asia/Pakistan/Multan/) | `metro-4car` | 5 | 83 | 118.6 | 209 | 69% |
| [Peshawar](south-asia/Pakistan/Peshawar/) | `metro-4car` | 5 | 105 | 186.7 | 297 | 64% |
| [Quetta](south-asia/Pakistan/Quetta/) | `metro-4car` | 4 | 80 | 120.7 | 185 | 50% |
| [Rahim-Yar-Khan](south-asia/Pakistan/Rahim-Yar-Khan/) | `light-metro-3car` | 3 | 29 | 53.6 | 140 | 76% |
| [Sheikhupura](south-asia/Pakistan/Sheikhupura/) | `light-metro-3car` | 2 | 12 | 16.6 | 44 | 77% |
| [Sialkot](south-asia/Pakistan/Sialkot/) | `light-metro-3car` | 3 | 34 | 55.4 | 144 | 46% |
| [Sukkur](south-asia/Pakistan/Sukkur/) | `light-metro-3car` | 3 | 29 | 43.7 | 115 | 72% |
| [Colombo](south-asia/Sri Lanka/Colombo/) | `metro-6car` | 9 | 199 | 320.9 | 677 | 68% |
| [Galle](south-asia/Sri Lanka/Galle/) | `light-metro-3car` | 3 | 36 | 63.7 | 163 | 54% |
| [Jaffna](south-asia/Sri Lanka/Jaffna/) | `light-metro-3car` | 3 | 30 | 53.4 | 143 | 70% |
| [Kandy](south-asia/Sri Lanka/Kandy/) | `light-metro-3car` | 3 | 41 | 75.4 | 190 | 57% |
| [Phnom-Penh](southeast-asia/Cambodia/Phnom-Penh/) | `metro-4car` | 6 | 137 | 238.4 | 396 | 75% |
| [Bandung](southeast-asia/Indonesia/Bandung/) | `metro-4car` | 6 | 147 | 245.6 | 417 | 60% |
| [Surabaya](southeast-asia/Indonesia/Surabaya/) | `metro-6car` | 9 | 178 | 293.8 | 629 | 74% |
| [Vientiane](southeast-asia/Laos/Vientiane/) | `light-metro-3car` | 3 | 44 | 74.4 | 188 | 50% |
| [Mandalay](southeast-asia/Myanmar/Mandalay/) | `metro-4car` | 6 | 121 | 221.9 | 368 | 67% |
| [Yangon](southeast-asia/Myanmar/Yangon/) | `metro-6car` | 9 | 240 | 418.1 | 871 | 58% |
| [Davao](southeast-asia/Philippines/Davao/) | `metro-4car` | 6 | 161 | 280.2 | 464 | 39% |
| [Ouagadougou](west-africa/Burkina Faso/Ouagadougou/) | `metro-4car` | 6 | 133 | 221.6 | 378 | 60% |
| [Bafoussam](west-africa/Cameroon/Bafoussam/) | `light-metro-3car` | 3 | 39 | 73.5 | 189 | 47% |
| [Bamenda](west-africa/Cameroon/Bamenda/) | `light-metro-3car` | 3 | 31 | 52.5 | 136 | 54% |
| [Bertoua](west-africa/Cameroon/Bertoua/) | `light-metro-3car` | 3 | 20 | 29.4 | 77 | 78% |
| [Douala](west-africa/Cameroon/Douala/) | `metro-6car` | 5 | 133 | 207.5 | 423 | 56% |
| [Edea](west-africa/Cameroon/Edea/) | `tram-2car` | 1 | 6 | 9.6 | 29 | 61% |
| [Garoua](west-africa/Cameroon/Garoua/) | `light-metro-3car` | 3 | 22 | 33.0 | 87 | 66% |
| [Kumba](west-africa/Cameroon/Kumba/) | `light-metro-3car` | 3 | 28 | 42.5 | 108 | 68% |
| [Maroua](west-africa/Cameroon/Maroua/) | `light-metro-3car` | 3 | 30 | 52.5 | 138 | 74% |
| [Ngaoundere](west-africa/Cameroon/Ngaoundere/) | `light-metro-3car` | 3 | 21 | 29.4 | 79 | 85% |
| [Yaounde](west-africa/Cameroon/Yaounde/) | `metro-6car` | 5 | 126 | 220.2 | 407 | 56% |
| [Conakry](west-africa/Guinea/Conakry/) | `metro-4car` | 3 | 47 | 82.0 | 124 | 81% |
| [Bamako](west-africa/Mali/Bamako/) | `metro-4car` | 6 | 123 | 212.5 | 354 | 56% |
| [Niamey](west-africa/Niger/Niamey/) | `metro-4car` | 6 | 97 | 157.6 | 269 | 68% |
| [Aba-Ng](west-africa/Nigeria/Aba-Ng/) | `light-metro-3car` | 3 | 20 | 31.9 | 85 | 68% |
| [Benin-City](west-africa/Nigeria/Benin-City/) | `metro-4car` | 5 | 78 | 122.7 | 227 | 77% |
| [Ibadan](west-africa/Nigeria/Ibadan/) | `metro-6car` | 5 | 85 | 135.3 | 286 | 38% |
| [Ilorin](west-africa/Nigeria/Ilorin/) | `light-metro-3car` | 3 | 33 | 56.8 | 144 | 55% |
| [Jos](west-africa/Nigeria/Jos/) | `light-metro-3car` | 3 | 31 | 45.9 | 115 | 43% |
| [Kano](west-africa/Nigeria/Kano/) | `metro-6car` | 9 | 248 | 434.4 | 898 | 58% |
| [Maiduguri](west-africa/Nigeria/Maiduguri/) | `metro-4car` | 5 | 100 | 168.4 | 271 | 49% |
| [Onitsha](west-africa/Nigeria/Onitsha/) | `metro-4car` | 5 | 107 | 188.6 | 273 | 79% |
| [Port-Harcourt](west-africa/Nigeria/Port-Harcourt/) | `metro-4car` | 5 | 119 | 193.8 | 314 | 48% |
| [Uyo](west-africa/Nigeria/Uyo/) | `light-metro-3car` | 3 | 22 | 34.0 | 88 | 70% |
| [Dakar](west-africa/Senegal/Dakar/) | `metro-6car` | 6 | 143 | 222.2 | 450 | 63% |
| [Arish](west-asia/Egypt/Arish/) | `tram-2car` | 2 | 12 | 17.3 | 54 | 62% |
| [Asyut](west-asia/Egypt/Asyut/) | `light-metro-3car` | 3 | 27 | 51.7 | 135 | 70% |
| [Beni-Suef](west-asia/Egypt/Beni-Suef/) | `light-metro-3car` | 3 | 26 | 40.0 | 104 | 49% |
| [Damanhur](west-asia/Egypt/Damanhur/) | `light-metro-3car` | 3 | 29 | 47.4 | 123 | 86% |
| [Damietta](west-asia/Egypt/Damietta/) | `light-metro-3car` | 3 | 41 | 73.5 | 194 | 72% |
| [Fayoum](west-asia/Egypt/Fayoum/) | `light-metro-3car` | 3 | 39 | 68.8 | 174 | 71% |
| [Hurghada](west-asia/Egypt/Hurghada/) | `tram-2car` | 3 | 27 | 39.0 | 117 | 58% |
| [Ismailia](west-asia/Egypt/Ismailia/) | `light-metro-3car` | 3 | 32 | 47.7 | 121 | 63% |
| [Kafr-El-Sheikh](west-asia/Egypt/Kafr-El-Sheikh/) | `tram-2car` | 3 | 20 | 31.6 | 95 | 81% |
| [Luxor](west-asia/Egypt/Luxor/) | `light-metro-3car` | 3 | 31 | 50.7 | 127 | 73% |
| [Mahalla](west-asia/Egypt/Mahalla/) | `light-metro-3car` | 3 | 22 | 38.3 | 101 | 68% |
| [Mansoura-Eg](west-asia/Egypt/Mansoura-Eg/) | `light-metro-3car` | 3 | 31 | 51.6 | 131 | 71% |
| [Minya](west-asia/Egypt/Minya/) | `light-metro-3car` | 3 | 34 | 53.2 | 137 | 69% |
| [Port-Said](west-asia/Egypt/Port-Said/) | `light-metro-3car` | 3 | 23 | 29.2 | 76 | 66% |
| [Qena](west-asia/Egypt/Qena/) | `light-metro-3car` | 3 | 29 | 49.3 | 129 | 82% |
| [Sohag](west-asia/Egypt/Sohag/) | `light-metro-3car` | 3 | 24 | 44.4 | 119 | 77% |
| [Suez](west-asia/Egypt/Suez/) | `light-metro-3car` | 3 | 35 | 60.6 | 154 | 57% |
| [Tanta](west-asia/Egypt/Tanta/) | `light-metro-3car` | 3 | 38 | 74.9 | 193 | 56% |
| [Zagazig](west-asia/Egypt/Zagazig/) | `light-metro-3car` | 3 | 26 | 42.9 | 116 | 63% |
| [Amarah](west-asia/Iraq/Amarah/) | `light-metro-3car` | 3 | 32 | 46.6 | 114 | 57% |
| [Baghdad](west-asia/Iraq/Baghdad/) | `metro-6car` | 9 | 261 | 501.3 | 998 | 86% |
| [Baqubah](west-asia/Iraq/Baqubah/) | `light-metro-3car` | 3 | 36 | 60.9 | 157 | 60% |
| [Basra](west-asia/Iraq/Basra/) | `metro-6car` | 7 | 168 | 305.4 | 584 | 82% |
| [Diwaniyah](west-asia/Iraq/Diwaniyah/) | `light-metro-3car` | 3 | 30 | 49.8 | 127 | 50% |
| [Duhok](west-asia/Iraq/Duhok/) | `light-metro-3car` | 3 | 35 | 57.3 | 148 | 60% |
| [Erbil](west-asia/Iraq/Erbil/) | `metro-4car` | 5 | 79 | 138.1 | 303 | 62% |
| [Fallujah](west-asia/Iraq/Fallujah/) | `light-metro-3car` | 3 | 33 | 55.8 | 143 | 70% |
| [Hillah](west-asia/Iraq/Hillah/) | `light-metro-3car` | 3 | 35 | 57.9 | 152 | 66% |
| [Karbala](west-asia/Iraq/Karbala/) | `metro-4car` | 6 | 107 | 168.5 | 282 | 60% |
| [Kirkuk](west-asia/Iraq/Kirkuk/) | `metro-4car` | 5 | 88 | 143.9 | 233 | 61% |
| [Kut](west-asia/Iraq/Kut/) | `light-metro-3car` | 3 | 27 | 46.4 | 122 | 60% |
| [Mosul](west-asia/Iraq/Mosul/) | `metro-4car` | 6 | 121 | 207.3 | 343 | 62% |
| [Najaf](west-asia/Iraq/Najaf/) | `metro-4car` | 6 | 101 | 165.1 | 312 | 52% |
| [Nasiriyah](west-asia/Iraq/Nasiriyah/) | `light-metro-3car` | 3 | 29 | 51.1 | 134 | 59% |
| [Ramadi](west-asia/Iraq/Ramadi/) | `light-metro-3car` | 3 | 32 | 48.0 | 123 | 70% |
| [Samawah](west-asia/Iraq/Samawah/) | `light-metro-3car` | 3 | 32 | 50.4 | 125 | 59% |
| [Sulaymaniyah](west-asia/Iraq/Sulaymaniyah/) | `metro-4car` | 4 | 69 | 119.8 | 167 | 67% |
| [Amman](west-asia/Jordan/Amman/) | `metro-6car` | 9 | 212 | 358.4 | 746 | 67% |
| [Aqaba](west-asia/Jordan/Aqaba/) | `tram-2car` | 3 | 23 | 34.6 | 105 | 63% |
| [Irbid](west-asia/Jordan/Irbid/) | `light-metro-3car` | 3 | 29 | 48.7 | 127 | 65% |
| [Zarqa](west-asia/Jordan/Zarqa/) | `light-metro-3car` | 3 | 43 | 72.5 | 185 | 56% |
| [Beirut](west-asia/Lebanon/Beirut/) | `metro-4car` | 6 | 95 | 142.6 | 266 | 60% |
| [Sidon](west-asia/Lebanon/Sidon/) | `tram-2car` | 3 | 21 | 37.8 | 111 | 85% |
| [Tripoli-Lb](west-asia/Lebanon/Tripoli-Lb/) | `light-metro-3car` | 3 | 30 | 45.6 | 116 | 57% |
| [Gaza-City](west-asia/Palestine/Gaza-City/) | `light-metro-3car` | 3 | 25 | 38.8 | 100 | 62% |
| [Hebron](west-asia/Palestine/Hebron/) | `light-metro-3car` | 3 | 36 | 60.3 | 153 | 73% |
| [Nablus](west-asia/Palestine/Nablus/) | `light-metro-3car` | 3 | 37 | 71.7 | 186 | 71% |
| [Abha](west-asia/Saudi Arabia/Abha/) | `light-metro-3car` | 3 | 35 | 59.1 | 150 | 29% |
| [Al-Kharj](west-asia/Saudi Arabia/Al-Kharj/) | `light-metro-3car` | 3 | 39 | 67.7 | 170 | 70% |
| [Buraidah](west-asia/Saudi Arabia/Buraidah/) | `light-metro-3car` | 3 | 43 | 69.2 | 173 | 46% |
| [Dammam](west-asia/Saudi Arabia/Dammam/) | `metro-4car` | 6 | 162 | 272.9 | 454 | 49% |
| [Hail](west-asia/Saudi Arabia/Hail/) | `light-metro-3car` | 3 | 37 | 63.1 | 155 | 47% |
| [Hofuf](west-asia/Saudi Arabia/Hofuf/) | `light-metro-3car` | 3 | 47 | 77.9 | 190 | 49% |
| [Jeddah](west-asia/Saudi Arabia/Jeddah/) | `metro-6car` | 9 | 210 | 375.4 | 768 | 69% |
| [Jizan](west-asia/Saudi Arabia/Jizan/) | `light-metro-3car` | 3 | 30 | 47.9 | 124 | 68% |
| [Khamis-Mushait](west-asia/Saudi Arabia/Khamis-Mushait/) | `light-metro-3car` | 3 | 44 | 81.2 | 206 | 45% |
| [Mecca](west-asia/Saudi Arabia/Mecca/) | `metro-4car` | 6 | 129 | 223.1 | 371 | 46% |
| [Medina](west-asia/Saudi Arabia/Medina/) | `metro-4car` | 6 | 105 | 179.8 | 297 | 51% |
| [Najran](west-asia/Saudi Arabia/Najran/) | `light-metro-3car` | 3 | 35 | 56.7 | 143 | 46% |
| [Tabuk](west-asia/Saudi Arabia/Tabuk/) | `light-metro-3car` | 3 | 37 | 63.0 | 161 | 46% |
| [Taif](west-asia/Saudi Arabia/Taif/) | `light-metro-3car` | 3 | 34 | 59.5 | 154 | 69% |
| [Aleppo](west-asia/Syria/Aleppo/) | `metro-4car` | 6 | 119 | 183.9 | 314 | 61% |
| [Damascus](west-asia/Syria/Damascus/) | `metro-4car` | 6 | 122 | 197.9 | 335 | 77% |
| [Deir-Ez-Zor](west-asia/Syria/Deir-Ez-Zor/) | `light-metro-3car` | 3 | 31 | 51.4 | 135 | 65% |
| [Hama](west-asia/Syria/Hama/) | `light-metro-3car` | 3 | 30 | 51.4 | 134 | 64% |
| [Homs](west-asia/Syria/Homs/) | `light-metro-3car` | 3 | 28 | 40.0 | 102 | 48% |
| [Idlib](west-asia/Syria/Idlib/) | `tram-2car` | 3 | 18 | 32.0 | 93 | 75% |
| [Latakia](west-asia/Syria/Latakia/) | `light-metro-3car` | 3 | 25 | 42.8 | 113 | 57% |
| [Raqqa](west-asia/Syria/Raqqa/) | `light-metro-3car` | 3 | 28 | 48.7 | 126 | 86% |
| [Tartus](west-asia/Syria/Tartus/) | `tram-2car` | 3 | 20 | 27.8 | 89 | 83% |
| [Aden](west-asia/Yemen/Aden/) | `light-metro-3car` | 3 | 29 | 45.8 | 119 | 72% |
| [Dhamar](west-asia/Yemen/Dhamar/) | `tram-2car` | 3 | 18 | 29.1 | 89 | 72% |
| [Hodeidah](west-asia/Yemen/Hodeidah/) | `light-metro-3car` | 3 | 23 | 30.7 | 79 | 66% |
| [Ibb](west-asia/Yemen/Ibb/) | `light-metro-3car` | 3 | 27 | 49.9 | 130 | 74% |
| [Lahij](west-asia/Yemen/Lahij/) | `tram-2car` | 3 | 19 | 28.9 | 90 | 82% |
| [Mukalla](west-asia/Yemen/Mukalla/) | `light-metro-3car` | 3 | 35 | 61.6 | 160 | 63% |
| [Sanaa](west-asia/Yemen/Sanaa/) | `metro-6car` | 7 | 140 | 233.1 | 474 | 73% |
| [Sayun](west-asia/Yemen/Sayun/) | `tram-2car` | 3 | 18 | 24.4 | 77 | 79% |
| [Taiz](west-asia/Yemen/Taiz/) | `light-metro-3car` | 3 | 25 | 42.8 | 113 | 65% |

```bash
scripts/regenerate-city.sh samawah
```

The command refreshes the full package in the canonical `designs/` tree.
