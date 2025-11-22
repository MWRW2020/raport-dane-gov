import xml.etree.ElementTree as ET
from datetime import date
import hashlib
from xml.dom import minidom # Import dla ładnego formatowania XML

# --- Konfiguracja (Zmień te wartości na własne) ---
DEWELOPER_NAME = "MWRW Sp. z o.o."
# UNIKALNY, 36-ZNAKOWY ID ZBIORU DANYCH - NIE ZMIENIAĆ PO PIERWSZEJ PUBLIKACJI!
# PRZYKŁADOWY ID - ZMIEŃ NA SWÓJ WŁASNY Z GENERATORA UUID!
DEWELOPER_EXTIDENT = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0" 
# Baza URL Twojej strony na GitHub Pages
RESOURCE_BASE_URL = "https://mwrw2020.github.io/raport-dane-gov"
# Nazwa pliku z rzeczywistymi danymi (Zgodnie z Twoim życzeniem: dane_wzor.xlsx)
ACTUAL_DATA_FILENAME = "dane_wzor.xlsx"
XML_FILE_NAME = "raport_cen_mieszkan.xml"
MD5_FILE_NAME = "raport_cen_mieszkan.md5"
# ----------------------------------------------------

# Bieżąca data
TODAY_DATE = date.today()
TODAY_DATE_STR = TODAY_DATE.isoformat() # YYYY-MM-DD
TODAY_DATE_ID = TODAY_DATE.strftime("%Y%m%d") # YYYYMMDD

# Unikalny ID zasobu (MUSI się zmieniać CODZIENNIE, aby system wiedział, że ma zaimportować nowy plik)
RESOURCE_EXTIDENT = f"ZASOB_{DEWELOPER_EXTIDENT}_{TODAY_DATE_ID}"

# URL do rzeczywistego pliku z danymi hostowanego na Twojej stronie GitHub Pages.
# Plik musi znajdować się w katalogu głównym repozytorium.
ACTUAL_DATA_URL = f"{RESOURCE_BASE_URL}/{ACTUAL_DATA_FILENAME}"

def prettify_xml(elem):
    """Dodaje wcięcia do XML."""
    xml_string = ET.tostring(elem, encoding='utf-8').decode('utf-8')
    # Użycie minidom dla formatowania
    reparsed = minidom.parseString(xml_string)
    # Zwraca sformatowany XML bez nagłówka deklaracji XML
    return '\n'.join(reparsed.toprettyxml(indent="  ").splitlines()[1:])

