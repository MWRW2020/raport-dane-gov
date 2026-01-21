import datetime
import xml.etree.ElementTree as ET

def generate_xml():
    # 1. Definicja adresów URI - bez żadnych zbędnych spacji
    NS_URI = "urn:otwarte-dane:harvester:1.13"
    XSI_URI = "http://www.w3.org/2001/XMLSchema-instance"

    # 2. Tworzenie elementu głównego
    root = ET.Element("ns2:datasets", {
        "xmlns:ns2": NS_URI,
        "xmlns:xsi": XSI_URI,
        "xsi:schemaLocation": f"{NS_URI} harvester-1.13.xsd"
    })

    # 3. Element dataset (BEZ PREFIKSU ns2)
    dataset = ET.SubElement(root, "dataset", {"status": "published"})

    ET.SubElement(dataset, "extIdent").text = "9543cc89-477f-4e21-6865-2aef92679a20"

    title = ET.SubElement(dataset, "title")
    ET.SubElement(title, "polish").text = "Ceny ofertowe mieszkań dewelopera MWRW Sp. z o.o. w 2026 r."
    ET.SubElement(title, "english").text = "Offer prices of apartments of developer MWRW Sp. z o.o. in 2026."

    desc = ET.SubElement(dataset, "description")
    desc_txt = ("Zbiór danych zawiera informacje o cenach ofertowych mieszkań dewelopera "
                "udostępniane zgodnie z art. 19b. ust. 1 Ustawy z dnia 20 maja 2021 r. "
                "o ochronie praw nabywcy lokalu mieszkalnego lub domu jednorodzinnego "
                "oraz Deweloperskim Funduszu Gwarancyjnym (Dz. U. z 2024 r. poz. 695).")
    ET.SubElement(desc, "polish").text = desc_txt
    ET.SubElement(desc, "english").text = desc_txt

    ET.SubElement(dataset, "updateFrequency").text = "daily"
    ET.SubElement(dataset, "hasDynamicData").text = "false"
    ET.SubElement(dataset, "hasHighValueData").text = "true"
    ET.SubElement(dataset, "hasHighValueDataFromEuropeanCommissionList").text = "false"
    ET.SubElement(dataset, "hasResearchData").text = "false"

    categories = ET.SubElement(dataset, "categories")
    ET.SubElement(categories, "category").text = "ECON"

    resources = ET.SubElement(dataset, "resources")

    # 4. Generowanie zasobów (do dzisiaj)
    start_date = datetime.date(2026, 1, 1)
    end_date = datetime.date.today()
    current_date = start_date

    while current_date <= end_date:
        date_iso = current_date.strftime("%Y-%m-%d")
        date_compact = current_date.strftime("%Y%m%d")

        resource = ET.SubElement(resources, "resource", {"status": "published"})
        ET.SubElement(resource, "extIdent").text = f"ZASOB_9543cc89-477f-4e21-6865-2aef92679a20_{date_compact}"
        ET.SubElement(resource, "url").text = "https://mwrw2020.github.io/raport-dane-gov/dane_wzor.xlsx"

        r_title = ET.SubElement(resource, "title")
        ET.SubElement(r_title, "polish").text = f"Ceny ofertowe mieszkań dewelopera MWRW Sp. z o.o. {date_iso}"
        ET.SubElement(r_title, "english").text = f"Offer prices for developer's apartments MWRW Sp. z o.o. {date_iso}"

        r_desc = ET.SubElement(resource, "description")
        r_desc_txt = f"Dane dotyczące cen ofertowych mieszkań dewelopera MWRW Sp. z o.o. udostępnione {date_iso}"
        ET.SubElement(r_desc, "polish").text = r_desc_txt
        ET.SubElement(r_desc, "english").text = r_desc_txt

        ET.SubElement(resource, "availability").text = "local"
        ET.SubElement(resource, "dataDate").text = date_iso

        signs = ET.SubElement(resource, "specialSigns")
        ET.SubElement(signs, "specialSign").text = "X"

        ET.SubElement(resource, "hasDynamicData").text = "false"
        ET.SubElement(resource, "hasHighValueData").text = "true"
        ET.SubElement(resource, "hasHighValueDataFromEuropeanCommissionList").text = "false"
        ET.SubElement(resource, "hasResearchData").text = "false"
        ET.SubElement(resource, "containsProtectedData").text = "false"

        current_date += datetime.timedelta(days=1)

    # 5. Konwersja i czyszczenie końcowe
    xml_content = ET.tostring(root, encoding="utf-8").decode("utf-8")

    # PRECYZYJNA NAPRAWA BŁĘDÓW WIDOCZNYCH W RAPORCIE 15:29:
    replacements = {
        "urn:otwarte-dane: harvester": "urn:otwarte-dane:harvester",
        "From European": "FromEuropean",
        "Commission List": "CommissionList",
        "Protected Data": "ProtectedData",
        "European Commission": "EuropeanCommission",
        "2aef92679a20 20260121": "2aef92679a20_20260121" # Naprawa dzisiejszego ID
    }

    for old, new in replacements.items():
        xml_content = xml_content.replace(old, new)

    header = '<?xml version="1.0" encoding="UTF-8"?>\n'
    with open("raport_cen_mieszkan.xml", "w", encoding="utf-8") as f:
        f.write(header + xml_content)