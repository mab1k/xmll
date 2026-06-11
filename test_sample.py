"""Генерация conclusion.xml с полным набором тестовых данных."""
import glob
import os
import shutil
import xml.etree.ElementTree as ET
import zlib
from xml.dom import minidom

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def prettify(elem):
    rough_string = ET.tostring(elem, encoding='utf-8', method='xml')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


def write_conclusion_xml(conclusion, output_path="conclusion.xml"):
    xml_pretty_str = prettify(conclusion)
    full_xml_str = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<?xml-stylesheet type="text/xsl" href="conclusion-01-03.xsl" ?>\n'
    ) + xml_pretty_str
    lines = full_xml_str.splitlines()
    del lines[2]
    with open(output_path, "w", encoding="utf-8") as f:
        f.write('\n'.join(lines))


def compute_file_checksum(file_path, uppercase=False):
    with open(file_path, "rb") as f:
        value = f"{zlib.crc32(f.read()) & 0xFFFFFFFF:08x}"
        return value.upper() if uppercase else value


def get_file_metadata(file_path, checksum_upper=False):
    file_name = os.path.basename(file_path)
    return {
        "file_path": file_path,
        "file_name": file_name,
        "file_format": os.path.splitext(file_name)[1].lstrip(".").lower(),
        "file_checksum": compute_file_checksum(file_path, uppercase=checksum_upper),
    }


def resolve_path(filename):
    return os.path.join(SCRIPT_DIR, filename)


def find_sign_file():
    matches = glob.glob(os.path.join(SCRIPT_DIR, "*.sig"))
    if not matches:
        raise FileNotFoundError("Не найден файл .sig в папке проекта")
    return matches[0]


def append_documents(conclusion, documents, output_dir):
    documents_elem = ET.SubElement(conclusion, 'Documents')
    for doc in documents:
        document = ET.SubElement(documents_elem, 'Document')
        ET.SubElement(document, 'DocType').text = doc["doc_type"]
        ET.SubElement(document, 'DocName').text = doc["doc_name"]
        if doc.get("doc_number"):
            ET.SubElement(document, 'DocNumber').text = doc["doc_number"]
        ET.SubElement(document, 'DocDate').text = doc["doc_date"]
        if doc.get("doc_author"):
            ET.SubElement(document, 'DocIssueAuthor').text = doc["doc_author"]
        if doc.get("doc_changes"):
            ET.SubElement(document, 'DocChanges').text = doc["doc_changes"]

        file_meta = get_file_metadata(doc["file_path"])
        file_elem = ET.SubElement(document, 'File')
        ET.SubElement(file_elem, 'FileName').text = file_meta["file_name"]
        ET.SubElement(file_elem, 'FileFormat').text = file_meta["file_format"]
        ET.SubElement(file_elem, 'FileChecksum').text = file_meta["file_checksum"]

        dest_path = os.path.join(output_dir, file_meta["file_name"])
        if os.path.abspath(doc["file_path"]) != os.path.abspath(dest_path):
            shutil.copy2(doc["file_path"], dest_path)

        for sign_path in doc.get("sign_files", []):
            sign_meta = get_file_metadata(sign_path, checksum_upper=True)
            sign_elem = ET.SubElement(file_elem, 'SignFile')
            ET.SubElement(sign_elem, 'FileName').text = sign_meta["file_name"]
            ET.SubElement(sign_elem, 'FileFormat').text = sign_meta["file_format"]
            ET.SubElement(sign_elem, 'FileChecksum').text = sign_meta["file_checksum"]

            dest_sign_path = os.path.join(output_dir, sign_meta["file_name"])
            if os.path.abspath(sign_path) != os.path.abspath(dest_sign_path):
                shutil.copy2(sign_path, dest_sign_path)


def append_address_xml(parent_elem, address_data):
    address = ET.SubElement(parent_elem, 'Address')
    for key, tag in [
        ("country", "Country"),
        ("region", "Region"),
        ("district", "District"),
        ("city", "City"),
        ("settlement", "Settlement"),
        ("street", "Street"),
        ("building", "Building"),
        ("room", "Room"),
        ("note", "Note"),
    ]:
        value = address_data.get(key, "")
        if value:
            ET.SubElement(address, tag).text = value


