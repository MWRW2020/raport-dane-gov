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
    """
    Tworzy podstawową strukturę <dataset> dla pierwszego uruchomienia.
    UWAGA: Zawiera poprawkę błędu TypeError w sekcji <categories>.
    """
    
    # Zgodnie z wytycznymi, status powinien być "draft" na czas testów/integracji
    # (docelowo "published" [4-6])
    dataset = SubElement(root, 'dataset', status='draft') 
    
    SubElement(dataset, 'extIdent').text = f"dataset_{CONFIG['INWESTYCJA_ID']}"
    
    title_dataset = SubElement(dataset, 'title')
    SubElement(title_dataset, 'polish').text = f"Ceny ofertowe mieszkań dewelopera {CONFIG['DEWELOPER_NAZWA']} w {CONFIG['ROK_ZBIORU']} r." [7]
    SubElement(title_dataset, 'english').text = f"Offer prices of apartments of developer {CONFIG['DEWELOPER_NAZWA']} in {CONFIG['ROK_ZBIORU']}." [7]
    
    description_dataset = SubElement(dataset, 'description')
    desc_text_pl = (f"Zbiór danych zawiera informacje o cenach ofertowych mieszkań dewelopera {CONFIG['DEWELOPER_NAZWA']} "
                    f"udostępniane zgodnie z art. 19b. ust. 1 Ustawy z dnia 20 maja 2021 r. o ochronie praw nabywcy lokalu "
                    f"mieszkalnego lub domu jednorodzinnego oraz Deweloperskim Funduszu Gwarancyjnym (Dz. U. z 2024 r. poz. 695).") [8, 9]
    SubElement(description_dataset, 'polish').text = desc_text_pl
    SubElement(description_dataset, 'english').text = desc_text_pl # W metadanych używamy tego samego opisu [8, 10]
    
    SubElement(dataset, 'url').text = CONFIG['INWESTYCJA_URL'] [2]
    
    # KOREKTA BŁĘDU: <categories> musi zawierać zagnieżdżony element <category> z wartością 'ECON' [11, 12].
    categories = SubElement(dataset, 'categories')
    SubElement(categories, 'category').text = 'ECON'
    
    tags = SubElement(dataset, 'tags')
    SubElement(tags, 'tag').text = 'deweloper' [2]
    
    SubElement(dataset, 'updateFrequency').text = 'daily' [11, 13]
    SubElement(dataset, 'hasDynamicData').text = 'false' [11, 13]
    SubElement(dataset, 'hasHighValueData').text = 'true' [11, 13]
    SubElement(dataset, 'hasHighValueDataFromEuropeanCommissionList').text = 'false' [11, 14]
    SubElement(dataset, 'hasResearchData').text = 'false' [11, 14]
    
    # Utworzenie listy zasobów
    resources = SubElement(dataset, 'resources') [12]
    
    # Zwracamy listę zasobów, do której będziemy dodawać nowe wpisy
    return resources

def create_resource_element(resources, today_str, today_str_compact, daily_data_url):
    """Tworzy i dodaje nowy element <resource> (dzienny raport) do listy zasobów."""
    
    # Używamy statusu "draft" na czas testów [2, 15]
    resource = SubElement(resources, 'resource', status='draft')
    
    # Unikalny identyfikator zewnętrzny zawierający datę jest kluczowy dla akumulacji [16, 17]
    ext_ident = f"resource_{CONFIG['INWESTYCJA_ID']}_{today_str_compact}"
    SubElement(resource, 'extIdent').text = ext_ident 
    
    # URL do pliku z danymi na dany dzień [17, 18]
    SubElement(resource, 'url').text = daily_data_url
    
    title_resource = SubElement(resource, 'title')
    SubElement(title_resource, 'polish').text = f"Ceny ofertowe mieszkań dewelopera {CONFIG['DEWELOPER_NAZWA']} {today_str}" [19]
    SubElement(title_resource, 'english').text = f"Offer prices for developer's apartments {CONFIG['DEWELOPER_NAZWA']} {today_str}" [19]
    
    description_resource = SubElement(resource, 'description')
    desc_res_text_pl = (f"Dane dotyczące cen ofertowych mieszkań dewelopera {CONFIG['DEWELOPER_NAZWA']} udostępnione {today_str} "
                        f"zgodnie z art. 19b. ust. 1 Ustawy.") [19]
    SubElement(description_resource, 'polish').text = desc_res_text_pl
    SubElement(description_resource, 'english').text = desc_res_text_pl 
    
    # Dostępność: local, ponieważ plik jest w repozytorium [20]
    SubElement(resource, 'availability').text = 'local' 
    
    # Data, której dotyczą dane [21]
    SubElement(resource, 'dataDate').text = today_str 

    # Znaki umowne, muszą zawierać 'X' (Iks) [22]
    special_signs = SubElement(resource, 'specialSigns')
    SubElement(special_signs, 'specialSign').text = 'X' [22]
    
    # Pozostałe wymagane metadane zasobu [23, 24]
    SubElement(resource, 'hasDynamicData').text = 'false'
    SubElement(resource, 'hasHighValueData').text = 'true'
    SubElement(resource, 'hasHighValueDataFromEuropeanCommissionList').text = 'false'
    SubElement(resource, 'hasResearchData').text = 'false'
    SubElement(resource, 'containsProtectedData').text = 'false'


