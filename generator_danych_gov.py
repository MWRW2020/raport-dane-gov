import hashlib [4]
import os [4]
from datetime import datetime [4]
from xml.etree import ElementTree as ET [4]
from xml.dom import minidom [4]

# Rejestracja przestrzeni nazw jest kluczowa dla ElementTree [4]
ET.register_namespace('p', 'https://www.dane.gov.pl/static/xml/otwarte_dane_latest.xsd') [4]

# --- SEKCJA KONFIGURACYJNA ---
CONFIG = {
    "DEWELOPER_NAZWA": "MWRW Sp. z o.o.", [4]
    "INWESTYCJA_NAZWA": "Brzozowy Zakątek", [4]
    "ROK_ZBIORU": "2025", [4]
    "INWESTYCJA_ID": "brzozowy_zakatek_kliny", [4]
    "INWESTYCJA_URL": "https://www.mwrw.net/kliny", [4]
    "DANE_BASE_URL": "https://mwrw2020.github.io/raport-dane-gov/", [5]
    "XML_FILENAME": "dane_deweloper_brzozowy", [5]
    "SCHEMA_URL": "https://www.dane.gov.pl/static/xml/otwarte_dane_latest.xsd", [5]
    "NAMESPACE": "p" [5]
}
# -----------------------------

def create_dataset_structure(root):
    """
    Tworzy podstawową strukturę <dataset> dla pierwszego uruchomienia.
    Zawiera KOREKTĘ błędu TypeError w sekcji <categories> [2, 5].
    """
    # Tworzenie elementu <dataset> z pełną przestrzenią nazw
    # Atrybut status='draft' jest na czas testów [6].
    dataset = ET.SubElement(root, f"{{{CONFIG['SCHEMA_URL']}}}dataset", status='draft') [6]
    ET.SubElement(dataset, 'extIdent').text = f"dataset_{CONFIG['INWESTYCJA_ID']}" [6]

    title_dataset = ET.SubElement(dataset, 'title') [6]
    ET.SubElement(title_dataset, 'polish').text = f"Ceny ofertowe mieszkań dewelopera\n{CONFIG['DEWELOPER_NAZWA']} w {CONFIG['ROK_ZBIORU']} r." [6]
    ET.SubElement(title_dataset, 'english').text = f"Offer prices of apartments of developer\n{CONFIG['DEWELOPER_NAZWA']} in {CONFIG['ROK_ZBIORU']}." [6]

    description_dataset = ET.SubElement(dataset, 'description') [7]
    desc_text_pl = (f"Zbiór danych zawiera informacje o cenach ofertowych mieszkań\ndewelopera {CONFIG['DEWELOPER_NAZWA']} "
                    f"udostępniane zgodnie z art. 19b. ust. 1 Ustawy z dnia 20 maja 2021 r. o ochronie\npraw nabywcy lokalu "
                    f"mieszkalnego lub domu jednorodzinnego oraz Deweloperskim Funduszu\nGwarancyjnym (Dz. U. z 2024 r. poz. 695).") [7]
    ET.SubElement(description_dataset, 'polish').text = desc_text_pl [7]
    ET.SubElement(description_dataset, 'english').text = desc_text_pl [2]
    ET.SubElement(dataset, 'url').text = CONFIG['INWESTYCJA_URL'] [2]

    # *******************************************************************
    # KOREKTA BŁĘDU (KONIECZNIE DWIE LINIE): Zapewnienie zagnieżdżonej struktury <categories><category> [2]
    categories = ET.SubElement(dataset, 'categories') # Linia 80: Tworzymy tag nadrzędny [2]
    ET.SubElement(categories, 'category').text = 'ECON' # Linia 81: Tworzymy tag zagnieżdżony [2]
    # (Gospodarka i finanse) [8]
    # *******************************************************************

    tags = ET.SubElement(dataset, 'tags') [8]
    ET.SubElement(tags, 'tag').text = 'deweloper' [8]
    ET.SubElement(dataset, 'updateFrequency').text = 'daily' # Wymagane [8]
    ET.SubElement(dataset, 'hasDynamicData').text = 'false' [8]
    ET.SubElement(dataset, 'hasHighValueData').text = 'true' [8]
    ET.SubElement(dataset, 'hasHighValueDataFromEuropeanCommissionList').text = 'false' [8, 9]
    ET.SubElement(dataset, 'hasResearchData').text = 'false' [9]
    resources = ET.SubElement(dataset, 'resources') [9]
    return root, resources