def append_addresses_xml(parent_elem, addresses):
    for address_data in addresses:
        append_address_xml(parent_elem, address_data)


def append_capital_object(conclusion, data):
    obj = ET.SubElement(conclusion, 'Object')
    ET.SubElement(obj, 'Name').text = data["name"]
    append_addresses_xml(obj, data["addresses"])
    if data.get("type"):
        ET.SubElement(obj, 'Type').text = data["type"]
    if data.get("functions_class"):
        ET.SubElement(obj, 'FunctionsClass').text = data["functions_class"]
    for tei in data["tei"]:
        tei_elem = ET.SubElement(obj, 'TEI')
        ET.SubElement(tei_elem, 'Name').text = tei["name"]
        ET.SubElement(tei_elem, 'Measure').text = tei["measure"]
        ET.SubElement(tei_elem, 'Value').text = tei["value"]
    for part in data.get("parts", []):
        part_elem = ET.SubElement(obj, 'ObjectPart')
        ET.SubElement(part_elem, 'Name').text = part["name"]
        append_addresses_xml(part_elem, part["addresses"])
        if part.get("functions_class"):
            ET.SubElement(part_elem, 'FunctionsClass').text = part["functions_class"]
        for tei in part["tei"]:
            tei_elem = ET.SubElement(part_elem, 'TEI')
            ET.SubElement(tei_elem, 'Name').text = tei["name"]
            ET.SubElement(tei_elem, 'Measure').text = tei["measure"]
            ET.SubElement(tei_elem, 'Value').text = tei["value"]


def build_sample_capital_object():
    address_base = {
        "country": "123",
        "district": "123",
        "city": "123",
        "settlement": "123",
        "street": "123",
        "building": "123",
    }
    tei_main = {"name": "1231", "measure": "123", "value": "123"}
    tei_part = {"name": "123", "measure": "123", "value": "123"}
    return {
        "name": "123",
        "addresses": [
            {**address_base, "region": "01", "room": "3223", "note": "23"},
            {**address_base, "region": "02", "room": "123", "note": "123"},
        ],
        "type": "1",
        "functions_class": "12.32.323.1",
        "tei": [tei_main],
        "parts": [{
            "name": "123",
            "addresses": [
                {
                    "country": "323",
                    "region": "09",
                    "district": "23",
                    "city": "23",
                    "settlement": "23",
                    "building": "23",
                    "room": "123",
                    "note": "43",
                },
                {**address_base, "region": "07", "room": "123", "note": "123"},
            ],
            "functions_class": "12.31.232.32",
            "tei": [tei_part],
        }],
    }


def append_previous_simple_conclusions(conclusion, items):
    if not items:
        return
    previous_simple = ET.SubElement(conclusion, 'PreviousSimpleConclusions')
    for item in items:
        elem = ET.SubElement(previous_simple, 'PreviousSimpleConclusion')
        ET.SubElement(elem, 'Date').text = item["date"]
        ET.SubElement(elem, 'Number').text = item["number"]
        ET.SubElement(elem, 'ExaminationObjectType').text = item["object_type"]
        ET.SubElement(elem, 'Result').text = item["result"]


def build_sample_documents():
    sign_file = find_sign_file()
    return [
        {
            "doc_type": "02.99",
            "doc_name": "123",
            "doc_number": "123",
            "doc_date": "3222-02-23",
            "doc_author": "2323",
            "doc_changes": "313",
            "file_path": resolve_path("2.pdf"),
        },
        {
            "doc_type": "02.07",
            "doc_name": "123",
            "doc_number": "123",
            "doc_date": "2004-09-21",
            "doc_author": "ппп",
            "doc_changes": "123",
            "file_path": resolve_path("1774366449_3.pdf"),
            "sign_files": [sign_file],
        },
    ]