def generate_xml_and_md5():
    """Główna funkcja logiki: ładuje, modyfikuje/tworzy, zapisuje XML i MD5 (akumulacja)."""
    
    xml_file_path = f"{CONFIG['XML_FILENAME']}.xml"
    today = datetime.now()
    today_str = today.strftime("%Y-%m-%d")
    today_str_compact = today.strftime("%Y%m%d")
    daily_data_filename = f"ceny-{CONFIG['INWESTYCJA_ID']}-{today_str}.xlsx"
    daily_data_url = CONFIG['DANE_BASE_URL'] + daily_data_filename
    
    namespace = {CONFIG['NAMESPACE']: CONFIG['SCHEMA_URL']}
    
    # --- Tryb Wczytywania (Akumulacja) ---
    if os.path.exists(xml_file_path):
        # Sprawdzenie, czy plik XML już istnieje (tryb akumulacji)
        print(f"  Znaleziono istniejący plik: {xml_file_path}. Aktywacja trybu AKUMULACJI.") [25, 26]
        
        try:
            # Wczytanie istniejącego pliku z obsługą przestrzeni nazw
            tree = minidom.parse(xml_file_path) # Używamy minidom do parsowania
            root = tree.documentElement
            
            # Wyszukiwanie istniejącej sekcji <resources>
            resources_element = root.getElementsByTagNameNS(CONFIG['SCHEMA_URL'], 'resources')
            
        except Exception as e:
            print(f"Błąd podczas parsowania istniejącego pliku XML: {e}")
            # W przypadku błędu parsowania, przechodzimy do trybu tworzenia od nowa, aby uniknąć kolejnych awarii
            os.remove(xml_file_path)
            # Wymuszamy przejście do trybu tworzenia (Tryb Tworzenia od Nowa)
            # Powtórne wywołanie funkcji create_dataset_structure
            root = Element(f"{CONFIG['NAMESPACE']}:datasets", attrib={'xmlns:' + CONFIG['NAMESPACE']: CONFIG['SCHEMA_URL']})
            resources_element = create_dataset_structure(root)
            print("  Wykryto błąd parsowania. Plik usunięty i utworzona nowa struktura od podstaw.")
            
    # --- Tryb Tworzenia od Nowa (Pierwsze uruchomienie) ---
    else:
        print("  Plik XML nie istnieje. Tworzenie nowej struktury (pierwsze uruchomienie).") [25, 26]
        
        # Definicja elementu głównego z przestrzeniami nazw
        root = Element(
            f"{CONFIG['NAMESPACE']}:datasets",
            attrib={'xmlns:' + CONFIG['NAMESPACE']: CONFIG['SCHEMA_URL']}
        )
        # Tworzenie struktury <dataset> i uzyskanie referencji do <resources>
        resources_element = create_dataset_structure(root)
    
    # --- Dodawanie Nowego Zasobu ---
    
    # Sprawdzenie, czy zasób dla dzisiejszej daty już istnieje
    ext_ident_today = f"resource_{CONFIG['INWESTYCJA_ID']}_{today_str_compact}"
    
    # Wyszukujemy wszystkie elementy <extIdent> w sekcji <resources>
    # Ze względu na mieszane użycie xml.etree i minidom, to jest uproszczona weryfikacja:
    existing_idents = [elem.firstChild.nodeValue for elem in resources_element.getElementsByTagName('extIdent')]
    
    if ext_ident_today in existing_idents:
        # Ten warunek może wystąpić, jeśli skrypt jest uruchomiony więcej niż raz tego samego dnia
        print(f"  Zasób dla daty {today_str} (extIdent: {ext_ident_today}) już istnieje w pliku. Nie dodano nowego wpisu.")
    else:
        # Dodanie nowego elementu <resource>
        # Uwaga: Musimy go stworzyć za pomocą ElementTree, a następnie zaimportować do struktury minidom/dom
        new_resource_root = Element('resource', status='draft')
        
        # Tworzymy tymczasowy element <resources> używając ElementTree
        temp_resources = Element('resources')
        create_resource_element(temp_resources, today_str, today_str_compact, daily_data_url)
        
        # Konwertujemy ElementTree na string i następnie na element DOM/minidom
        new_resource_string = tostring(temp_resources, 'utf-8').decode('utf-8')
        
        # Ponieważ potrzebujemy tylko zawartości <resource>, musimy wyodrębnić tylko ten fragment,
        # ale ze względu na ograniczenia użyjemy prostszego podejścia:
        # Przetwarzamy XML ręcznie za pomocą minidom
        
        # Ręczne tworzenie elementu <resource> w przestrzeni minidom
        resource_node = tree.createElement('resource') if os.path.exists(xml_file_path) else minidom.Document().createElement('resource')
        resource_node.setAttribute('status', 'draft')

        # To jest uproszczona i bezpieczna droga: zamiast skomplikowanego parsowania wstecz, po prostu dołączamy
        # Nowy element do DOM.
        
        # Wracamy do logiki ElementTree, bo jest łatwiejsza w obsłudze SubElement
        
        # Dodanie nowego zasobu za pomocą funkcji create_resource_element
        new_resource_element = Element('resources')
        create_resource_element(new_resource_element, today_str, today_str_compact, daily_data_url)
        
        # Ze względu na problem mieszania ElementTree i minidom, konieczne jest skorygowanie ścieżki:
        # Prawidłowy kod powinien wyglądać tak (wykorzystując wyłącznie ElementTree):

        if os.path.exists(xml_file_path):
             # Tryb akumulacyjny: Wczytujemy XML za pomocą ElementTree, modyfikujemy go i zapisujemy
             from xml.etree import ElementTree as ET
             ET.register_namespace(CONFIG['NAMESPACE'], CONFIG['SCHEMA_URL'])

             tree_et = ET.parse(xml_file_path)
             root_et = tree_et.getroot()
             
             # Wyszukujemy resources
             resources_xpath = f".//{{{CONFIG['SCHEMA_URL']}}}resources"
             resources_element_et = root_et.find(resources_xpath)

             # Tworzymy nowy element resource
             new_resource = ET.SubElement(resources_element_et, 'resource', status='draft')
             
             # Wypełnianie nowego zasobu
             SubElement(new_resource, 'extIdent').text = ext_ident_today
             SubElement(new_resource, 'url').text = daily_data_url
             
             title_resource = SubElement(new_resource, 'title')
             SubElement(title_resource, 'polish').text = f"Ceny ofertowe mieszkań dewelopera {CONFIG['DEWELOPER_NAZWA']} {today_str}"
             SubElement(title_resource, 'english').text = f"Offer prices for developer's apartments {CONFIG['DEWELOPER_NAZWA']} {today_str}"
             
             description_resource = SubElement(new_resource, 'description')
             desc_res_text_pl = (f"Dane dotyczące cen ofertowych mieszkań dewelopera {CONFIG['DEWELOPER_NAZWA']} udostępnione {today_str} "
                                 f"zgodnie z art. 19b. ust. 1 Ustawy.")
             SubElement(description_resource, 'polish').text = desc_res_text_pl
             SubElement(description_resource, 'english').text = desc_res_text_pl
             
             SubElement(new_resource, 'availability').text = 'local'
             SubElement(new_resource, 'dataDate').text = today_str
             
             special_signs = SubElement(new_resource, 'specialSigns')
             SubElement(special_signs, 'specialSign').text = 'X'
             
             SubElement(new_resource, 'hasDynamicData').text = 'false'
             SubElement(new_resource, 'hasHighValueData').text = 'true'
             SubElement(new_resource, 'hasHighValueDataFromEuropeanCommissionList').text = 'false'
             SubElement(new_resource, 'hasResearchData').text = 'false'
             SubElement(new_resource, 'containsProtectedData').text = 'false'
             
             # Serializacja do stringu z utf-8
             xml_string_raw = ET.tostring(root_et, 'utf-8', method='xml')
             
             print(f"  Dodano nowy zasób dla daty: {today_str}.")
             
        else:
             # Tryb tworzenia od nowa: Używamy pierwotnej logiki
             # W tym bloku nie zachodzi problem parsowania, wystarczy wywołać pierwotną logikę
             # Tworzymy element główny i struktury za pomocą ElementTree:
             root_et = Element(f"{CONFIG['NAMESPACE']}:datasets", attrib={'xmlns:' + CONFIG['NAMESPACE']: CONFIG['SCHEMA_URL']})
             resources_element_et = create_dataset_structure(root_et)
             
             # Tworzymy pierwszy zasób
             create_resource_element_et(resources_element_et, today_str, today_str_compact, daily_data_url)
             
             xml_string_raw = ET.tostring(root_et, 'utf-8', method='xml')
             print(f"  Utworzono pierwszy zasób dla daty: {today_str}.")


    # --- Zapisywanie pliku XML ---
    
    # 1. Parsowanie i pretty-print (formatowanie) przy użyciu minidom
    # Używamy minidom do formatowania
    try:
        parsed_string = minidom.parseString(xml_string_raw)
        pretty_xml = parsed_string.toprettyxml(indent="  ", encoding="utf-8")
    except Exception as e:
        print(f"Błąd podczas formatowania XML za pomocą minidom: {e}")
        # W przypadku błędu formatowania, zapisujemy surowy string
        pretty_xml = xml_string_raw
    
    # Zapisanie sformatowanego pliku XML
    with open(xml_file_path, "wb") as f:
        f.write(pretty_xml)
    print(f"  Plik XML został ZAKTUALIZOWANY i zapisany: {xml_file_path}")
    
    # --- Generowanie MD5 ---
    
    # Sumę kontrolną liczymy z gotowego, sformatowanego XML
    md5_sum = hashlib.md5(pretty_xml).hexdigest() [27-29]
    md5_file_path = f"{CONFIG['XML_FILENAME']}.md5"
    
    # Suma kontrolna musi być małymi literami [29, 30]
    with open(md5_file_path, "w") as f:
        f.write(md5_sum)
    print(f"  Plik MD5 został ZAKTUALIZOWANY i zapisany: {md5_file_path}")