def create_resource_element(resources_element_et, today_str, today_str_compact,
                            daily_data_url):
    """Tworzy i dodaje nowy element <resource> (dzienny raport) do listy zasobów ElementTree [9]."""
    ext_ident_today = f"resource_{CONFIG['INWESTYCJA_ID']}_{today_str_compact}" [9]

    # 1. Sprawdzenie, czy zasób dla dzisiejszej daty już istnieje [10]
    xpath_check = f"./resource[extIdent='{ext_ident_today}']" [10]
    if resources_element_et.find(xpath_check) is not None:
        print(f"  Zasób dla daty {today_str} (extIdent: {ext_ident_today}) już istnieje w pliku. Nie\ndodano nowego wpisu.") [10]
        return False

    # 2. Tworzenie i dodawanie nowego zasobu (status='draft' na czas testów) [10]
    resource = ET.SubElement(resources_element_et, 'resource', status='draft') [10]
    ET.SubElement(resource, 'extIdent').text = ext_ident_today # Unikalny identyfikator [10]
    ET.SubElement(resource, 'url').text = daily_data_url # Link do dziennego pliku XLSX/CSV [11]
    
    title_resource = ET.SubElement(resource, 'title') [11]
    ET.SubElement(title_resource, 'polish').text = f"Ceny ofertowe mieszkań dewelopera\n{CONFIG['DEWELOPER_NAZWA']} {today_str}" [11]
    ET.SubElement(title_resource, 'english').text = f"Offer prices for developer's apartments\n{CONFIG['DEWELOPER_NAZWA']} {today_str}" [11]
    
    description_resource = ET.SubElement(resource, 'description') [11]
    desc_res_text_pl = (f"Dane dotyczące cen ofertowych mieszkań dewelopera\n{CONFIG['DEWELOPER_NAZWA']} udostępnione {today_str} "
                        f"zgodnie z art. 19b. ust. 1 Ustawy.") [12]
    ET.SubElement(description_resource, 'polish').text = desc_res_text_pl [12]
    ET.SubElement(description_resource, 'english').text = desc_res_text_pl [12]
    
    ET.SubElement(resource, 'availability').text = 'local' # Plik jest udostępniany z repozytorium OD [12]
    ET.SubElement(resource, 'dataDate').text = today_str # Data raportowania [12]
    
    special_signs = ET.SubElement(resource, 'specialSigns') [12]
    ET.SubElement(special_signs, 'specialSign').text = 'X' # Wymagany znak umowny [13]

    ET.SubElement(resource, 'hasDynamicData').text = 'false' [13]
    ET.SubElement(resource, 'hasHighValueData').text = 'true' [13]
    ET.SubElement(resource, 'hasHighValueDataFromEuropeanCommissionList').text = 'false' [13]
    ET.SubElement(resource, 'hasResearchData').text = 'false' [13]
    ET.SubElement(resource, 'containsProtectedData').text = 'false' [13]
    
    print(f"  Dodano nowy zasób dla daty: {today_str}.") [13]
    return True [14]

