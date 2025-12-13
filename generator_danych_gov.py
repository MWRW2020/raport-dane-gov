from lxml import etree
from datetime import date, timedelta
import hashlib
import os
import re

# --- Konfiguracja (ZMIEŃ TE WARTOŚCI NA SWOJE) ---
DEWELOPER_NAME = "MWRW Sp. z o.o."
DEWELOPER_EXTIDENT = "9543cc89-477f-4e21-6865-2aef92679a20"
RESOURCE_BASE_URL = "https://mwrw2020.github.io/raport-dane-gov"
ACTUAL_DATA_FILENAME = "dane_wzor.xlsx"
MAX_HISTORY_DAYS = 3000
XML_FILE_NAME = "raport_cen_mieszkan.xml"
MD5_FILE_NAME = "raport_cen_mieszkan.md5"
HISTORY_FILE = "history_dates.txt" # Plik do przechowywania historii dat

# --- DEFINICJA PRZESTRZENI NAZW (OSTATECZNA POPRAWKA DLA LXML) ---
# Ustawienie klucza None w nsmap jest wymagane, aby uzyskać domyślną przestrzeń nazw (xmlns="..."),
# co jest wymagane przez walidator dane.gov.pl
NS_URI = 'urn:otwarte-dane:harvester:1.13'

# Słownik przestrzeni nazw dla lxml
NAMESPACES = {
    None: NS_URI, # KRYTYCZNA ZMIANA: Użycie klucza None
    'xsi': "http://www.w3.org/2001/XMLSchema-instance"
}

# Bieżąca data
TODAY_DATE = date.today()
TODAY_DATE_STR = TODAY_DATE.isoformat()
TODAY_DATE_ID = TODAY_DATE.strftime("%Y%m%d")
RESOURCE_EXTIDENT_TODAY = f"ZASOB_{DEWELOPER_EXTIDENT}_{TODAY_DATE_ID}"

# Definicje QName do użycia przy tworzeniu elementów w lxml
def qname(tag_name):
 """Tworzy pełną nazwę tagu z URL przestrzeni nazw."""
 return etree.QName(NS_URI, tag_name)


def create_resource_element(data_date_str):
 """Tworzy element <resource> dla konkretnej daty."""
 data_date_id = data_date_str.replace('-', '')
 resource_extident = f"ZASOB_{DEWELOPER_EXTIDENT}_{data_date_id}"

 # Używamy QNAME
 resource = etree.Element(qname('resource'), status='published')

 etree.SubElement(resource, qname('extIdent')).text = resource_extident
 etree.SubElement(resource, 'url').text = f"{RESOURCE_BASE_URL}/{ACTUAL_DATA_FILENAME}"

 res_title = etree.SubElement(resource, 'title')
 etree.SubElement(res_title, 'polish').text = f"Ceny ofertowe mieszkań dewelopera {DEWELOPER_NAME} {data_date_str}"
 etree.SubElement(res_title, 'english').text = f"Offer prices for developer's apartments {DEWELOPER_NAME} {data_date_str}"

 res_description = etree.SubElement(resource, 'description')
 res_desc_text = f"Dane dotyczące cen ofertowych mieszkań dewelopera {DEWELOPER_NAME} udostępnione {data_date_str} zgodnie z art. 19b. ust. 1 Ustawy z dnia 20 maja 2021 r. o ochronie praw nabywcy lokalu mieszkalnego lub domu jednorodzinnego oraz Deweloperskim Funduszu Gwarancyjnym (Dz. U. z 2024 r. poz. 695)."
 etree.SubElement(res_description, 'polish').text = res_desc_text
 etree.SubElement(res_description, 'english').text = res_desc_text.replace("Dane dotyczące cen ofertowych", "Data on offer prices")

 etree.SubElement(resource, 'availability').text = 'local'
 etree.SubElement(resource, qname('dataDate')).text = data_date_str

 special_signs = etree.SubElement(resource, 'specialSigns')
 etree.SubElement(special_signs, 'specialSign').text = 'X'

 etree.SubElement(resource, 'hasDynamicData').text = 'false'
 etree.SubElement(resource, 'hasHighValueData').text = 'true'
 etree.SubElement(resource, 'hasHighValueDataFromEuropeanCommissionList').text = 'false'
 etree.SubElement(resource, 'hasResearchData').text = 'false'
 etree.SubElement(resource, 'containsProtectedData').text = 'false'

 return resource

def update_history(current_history):
 """Aktualizuje plik historii, zachowując tylko MAX_HISTORY_DAYS dat."""

 # Dodanie dzisiejszej daty (jeśli jej nie ma)
 if TODAY_DATE_STR not in current_history:
  current_history.add(TODAY_DATE_STR)

 # Filtrowanie dat starszych niż MAX_HISTORY_DAYS
 cutoff_date = TODAY_DATE - timedelta(days=MAX_HISTORY_DAYS)
 new_history = set()

 for date_str in current_history:
  try:
   resource_date = date.fromisoformat(date_str)
   if resource_date >= cutoff_date:
    new_history.add(date_str)
   else:
    print(f"Usunięto stary zasób z datą {date_str} (historia > {MAX_HISTORY_DAYS} dni).")
  except ValueError:
   pass

 sorted_history = sorted(list(new_history))

 # Zapis nowej historii do pliku
 with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
  f.write('\n'.join(sorted_history) + '\n')

 return sorted_history

def load_history():
 """Wczytuje unikalne daty z pliku historii."""
 if not os.path.exists(HISTORY_FILE):
  return set()

 with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
  dates = set(f.read().splitlines())

 return {d for d in dates if d}

def generate_xml_and_md5():

 # 1. Zarządzanie historią
 history_set = load_history()
 sorted_dates = update_history(history_set)

 # 2. Tworzenie nowej struktury XML od zera (ZAWSZE)
 print(f"Tworzenie nowej struktury XML od zera na podstawie historii...")

 # Tworzenie root elementu z URI i atrybutami (lxml ma specjalny argument nsmap)
 # Dzięki NAMESPACES={None: NS_URI} otrzymujemy <datasets xmlns="urn:..." ...>
 root = etree.Element(qname('datasets'), nsmap=NAMESPACES)

 # Tworzenie <dataset>
 dataset = etree.SubElement(root, qname('dataset'), status='published')
 etree.SubElement(dataset, 'extIdent').text = DEWELOPER_EXTIDENT

 # ... (tytuły i opisy)
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

 tags = etree.SubElement(dataset, 'tags')
 etree.SubElement(tags, 'tag', lang='pl').text = 'Deweloper'

 # Dodanie