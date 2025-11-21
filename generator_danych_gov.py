import hashlib
import uuid
import os
from datetime import datetime
from xml.etree.ElementTree import Element, SubElement, parse, tostring
from xml.dom import minidom

# --- SEKCJA KONFIGURACYJNA ---
# Uzupełnij poniższe dane zgodnie z Twoją inwestycją.
CONFIG = {
    "DEWELOPER_NAZWA": "MWRW Sp. z o.o.",
    "INWESTYCJA_NAZWA": "Brzozowy Zakątek",
    "ROK_ZBIORU": "2025",
    "INWESTYCJA_ID": "brzozowy_zakatek_kliny",
    "INWESTYCJA_URL": "https://www.mwrw.net/kliny",
    "DANE_BASE_URL": "https://mwrw2020.github.io/raport-dane-gov/",
    "XML_FILENAME": "dane_deweloper_brzozowy",
    # Namespace jest wymagany do poprawnego odczytu i zapisu XML
    "SCHEMA_URL": "https://www.dane.gov.pl/static/xml/otwarte_dane_latest.xsd",
    "NAMESPACE": "p"
}
# -----------------------------

def create_dataset_structure(root):
    """Tworzy podstawową strukturę <dataset> dla pierwszego uruchomienia."""
    dataset = SubElement(root, f"{CONFIG['NAMESPACE']}:dataset", status='draft')
    # Status zbioru danych powinien być docelowo "published" [10, 11].
    # Zostawiamy "draft" na czas testów, ale powinien być zmieniony na "published" przed zgłoszeniem [10, 12].
    
    SubElement(dataset, 'extIdent').text = f"dataset_{CONFIG['INWESTYCJA_ID']}"
    title_dataset = SubElement(dataset, 'title')
    SubElement(title_dataset, 'polish').text = f"Ceny ofertowe mieszkań dewelopera {CONFIG['DEWELOPER_NAZWA']} w {CONFIG['ROK_ZBIORU']} r." [13]
    SubElement(title_dataset, 'english').text = f"Offer prices of apartments of developer {CONFIG['DEWELOPER_NAZWA']} in {CONFIG['ROK_ZBIORU']}." [13]
    description_dataset = SubElement(dataset, 'description')
    desc_text_pl = (f"Zbiór danych zawiera informacje o cenach ofertowych mieszkań dewelopera {CONFIG['DEWELOPER_NAZWA']} "
                    f"udostępniane zgodnie z art. 19b. ust. 1 Ustawy z dnia 20 maja 2021 r. o ochronie praw nabywcy lokalu "
                    f"mieszkalnego lub domu jednorodzinnego oraz Deweloperskim Funduszu Gwarancyjnym (Dz. U. z 2024 r. poz. 695).") [14]
    SubElement(description_dataset, 'polish').text = desc_text_pl
    SubElement(description_dataset, 'english').text = desc_text_pl # W oryginalnym XML jest ten sam tekst w PL i ENG [14]
    SubElement(dataset, 'url').text = CONFIG['INWESTYCJA_URL'] [15]
    SubElement(dataset, 'categories').text = 'ECON' [15, 16]
    tags = SubElement(dataset, 'tags')
    SubElement(tags, 'tag').text = 'deweloper' [15]
    SubElement(dataset, 'updateFrequency').text = 'daily' [15, 17] # Częstotliwość aktualizacji: codziennie [18]
    SubElement(dataset, 'hasDynamicData').text = 'false' [15, 17]
    SubElement(dataset, 'hasHighValueData').text = 'true' [15, 17]
    SubElement(dataset, 'hasHighValueDataFromEuropeanCommissionList').text = 'false' [15, 19]
    SubElement(dataset, 'hasResearchData').text = 'false' [15, 19]
    
    resources = SubElement(dataset, 'resources') [15, 16]
    # Zwracamy listę zasobów, do której będziemy dodawać nowe wpisy
    return resources

def create_resource_element(resources, today_str, today_str_compact, daily_data_url):
    """Tworzy i dodaje nowy element <resource> (dzienny raport) do listy zasobów."""
    
    # Tworzymy nowy zasób [20]
    resource = SubElement(resources, 'resource', status='draft')
    # Status zasobu powinien być docelowo "published" [12].
    
    # Unikalny identyfikator zewnętrzny zawierający datę [4, 21, 22]
    ext_ident = f"resource_{CONFIG['INWESTYCJA_ID']}_{today_str_compact}"
    SubElement(resource, 'extIdent').text = ext_ident 
    
    # URL do pliku z danymi na dany dzień [22]
    SubElement(resource, 'url').text = daily_data_url
    
    title_resource = SubElement(resource, 'title')
    SubElement(title_resource, 'polish').text = f"Ceny ofertowe mieszkań dewelopera {CONFIG['DEWELOPER_NAZWA']} {today_str}" [23]
    SubElement(title_resource, 'english').text = f"Offer prices for developer's apartments {CONFIG['DEWELOPER_NAZWA']} {today_str}" [23]
    
    description_resource = SubElement(resource, 'description')
    desc_res_text_pl = (f"Dane dotyczące cen ofertowych mieszkań dewelopera {CONFIG['DEWELOPER_NAZWA']} udostępnione {today_str} "
                        f"zgodnie z art. 19b. ust. 1 Ustawy.") [24]
    SubElement(description_resource, 'polish').text = desc_res_text_pl
    SubElement(description_resource, 'english').text = desc_res_text_pl # W oryginalnym XML jest ten sam tekst w PL i ENG [25]
    
    # Dostępność: local, ponieważ plik jest w repozytorium [26]
    SubElement(resource, 'availability').text = 'local' 
    
    # Data, której dotyczą dane [26]
    SubElement(resource, 'dataDate').text = today_str 

    # Znaki umowne, muszą zawierać 'X' [27]
    special_signs = SubElement(resource, 'specialSigns')
    SubElement(special_signs, 'specialSign').text = 'X' 
    
    # Pozostałe wymagane metadane zasobu [28, 29]
    SubElement(resource, 'hasDynamicData').text = 'false'
    SubElement(resource, 'hasHighValueData').text = 'true'
    SubElement(resource, 'hasHighValueDataFromEuropeanCommissionList').text = 'false'
    SubElement(resource, 'hasResearchData').text = 'false'
    SubElement(resource, 'containsProtectedData').text = 'false'