def build_sample_conclusion():
    conclusion = ET.Element('Conclusion', {
        'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        'xsi:noNamespaceSchemaLocation': 'conclusion-01-03.xsd',
        'ConclusionGUID': '7745F3C8-AAA9-9FC7-42B5-93E8D2EDF425',
        'SchemaVersion': '01.03',
    })

    expert_organization = ET.SubElement(conclusion, 'ExpertOrganization')
    ET.SubElement(expert_organization, 'OrgFullName').text = 'Полное'
    ET.SubElement(expert_organization, 'OrgOGRN').text = '1234567890102'
    ET.SubElement(expert_organization, 'OrgINN').text = '1234567890'
    ET.SubElement(expert_organization, 'OrgKPP').text = '123456789'
    address = ET.SubElement(expert_organization, 'Address')
    ET.SubElement(address, 'Country').text = 'Россия'
    ET.SubElement(address, 'Region').text = '52'
    ET.SubElement(address, 'City').text = 'Подольск'
    ET.SubElement(address, 'Street').text = 'Подольская'
    ET.SubElement(address, 'Building').text = '12'
    ET.SubElement(address, 'Room').text = '1'

    approver = ET.SubElement(conclusion, 'Approver')
    ET.SubElement(approver, 'FamilyName').text = 'Пахалков'
    ET.SubElement(approver, 'FirstName').text = 'Иван'
    ET.SubElement(approver, 'SecondName').text = 'Викторович'
    ET.SubElement(approver, 'Position').text = 'Студент'

    examination_object = ET.SubElement(conclusion, 'ExaminationObject')
    ET.SubElement(examination_object, 'ExaminationForm').text = '1'
    ET.SubElement(examination_object, 'ExaminationResult').text = '1'
    ET.SubElement(examination_object, 'ExaminationObjectType').text = '2'
    ET.SubElement(examination_object, 'ExaminationType').text = '1'
    ET.SubElement(examination_object, 'ConstructionType').text = '1'
    ET.SubElement(examination_object, 'ExaminationStage').text = '1'
    ET.SubElement(examination_object, 'Name').text = 'Стройка'
    ET.SubElement(examination_object, 'ProjectDocumentationIM').text = 'да'
    ET.SubElement(examination_object, 'EngineeringSurveysIM').text = 'да'

    documents = build_sample_documents()
    append_documents(conclusion, documents, SCRIPT_DIR)

    previous_conclusions = ET.SubElement(conclusion, 'PreviousConclusions')
    prev_elem = ET.SubElement(previous_conclusions, 'PreviousConclusion')
    ET.SubElement(prev_elem, 'Date').text = '2025-02-21'
    number_elem = ET.SubElement(prev_elem, 'Number')
    ET.SubElement(number_elem, 'noEGRZ').text = '123123'
    ET.SubElement(prev_elem, 'ExaminationObjectType').text = '1'
    ET.SubElement(prev_elem, 'Name').text = '123'
    ET.SubElement(prev_elem, 'Result').text = '1'

    append_previous_simple_conclusions(conclusion, [{
        'date': '2002-02-21',
        'number': '123',
        'object_type': '1',
        'result': '1',
    }])

    append_capital_object(conclusion, build_sample_capital_object())

    ecology = ET.SubElement(conclusion, 'EcologyExpertise')
    ET.SubElement(ecology, 'NeedExpertise').text = 'да'
    ET.SubElement(ecology, 'Comment').text = 'ппп'
    ET.SubElement(conclusion, 'CadastralNumber').text = '77:01:0002401:107'

    declarant = ET.SubElement(conclusion, 'Declarant')
    organization = ET.SubElement(declarant, 'Organization')
    ET.SubElement(organization, 'OrgFullName').text = '232'
    ET.SubElement(organization, 'OrgOGRN').text = '2322432543245'
    ET.SubElement(organization, 'OrgINN').text = '1243124235'
    ET.SubElement(organization, 'OrgKPP').text = '124124235'
    address = ET.SubElement(organization, 'Address')
    ET.SubElement(address, 'Country').text = 'dtrhb'
    ET.SubElement(address, 'Region').text = '03'
    ET.SubElement(address, 'District').text = 'erh'
    ET.SubElement(address, 'City').text = 'erth'
    ET.SubElement(address, 'Settlement').text = 'tyht'
    ET.SubElement(address, 'Street').text = 'yj'
    ET.SubElement(address, 'Building').text = 'yjy'
    ET.SubElement(address, 'Room').text = 'y'
    ET.SubElement(address, 'Note').text = 'yj'
    ET.SubElement(organization, 'Email').text = 'piv0004@yandex.ru'

    finance = ET.SubElement(conclusion, 'Finance')
    ET.SubElement(finance, 'FinanceType').text = '1'
    ET.SubElement(finance, 'BudgetType').text = '1'
    ET.SubElement(finance, 'FinanceSize').text = '123'
    finance_owner = ET.SubElement(finance, 'FinanceOwner')
    owner_org = ET.SubElement(finance_owner, 'Organization')
    ET.SubElement(owner_org, 'OrgFullName').text = '323'
    ET.SubElement(owner_org, 'OrgOGRN').text = '2321231231212'
    ET.SubElement(owner_org, 'OrgINN').text = '3123123123'
    ET.SubElement(owner_org, 'OrgKPP').text = '123123123'
    owner_address = ET.SubElement(owner_org, 'Address')
    ET.SubElement(owner_address, 'Country').text = '123'
    ET.SubElement(owner_address, 'Region').text = '50'
    ET.SubElement(owner_address, 'District').text = '123'
    ET.SubElement(owner_address, 'City').text = '432'
    ET.SubElement(owner_address, 'Street').text = '5435'
    ET.SubElement(owner_address, 'Building').text = '3'
    ET.SubElement(owner_address, 'Room').text = '436'
    ET.SubElement(owner_address, 'Note').text = '34634'
    ET.SubElement(owner_org, 'Email').text = 'piv0004@yandex.ru'

    estimated_cost = ET.SubElement(conclusion, 'EstimatedCost')
    ET.SubElement(estimated_cost, 'Currency').text = 'рубли'
    complex_before = ET.SubElement(estimated_cost, 'EstimatedComplexCostBefore')
    for tag, value in {
        'CostBasic': '123.',
        'WorksCostBasic': '124.',
        'HardwareCostBasic': '2354.',
        'OtherCostBasic': '345.',
        'ProjectWorksCostBasic': '456.',
        'BackSumCostBasic': '8678.',
        'Cost': '567.',
        'WorksCost': '678.',
        'HardwareCost': '789.',
        'OtherCost': '679.',
        'ProjectWorksCost': '78.',
        'NDSCost': '789.',
        'BackSumCost': '789.',
        'CostBasicComment': 'пп',
        'CostComment': 'пп',
    }.items():
        ET.SubElement(complex_before, tag).text = value
    complex_post = ET.SubElement(estimated_cost, 'EstimatedComplexCostPost')
    for tag, value in {
        'CostBasic': '789.',
        'WorksCostBasic': '789.',
        'HardwareCostBasic': '789.',
        'OtherCostBasic': '898.',
        'ProjectWorksCostBasic': '789.',
        'BackSumCostBasic': '8797.',
        'Cost': '89798.',
        'WorksCost': '9879.',
        'HardwareCost': '789.',
        'OtherCost': '78.',
        'ProjectWorksCost': '7897.',
        'NDSCost': '79879.',
        'BackSumCost': '9789.',
        'CostBasicComment': 'пп',
        'CostComment': 'пп',
    }.items():
        ET.SubElement(complex_post, tag).text = value

    climate = ET.SubElement(conclusion, 'ClimateConditions')
    ET.SubElement(climate, 'ClimateDistrict').text = 'II'
    ET.SubElement(climate, 'GeologicalConditions').text = 'II'
    ET.SubElement(climate, 'WindDistrict').text = 'III'
    ET.SubElement(climate, 'SnowDistrict').text = 'IV'
    ET.SubElement(climate, 'SeismicActivity').text = '7'

    designer = ET.SubElement(conclusion, 'Designer', General='да')
    designer_org = ET.SubElement(designer, 'Organization')
    ET.SubElement(designer_org, 'OrgFullName').text = 'ООО Проект'
    ET.SubElement(designer_org, 'OrgOGRN').text = '1234567890123'
    ET.SubElement(designer_org, 'OrgINN').text = '1234567890'
    ET.SubElement(designer_org, 'OrgKPP').text = '123456789'
    designer_address = ET.SubElement(designer_org, 'Address')
    ET.SubElement(designer_address, 'Region').text = '77'
    ET.SubElement(designer_address, 'City').text = 'Москва'
    ET.SubElement(designer_address, 'Street').text = 'Ленина'
    ET.SubElement(designer_address, 'Building').text = '1'

    return conclusion, documents


