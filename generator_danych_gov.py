import hashlib
import uuid
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom

# --- SEKCJA KONFIGURACYJNA ---
# Uzupełnij poniższe dane zgodnie z Twoją inwestycją.
CONFIG = {
    "DEWELOPER_NAZWA": "MWRW Sp. z o.o.",
    "INWESTYCJA_NAZWA": "Brzozowy Zakątek",
    "ROK_ZBIORU": "2025",
    "INWESTYCJA_ID": "brzozowy_zakatek_kliny",
    "INWESTYCJA_URL": "https://www.mwrw.net/kliny",
    "DANE_BASE_URL": "https://mwrw2020.github.io/dane-deweloper/",
    "XML_FILENAME": "dane_deweloper_brzozowy",
}
# -----------------------------

def generate_xml_content():
    """
    Generuje zawartość pliku XML zgodnie ze schematem dane.gov.pl dla deweloperów.
    """
    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    today_str_compact = today.strftime("%Y%m%d")

    daily_data_filename = f"ceny-{CONFIG['INWESTYCJA_ID']}-{today_str}.xlsx"
    daily_data_url = CONFIG['DANE_BASE_URL'] + daily_data_filename

    # --- NOWA, POPRAWIONA WERSJA TWORZENIA GŁÓWNEGO ELEMENTU ---
    # Definiujemy przestrzeń nazw (namespace) bezpośrednio w atrybutach elementu root.
    # To jest kluczowa zmiana, która rozwiązuje problem "unbound prefix" w sposób uniwersalny.
    SCHEMA_URL = "https://www.dane.gov.pl/static/xml/otwarte_dane_latest.xsd"
    root = Element(
        'p:datasets',
        attrib={'xmlns:p': SCHEMA_URL}
    )
    # -----------------------------------------------------------------

    # --- Zbiór danych - <dataset> ---
    dataset = SubElement(root, 'dataset', status='published')
    
    SubElement(dataset, 'extIdent').text = f"dataset_{CONFIG['INWESTYCJA_ID']}"
    
    title_dataset = SubElement(dataset, 'title')
    SubElement(title_dataset, 'polish').text = f"Ceny ofertowe mieszkań dewelopera {CONFIG['DEWELOPER_NAZWA']} w {CONFIG['ROK_ZBIORU']} r."
    SubElement(title_dataset, 'english').text = f"Offer prices of apartments of developer {CONFIG['DEWELOPER_NAZWA']} in {CONFIG['ROK_ZBIORU']}."
    
    description_dataset = SubElement(dataset, 'description')
    desc_text_pl = (f"Zbiór danych zawiera informacje o cenach ofertowych mieszkań dewelopera {CONFIG['DEWELOPER_NAZWA']} "
                    f"udostępniane zgodnie z art. 19b. ust. 1 Ustawy z dnia 20 maja 2021 r. o ochronie praw nabywcy lokalu "
                    f"mieszkalnego lub domu jednorodzinnego oraz Deweloperskim Funduszu Gwarancyjnym (Dz. U. z 2024 r. poz. 695).")
    SubElement(description_dataset, 'polish').text = desc_text_pl
    SubElement(description_dataset, 'english').text = desc_text_pl
    
    SubElement(dataset, 'url').text = CONFIG['INWESTYCJA_URL']
    SubElement(dataset, 'categories').text = 'ECON'
    
    tags = SubElement(dataset, 'tags')
    SubElement(tags, 'tag').text = 'deweloper'

    SubElement(dataset, 'updateFrequency').text = 'daily'
    
    SubElement(dataset, 'hasDynamicData').text = 'false'
    SubElement(dataset, 'hasHighValueData').text = 'true'
    SubElement(dataset, 'hasHighValueDataFromEuropeanCommissionList').text = 'false'
    SubElement(dataset, 'hasResearchData').text = 'false'

    resources = SubElement(dataset, 'resources')
    
    # --- Zasób - <resource> ---
    resource = SubElement(resources, 'resource', status='published')
    
    SubElement(resource, 'extIdent').text = f"resource_{CONFIG['INWESTYCJA_ID']}_{today_str_compact}"
    SubElement(resource, 'url').text = daily_data_url

    title_resource = SubElement(resource, 'title')
    SubElement(title_resource, 'polish').text = f"Ceny ofertowe mieszkań dewelopera {CONFIG['DEWELOPER_NAZWA']} {today_str}"
    SubElement(title_resource, 'english').text = f"Offer prices for developer's apartments {CONFIG['DEWELOPER_NAZWA']} {today_str}"

    description_resource = SubElement(resource, 'description')
    desc_res_text_pl = (f"Dane dotyczące cen ofertowych mieszkań dewelopera {CONFIG['DEWELOPER_NAZWA']} udostępnione {today_str} "
                        f"zgodnie z art. 19b. ust. 1 Ustawy.")
    SubElement(description_resource, 'polish').text = desc_res_text_pl
    SubElement(description_resource, 'english').text = desc_res_text_pl

    SubElement(resource, 'availability').text = 'local'
    SubElement(resource, 'dataDate').text = today_str

    special_signs = SubElement(resource, 'specialSigns')
    SubElement(special_signs, 'specialSign').text = 'X'

    SubElement(resource, 'hasDynamicData').text = 'false'
    SubElement(resource, 'hasHighValueData').text = 'true'
    SubElement(resource, 'hasHighValueDataFromEuropeanCommissionList').text = 'false'
    SubElement(resource, 'hasResearchData').text = 'false'
    SubElement(resource, 'containsProtectedData').text = 'false'

    xml_string = tostring(root, 'utf-8')
    parsed_string = minidom.parseString(xml_string)
    pretty_xml = parsed_string.toprettyxml(indent="  ", encoding="utf-8")
    
    return pretty_xml

def calculate_md5(file_content):
    md5_hash = hashlib.md5(file_content).hexdigest()
    return md5_hash

if __name__ == "__main__":
    xml_data = generate_xml_content()
    
    xml_file_path = f"{CONFIG['XML_FILENAME']}.xml"
    with open(xml_file_path, "wb") as f:
        f.write(xml_data)
    print(f"✅ Plik XML został wygenerowany: {xml_file_path}")

    md5_sum = calculate_md5(xml_data)
    
    md5_file_path = f"{CONFIG['XML_FILENAME']}.md5"
    with open(md5_file_path, "w") as f:
        f.write(md5_sum)
    print(f"✅ Plik MD5 został wygenerowany: {md5_file_path}")

