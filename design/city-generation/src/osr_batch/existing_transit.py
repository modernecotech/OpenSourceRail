"""Cities that already operate metro, tram, or light-rail transit.

OpenSourceRail auto-generates urban rail for cities that currently *lack*
one. Feeding a city like Paris into the solver wastes compute and emits a
design that would never be built. This module supplies the exclusion
filter used by `osr-cities-scan` (and anything else that needs it).

Scope: any city operating, as of 2026-Q2, at least one of:
    - heavy metro / subway / underground
    - light metro / light rail / LRT
    - modern or heritage tram / streetcar (in regular scheduled service)

Excludes systems that are strictly:
    - mainline / commuter rail only (no urban-rail character)
    - bus rapid transit
    - monorail as airport shuttle
    - funicular / cable car as tourist infra
    - lines in construction but not yet operational

Matching is on (ISO-2 country, name) with normalisation: lowercase,
diacritic stripping, apostrophe + hyphen collapse. GeoNames' `asciiname`
and `name` columns are both tried against the denylist.

When a new system opens, add the city here. Source of truth is the
project's own decisions, not Wikipedia — but Wikipedia's lists
(`List of metro systems`, `List of tram and light rail transit systems`)
are a reasonable place to cross-check before edits.
"""

from __future__ import annotations

import unicodedata


def _norm(s: str) -> str:
    """Normalise a city name for denylist matching.

    Lowercases, strips diacritics, collapses whitespace, drops
    apostrophes, and swaps hyphens for spaces so "saint-petersburg",
    "saint petersburg", and "sankt-peterburg" (after ascii fold) share
    a canonical form.
    """
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = s.lower().replace("'", "").replace("-", " ")
    return " ".join(s.split())