def main():
    conclusion, documents = build_sample_conclusion()
    write_conclusion_xml(conclusion, os.path.join(SCRIPT_DIR, 'conclusion.xml'))

    xml_text = prettify(conclusion)
    assert '<Documents>' in xml_text
    assert '<DocType>02.99</DocType>' in xml_text
    assert '<DocType>02.07</DocType>' in xml_text
    assert '<SignFile>' in xml_text
    assert '<FileChecksum>51525733</FileChecksum>' in xml_text
    assert '<FileChecksum>F7520FA6</FileChecksum>' in xml_text
    assert '<PreviousSimpleConclusions>' in xml_text
    assert '<noEGRZ>123123</noEGRZ>' in xml_text
    assert '<Object>' in xml_text
    assert '<FunctionsClass>12.32.323.1</FunctionsClass>' in xml_text
    assert '<ObjectPart>' in xml_text
    assert '<FunctionsClass>12.31.232.32</FunctionsClass>' in xml_text
    object_section = xml_text.split('<Object>')[1].split('</Object>')[0]
    assert object_section.count('<Address>') == 4
    assert '<Region>01</Region>' in xml_text
    assert '<Region>02</Region>' in xml_text
    assert '<Region>09</Region>' in xml_text
    assert '<Region>07</Region>' in xml_text
    assert '<EcologyExpertise>' in xml_text
    assert '<NeedExpertise>да</NeedExpertise>' in xml_text
    assert '<CadastralNumber>77:01:0002401:107</CadastralNumber>' in xml_text
    assert '<Declarant>' in xml_text
    assert '<Organization>' in xml_text
    assert '<OrgFullName>232</OrgFullName>' in xml_text
    assert '<Email>piv0004@yandex.ru</Email>' in xml_text
    assert '<Finance>' in xml_text
    assert '<FinanceType>1</FinanceType>' in xml_text
    assert '<BudgetType>1</BudgetType>' in xml_text
    assert '<FinanceSize>123</FinanceSize>' in xml_text
    assert '<FinanceOwner>' in xml_text
    assert '<OrgFullName>323</OrgFullName>' in xml_text
    assert '<EstimatedCost>' in xml_text
    assert '<Currency>рубли</Currency>' in xml_text
    assert '<EstimatedComplexCostBefore>' in xml_text
    assert '<EstimatedComplexCostPost>' in xml_text
    assert '<CostBasic>123.</CostBasic>' in xml_text
    assert '<BackSumCost>9789.</BackSumCost>' in xml_text
    assert '<CostComment>пп</CostComment>' in xml_text
    assert '<ClimateConditions>' in xml_text
    assert '<ClimateDistrict>II</ClimateDistrict>' in xml_text
    assert '<SeismicActivity>7</SeismicActivity>' in xml_text
    assert '<Designer General="да">' in xml_text
    assert '<OrgFullName>ООО Проект</OrgFullName>' in xml_text
    assert os.path.isfile(documents[0]["file_path"])
    assert os.path.isfile(documents[1]["file_path"])
    print('ok — conclusion.xml создан (Documents + Object)')


if __name__ == '__main__':
    main()