def format_xml(root_element):
    """
    Formatowanie XML za pomocą minidom, z przywróceniem przestrzeni nazw [14].
    """
    xml_string_raw = ET.tostring(root_element, 'utf-8', method='xml') [14]
    parsed_string = minidom.parseString(xml_string_raw) [14]
    pretty_xml = parsed_string.toprettyxml(indent="  ", encoding="utf-8") [14]
    pretty_xml_str = pretty_xml.decode('utf-8') [14]
    lines = pretty_xml_str.split('\n') [14]
    formatted_lines = [line for line in lines if line.strip() and not line.startswith('<?xml')] [15]
    
    # Przywracanie poprawnego formatu tagu root z przestrzenią nazw p:datasets [15]
    final_xml = '\n'.join(formatted_lines).replace('<datasets>', f'p:datasets\nxmlns:p="{CONFIG["SCHEMA_URL"]}">') [15]
    final_xml = final_xml.replace('</datasets>', f'</p:datasets>') [15]
    return final_xml.encode('utf-8') [15]

def generate_xml_and_md5():
    """Główna funkcja logiki: ładuje, modyfikuje/tworzy, zapisuje XML i MD5 (akumulacja) [15]."""
    xml_file_path = f"{CONFIG['XML_FILENAME']}.xml" [15]
    today = datetime.now() [1]
    
    today_str = today.strftime("%Y-%m-%d") [1]
    today_str_compact = today.strftime("%Y%m%d") [1]
    daily_data_filename = f"ceny-{CONFIG['INWESTYCJA_ID']}-{today_str}.xlsx" [1]
    daily_data_url = CONFIG['DANE_BASE_URL'] + daily_data_filename [1]
    
    resources_element_et = None
    root_et = None

    # --- 1. Tryb Wczytywania (Akumulacja) --- [1]
    if os.path.exists(xml_file_path): [1]
        print(f"  Znaleziono istniejący plik: {xml_file_path}. Aktywacja trybu AKUMULACJI.") [1]
        try:
            tree_et = ET.parse(xml_file_path) [1]
            root_et = tree_et.getroot() [16]
            # Wyszukiwanie istniejącej sekcji <resources> z przestrzenią nazw [16]
            resources_xpath = f".//{{{CONFIG['SCHEMA_URL']}}}resources" [16]
            resources_element_et = root_et.find(resources_xpath) [16]
            if resources_element_et is None:
                raise ValueError("Błąd: Nie znaleziono elementu <resources> w istniejącym pliku\nXML.") [16]
        except Exception as e:
            print(f"Błąd podczas parsowania istniejącego pliku XML ({e}). Przechodzę do trybu\ntworzenia od nowa.") [3]
            root_et = None [3]

    # --- 2. Tryb Tworzenia od Nowa (Pierwsze uruchomienie / Błąd Parsowania) --- [3]
    if root_et is None:
        print("  Plik XML nie istnieje lub parsowanie nie powiodło się. Tworzenie nowej\nstruktury.") [3]
        # Tworzenie elementu głównego: p:datasets (zgodnie ze schematem) [3]
        root_placeholder = ET.Element(f"{CONFIG['NAMESPACE']}:datasets",
                                     attrib={f"xmlns:{CONFIG['NAMESPACE']}": CONFIG['SCHEMA_URL']}) [3]
        # Tworzenie struktury <dataset> i uzyskanie referencji do <resources> [17]
        root_et, resources_element_et = create_dataset_structure(root_placeholder) [17]

    # --- 3. Dodawanie Nowego Zasobu --- [17]
    create_resource_element(resources_element_et, today_str, today_str_compact, daily_data_url) [17]

    # --- 4. Zapisywanie pliku XML --- [17]
    final_xml_data = format_xml(root_et) [17]
    with open(xml_file_path, "wb") as f: [17]
        f.write(final_xml_data) [17]
    print(f"  Plik XML został ZAKTUALIZOWANY i zapisany: {xml_file_path}") [17]

    # --- 5. Generowanie MD5 --- [18]
    md5_sum = hashlib.md5(final_xml_data).hexdigest() [18]
    md5_file_path = f"{CONFIG['XML_FILENAME']}.md5" [18]
    # Hash musi być małymi literami [18]
    with open(md5_file_path, "w") as f: [18]
        f.write(md5_sum) [18]
    print(f"  Plik MD5 został ZAKTUALIZOWANY i zapisany: {md5_file_path}") [18]

if __name__ == "__main__":
    generate_xml_and_md5() [18]
