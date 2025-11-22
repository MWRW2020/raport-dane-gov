import hashlib
import os
from datetime import datetime
from xml.etree import ElementTree as ET
from xml.dom import minidom 

# Rejestracja przestrzeni nazw jest kluczowa dla ElementTree, aby działało parsowanie
ET.register_namespace('p', 'https://www.dane.gov.pl/static/xml/otwarte_dane_latest.xsd')

# --- SEKCJA KONFIGURACYJNA ---
CONFIG = {
    "DEWELOPER_NAZWA": "MWRW Sp. z o.o.",
    "INWESTYCJA_NAZWA": "Brzozowy Zakątek",
    "ROK_ZBIORU": "2025",
    "INWESTYCJA_ID": "brzozowy_zakatek_kliny",
    "INWESTYCJA_URL": "https://www.mwrw.net/kliny",
    "DANE_BASE_URL": "https://mwrw2020.github.io/raport-dane-gov/",
    "XML_FILENAME": "dane_deweloper_brzozowy",
    "SCHEMA_URL": "https://www.dane.gov.pl/static/xml/otwarte_dane_latest.xsd",
    "NAMESPACE": "p"
}
# -----------------------------

def create_dataset_structure(root):
    """
    Tworzy podstawową strukturę <dataset> dla pierwszego uruchomienia.
    UWAGA: Zawiera trwałą KOREKTĘ błędu TypeError w sekcji <categories> (linie 79-80).
    """
    
    # Używamy pełnej nazwy elementu z przestrzenią nazw
    # Atrybut status='draft' jest na czas testów. Docelowo: 'published' [3].
    dataset = ET.SubElement(root, f"{{{CONFIG['SCHEMA_URL']}}}dataset", status='draft') 
    
    ET.SubElement(dataset, 'extIdent').text = f"dataset_{CONFIG['INWESTYCJA_ID']}" [4]
    
    title_dataset = ET.SubElement(dataset, 'title')
    ET.SubElement(title_dataset, 'polish').text = f"Ceny ofertowe mieszkań dewelopera {CONFIG['DEWELOPER_NAZWA']} w {CONFIG['ROK_ZBIORU']} r."
    ET.SubElement(title_dataset, 'english').text = f"Offer prices of apartments of developer {CONFIG['DEWELOPER_NAZWA']} in {CONFIG['ROK_ZBIORU']}."
    
    description_dataset = ET.SubElement(dataset, 'description')
    desc_text_pl = (f"Zbiór danych zawiera informacje o cenach ofertowych mieszkań dewelopera {CONFIG['DEWELOPER_NAZWA']} "
                    f"udostępniane zgodnie z art. 19b. ust. 1 Ustawy z dnia 20 maja 2021 r. o ochronie praw nabywcy lokalu "
                    f"mieszkalnego lub domu jednorodzinnego oraz Deweloperskim Funduszu Gwarancyjnym (Dz. U. z 2024 r. poz. 695).")
    ET.SubElement(description_dataset, 'polish').text = desc_text_pl
    ET.SubElement(description_dataset, 'english').text = desc_text_pl
    
    ET.SubElement(dataset, 'url').text = CONFIG['INWESTYCJA_URL']
    
    # *******************************************************************
    # PRAWIDŁOWA KOREKTA BŁĘDU: ZAPEWNIENIE ZAGNIEŻDŻONEJ STRUKTURY
    # Wymagane jest <categories><category>ECON</category></categories> [1, 2].
    categories = ET.SubElement(dataset, 'categories') # Tworzymy tag nadrzędny
    ET.SubElement(categories, 'category').text = 'ECON' # Tworzymy tag zagnieżdżony
    # *******************************************************************
    
    tags = ET.SubElement(dataset, 'tags')
    ET.SubElement(tags, 'tag').text = 'deweloper'
    
    ET.SubElement(dataset, 'updateFrequency').text = 'daily' [5]
    ET.SubElement(dataset, 'hasDynamicData').text = 'false' [5]
    ET.SubElement(dataset, 'hasHighValueData').text = 'true' [5]
    ET.SubElement(dataset, 'hasHighValueDataFromEuropeanCommissionList').text = 'false' [6]
    ET.SubElement(dataset, 'hasResearchData').text = 'false' [6]
    
    resources = ET.SubElement(dataset, 'resources') [2]
    
    return root, resources

