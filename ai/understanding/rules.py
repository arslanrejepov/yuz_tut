CATEGORY_SYNONYMS = {
    "Egin-eşik we Aýakgap": ["eşik", "geýim", "köýnek", "jinsi", "aýakgap", "botinka", "krossofka"],
    "Matalar we köýnekler": ["mata", "tikin esbaby", "tikinlik"],
    "Süýjülikler": ["süýji", "şokolad", "konfet"],
    "Kofe": ["kofe", "kapuçino", "latte"],
    "Aziýa tagamlary": ["aziýa tagam", "aziýa restoran"],
    "Ýewropa tagamlary": ["ýewropa tagam", "ýewropa restoran"],
    "Elektronika": ["elektronika", "noutbuk", "kompýuter", "printer"],
    "Pizza": ["pizza"],
    "Milli tagamlar": ["milli tagam", "milli restoran", "gutap", "çekdirme", "palow"],
    "Gurluşyk we Hojalyk harytlary": ["gurluşyk haryt", "hojalyk haryt"],
    "Mebel we interýer": ["mebel", "diwan", "krowat", "stol", "stul"],
    "Parfýumeriýa we Kosmetika": ["atyr", "kosmetika", "parfýumeriýa"],
    "Mangal": ["mangal", "kebap", "şaşlyk"],
    "Güller we sowgatlyklar": ["gül", "sowgat", "sowgatlyk"],
    "Türk tagamlary": ["türk tagam", "türk restoran"],
    "Altyn şaý-sepler": ["altyn", "şaý-sep", "gyzyl haryt"],
    "Çagalar harytlary": ["çaga haryt", "oýnawaç", "oýunjak"],
    "Tikinçilik öýi we harytlary (Atelýe)": ["ateýle", "tikinçi", "tikin öýi"],
    "Çaga egin-eşikleri we aýakgaplary": ["çaga eşik", "çaga aýakgap"],
    "Gap-gaçlar we öý harytlary": ["gap-gaç", "öý haryt"],
    "Sumkalar": ["sumka"],
    "Burger": ["burger", "gamburger"],
    "Hojalyk tehnikalary": ["hojalyk tehnika", "hojalyk enjam", "sowadyjy", "kir ýuwujy"],
    "Ertirlik": ["ertirlik", "nahar günortanlyk"],
    "Telefon we gadjetler": ["telefon", "gadjet", "smartfon"],
    "Konditerler": ["kondit", "tort dükany"],
    "Döner": ["döner"],
    "Fastfood": ["fastfood", "çalt tagam"],
    "Şaý-sepler": ["şaý-sep", "bijuteriýa"],
    "Awto hyzmatlar": ["awto hyzmat", "awtoserwis", "maşyn abatlamak", "maşyn döwüldi", "maşyn döwülen"],
    "Haly we perdeler": ["haly", "perde"],
    "Sowuk içgiler": ["sowuk içgi", "limonad", "gazly suw"],
    "Supermarket": ["supermarket", "market", "azyk dükany"],
    "Ýaglyklar": ["ýaglyk", "şarf"],
    "Toý Mekan": ["toý mekan", "toý jaý"],
    "Dizaýn we Programmirleme": ["dizaýn", "programmirleme", "web sahypa"],
    "Bezeg işleri": ["bezeg", "remont"],
    "Steýk": ["steýk"],
    "Balyk": ["balyk restoran", "balyk tagamy"],
    "Mahabat we poligrafiýa": ["mahabat", "poligrafiýa", "banner"],
    "Suşi": ["suşi", "roll"],
    "Awtoşaýlar we awtoulaglar": ["awtoşaý", "ätiýaçlyk şaý", "maşyn şaý"],
    "Aýdym-saz": ["aýdym-saz", "aýdymçy", "saz"],
    "Foto we Wideostudio": ["foto", "surat düşürmek", "wideo düşürmek"],
    "Söwda merkezleri": ["söwda merkezi", "mol"],
    "Eltip bermek": ["eltip bermek", "delivery"],
    "Gözellik Salony": ["gözellik salon", "salon", "saç kesdirmek", "manikýur"],
    "Bank": ["bank", "kredit"],
    "Tortlar": ["tort"],
    "Toý salonlar": ["toý salon"],
    "Doňdurma": ["doňdurma", "morožnoý"],
    "Kitap dükanlary": ["kitap dükany", "kitap"],
    "Sagatlar": ["sagat dükany", "sagat"],
    "Toý hyzmatlary": ["toý hyzmat"],
    "Karaoke": ["karaoke"],
    "Kompýuter tehnikalary": ["kompýuter tehnika"],
    "Himiki arassalaýyş": ["himiki arassalaýyş", "hemçistka"],
    "Ýangyç bekedi": ["ýangyç beket", "benzin", "azs"],
    "Emläk agentligi": ["emläk", "kwartira", "jaý satyn almak"],
    "Dermanhana": ["derman", "aptek", "dermanhana"],
    "Optika": ["optika", "äýnek"],
    "Kinoteatr": ["kino", "kinoteatr"],
}

SORT_INTENT_KEYWORDS = {
    "sort_by_rating": ["iň gowy", "in gowy", "gowusy", "reýtingi ýokary"],
    "sort_by_price_asc": ["arzan", "arzanrak", "iň arzan"],
    "sort_by_distance": ["ýakyn", "golaý", "iň ýakyn"],
}

OPEN_NOW_KEYWORDS = ["gije işleýän", "häzir açyk", "şu wagt açyk", "24 sagat"]


def normalize(text):
    return text.lower().strip()


def rule_based_extract(query):
    q = normalize(query)
    matched_category = None
    for category, synonyms in CATEGORY_SYNONYMS.items():
        for syn in synonyms:
            if syn in q:
                matched_category = category
                break
        if matched_category:
            break

    sort_by = None
    for sort_key, keywords in SORT_INTENT_KEYWORDS.items():
        if any(kw in q for kw in keywords):
            sort_by = sort_key
            break

    open_now_only = any(kw in q for kw in OPEN_NOW_KEYWORDS)

    return {
        "category": matched_category,
        "sort_by": sort_by,
        "open_now_only": open_now_only,
    }