from lxml import etree
from datetime import date, timedelta
import hashlib
import os

# --- Konfiguracja ---
DEWELOPER_NAME = "MWRW Sp. z o.o."
DEWELOPER_EXTIDENT = "9543cc89-477f-4e21-6865-2aef92679a20"
RESOURCE_BASE_URL = "https://mwrw2020.github.io/raport-dane-gov"
ACTUAL_DATA_FILENAME = "dane_wzor.xlsx"
MAX_HISTORY_DAYS = 3000
XML_FILE_NAME = "raport_cen_mieszkan.xml"
MD5_FILE_NAME = "raport_cen_mieszkan.md5"
HISTORY_FILE = "history_dates.txt"

# URI przestrzeni nazw
NS_URI = 'urn:otwarte-dane:harvester:1.13'
# Słownik z prefiksem ns2 (zgodnie z wzorcem )
NAMESPACES = {
    'ns2': NS_URI,
    'xsi': "http://www.w3.org/2001/XMLSchema-instance"
}

TODAY_DATE = date.today()
TODAY_DATE_STR = TODAY_DATE.isoformat()

def create_resource_element(data_date_str):
    """Tworzy element <resource> BEZ przestrzeni nazw."""
    data_date_id = data_date_str.replace('-', '')
    resource_extident = f"ZASOB_{DEWELOPER_EXTIDENT}_{data_date_id}"

    # Tworzymy element bez namespace (brak QName)
    resource = etree.Element('resource', status='published')

    etree.SubElement(resource, 'extIdent').text = resource_extident
    etree.SubElement(resource, 'url').text = f"{RESOURCE_BASE_URL}/{ACTUAL_DATA_FILENAME}"

    res_title = etree.SubElement(resource, 'title')
    etree.SubElement(res_title, 'polish').text = f"Ceny ofertowe mieszkań dewelopera {DEWELOPER_NAME} {data_date_str}"
    etree.SubElement(res_title, 'english').text = f"Offer prices for developer's apartments {DEWELOPER_NAME} {data_date_str}"

    res_description = etree.SubElement(resource, 'description')
    res_desc_text = f"Dane dotyczące cen ofertowych mieszkań dewelopera {DEWELOPER_NAME} udostępnione {data_date_str} zgodnie z art. 19b. ust. 1 Ustawy z dnia 20 maja 2021 r. o ochronie praw nabywcy lokalu mieszkalnego lub domu jednorodzinnego oraz Deweloperskim Funduszu Gwarancyjnym (Dz. U. z 2024 r. poz. 695)."
    etree.SubElement(res_description, 'polish').text = res_desc_text
    etree.SubElement(res_description, 'english').text = res_desc_text.replace("Dane dotyczące cen ofertowych", "Data on offer prices")

    etree.SubElement(resource, 'availability').text = 'local'
    etree.SubElement(resource, 'dataDate').text = data_date_str

    special_signs = etree.SubElement(resource, 'specialSigns')
    etree.SubElement(special_signs, 'specialSign').text = 'X'

    etree.SubElement(resource, 'hasDynamicData').text = 'false'
    etree.SubElement(resource, 'hasHighValueData').text = 'true'
    etree.SubElement(resource, 'hasHighValueDataFromEuropeanCommissionList').text = 'false'
    etree.SubElement(resource, 'hasResearchData').text = 'false'
    etree.SubElement(resource, 'containsProtectedData').text = 'false'

    return resource

def update_history(current_history):
    if TODAY_DATE_STR not in current_history:
        current_history.add(TODAY_DATE_STR)
    cutoff_date = TODAY_DATE - timedelta(days=MAX_HISTORY_DAYS)
    new_history = {d for d in current_history if date.fromisoformat(d) >= cutoff_date}
    sorted_history = sorted(list(new_history))
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sorted_history) + '\n')
    return sorted_history

def load_history():
    if not os.path.exists(HISTORY_FILE): return set()
    with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
        return {d for d in f.read().splitlines() if d}

def generate_xml_and_md5():
    sorted_dates = update_history(load_history())

    # TYLKO root (datasets) ma prefiks ns2 
    root_tag = etree.QName(NS_URI, 'datasets')
    root = etree.Element(root_tag, nsmap=NAMESPACES)

    # dataset i pozostałe są BEZ namespace [cite: 4, 23, 24]
    dataset = etree.SubElement(root, 'dataset', status='published')
    etree.SubElement(dataset, 'extIdent').text = DEWELOPER_EXTIDENT

    title = etree.SubElement(dataset, 'title')
    etree.SubElement(title, 'polish').text = f"Ceny ofertowe mieszkań dewelopera {DEWELOPER_NAME} w {TODAY_DATE.year} r."
    etree.SubElement(title, 'english').text = f"Offer prices of apartments of developer {DEWELOPER_NAME} in {TODAY_DATE.year}."
    
    description = etree.SubElement(dataset, 'description')
    desc_base = "Zbiór danych zawiera informacje o cenach ofertowych mieszkań dewelopera udostępniane zgodnie z art. 19b. ust. 1 Ustawy z dnia 20 maja 2021 r. o ochronie praw nabywcy lokalu mieszkalnego lub domu jednorodzinnego oraz Deweloperskim Funduszu Gwarancyjnym (Dz. U. z 2024 r. poz. 695)."
    etree.SubElement(description, 'polish').text = desc_base
    etree.SubElement(description, 'english').text = desc_base.replace("Zbiór danych zawiera informacje", "The dataset contains information")

    etree.SubElement(dataset, 'updateFrequency').text = 'daily'
    etree.SubElement(dataset, 'hasDynamicData').text = 'false'
    etree.SubElement(dataset, 'hasHighValueData').text = 'true'
    etree.SubElement(dataset, 'hasHighValueDataFromEuropeanCommissionList').text = 'false'
    etree.SubElement(dataset, 'hasResearchData').text = 'false'

    categories = etree.SubElement(dataset, 'categories')
    etree.SubElement(categories, 'category').text = 'ECON'

    resources_container = etree.SubElement(dataset, 'resources')
    for data_date_str in sorted_dates:
        resources_container.append(create_resource_element(data_date_str))

    tags = etree.SubElement(dataset, 'tags')
    etree.SubElement(tags, 'tag', lang='pl').text = 'Deweloper'

    # Zapis
    xml_output = etree.tostring(root, pretty_print=True, xml_declaration=True, encoding='UTF-8').decode('utf-8')
    with open(XML_FILE_NAME, 'w', encoding='utf-8') as f:
        f.write(xml_output)

    with open(XML_FILE_NAME, 'rb') as f:
        md5_hash = hashlib.md5(f.read()).hexdigest()
    with open(MD5_FILE_NAME, 'w', encoding='utf-8') as f:
        f.write(md5_hash)
    
    print(f"Wygenerowano XML i MD5 ({md5_hash}).")

if __name__ == "__main__":
    generate_xml_and_md5()