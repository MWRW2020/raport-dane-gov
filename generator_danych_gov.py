import xml.etree.ElementTree as ET
from datetime import date, timedelta
import hashlib
from xml.dom import minidom
import os
import re

# --- Konfiguracja (ZMIEŃ TE WARTOŚCI NA SWOJE) ---

# 1. Nazwa dewelopera.
DEWELOPER_NAME = "MWRW Sp. z o.o."

# 2. UNIKALNY, 36-ZNAKOWY ID ZBIORU DANYCH (Dataset) - NIE ZMIENIAĆ PO PIERWSZEJ PUBLIKACJI!
DEWELOPER_EXTIDENT = "9543cc89-477f-4e21-b865-2aef92679a20" 

# 3. Baza URL Twojej strony na GitHub Pages
RESOURCE_BASE_URL = "https://mwrw2020.github.io/raport-dane-gov"

# 4. Nazwa pliku z rzeczywistymi danymi (musi istnieć w repozytorium)
ACTUAL_DATA_FILENAME = "dane_wzor.xlsx"

# 5. Ograniczenie: ile dni wstecz zasoby mają być trzymane w pliku XML
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

    # Metadane techniczne zbioru (Używamy bezpiecznej składni)
    
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
    
    # Kategoria: Gospodarka i finanse (Bezpieczna składnia)
    categories = ET.SubElement(dataset, 'categories')
    category_elem = ET.SubElement(categories, 'category')
    #category_elem.text = 'ECON'
    
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

    # Dodatkowe metadane zasobu (Używamy bezpiecznej składni)
    
    res_dynamic_data_elem = ET.SubElement(resource, 'hasDynamicData')
    res_dynamic_data_elem.text = 'false'
    
    res_high_value_data_elem = ET.SubElement(resource, 'hasHighValueData')
    res_high_value_data_elem.text = 'true'