def create_resource_element(resources_element_et, today_str, today_str_compact, daily_data_url):
    """Tworzy i dodaje nowy element <resource> (dzienny raport) do listy zasobów ElementTree."""
    
    ext_ident_today = f"resource_{CONFIG['INWESTYCJA_ID']}_{today_str_compact}"
    
    # 1. Sprawdzenie, czy zasób dla dzisiejszej daty już istnieje (zapobiega duplikatom)
    xpath_check = f"./resource[extIdent='{ext_ident_today}']"
    if resources_element_et.find(xpath_check) is not None:
        print(f"  Zasób dla daty {today_str} (extIdent: {ext_ident_today}) już istnieje w pliku. Nie dodano nowego wpisu.")
        return False
        
    # 2. Tworzenie i dodawanie nowego zasobu (status='draft' na czas testów) [7]
    resource = ET.SubElement(resources_element_et, 'resource', status='draft')
    
    ET.SubElement(resource, 'extIdent').text = ext_ident_today [8]
    ET.SubElement(resource, 'url').text = daily_data_url [8]
    
    title_resource = ET.SubElement(resource, 'title')
    ET.SubElement(title_resource, 'polish').text = f"Ceny ofertowe mieszkań dewelopera {CONFIG['DEWELOPER_NAZWA']} {today_str}"
    ET.SubElement(title_resource, 'english').text = f"Offer prices for developer's apartments {CONFIG['DEWELOPER_NAZWA']} {today_str}"
    
    description_resource = ET.SubElement(resource, 'description')
    desc_res_text_pl = (f"Dane dotyczące cen ofertowych mieszkań dewelopera {CONFIG['DEWELOPER_NAZWA']} udostępnione {today_str} "
                        f"zgodnie z art. 19b. ust. 1 Ustawy.") 
    ET.SubElement(description_resource, 'polish').text = desc_res_text_pl
    ET.SubElement(description_resource, 'english').text = desc_res_text_pl
    
    ET.SubElement(resource, 'availability').text = 'local' [9]
    ET.SubElement(resource, 'dataDate').text = today_str [9]

    special_signs = ET.SubElement(resource, 'specialSigns') [10]
    ET.SubElement(special_signs, 'specialSign').text = 'X' [10]
    
    ET.SubElement(resource, 'hasDynamicData').text = 'false' [11]
    ET.SubElement(resource, 'hasHighValueData').text = 'true' [11]
    ET.SubElement(resource, 'hasHighValueDataFromEuropeanCommissionList').text = 'false' [12]
    ET.SubElement(resource, 'hasResearchData').text = 'false' [12]
    ET.SubElement(resource, 'containsProtectedData').text = 'false' [12]
    
    print(f"  Dodano nowy zasób dla daty: {today_str}.")
    return True

def format_xml(root_element):
    """
    Formatowanie XML za pomocą minidom.
    """
    # Serializacja do stringu z utf-8
    xml_string_raw = ET.tostring(root_element, 'utf-8', method='xml')
    
    # Używamy minidom do formatowania (pretty-print)
    parsed_string = minidom.parseString(xml_string_raw)
    
    pretty_xml = parsed_string.toprettyxml(indent="  ", encoding="utf-8")
    
    # Minidom może dodawać niechciane nagłówki i puste linie, które usuwamy
    pretty_xml_str = pretty_xml.decode('utf-8')
    lines = pretty_xml_str.split('\n')
    formatted_lines = [line for line in lines if line.strip() and not line.startswith('<?xml')]
    
    return '\n'.join(formatted_lines).encode('utf-8')


def generate_xml_and_md5():
    """Główna funkcja logiki: ładuje, modyfikuje/tworzy, zapisuje XML i MD5 (akumulacja)."""
    
    xml_file_path = f"{CONFIG['XML_FILENAME']}.xml"
    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    today_str_compact = today.strftime("%Y%m%d")
    daily_data_filename = f"ceny-{CONFIG['INWESTYCJA_ID']}-{today_str}.xlsx"
    daily_data_url = CONFIG['DANE_BASE_URL'] + daily_data_filename
    
    resources_element_et = None
    root_et = None

    # --- 1. Tryb Wczytywania (Akumulacja) ---
    if os.path.exists(xml_file_path):
        print(f"  Znaleziono istniejący plik: {xml_file_path}. Aktywacja trybu AKUMULACJI.")
        
        try:
            tree_et = ET.parse(xml_file_path)
            root_et = tree_et.getroot()
            
            # Wyszukiwanie istniejącej sekcji <resources> z przestrzenią nazw
            resources_xpath = f".//{{{CONFIG['SCHEMA_URL']}}}resources"
            resources_element_et = root_et.find(resources_xpath)

            if resources_element_et is None:
                raise ValueError("Błąd: Nie znaleziono elementu <resources> w istniejącym pliku XML.")
            
        except Exception as e:
            print(f"Błąd podczas parsowania istniejącego pliku XML ({e}). Przechodzę do trybu tworzenia od nowa.")
            root_et = None 

    # --- 2. Tryb Tworzenia od Nowa (Pierwsze uruchomienie / Błąd Parsowania) ---
    if root_et is None:
        print("  Plik XML nie istnieje lub parsowanie nie powiodło się. Tworzenie nowej struktury.")
        
        # Tworzenie elementu głównego: p:datasets (zgodnie ze schematem)
        root_et = ET.Element(f"{CONFIG['NAMESPACE']}:datasets", attrib={f"xmlns:{CONFIG['NAMESPACE']}": CONFIG['SCHEMA_URL']})
        
        # Tworzenie struktury <dataset> i uzyskanie referencji do <resources>
        root_et, resources_element_et = create_dataset_structure(root_et)

    # --- 3. Dodawanie Nowego Zasobu ---
    create_resource_element(resources_element_et, today_str, today_str_compact, daily_data_url)

    # --- 4. Zapisywanie pliku XML ---
    
    final_xml_data = format_xml(root_et)
    
    with open(xml_file_path, "wb") as f:
        f.write(final_xml_data)
    print(f"  Plik XML został ZAKTUALIZOWANY i zapisany: {xml_file_path}")
    
    # --- 5. Generowanie MD5 ---
    
    md5_sum = hashlib.md5(final_xml_data).hexdigest()
    md5_file_path = f"{CONFIG['XML_FILENAME']}.md5"
    
    # Hash musi być małymi literami [13]
    with open(md5_file_path, "w") as f:
        f.write(md5_sum)
    print(f"  Plik MD5 został ZAKTUALIZOWANY i zapisany: {md5_file_path}")


if __name__ == "__main__":
    generate_xml_and_md5()