def generate_xml_and_md5():
    """Główna funkcja logiki: ładuje, modyfikuje/tworzy, zapisuje XML i MD5."""
    
    xml_file_path = f"{CONFIG['XML_FILENAME']}.xml"
    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    today_str_compact = today.strftime("%Y%m%d")
    daily_data_filename = f"ceny-{CONFIG['INWESTYCJA_ID']}-{today_str}.xlsx"
    daily_data_url = CONFIG['DANE_BASE_URL'] + daily_data_filename
    
    # Sprawdzenie, czy plik XML już istnieje
    if os.path.exists(xml_file_path):
        print(f"  Znaleziono istniejący plik: {xml_file_path}. Aktywacja trybu AKUMULACJI.")
        
        # Wczytanie istniejącego pliku z obsługą przestrzeni nazw
        try:
            tree = parse(xml_file_path)
            root = tree.getroot()
            
            # Wyszukiwanie istniejącej sekcji <resources>
            # Trzeba użyć pełnej ścieżki i przestrzeni nazw (p)
            namespace = {CONFIG['NAMESPACE']: CONFIG['SCHEMA_URL']}
            resources_element = root.find(f".//{{{CONFIG['SCHEMA_URL']}}}resources", namespace)
            
            if resources_element is None:
                raise ValueError("Błąd: Nie znaleziono elementu <resources> w istniejącym pliku XML.")
                
        except Exception as e:
            print(f"Błąd podczas parsowania istniejącego pliku XML: {e}")
            return # Przerwanie działania
    else:
        print("  Plik XML nie istnieje. Tworzenie nowej struktury (pierwsze uruchomienie).")
        
        # Definicja elementu głównego z przestrzeniami nazw (dla pierwszego uruchomienia)
        root = Element(
            f"{CONFIG['NAMESPACE']}:datasets",
            attrib={'xmlns:' + CONFIG['NAMESPACE']: CONFIG['SCHEMA_URL']}
        )
        # Tworzenie struktury <dataset> i uzyskanie referencji do <resources>
        resources_element = create_dataset_structure(root)
    
    # Sprawdzenie, czy zasób dla dzisiejszej daty już istnieje
    # System musi dodawać nowy, unikalny wpis każdego dnia, aby spełnić wymóg "raz na dobę" [4, 7, 21].
    ext_ident_today = f"resource_{CONFIG['INWESTYCJA_ID']}_{today_str_compact}"
    
    # Używamy findall do sprawdzenia, czy zasób o tym extIdent już istnieje
    existing_resource = resources_element.findall(f".//extIdent[.='{ext_ident_today}']", namespace) if 'namespace' in locals() else []
    
    if existing_resource:
        # Ten warunek może wystąpić, jeśli skrypt jest uruchomiony więcej niż raz tego samego dnia
        print(f"  Zasób dla daty {today_str} (extIdent: {ext_ident_today}) już istnieje w pliku. Nie dodano nowego wpisu.")
    else:
        # Dodanie nowego elementu <resource>
        create_resource_element(resources_element, today_str, today_str_compact, daily_data_url)
        print(f"  Dodano nowy zasób dla daty: {today_str}.")

    # --- Zapisywanie pliku XML ---
    
    # 1. Serializacja do stringu z utf-8
    xml_string_raw = tostring(root, 'utf-8')
    
    # 2. Parsowanie i pretty-print (formatowanie) przy użyciu minidom
    parsed_string = minidom.parseString(xml_string_raw)
    pretty_xml = parsed_string.toprettyxml(indent="  ", encoding="utf-8")
    
    # Zapisanie sformatowanego pliku XML
    with open(xml_file_path, "wb") as f:
        f.write(pretty_xml)
    print(f"  Plik XML został ZAKTUALIZOWANY i zapisany: {xml_file_path}")
    
    # --- Generowanie MD5 ---
    
    # Sumę kontrolną liczymy z gotowego, sformatowanego XML [30, 31]
    md5_sum = hashlib.md5(pretty_xml).hexdigest()
    md5_file_path = f"{CONFIG['XML_FILENAME']}.md5"
    
    # Suma kontrolna musi być małymi literami [32]
    with open(md5_file_path, "w") as f:
        f.write(md5_sum)
    print(f"  Plik MD5 został ZAKTUALIZOWANY i zapisany: {md5_file_path}")


if __name__ == "__main__":
    generate_xml_and_md5()