# Funkcja pomocnicza do tworzenia zasobów (gdy używamy ElementTree)
def create_resource_element_et(resources, today_str, today_str_compact, daily_data_url):
    from xml.etree import ElementTree as ET
    resource = ET.SubElement(resources, 'resource', status='draft')
    ext_ident = f"resource_{CONFIG['INWESTYCJA_ID']}_{today_str_compact}"
    ET.SubElement(resource, 'extIdent').text = ext_ident 
    ET.SubElement(resource, 'url').text = daily_data_url
    title_resource = ET.SubElement(resource, 'title')
    ET.SubElement(title_resource, 'polish').text = f"Ceny ofertowe mieszkań dewelopera {CONFIG['DEWELOPER_NAZWA']} {today_str}"
    ET.SubElement(title_resource, 'english').text = f"Offer prices for developer's apartments {CONFIG['DEWELOPER_NAZWA']} {today_str}"
    description_resource = ET.SubElement(resource, 'description')
    desc_res_text_pl = (f"Dane dotyczące cen ofertowych mieszkań dewelopera {CONFIG['DEWELOPER_NAZWA']} udostępnione {today_str} "
                        f"zgodnie z art. 19b. ust. 1 Ustawy.")
    ET.SubElement(description_resource, 'polish').text = desc_res_text_pl
    ET.SubElement(description_resource, 'english').text = desc_res_text_pl
    ET.SubElement(resource, 'availability').text = 'local'
    ET.SubElement(resource, 'dataDate').text = today_str
    special_signs = ET.SubElement(resource, 'specialSigns')
    ET.SubElement(special_signs, 'specialSign').text = 'X'
    ET.SubElement(resource, 'hasDynamicData').text = 'false'
    ET.SubElement(resource, 'hasHighValueData').text = 'true'
    ET.SubElement(resource, 'hasHighValueDataFromEuropeanCommissionList').text = 'false'
    ET.SubElement(resource, 'hasResearchData').text = 'false'
    ET.SubElement(resource, 'containsProtectedData').text = 'false'


if __name__ == "__main__":
    generate_xml_and_md5()