def generate_xml_and_md5():
    # Definicja przestrzeni nazw
    NS = {'ns2': 'urn:otwarte-dane:harvester:1.13'}
    ET.register_namespace('ns2', NS['ns2'])
    
    # Tworzenie elementu głównego
    root = ET.Element('{urn:otwarte-dane:harvester:1.13}datasets',
                      attrib={'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance"})

    # --- Element Dataset (Zbiór Danych) ---
    dataset = ET.SubElement(root, 'dataset', attrib={'status': 'published'})
    ET.SubElement(dataset, 'extIdent').text = DEWELOPER_EXTIDENT # STAŁY ID ZBIORU
    
    # Tytuły
    title = ET.SubElement(dataset, 'title')
    ET.SubElement(title, 'polish').text = f"Ceny ofertowe mieszkań dewelopera {DEWELOPER_NAME} w {TODAY_DATE.year} r."
    ET.SubElement(title, 'english').text = f"Offer prices of apartments of developer {DEWELOPER_NAME} in {TODAY_DATE.year}."
    
    # Opisy
    description = ET.SubElement(dataset, 'description')
    desc_base = "Zbiór danych zawiera informacje o cenach ofertowych mieszkań dewelopera udostępniane zgodnie z art. 19b. ust. 1 Ustawy z dnia 20 maja 2021 r. o ochronie praw nabywcy lokalu mieszkalnego lub domu jednorodzinnego oraz Deweloperskim Funduszu Gwarancyjnym (Dz. U. z 2024 r. poz. 695)."
    ET.SubElement(description, 'polish').text = desc_base
    ET.SubElement(description, 'english').text = desc_base.replace("Zbiór danych zawiera informacje", "The dataset contains information")

    # Inne wymagane metadane zbioru danych
    ET.SubElement(dataset, 'updateFrequency').text = 'daily'
    ET.SubElement(dataset, 'hasDynamicData').text = 'false'
    ET.SubElement(dataset, 'hasHighValueData').text = 'true'
    ET.SubElement(dataset, 'hasHighValueDataFromEuropeanCommissionList').text = 'false'
    ET.SubElement(dataset, 'hasResearchData').text = 'false'
    
    categories = ET.SubElement(dataset, 'categories')
    ET.SubElement(categories, 'category').text = 'ECON' # Kategoria: Gospodarka i finanse

    # --- Element Resources (Zasoby) ---
    resources = ET.SubElement(dataset, 'resources')
    
    # --- Dodanie pojedynczego zasobu z aktualnymi danymi ---
    resource = ET.SubElement(resources, 'resource', attrib={'status': 'published'})
    ET.SubElement(resource, 'extIdent').text = RESOURCE_EXTIDENT # CODZIENNIE ZMIENNY ID ZASOBU
    ET.SubElement(resource, 'url').text = ACTUAL_DATA_URL # URL do pliku dane_wzor.xlsx
    
    # Tytuły zasobu
    res_title = ET.SubElement(resource, 'title')
    ET.SubElement(res_title, 'polish').text = f"Ceny ofertowe mieszkań dewelopera {DEWELOPER_NAME} {TODAY_DATE_STR}"
    ET.SubElement(res_title, 'english').text = f"Offer prices for developer's apartments {DEWELOPER_NAME} {TODAY_DATE_STR}"

    # Opisy zasobu
    res_description = ET.SubElement(resource, 'description')
    res_desc_text = f"Dane dotyczące cen ofertowych mieszkań dewelopera {DEWELOPER_NAME} udostępnione {TODAY_DATE_STR} zgodnie z art. 19b. ust. 1 Ustawy z dnia 20 maja 2021 r. o ochronie praw nabywcy lokalu mieszkalnego lub domu jednorodzinnego oraz Deweloperskim Funduszu Gwarancyjnym (Dz. U. z 2024 r. poz. 695)."
    ET.SubElement(res_description, 'polish').text = res_desc_text
    ET.SubElement(res_description, 'english').text = res_desc_text.replace("Dane dotyczące cen ofertowych", "Data on offer prices")

    ET.SubElement(resource, 'availability').text = 'local'
    ET.SubElement(resource, 'dataDate').text = TODAY_DATE_STR # Data publikacji cennika

    # Znaki umowne
    special_signs = ET.SubElement(resource, 'specialSigns')
    ET.SubElement(special_signs, 'specialSign').text = 'X' # Znak umowny X (Wypełnienie jest niemożliwe/niecelowe)

    # Zapis pliku XML
    xml_output = '<?xml version="1.0" encoding="utf-8"?>\n' + prettify_xml(root)
    with open(XML_FILE_NAME, 'w', encoding='utf-8') as f:
        f.write(xml_output)
    
    print(f"Wygenerowano plik XML: {XML_FILE_NAME}")
    
    # --- Generowanie MD5 ---
    # Musi być obliczone na bajtach pliku XML
    with open(XML_FILE_NAME, 'rb') as f:
        data = f.read()

    md5_hash = hashlib.md5(data).hexdigest()
    
    # Zapis pliku MD5
    with open(MD5_FILE_NAME, 'w', encoding='utf-8') as f:
        f.write(md5_hash)
        
    print(f"Wygenerowano plik MD5: {MD5_FILE_NAME} z hashem: {md5_hash}")

if __name__ == "__main__":
    try:
        generate_xml_and_md5()
    except Exception as e:
        print(f"Wystąpił błąd podczas generowania plików: {e}")