# {country_code: frozenset of normalised names}.
# Multiple entries per city cover common romanisations.
_RAW: dict[str, list[str]] = {
    # ---- North America -------------------------------------------------
    "US": [
        "new york", "new york city", "boston", "washington",
        "chicago", "los angeles", "san francisco", "atlanta", "miami",
        "philadelphia", "baltimore", "cleveland", "portland", "seattle",
        "denver", "minneapolis", "saint paul", "st. paul", "houston",
        "dallas", "phoenix", "saint louis", "st. louis", "buffalo",
        "charlotte", "pittsburgh", "salt lake city", "sacramento",
        "san diego", "san jose", "newark", "jersey city", "hoboken",
        "norfolk", "tampa", "memphis", "detroit", "kansas city",
        "tucson", "new orleans", "little rock", "honolulu", "tacoma",
        "oklahoma city", "el paso",
    ],
    "CA": [
        "toronto", "montreal", "vancouver", "calgary", "edmonton",
        "ottawa", "waterloo", "kitchener",
    ],
    "MX": [
        "mexico city", "ciudad de mexico", "monterrey", "guadalajara",
        "puebla",
    ],
    # ---- Central + South America ---------------------------------------
    "BR": [
        "sao paulo", "rio de janeiro", "brasilia", "belo horizonte",
        "recife", "porto alegre", "salvador", "fortaleza", "curitiba",
        "teresina", "maceio", "joao pessoa", "natal", "cariri", "campinas",
    ],
    "AR": ["buenos aires", "mendoza"],
    "CL": ["santiago", "valparaiso", "vina del mar"],
    "CO": ["medellin", "manizales"],
    "PE": ["lima", "callao"],
    "VE": ["caracas", "maracaibo", "valencia", "los teques"],
    "EC": ["quito"],
    "DO": ["santo domingo"],
    "PA": ["panama city", "panama"],
    "PR": ["san juan"],
    # ---- British Isles -------------------------------------------------
    "GB": [
        "london", "newcastle", "newcastle upon tyne", "glasgow",
        "liverpool", "manchester", "birmingham", "sheffield",
        "nottingham", "croydon", "edinburgh", "blackpool",
    ],
    "IE": ["dublin"],
    # ---- France --------------------------------------------------------
    "FR": [
        "paris", "lyon", "marseille", "lille", "toulouse", "rennes",
        "strasbourg", "bordeaux", "nice", "nantes", "grenoble",
        "montpellier", "reims", "rouen", "dijon", "tours", "angers",
        "orleans", "saint etienne", "le mans", "le havre", "caen",
        "clermont ferrand", "brest", "valenciennes", "mulhouse",
        "aubagne", "avignon", "besancon", "tournai",
    ],
    # ---- Germany / Austria / Switzerland -------------------------------
    "DE": [
        "berlin", "hamburg", "munich", "muenchen", "frankfurt",
        "stuttgart", "cologne", "koeln", "duesseldorf", "dusseldorf",
        "nuremberg", "nuernberg", "hannover", "hanover", "leipzig",
        "dresden", "bremen", "bonn", "essen", "bochum", "dortmund",
        "duisburg", "karlsruhe", "kassel", "augsburg", "mainz",
        "braunschweig", "bielefeld", "mannheim", "heidelberg",
        "freiburg", "ulm", "gera", "halle", "chemnitz", "erfurt",
        "jena", "magdeburg", "potsdam", "zwickau", "plauen",
        "goerlitz", "rostock", "schwerin", "cottbus", "darmstadt",
        "heilbronn", "strausberg", "woltersdorf", "brandenburg",
        "naumburg", "nordhausen",
    ],
    "AT": [
        "vienna", "wien", "linz", "graz", "innsbruck", "gmunden",
    ],
    "CH": [
        "zurich", "zuerich", "geneva", "basel", "bern", "berne",
        "lausanne", "neuchatel",
    ],
    # ---- Low Countries -------------------------------------------------
    "NL": [
        "amsterdam", "rotterdam", "the hague", "den haag", "utrecht",
    ],
    "BE": [
        "brussels", "bruxelles", "antwerp", "antwerpen", "charleroi",
        "ghent", "gent",
    ],
    "LU": ["luxembourg", "luxembourg city"],
    # ---- Iberia --------------------------------------------------------
    "ES": [
        "madrid", "barcelona", "bilbao", "valencia", "seville",
        "sevilla", "malaga", "palma", "palma de mallorca", "zaragoza",
        "alicante", "murcia", "granada", "parla", "vitoria",
        "vitoria gasteiz", "cadiz", "jaen", "cuenca", "santa cruz",
        "santa cruz de tenerife",
    ],
    "PT": ["lisbon", "lisboa", "porto"],
    # ---- Italy ---------------------------------------------------------
    "IT": [
        "rome", "roma", "milan", "milano", "turin", "torino", "naples",
        "napoli", "genoa", "genova", "brescia", "catania", "palermo",
        "florence", "firenze", "messina", "padua", "padova", "bergamo",
        "venice", "venezia", "sassari", "cagliari",
    ],
    # ---- Nordic --------------------------------------------------------
    "SE": [
        "stockholm", "gothenburg", "goteborg", "norrkoping", "lund",
    ],
    "NO": ["oslo", "bergen", "trondheim"],
    "DK": ["copenhagen", "kobenhavn", "aarhus", "odense"],
    "FI": ["helsinki", "tampere"],
    # ---- Central + Eastern Europe --------------------------------------
    "PL": [
        "warsaw", "warszawa", "krakow", "cracow", "lodz", "wroclaw",
        "poznan", "gdansk", "gdynia", "szczecin", "bydgoszcz", "torun",
        "katowice", "sosnowiec", "tychy", "elblag", "grudziadz",
        "czestochowa", "olsztyn", "bytom", "chorzow", "swietochlowice",
        "ruda slaska",
    ],
    "CZ": [
        "prague", "praha", "brno", "ostrava", "olomouc", "plzen",
        "pilsen", "liberec", "most", "litvinov",
    ],
    "SK": ["bratislava", "kosice"],
    "HU": ["budapest", "szeged", "debrecen", "miskolc"],
    "RO": [
        "bucharest", "bucuresti", "timisoara", "iasi", "oradea", "arad",
        "braila", "galati", "ploiesti",
    ],
    "BG": ["sofia"],
    "HR": ["zagreb", "osijek"],
    "RS": ["belgrade", "beograd"],
    "BA": ["sarajevo"],
    # ---- Former USSR ---------------------------------------------------
    "RU": [
        "moscow", "moskva", "saint petersburg", "st petersburg",
        "sankt peterburg", "kazan", "yekaterinburg", "ekaterinburg",
        "nizhny novgorod", "novosibirsk", "samara", "volgograd",
        "krasnodar", "ulyanovsk", "saratov", "rostov on don", "tula",
        "irkutsk", "perm", "kursk", "izhevsk", "kaliningrad", "smolensk",
        "yaroslavl", "orsk", "magnitogorsk", "pyatigorsk", "vladikavkaz",
        "tomsk", "krasnoyarsk", "kemerovo", "novokuznetsk", "prokopyevsk",
        "taganrog", "ufa", "cheboksary", "chelyabinsk", "biysk",
        "nizhnekamsk", "omsk", "naberezhnye chelny", "salavat", "achinsk",
        "angarsk", "tver", "noginsk", "khabarovsk", "vladivostok",
        "barnaul", "kolomna", "orel", "lipetsk", "ust ilimsk",
    ],
    "UA": [
        "kyiv", "kiev", "kharkiv", "kharkov", "dnipro", "dnipropetrovsk",
        "lviv", "lvov", "odesa", "odessa", "vinnytsia", "vinnitsa",
        "kryvyi rih", "krivoy rog", "mariupol", "zhytomyr", "mykolaiv",
        "nikolaev", "konotop", "kamianske", "kremenchuk", "avdiivka",
        "druzhkivka",
    ],
    "BY": ["minsk", "mazyr", "novopolotsk", "vitebsk"],
    "LV": ["riga", "liepaja", "daugavpils"],
    "EE": ["tallinn"],
    # ---- Turkey + Caucasus --------------------------------------------
    "TR": [
        "istanbul", "ankara", "izmir", "bursa", "kayseri", "konya",
        "eskisehir", "gaziantep", "samsun", "antalya", "adana",
        "kocaeli", "izmit", "denizli", "mersin",
    ],
    "AZ": ["baku"],
    "AM": ["yerevan"],
    "GE": ["tbilisi"],
    # ---- Middle East --------------------------------------------------
    "IL": ["jerusalem", "tel aviv", "tel aviv yafo", "haifa"],
    "SA": ["mecca", "makkah", "riyadh", "medina"],
    "AE": ["dubai"],
    "QA": ["doha"],
    "IR": [
        "tehran", "mashhad", "isfahan", "esfahan", "shiraz", "tabriz",
        "ahvaz", "karaj", "qom",
    ],
    # ---- North Africa --------------------------------------------------
    "EG": ["cairo", "al qahirah", "alexandria", "al iskandariyah"],
    "DZ": [
        "algiers", "alger", "oran", "constantine", "setif",
        "sidi bel abbes", "ouargla", "mostaganem",
    ],
    "MA": ["casablanca", "rabat"],
    "TN": ["tunis"],
    # ---- Sub-Saharan Africa -------------------------------------------
    "ET": ["addis ababa", "addis abeba"],
    "NG": ["abuja", "lagos"],
    "ZA": ["johannesburg", "pretoria"],
    # ---- South Asia ---------------------------------------------------
    "IN": [
        "delhi", "new delhi", "mumbai", "bangalore", "bengaluru",
        "chennai", "kolkata", "calcutta", "hyderabad", "jaipur",
        "lucknow", "kochi", "cochin", "ahmedabad", "nagpur", "noida",
        "pune", "kanpur", "agra", "gurgaon", "gurugram", "ghaziabad",
    ],
    "PK": ["lahore"],
    "BD": ["dhaka"],
    # ---- East Asia ----------------------------------------------------
    "CN": [
        "beijing", "peking", "shanghai", "guangzhou", "canton",
        "shenzhen", "chengdu", "wuhan", "chongqing", "xian", "tianjin",
        "nanjing", "hangzhou", "suzhou", "shenyang", "dalian", "harbin",
        "changchun", "qingdao", "kunming", "changsha", "zhengzhou",
        "hefei", "nanchang", "fuzhou", "xiamen", "ningbo", "wuxi",
        "urumqi", "lanzhou", "nanning", "guiyang", "taiyuan",
        "shijiazhuang", "jinan", "xuzhou", "luoyang", "sanya",
        "dongguan", "foshan", "huizhou", "zhuhai", "wenzhou",
        "changzhou", "baotou", "hohhot", "anshan", "daqing", "yinchuan",
        "jinhua", "shaoxing", "taizhou", "jiaxing", "shantou",
    ],
    "HK": ["hong kong"],
    "MO": ["macau", "macao"],
    "TW": [
        "taipei", "new taipei", "kaohsiung", "taichung", "taoyuan",
    ],
    "JP": [
        "tokyo", "osaka", "yokohama", "kyoto", "nagoya", "kobe",
        "sapporo", "fukuoka", "sendai", "hiroshima", "kitakyushu",
        "hakodate", "toyama", "okayama", "matsuyama", "kagoshima",
        "kumamoto", "kochi", "nagasaki", "takaoka", "toyohashi",
        "tokorozawa",
    ],
    "KR": [
        "seoul", "busan", "pusan", "daegu", "taegu", "daejeon",
        "taejon", "gwangju", "kwangju", "incheon", "inchon", "seongnam",
        "yongin", "uijeongbu",
    ],
    "KP": ["pyongyang"],
    # ---- Southeast Asia -----------------------------------------------
    "PH": ["manila", "quezon city"],
    "MY": ["kuala lumpur"],
    "SG": ["singapore"],
    "ID": ["jakarta", "palembang"],
    "TH": ["bangkok"],
    "VN": ["hanoi", "ho chi minh city", "saigon"],
    # ---- Central Asia -------------------------------------------------
    "KZ": ["almaty"],
    "UZ": ["tashkent", "samarkand"],
    # ---- Oceania ------------------------------------------------------
    "AU": [
        "sydney", "melbourne", "brisbane", "perth", "adelaide",
        "gold coast", "canberra", "newcastle",
    ],
    "NZ": ["auckland", "wellington"],
}

# Precompute normalised sets for O(1) lookup.
EXISTING_TRANSIT: dict[str, frozenset[str]] = {
    cc: frozenset(_norm(n) for n in names) for cc, names in _RAW.items()
}


def has_existing_transit(country: str, *names: str) -> bool:
    """True if any of the passed names matches a denylisted city in the country."""
    bucket = EXISTING_TRANSIT.get(country.upper())
    if not bucket:
        return False
    for n in names:
        if n and _norm(n) in bucket:
            return True
    return False
