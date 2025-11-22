import xml.etree.ElementTree as ET
from datetime import date, timedelta
import hashlib
from xml.dom import minidom
import os
import re

# --- Konfiguracja (Zmień te wartości na własne) ---

# 1. Nazwa dewelopera, która będzie wyświetlana w tytułach i opisach.
DEWELOPER_NAME = "MWRW Sp. z o.o."

# 2. UNIKALNY, 36-ZNAKOWY ID ZBIORU DANYCH (Dataset) - NIE ZMIENIAĆ!
# MUSISZ wygenerować własny UUID (np. na stronie internetowej) i wkleić go tutaj.
DEWELOPER_EXTIDENT = "9543cc89-477f-4e21-b865-2aef92679a20" 

# 3. Baza URL Twojej strony na GitHub Pages
RESOURCE_BASE_URL = "https://mwrw2020.github.io/raport-dane-gov"

# 4. Nazwa pliku z rzeczywistymi danymi (musi istnieć w repozytorium)
ACTUAL_DATA_FILENAME = "dane_wzor.xlsx"

# 5. Ograniczenie: ile dni wstecz zasoby mają być trzymane w pliku XML.
# 30 dni to bezpieczna, standardowa wartość.
MAX_HISTORY_DAYS = 3000 

# Nazwy generowanych plików wyjściowych
XML_FILE_NAME = "raport_cen_mieszkan.xml"
MD5_FILE_NAME = "raport_cen_mieszkan.md5"

# Przestrzenie nazw
NS = {'ns2': 'urn:otwarte-dane:harvester:1.13'}
# ----------------------------------------------------

# Bieżąca data
TODAY_DATE = date.today()
TODAY_DATE_STR = TODAY_DATE.isoformat() 
TODAY_DATE_ID = TODAY_DATE.strftime("%Y%m%d")

# Unikalny ID zasobu (Resource) dla dzisiejszego dnia
RESOURCE_EXTIDENT_TODAY = f"ZASOB_{DEWELOPER_EXTIDENT}_{TODAY_DATE_ID}"

def prettify_xml(elem):
    """Dodaje wcięcia do XML przy użyciu minidom."""
    ET.register_namespace('ns2', NS['ns2'])
    xml_string = ET.tostring(elem, encoding='utf-8').decode('utf-8')
    reparsed = minidom.parseString(xml_string)
    # Zwraca sformatowany XML z nagłówkiem deklaracji XML
    return reparsed.toprettyxml(indent="  ")

def create_base_dataset():
    """Tworzy bazowy element <dataset> dla nowego pliku XML."""
    dataset = ET.Element('{urn:otwarte-dane:harvester:1.13}dataset', attrib={'status': 'published'})
    ET.SubElement(dataset, 'extIdent').text = DEWELOPER_EXTIDENT
    
    # Tytuły
    title = ET.SubElement(dataset, 'title')
    ET.SubElement(title, 'polish').text = f"Ceny ofertowe mieszkań dewelopera {DEWELOPER_NAME} w {TODAY_DATE.year} r."
    ET.SubElement(title, 'english').text = f"Offer prices of apartments of developer {DEWELOPER_NAME} in {TODAY_DATE.year}."
    
    # Opisy
    description = ET.SubElement(dataset, 'description')
    desc_base = "Zbiór danych zawiera informacje o cenach ofertowych mieszkań dewelopera udostępniane zgodnie z art. 19b. ust. 1 Ustawy z dnia 20 maja 2021 r. o ochronie praw nabywcy lokalu mieszkalnego lub domu jednorodzinnego oraz Deweloperskim Funduszu Gwarancyjnym (Dz. U. z 2024 r. poz. 695)."
    ET.SubElement(description, 'polish').text = desc_base
    ET.SubElement(description, 'english').text = desc_base.replace("Zbiór danych zawiera informacje", "The dataset contains information")

    # Metadane techniczne zbioru
    ET.SubElement(dataset, 'updateFrequency').text = 'daily'
    ET.SubElement(dataset, 'hasDynamicData').text = 'false'
    ET.SubElement(dataset, 'hasHighValueData').text = 'true'
    ET.SubElement(dataset, 'hasHighValueDataFromEuropeanCommissionList').text = 'false'
    ET.SubElement(dataset, 'hasResearchData').text = 'false'
    
    categories = ET.SubElement(dataset, 'categories')
    ET.SubElement(categories, 'category').text = 'ECON'
    
    # Dodaj pusty węzeł <resources> (będzie wypełniony zasobami)
    ET.SubElement(dataset, 'resources')
    
    return dataset

