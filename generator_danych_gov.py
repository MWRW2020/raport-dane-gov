import xml.etree.ElementTree as ET
from datetime import date, timedelta
import hashlib
from xml.dom import minidom
import os
import re

# --- Konfiguracja (ZMIEŃ TE WARTOŚCI NA SWOJE) ---
# Ważne: Wprowadź tutaj swoje wartości!
DEWELOPER_NAME = "MWRW Sp. z o.o."
DEWELOPER_EXTIDENT = "9543cc89-477f-4e21-b865-2aef92679a20" 
RESOURCE_BASE_URL = "https://mwrw2020.github.io/raport-dane-gov"
ACTUAL_DATA_FILENAME = "dane_wzor.xlsx"
MAX_HISTORY_DAYS = 3000
XML_FILE_NAME = "raport_cen_mieszkan.xml"
MD5_FILE_NAME = "raport_cen_mieszkan.md5"
NS = {'ns2': 'urn:otwarte-dane:harvester:1.13'}
# ----------------------------------------------------

# Bieżąca data
TODAY_DATE = date.today()
TODAY_DATE_STR = TODAY_DATE.isoformat() 
TODAY_DATE_ID = TODAY_DATE.strftime("%Y%m%d")
RESOURCE_EXTIDENT_TODAY = f"ZASOB_{DEWELOPER_EXTIDENT}_{TODAY_DATE_ID}"

def prettify_xml(elem):
    """Dodaje wcięcia do XML przy użyciu minidom."""
    ET.register_namespace('ns2', NS['ns2'])
    xml_string = ET.tostring(elem, encoding='utf-8').decode('utf-8')
    reparsed = minidom.parseString(xml_string)
    return reparsed.toprettyxml(indent="  ")

def create_base_dataset():
    """Tworzy bazowy element <dataset> i stałe metadane."""
    dataset = ET.Element(f"{{{NS['ns2']}}}dataset", attrib={'status': 'published'})
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

    # Metadane techniczne zbioru (Bezpieczna składnia)
    update_freq_elem = ET.SubElement(dataset, 'updateFrequency')
    update_freq_elem.text = 'daily'
    
    dynamic_data_elem = ET.SubElement(dataset, 'hasDynamicData')
    dynamic_data_elem.text = 'false'
    
    high_value_data_elem = ET.SubElement(dataset, 'hasHighValueData')
    high_value_data_elem.text = 'true'
    
    high_value_ec_elem = ET.SubElement(dataset, 'hasHighValueDataFromEuropeanCommissionList')
    high_value_ec_elem.text = 'false'
    
    research_data_elem = ET.SubElement(dataset, 'hasResearchData')
    research_data_elem.text = 'false'
    
    # Kategoria: Gospodarka i finanse (BEZPIECZNA SKŁADNIA)
    categories = ET.SubElement(dataset, 'categories')
    category_elem = ET.SubElement(categories, 'category')
    category_elem.text = 'ECON' 
    
    # Dodanie sekcji TAGS
    tags = ET.SubElement(dataset, 'tags')
    ET.SubElement(tags, 'tag', attrib={'lang': 'pl'}).text = 'Deweloper'

    # Dodaj pusty węzeł <resources>
    ET.SubElement(dataset, 'resources')
    
    return dataset

def create_resource_element(data_date_str):
    """Tworzy element <resource> dla konkretnej daty."""
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
    ET.SubElement(resource, 'dataDate').text = data_date_str 

    # Znaki umowne
    special_signs = ET.SubElement(resource, 'specialSigns')
    ET.SubElement(special_signs, 'specialSign').text = 'X' 

    # Dodatkowe metadane zasobu (Bezpieczna składnia)
    res_dynamic_data_elem = ET.SubElement(resource, 'hasDynamicData')
    res_dynamic_data_elem.text = 'false'
    
    res_high_value_data_elem = ET.SubElement(resource, 'hasHighValueData')
    res_high_value_data_elem.text = 'true'
    
    res_high_value_ec_elem = ET.SubElement(resource, 'hasHighValueDataFromEuropeanCommissionList')
    res_high_value_ec_elem.text = 'false'
    
    res_research_data_elem = ET.SubElement(resource, 'hasResearchData')
    res_research_data_elem.text = 'false'
    
    res_protected_data_elem = ET.SubElement(resource, 'containsProtectedData')
    res_protected_data_elem.text = 'false'
    
    return resource

