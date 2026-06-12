"""Генерация conclusion.xml на основе реального образца ЕГРЗ."""
import glob
import os
import shutil
import xml.etree.ElementTree as ET
import zlib
from xml.dom import minidom

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REAL_SAMPLE_PATH = os.path.join(SCRIPT_DIR, '00019-26_056-0185626_conclusion.xml')


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


def resolve_path(filename):
    return os.path.join(SCRIPT_DIR, filename)


def find_sign_file():
    matches = glob.glob(os.path.join(SCRIPT_DIR, "*.sig"))
    if not matches:
        raise FileNotFoundError("Не найден файл .sig в папке проекта")
    return matches[0]


def load_real_sample_conclusion():
    if not os.path.isfile(REAL_SAMPLE_PATH):
        raise FileNotFoundError(f"Не найден образец: {REAL_SAMPLE_PATH}")
    return ET.parse(REAL_SAMPLE_PATH).getroot()


def remap_document_files(conclusion, output_dir):
    pdf_sources = [resolve_path("2.pdf"), resolve_path("1774366449_3.pdf")]
    sign_source = find_sign_file()
    copied_files = []
    pdf_index = 0

    documents = conclusion.find('Documents')
    if documents is None:
        return copied_files

    for document in documents.findall('Document'):
        for file_elem in document.findall('File'):
            file_name_elem = file_elem.find('FileName')
            file_format_elem = file_elem.find('FileFormat')
            file_checksum_elem = file_elem.find('FileChecksum')
            if file_name_elem is None:
                continue

            source_pdf = pdf_sources[pdf_index % len(pdf_sources)]
            pdf_index += 1
            file_name = file_name_elem.text.strip()
            dest_path = os.path.join(output_dir, file_name)
            shutil.copy2(source_pdf, dest_path)
            copied_files.append(dest_path)

            if file_format_elem is not None:
                file_format_elem.text = os.path.splitext(file_name)[1].lstrip(".").lower() or "pdf"
            if file_checksum_elem is not None:
                file_checksum_elem.text = compute_file_checksum(dest_path, uppercase=True)

            sign_elem = file_elem.find('SignFile')
            if sign_elem is None:
                continue

            sign_name_elem = sign_elem.find('FileName')
            sign_format_elem = sign_elem.find('FileFormat')
            sign_checksum_elem = sign_elem.find('FileChecksum')
            if sign_name_elem is None:
                continue

            sign_name = sign_name_elem.text.strip()
            sign_dest = os.path.join(output_dir, sign_name)
            shutil.copy2(sign_source, sign_dest)
            copied_files.append(sign_dest)

            if sign_format_elem is not None:
                sign_format_elem.text = "sig"
            if sign_checksum_elem is not None:
                sign_checksum_elem.text = compute_file_checksum(sign_dest, uppercase=True)

    return copied_files


def build_sample_conclusion():
    conclusion = load_real_sample_conclusion()
    copied_files = remap_document_files(conclusion, SCRIPT_DIR)
    return conclusion, copied_files


def main():
    conclusion, copied_files = build_sample_conclusion()
    output_path = os.path.join(SCRIPT_DIR, 'conclusion.xml')
    write_conclusion_xml(conclusion, output_path)

    xml_text = prettify(conclusion)
    examination_object = conclusion.find('ExaminationObject')

    assert conclusion.get('SchemaVersion') == '01.03'
    assert examination_object is not None
    assert examination_object.findtext('ExaminationForm') == '2'
    assert examination_object.findtext('ExaminationResult') == '1'
    assert examination_object.findtext('ExaminationObjectType') == '3'
    assert [node.text for node in examination_object.findall('ExaminationType')] == ['1', '2']
    assert 'Тавельского нефтяного месторождения' in (examination_object.findtext('Name') or '')

    expert_org = conclusion.find('ExpertOrganization')
    assert expert_org is not None
    assert 'Национальный Экспертный Центр' in (expert_org.findtext('OrgFullName') or '')

    obj = conclusion.find('Object')
    assert obj is not None
    assert obj.findtext('Type') == '1'
    assert obj.findtext('FunctionsClass') == '08.06.002.008'
    assert len(obj.findall('TEI')) == 4

    documents = conclusion.find('Documents')
    assert documents is not None
    assert len(documents.findall('Document')) >= 30
    assert documents.find(".//FullDocIssueAuthor/Organization/OrgFullName") is not None

    assert conclusion.find('EngineeringSurveyDeveloper') is not None
    assert conclusion.find('EngineeringSurveyAddress') is not None
    assert conclusion.find('ExpertEstimate') is not None
    assert conclusion.find('ExpertProjectDocuments') is None
    assert conclusion.find('ExpertEngineeringSurveys') is None

    summary = conclusion.find('Summary')
    assert summary is not None
    assert summary.findtext('EngineeringSurveySummary')
    assert summary.find('ExaminationSummary/ProjectDocumentsSummary') is not None
    assert summary.find('ExaminationSummary/EngineeringSurveysResultsSummary') is not None

    experts = conclusion.find('Experts')
    assert experts is not None
    assert len(experts.findall('Expert')) == 13
    assert any(
        expert.findtext('FamilyName') == 'Пахалков'
        for expert in experts.findall('Expert')
    )

    assert '<DocType>06.02</DocType>' in xml_text
    assert '<DocType>07.01</DocType>' in xml_text
    assert copied_files
    for path in copied_files:
        assert os.path.isfile(path)

    print(
        f'ok — conclusion.xml создан из {os.path.basename(REAL_SAMPLE_PATH)} '
        f'({len(documents.findall("Document"))} документов, {len(copied_files)} файлов)'
    )


if __name__ == '__main__':
    main()