def create_resource_element(data_date_str):
    """Tworzy element <resource> dla konkretnej daty."""
    # Data w formacie YYYYMMDD dla extIdent
    data_date_id = data_date_str.replace('-', '')
    resource_extident = f"ZASOB_{DEWELOPER_EXTIDENT}_{data_date_id}"
    
    resource = ET.Element('resource', attrib={'status': 'published'})
    ET.SubElement(resource, 'extIdent').text = resource_extident 
    ET.SubElement(resource, 'url').text = f"{RESOURCE_BASE_URL}/{ACTUAL_DATA_FILENAME}" 
    
    # Tytuły zasobu
    res_title = ET.SubElement(resource, 'title')
    ET.SubElement(res_title, 'polish').text = f"Ceny ofertowe mieszkań dewelopera {DEWELOPER_NAME} {data_date_str}"
    ET.SubElement(res_title, 'english').text = f"Offer prices for developer's apartments {DEWELOPER_NAME} {data_date_str}"

    # Opisy zasobu
    res_description = ET.SubElement(resource, 'description')
    res_desc_text = f"Dane dotyczące cen ofertowych mieszkań dewelopera {DEWELOPER_NAME} udostępnione {data_date_str} zgodnie z art. 19b. ust. 1 Ustawy z dnia 20 maja 2021 r. o ochronie praw nabywcy lokalu mieszkalnego lub domu jednorodzinnego oraz Deweloperskim Funduszu Gwarancyjnym (Dz. U. z 2024 r. poz. 695)."
    ET.SubElement(res_description, 'polish').text = res_desc_text
    ET.SubElement(res_description, 'english').text = res_desc_text.replace("Dane dotyczące cen ofertowych", "Data on offer prices")

    ET.SubElement(resource, 'availability').text = 'local'
    ET.SubElement(resource, 'dataDate').text = data_date_str # Data publikacji cennika

    # Znaki umowne
    special_signs = ET.SubElement(resource, 'specialSigns')
    ET.SubElement(special_signs, 'specialSign').text = 'X' 

    # Dodatkowe metadane (zgodnie z załączonym przykładem)
    ET.SubElement(resource, 'hasDynamicData').text = 'false'
    ET.SubElement(resource, 'hasHighValueData').text = 'true'
    ET.SubElement(resource, 'hasHighValueDataFromEuropeanCommissionList').text = 'false'
    ET.SubElement(resource, 'hasResearchData').text = 'false'
    ET.SubElement(resource, 'containsProtectedData').text = 'false'
    
    return resource