def generate_xml_and_md5():
    
    # Wyszukiwanie tagów z poprawną przestrzenią nazw
    dataset_tag = f"{{{NS['ns2']}}}dataset"
    resources_tag = f"{{{NS['ns2']}}}resources"
    resource_tag = f"{{{NS['ns2']}}}resource"
    extident_tag = f"{{{NS['ns2']}}}extIdent"
    data_date_tag = f"{{{NS['ns2']}}}dataDate"

    # 1. Ładowanie istniejącego XML lub tworzenie nowego
    if os.path.exists(XML_FILE_NAME):
        print(f"Znaleziono istniejący plik {XML_FILE_NAME}. Aktualizacja...")
        try:
            for prefix, uri in NS.items():
                ET.register_namespace(prefix, uri)
                
            tree = ET.parse(XML_FILE_NAME)
            root = tree.getroot()
            
            dataset = root.find(dataset_tag)
            resources_container = dataset.find(resources_tag)

            if dataset is None or resources_container is None:
                # W przypadku problemów, tworzymy nowy dataset z istniejącego roota (jeśli to możliwe)
                if dataset is None:
                    dataset = create_base_dataset()
                    root.append(dataset)
                    resources_container = dataset.find(resources_tag)
                elif resources_container is None:
                    resources_container = ET.SubElement(dataset, resources_tag.split('}')[-1])
                
                print("Przywrócono brakujące elementy XML.")

        except Exception as e:
            print(f"Błąd podczas parsowania XML ({e}). Tworzenie nowej struktury.")
            root = ET.Element(f"{{{NS['ns2']}}}datasets",
                              attrib={'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance"})
            dataset = create_base_dataset()
            root.append(dataset)
            resources_container = dataset.find(resources_tag)

    else:
        print(f"Nie znaleziono pliku {XML_FILE_NAME}. Tworzenie od podstaw.")
        root = ET.Element(f"{{{NS['ns2']}}}datasets",
                          attrib={'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance"})
        dataset = create_base_dataset()
        root.append(dataset)
        resources_container = dataset.find(resources_tag)

    # 2. Usuwanie istniejącego zasobu dla dzisiejszej daty (zapobieganie duplikatom)
    for res in resources_container.findall(resource_tag):
        ext_ident_elem = res.find(extident_tag)
        if ext_ident_elem is not None and ext_ident_elem.text == RESOURCE_EXTIDENT_TODAY:
            resources_container.remove(res)
            print(f"Zasób dla dnia {TODAY_DATE_STR} został zastąpiony.")
            break
            
    # 3. Dodawanie nowego zasobu (aktualne dane)
    new_resource = create_resource_element(TODAY_DATE_STR)
    resources_container.append(new_resource)
    print(f"Dodano nowy zasób dla dnia {TODAY_DATE_STR}.")
    
    # 4. Implementacja rolling window (usuwanie starych zasobów)
    cutoff_date = TODAY_DATE - timedelta(days=MAX_HISTORY_DAYS)
    resources_to_remove = []

    for res in resources_container.findall(resource_tag):
        resource_date = None
        data_date_elem = res.find(data_date_tag)
        
        # Próba odczytu daty
        if data_date_elem is not None and data_date_elem.text:
            try:
                resource_date = date.fromisoformat(data_date_elem.text)
            except ValueError:
                pass 

        # Jeśli data jest starsza niż limit, oznacz do usunięcia
        if resource_date is not None and resource_date < cutoff_date:
            resources_to_remove.append(res)

    for res in resources_to_remove:
        resources_container.remove(res)
        date_text = res.find(data_date_tag).text if res.find(data_date_tag) is not None else 'Nieznana'
        print(f"Usunięto stary zasób (historia > {MAX_HISTORY_DAYS} dni) z datą {date_text}.")
    
    # 5. Zapis pliku XML
    xml_output = prettify_xml(root)
    with open(XML_FILE_NAME, 'w', encoding='utf-8') as f:
        f.write(xml_output)
    
    print(f"\nGenerowanie zakończone. Liczba zasobów w pliku XML: {len(resources_container.findall(resource_tag))}")
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
        generate_xml_and_md5()
    except Exception as e:
        print(f"Wystąpił krytyczny błąd podczas generowania plików: {e}")
