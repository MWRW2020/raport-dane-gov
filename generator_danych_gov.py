import hashlib
import os
from datetime import datetime
from xml.etree import ElementTree as ET
from xml.dom import minidom # Używane tylko do formatowania (pretty-print)

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
    Zawiera KOREKTĘ błędu TypeError w sekcji <categories>.
    """
    
    # Używamy pełnej nazwy elementu z przestrzenią nazw
    dataset = ET.SubElement(root, f"{{{CONFIG['SCHEMA_URL']}}}dataset", status='draft') 
    
    # Tworzenie elementów bez przestrzeni nazw (automatycznie dziedziczą z root)
    ET.SubElement(dataset, 'extIdent').text = f"dataset_{CONFIG['INWESTYCJA_ID']}"
    
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
    # PRAWIDŁOWA KOREKTA BŁĘDU: Element <categories> jest zagnieżdżony.
    categories = ET.SubElement(dataset, 'categories') # Tworzymy tag nadrzędny
    ET.SubElement(categories, 'category').text = 'ECON' # Tworzymy tag zagnieżdżony (Gospodarka i finanse) [2]
    # *******************************************************************
    
    tags = ET.SubElement(dataset, 'tags')
    ET.SubElement(tags, 'tag').text = 'deweloper'
    
    ET.SubElement(dataset, 'updateFrequency').text = 'daily' # Wymagane "daily" [7]
    ET.SubElement(dataset, 'hasDynamicData').text = 'false' # Wymagane "false" [7]
    ET.SubElement(dataset, 'hasHighValueData').text = 'true' # Wymagane "true" [7]
    ET.SubElement(dataset, 'hasHighValueDataFromEuropeanCommissionList').text = 'false' # Wymagane "false" [8]
    ET.SubElement(dataset, 'hasResearchData').text = 'false' # Wymagane "false" [8]
    
    resources = ET.SubElement(dataset, 'resources')
    
    return root, resources

def create_resource_element(resources_element_et, today_str, today_str_compact, daily_data_url):
    """Tworzy i dodaje nowy element <resource> (dzienny raport) do listy zasobów ElementTree."""
    
    ext_ident_today = f"resource_{CONFIG['INWESTYCJA_ID']}_{today_str_compact}"
    
    # 1. Sprawdzenie, czy zasób dla dzisiejszej daty już istnieje (zapobiega duplikatom)
    xpath_check = f"./resource[extIdent='{ext_ident_today}']"
    if resources_element_et.find(xpath_check) is not None:
        print(f"  Zasób dla daty {today_str} (extIdent: {ext_ident_today}) już istnieje w pliku. Nie dodano nowego wpisu.")
        return False
        
    # 2. Tworzenie i dodawanie nowego zasobu (status='draft' na czas testów) [9]
    resource = ET.SubElement(resources_element_et, 'resource', status='draft')
    
    ET.SubElement(resource, 'extIdent').text = ext_ident_today 
    ET.SubElement(resource, 'url').text = daily_data_url
    
    title_resource = ET.SubElement(resource, 'title')
    ET.SubElement(title_resource, 'polish').text = f"Ceny ofertowe mieszkań dewelopera {CONFIG['DEWELOPER_NAZWA']} {today_str}"
    ET.SubElement(title_resource, 'english').text = f"Offer prices for developer's apartments {CONFIG['DEWELOPER_NAZWA']} {today_str}"
    
    description_resource = ET.SubElement(resource, 'description')
    desc_res_text_pl = (f"Dane dotyczące cen ofertowych mieszkań dewelopera {CONFIG['DEWELOPER_NAZWA']} udostępnione {today_str} "
                        f"zgodnie z art. 19b. ust. 1 Ustawy.") # [10]
    ET.SubElement(description_resource, 'polish').text = desc_res_text_pl
    ET.SubElement(description_resource, 'english').text = desc_res_text_pl
    
    ET.SubElement(resource, 'availability').text = 'local' # Wymagane 'local' [11]
    ET.SubElement(resource, 'dataDate').text = today_str # Wymagany format RRRR-MM-DD [11]

    special_signs = ET.SubElement(resource, 'specialSigns')
    ET.SubElement(special_signs, 'specialSign').text = 'X' # Wymagany znak umowny "X" [12]
    
    ET.SubElement(resource, 'hasDynamicData').text = 'false'
    ET.SubElement(resource, 'hasHighValueData').text = 'true'
    ET.SubElement(resource, 'hasHighValueDataFromEuropeanCommissionList').text = 'false'
    ET.SubElement(resource, 'hasResearchData').text = 'false'
    ET.SubElement(resource, 'containsProtectedData').text = 'false'
    
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
    
    # top rettyxml zwraca string w kodowaniu utf-8
    pretty_xml = parsed_string.toprettyxml(indent="  ", encoding="utf-8")
    
    # Konwersja na string i usunięcie zbędnego wiersza deklaracji XML
    pretty_xml_str = pretty_xml.decode('utf-8')
    
    # ElementTree domyślnie dodaje deklarację xmlns, ale minidom jej nie dodaje do root.
    # W celu zachowania czystej struktury wynikowej, przekazujemy surowy string do minidom.
    
    # Minidom dodaje niepotrzebny nagłówek XML. Usuwamy go.
    lines = pretty_xml_str.split('\n')
    formatted_lines = [line for line in lines if line.strip() and not line.startswith('<?xml')]
    
    # Ponownie serializujemy, aby uzyskać finalny, poprawnie sformatowany XML
    return '\n'.join(formatted_lines).encode('utf-8')


def generate_xml_and_md5():
    """Główna funkcja logiki: ładuje, modyfikuje/tworzy, zapisuje XML i MD5 (akumulacja)."""
    
    xml_file_path = f"{CONFIG['XML_FILENAME']}.xml"
    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    today_str_compact = today.strftime("%Y%m%d")
    daily_data_filename = f"ceny-{CONFIG['INWESTYCJA_ID']}-{today_str}.xlsx"
    daily_data_url = CONFIG['DANE_BASE_URL'] + daily_data_filename
    
    # --- 1. Tryb Wczytywania (Akumulacja) ---
    if os.path.exists(xml_file_path):
        print(f"  Znaleziono istniejący plik: {xml_file_path}. Aktywacja trybu AKUMULACJI.")
        
        try:
            # Wczytanie istniejącego pliku za pomocą ElementTree
            tree_et = ET.parse(xml_file_path)
            root_et = tree_et.getroot()
            
            # Wyszukiwanie istniejącej sekcji <resources> z przestrzenią nazw
            resources_xpath = f".//{{{CONFIG['SCHEMA_URL']}}}resources"
            resources_element_et = root_et.find(resources_xpath)

            if resources_element_et is None:
                raise ValueError("Błąd: Nie znaleziono elementu <resources> w istniejącym pliku XML.")
            
        except Exception as e:
            print(f"Błąd podczas parsowania istniejącego pliku XML ({e}). Przechodzę do trybu tworzenia od nowa.")
            root_et = None # Wymuszamy przejście do trybu tworzenia

    # --- 2. Tryb Tworzenia od Nowa (Pierwsze uruchomienie / Błąd Parsowania) ---
    if root_et is None:
        print("  Plik XML nie istnieje lub parsowanie nie powiodło się. Tworzenie nowej struktury.")
        
        # Definicja elementu głównego: p:datasets
        root_et = ET.Element(f"{CONFIG['NAMESPACE']}:datasets", attrib={f"xmlns:{CONFIG['NAMESPACE']}": CONFIG['SCHEMA_URL']})
        
        # Tworzenie struktury <dataset> i uzyskanie referencji do <resources>
        # Uwaga: Funkcja create_dataset_structure zwraca teraz zagnieżdżone elementy
        root_et, resources_element_et = create_dataset_structure(root_et)

    # --- 3. Dodawanie Nowego Zasobu ---
    # Ta funkcja obsługuje sprawdzenie, czy zasób na dany dzień już istnieje
    create_resource_element(resources_element_et, today_str, today_str_compact, daily_data_url)

    # --- 4. Zapisywanie pliku XML ---
    
    # Generowanie finalnego XML (z przestrzeniami nazw i formatowaniem)
    final_xml_data = format_xml(root_et)
    
    with open(xml_file_path, "wb") as f:
        f.write(final_xml_data)
    print(f"  Plik XML został ZAKTUALIZOWANY i zapisany: {xml_file_path}")
    
    # --- 5. Generowanie MD5 ---
    
    md5_sum = hashlib.md5(final_xml_data).hexdigest()
    md5_file_path = f"{CONFIG['XML_FILENAME']}.md5"
    
    # Wymóg: hash musi być małymi literami [13]
    with open(md5_file_path, "w") as f:
        f.write(md5_sum)
    print(f"  Plik MD5 został ZAKTUALIZOWANY i zapisany: {md5_file_path}")


if __name__ == "__main__":
    generate_xml_and_md5()