def generate_xml_and_md5():
    
    # 1. Ładowanie istniejącego XML lub tworzenie nowego
    if os.path.exists(XML_FILE_NAME):
        print(f"Znaleziono istniejący plik {XML_FILE_NAME}. Aktualizacja...")
        try:
            # Parsowanie pliku, z zachowaniem przestrzeni nazw
            tree = ET.parse(XML_FILE_NAME)
            root = tree.getroot()
            # Zakładamy, że w pliku jest jeden element <dataset>
            dataset = root.find('dataset', namespaces=NS)
            if dataset is None:
                raise ValueError("Nie znaleziono elementu <dataset>.")
            
            resources_container = dataset.find('resources', namespaces=NS)
            if resources_container is None:
                raise ValueError("Nie znaleziono elementu <resources>.")

        except Exception as e:
            print(f"Błąd podczas parsowania XML ({e}). Tworzenie nowego pliku.")
            # Jeśli parsowanie się nie uda, stwórz nowy bazowy XML
            root = ET.Element(f"{{{NS['ns2']}}}datasets",
                              attrib={'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance"})
            dataset = create_base_dataset()
            root.append(dataset)
            resources_container = dataset.find('resources', namespaces=NS)
    
    else:
        print(f"Nie znaleziono pliku {XML_FILE_NAME}. Tworzenie od podstaw.")
        # Tworzenie nowego XML
        root = ET.Element(f"{{{NS['ns2']}}}datasets",
                          attrib={'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance"})
        dataset = create_base_dataset()
        root.append(dataset)
        resources_container = dataset.find('resources', namespaces=NS)


    # 2. Usuwanie istniejącego zasobu dla dzisiejszej daty (jeśli istnieje)
    # Zapewnia to, że ponowne uruchomienie workflow w tym samym dniu nie stworzy duplikatu.
    today_resource_exists = False
    for res in resources_container.findall('resource', namespaces=NS):
        ext_ident_elem = res.find('extIdent', namespaces=NS)
        if ext_ident_elem is not None and ext_ident_elem.text == RESOURCE_EXTIDENT_TODAY:
            resources_container.remove(res)
            today_resource_exists = True
            break
            
    if today_resource_exists:
        print(f"Zasób dla dnia {TODAY_DATE_STR} został zastąpiony.")

    # 3. Dodawanie nowego zasobu (aktualne dane)
    new_resource = create_resource_element(TODAY_DATE_STR)
    resources_container.append(new_resource)
    print(f"Dodano nowy zasób dla dnia {TODAY_DATE_STR}.")
    
    # 4. Implementacja rolling window (usuwanie starych zasobów)
    cutoff_date = TODAY_DATE - timedelta(days=MAX_HISTORY_DAYS)
    resources_to_remove = []
    
    for res in resources_container.findall('resource', namespaces=NS):
        data_date_elem = res.find('dataDate', namespaces=NS)
        
        # Wyodrębnienie daty z extIdent, jeśli dataDate jest puste
        if data_date_elem is None or not data_date_elem.text:
            ext_ident_elem = res.find('extIdent', namespaces=NS)
            if ext_ident_elem is not None:
                # Szukamy daty YYYYMMDD na końcu extIdent
                match = re.search(r'(\d{8})$', ext_ident_elem.text)
                if match:
                    try:
                        resource_date = date(int(match.group(1)[:4]), int(match.group(1)[4:6]), int(match.group(1)[6:8]))
                    except:
                        continue # Nie udało się sparsować daty, zostawiamy zasób
                else:
                    continue
            else:
                continue
        else:
            try:
                resource_date = date.fromisoformat(data_date_elem.text)
            except ValueError:
                continue # Niepoprawny format daty, zostawiamy zasób

        # Sprawdzenie, czy zasób jest starszy niż limit
        if resource_date < cutoff_date:
            resources_to_remove.append(res)

    for res in resources_to_remove:
        resources_container.remove(res)
        print(f"Usunięto stary zasób z datą {res.find('dataDate', namespaces=NS).text if res.find('dataDate', namespaces=NS) is not None else 'Nieznana'}.")
    
    # 5. Zapis pliku XML
    xml_output = prettify_xml(root)
    with open(XML_FILE_NAME, 'w', encoding='utf-8') as f:
        f.write(xml_output)
    
    print(f"\nGenerowanie zakończone. Liczba zasobów w pliku XML: {len(resources_container.findall('resource', namespaces=NS))}")
    print(f"Wygenerowano plik XML: {XML_FILE_NAME}")
    
    # 6. Generowanie MD5
    with open(XML_FILE_NAME, 'rb') as f:
        data = f.read()

    md5_hash = hashlib.md5(data).hexdigest()
    
    with open(MD5_FILE_NAME, 'w', encoding='utf-8') as f:
        f.write(md5_hash)
        
    print(f"Wygenerowano plik MD5: {MD5_FILE_NAME} z hashem: {md5_hash}")

if __name__ == "__main__":
    try:
        # Rejestracja przestrzeni nazw, aby były poprawnie widoczne w outputcie
        ET.register_namespace('ns2', NS['ns2'])
        generate_xml_and_md5()
    except Exception as e:
        print(f"Wystąpił błąd podczas generowania plików: {e}")
