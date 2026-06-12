"""Сборка conclusion.xml из JSON-данных (без Tkinter)."""
from __future__ import annotations

import sys
import uuid
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.payload_converters import (
    capital_object_to_xml,
    climate_to_xml,
    declarant_to_xml,
    designer_to_xml,
    eepd_use_to_xml,
    engineering_survey_address_to_xml,
    estimated_cost_to_xml,
    expert_engineering_surveys_to_xml,
    expert_estimate_to_xml,
    expert_project_documents_to_xml,
    experts_to_xml,
    finance_item_to_xml,
    party_item_to_xml,
    previous_conclusion_to_xml,
    previous_simple_conclusion_to_xml,
    summary_to_xml,
)
from backend.tk_stub import install as install_tk_stub

install_tk_stub()
import main as core


class ValidationError(Exception):
    pass


def _err(message: str) -> None:
    raise ValidationError(message)


def _add_if_set(parent, tag: str, value: str | None) -> None:
    if value:
        ET.SubElement(parent, tag).text = value


def _format_date(value: str) -> str:
    return core.format_doc_date(value or "")


def _validate_cadastral_numbers(numbers: list[str]) -> list[str]:
    non_empty = [n.strip() for n in numbers if n and n.strip()]
    if not non_empty:
        return []
    for idx, value in enumerate(numbers, start=1):
        if not value or not value.strip():
            _err(f"Укажите кадастровый номер в строке {idx}!")
        if not core.CADASTRAL_NUMBER_RE.match(value.strip()):
            _err(
                f"Некорректный кадастровый номер в строке {idx} "
                f"(формат: 77:01:0002401:107)!"
            )
    return [n.strip() for n in numbers if n and n.strip()]


def _validate_experts(experts: list[dict]) -> None:
    if not experts:
        _err("Добавьте хотя бы одного эксперта!")
    for idx, data in enumerate(experts, start=1):
        required = (
            data.get("familyName"),
            data.get("firstName"),
            data.get("expertType"),
            data.get("expertCertificate"),
            data.get("certificateBeginDate"),
            data.get("certificateEndDate"),
        )
        if not all(required):
            _err(f"Заполните все обязательные поля для эксперта {idx}!")
        cert = data["expertCertificate"]
        if not core.EXPERT_CERTIFICATE_PATTERN.fullmatch(cert):
            _err(
                f"Некорректный номер аттестата у эксперта {idx}! "
                "Пример: МС-Э-49-5-12918"
            )
        if not _format_date(data["certificateBeginDate"]):
            _err(f"Укажите дату выдачи аттестата для эксперта {idx} (ДД.ММ.ГГГГ)!")
        if not _format_date(data["certificateEndDate"]):
            _err(f"Укажите дату окончания действия аттестата для эксперта {idx}!")


def _validate_summary(summary: dict) -> None:
    pd = summary.get("examinationProjectDocumentsSummary") or {}
    pd_values = [
        pd.get("engineeringSurveysResults"),
        pd.get("designAssignment"),
        pd.get("technicalRequirements"),
    ]
    if any(pd_values) and not all(pd_values):
        _err(
            "В общих выводах по проектной документации укажите все три подпункта "
            "или оставьте их пустыми!"
        )


def _prepare_documents(documents: list[dict], upload_dir: Path) -> list[dict]:
    prepared = []
    for idx, doc in enumerate(documents, start=1):
        doc_type = doc.get("docType", "")
        doc_name = (doc.get("docName") or "").strip()
        doc_date = _format_date(doc.get("docDate") or "")
        file_name = (doc.get("fileName") or "").strip()

        if not doc_type:
            _err(f"Укажите код типа документа для документа {idx}!")
        if not doc_name:
            _err(f"Укажите наименование документа {idx}!")
        if not doc_date:
            _err(f"Укажите корректную дату документа {idx} (ДД.ММ.ГГГГ)!")
        if not file_name:
            _err(f"Загрузите файл для документа {idx}!")

        file_path = upload_dir / file_name
        if not file_path.is_file():
            _err(f"Файл документа {idx} не найден на сервере!")

        meta = core.get_file_metadata(str(file_path))
        sign_files = []
        for sign_name in doc.get("signFileNames") or []:
            sign_path = upload_dir / sign_name
            if not sign_path.is_file():
                _err(f"Файл подписи «{sign_name}» не найден!")
            sign_files.append(core.get_file_metadata(str(sign_path), checksum_upper=True))

        prepared.append({
            "doc_type": doc_type,
            "doc_name": doc_name,
            "doc_number": (doc.get("docNumber") or "").strip(),
            "doc_date": doc_date,
            "doc_changes": (doc.get("docChanges") or "").strip(),
            "doc_author": (doc.get("docAuthor") or "").strip(),
            "file_path": str(file_path),
            "file_name": meta["file_name"],
            "file_format": meta["file_format"],
            "file_checksum": meta["file_checksum"],
            "sign_files": sign_files,
        })
    return prepared


def _collect_filled_previous_conclusions(raw: list[dict]) -> list[dict]:
    items = []
    for item in raw:
        data = previous_conclusion_to_xml(item)
        if core.is_previous_conclusion_filled(data):
            items.append(data)
    return items


def _validate_previous_conclusions(items: list[dict]) -> None:
    for idx, prev in enumerate(items, start=1):
        if not prev["date"]:
            _err(f"Укажите дату для ранее выданного заключения {idx}!")
        if not prev["number"]:
            _err(f"Укажите номер для ранее выданного заключения {idx}!")
        if not prev["object_type"]:
            _err(f"Укажите вид объекта для ранее выданного заключения {idx}!")
        if not prev["name"]:
            _err(f"Укажите наименование объекта для ранее выданного заключения {idx}!")
        if not prev["result"]:
            _err(f"Укажите результат для ранее выданного заключения {idx}!")


def _collect_filled_previous_simple(raw: list[dict]) -> list[dict]:
    items = []
    for item in raw:
        data = previous_simple_conclusion_to_xml(item)
        if core.is_previous_simple_conclusion_filled(data):
            items.append(data)
    return items


def _validate_previous_simple(items: list[dict]) -> None:
    for idx, simple in enumerate(items, start=1):
        if not simple["date"]:
            _err(f"Укажите дату для заключения по экспертному сопровождению {idx}!")
        if not simple["number"]:
            _err(f"Укажите номер для заключения по экспертному сопровождению {idx}!")
        if not simple["object_type"]:
            _err(f"Укажите вид объекта для заключения по экспертному сопровождению {idx}!")
        if not simple["result"]:
            _err(f"Укажите результат для заключения по экспертному сопровождению {idx}!")


def _validate_capital_object(data: dict) -> None:
    if not core.is_capital_object_filled(data):
        return
    if not data["name"]:
        _err("Укажите наименование объекта капитального строительства!")
    if not data["addresses"]:
        _err("Добавьте хотя бы один адрес объекта!")
    if not data["type"]:
        _err("Укажите вид объекта капитального строительства!")
    if not data["functions_class"]:
        _err("Укажите код классификатора объекта!")
    if not data["tei"]:
        _err("Добавьте хотя бы один технико-экономический показатель!")
    for idx, tei in enumerate(data["tei"], start=1):
        if not all([tei["name"], tei["measure"], tei["value"]]):
            _err(f"Заполните все поля показателя {idx}!")
    for idx, part in enumerate(data["parts"], start=1):
        if not part["name"]:
            _err(f"Укажите наименование составной части {idx}!")
        if not part["addresses"]:
            _err(f"Добавьте хотя бы один адрес для составной части {idx}!")
        if not part["functions_class"]:
            _err(f"Укажите код классификатора для составной части {idx}!")
        if not part["tei"]:
            _err(f"Добавьте показатель для составной части {idx}!")
        for tei_idx, tei in enumerate(part["tei"], start=1):
            if not all([tei["name"], tei["measure"], tei["value"]]):
                _err(
                    f"Заполните все поля показателя {tei_idx} составной части {idx}!"
                )


def _collect_filled_parties(raw: list[dict], is_filled) -> list[dict]:
    parties = []
    for item in raw:
        party = party_item_to_xml(item)
        if is_filled(party):
            parties.append(party)
    return parties


def _validate_project_documents_parties(parties: list[dict]) -> None:
    for idx, item in enumerate(parties, start=1):
        if item["party_type"] == "developer":
            error = core.validate_declarant_entity_data(
                item["entity"],
                f"застройщик проектной документации {idx}",
            )
        else:
            error = core.validate_technical_customer_data(
                item["entity"],
                f"технический заказчик проектной документации {idx}",
            )
        if error:
            _err(error)


def _validate_engineering_survey_parties(parties: list[dict]) -> None:
    for idx, item in enumerate(parties, start=1):
        if item["party_type"] == "developer":
            error = core.validate_declarant_entity_data(
                item["entity"],
                f"застройщик инженерных изысканий {idx}",
            )
        else:
            error = core.validate_technical_customer_data(
                item["entity"],
                f"технический заказчик инженерных изысканий {idx}",
            )
        if error:
            _err(error)


def _is_party_filled(party: dict) -> bool:
    if party["party_type"] == "developer":
        return core.is_declarant_data_filled(party["entity"])
    return core.is_technical_customer_filled(party["entity"])


def _validate_mismatch_list(
    mismatches: list[dict],
    section_label: str,
    block_index: int,
    block_label: str,
) -> None:
    for mismatch_idx, mismatch in enumerate(mismatches, start=1):
        if core.is_mismatch_filled(mismatch) and not core.is_mismatch_complete(mismatch):
            _err(
                f"Заполните все поля несоответствия {mismatch_idx} "
                f"({section_label}) в блоке экспертизы {block_label} {block_index}!"
            )


def _validate_mismatch_extended_list(
    mismatches: list[dict],
    section_label: str,
    block_label: str,
) -> None:
    for mismatch_idx, mismatch in enumerate(mismatches, start=1):
        if core.is_mismatch_extended_filled(mismatch) and not core.is_mismatch_extended_complete(mismatch):
            _err(
                f"Заполните все поля несоответствия {mismatch_idx} "
                f"({section_label}) в блоке {block_label}, включая направление деятельности!"
            )


def _collect_filled_designers(raw: list[dict]) -> list[dict]:
    items = []
    for item in raw:
        data = designer_to_xml(item)
        if core.is_designer_entity_filled(data):
            items.append(data)
    return items


def _collect_filled_eepd(raw: list[dict]) -> list[dict]:
    items = []
    for item in raw:
        data = eepd_use_to_xml(item)
        if core.is_eepd_use_filled(data):
            items.append(data)
    return items


def _collect_filled_survey_addresses(raw: list[dict]) -> list[dict]:
    items = []
    for item in raw:
        data = engineering_survey_address_to_xml(item)
        if core.is_engineering_survey_address_filled(data):
            items.append(data)
    return items


def _collect_filled_expert_surveys(raw: list[dict]) -> list[dict]:
    items = []
    for item in raw:
        data = expert_engineering_surveys_to_xml(item)
        if core.is_expert_engineering_surveys_filled(data):
            items.append(data)
    return items


def _collect_filled_expert_project_docs(raw: list[dict]) -> list[dict]:
    items = []
    for item in raw:
        data = expert_project_documents_to_xml(item)
        if core.is_expert_project_documents_filled(data):
            items.append(data)
    return items


def _validate_expert_engineering_surveys(items: list[dict]) -> None:
    for idx, data in enumerate(items, start=1):
        if not data["survey_type"]:
            _err(f"Укажите вид инженерных изысканий для блока экспертизы {idx}!")
        _validate_mismatch_list(
            data["norms_mismatches"],
            "несоответствие требованиям техрегламентов",
            idx,
            "инженерных изысканий",
        )


def _validate_expert_project_documents(items: list[dict]) -> None:
    for idx, data in enumerate(items, start=1):
        if not data["expert_type"]:
            _err(
                f"Укажите направление деятельности для блока экспертизы "
                f"проектной документации {idx}!"
            )
        for section_label, mismatches in [
            ("несоответствие результату инженерных изысканий", data["engineering_survey_mismatches"]),
            ("несоответствие заданию на проектирование", data["project_task_mismatches"]),
            ("несоответствие требованиям технических регламентов", data["norms_mismatches"]),
        ]:
            _validate_mismatch_list(
                mismatches,
                section_label,
                idx,
                "проектной документации",
            )
        if core.has_project_documents_mismatches_content(data):
            if not any([
                data["engineering_survey_mismatches"],
                data["project_task_mismatches"],
                data["norms_mismatches"],
            ]):
                _err(
                    f"В блоке экспертизы проектной документации {idx} укажите хотя бы одно "
                    "несоответствие (изыскания, задание или техрегламенты)!"
                )


def _validate_expert_estimate(data: dict) -> None:
    if not core.is_expert_estimate_filled(data):
        return
    if not data["estimate_norms"]:
        _err("Укажите информацию об использовании сметных нормативов!")
    mismatch_sections = [
        ("общее замечание", data["common_mismatches"], False),
        ("замечание по сводному сметному расчету", data["full_calculation_mismatches"], False),
        ("замечание по локальным сметным расчетам", data["local_calculation_mismatches"], False),
        ("замечание по соответствию расчетов проектной документации", data["project_documents_mismatches"], True),
        ("замечание по пересчету из базисного уровня цен", data["basic_mismatches"], False),
    ]
    for section_label, mismatches, extended in mismatch_sections:
        if extended:
            _validate_mismatch_extended_list(
                mismatches,
                section_label,
                "проверки сметной стоимости",
            )
        else:
            _validate_mismatch_list(
                mismatches,
                section_label,
                1,
                "проверки сметной стоимости",
            )


def build_conclusion_xml(payload: dict, upload_dir: Path) -> tuple[str, list[str]]:
    """Собирает XML и возвращает (xml_text, список путей к файлам для архива)."""
    org = payload.get("expertOrganization") or {}
    addr = org.get("address") or {}
    approver = payload.get("approver") or {}
    exam = payload.get("examinationObject") or {}
    ecology = payload.get("ecology") or {}
    declarant = payload.get("declarant") or {}
    summary = payload.get("summary") or {}
    experts = payload.get("experts") or []
    documents_raw = payload.get("documents") or []
    finance_raw = payload.get("finance") or []

    org_full_name = (org.get("orgFullName") or "").strip()
    org_ogrn = (org.get("orgOgrn") or "").strip()
    org_inn = (org.get("orgInn") or "").strip()
    org_kpp = (org.get("orgKpp") or "").strip()
    country = (addr.get("country") or "").strip()
    region = (addr.get("region") or "").strip()
    city = (addr.get("city") or "").strip()
    street = (addr.get("street") or "").strip()
    building = (addr.get("building") or "").strip()
    room = (addr.get("room") or "").strip()

    family_name = (approver.get("familyName") or "").strip()
    first_name = (approver.get("firstName") or "").strip()
    second_name = (approver.get("secondName") or "").strip()
    position = (approver.get("position") or "").strip()

    examination_types = [t for t in (exam.get("examinationTypes") or []) if t]
    object_name = (exam.get("name") or "").strip()

    if not examination_types:
        _err("Выберите хотя бы один предмет экспертизы!")
    if not object_name:
        _err("Укажите наименование объекта экспертизы!")
    if not all([family_name, first_name, position]):
        _err("Заполните обязательные поля лица, утвердившего заключение")
    if not all([org_full_name, org_ogrn, org_inn, org_kpp, country, region, city, street, building, room]):
        _err("Заполните все поля организации по проведению экспертизы!")
    if not documents_raw:
        _err("Добавьте хотя бы один документ!")

    documents_data = _prepare_documents(documents_raw, upload_dir)

    previous_conclusions = _collect_filled_previous_conclusions(payload.get("previousConclusions") or [])
    _validate_previous_conclusions(previous_conclusions)

    previous_simple = _collect_filled_previous_simple(payload.get("previousSimpleConclusions") or [])
    _validate_previous_simple(previous_simple)

    capital_object_data = capital_object_to_xml(payload.get("capitalObject"))
    if capital_object_data:
        _validate_capital_object(capital_object_data)

    need_expertise = ecology.get("needExpertise") or ""
    if not need_expertise:
        _err("Укажите необходимость проведения экологической экспертизы!")

    declarant_data = declarant_to_xml(declarant)
    declarant_error = core.validate_declarant_data(declarant_data)
    if declarant_error:
        _err(declarant_error)

    project_docs_parties = _collect_filled_parties(
        payload.get("projectDocumentsParties") or [],
        _is_party_filled,
    )
    _validate_project_documents_parties(project_docs_parties)

    finance_items = [finance_item_to_xml(item) for item in finance_raw]
    finance_items = [f for f in finance_items if f["finance_type"]]
    if not finance_items:
        _err("Добавьте хотя бы один источник финансирования!")
    for idx, finance_item in enumerate(finance_items, start=1):
        finance_error = core.validate_finance_data(finance_item, idx)
        if finance_error:
            _err(finance_error)

    estimated_cost_data = estimated_cost_to_xml(payload.get("estimatedCost"))
    if estimated_cost_data and core.is_estimated_cost_filled(estimated_cost_data):
        estimated_cost_error = core.validate_estimated_cost_data(estimated_cost_data)
        if estimated_cost_error:
            _err(estimated_cost_error)

    climate_data = climate_to_xml(payload.get("climateConditions"))
    if climate_data:
        climate_error = core.validate_climate_conditions_data(climate_data)
        if climate_error:
            _err(climate_error)

    designer_items = _collect_filled_designers(payload.get("designers") or [])
    for idx, designer_data in enumerate(designer_items, start=1):
        designer_error = core.validate_designer_entity_data(designer_data, idx)
        if designer_error:
            _err(designer_error)

    eepd_raw = payload.get("eepdUse")
    if isinstance(eepd_raw, dict):
        eepd_raw = [eepd_raw]
    eepd_use_items = _collect_filled_eepd(eepd_raw or [])
    for idx, eepd_data in enumerate(eepd_use_items, start=1):
        eepd_error = core.validate_eepd_use_data(eepd_data, idx)
        if eepd_error:
            _err(eepd_error)

    survey_address_items = _collect_filled_survey_addresses(
        payload.get("engineeringSurveyAddresses") or []
    )
    for idx, survey_data in enumerate(survey_address_items, start=1):
        survey_error = core.validate_engineering_survey_address_data(survey_data, idx)
        if survey_error:
            _err(survey_error)

    engineering_survey_parties = _collect_filled_parties(
        payload.get("engineeringSurveyParties") or [],
        _is_party_filled,
    )
    _validate_engineering_survey_parties(engineering_survey_parties)

    expert_surveys_items = _collect_filled_expert_surveys(
        payload.get("expertEngineeringSurveys") or []
    )
    _validate_expert_engineering_surveys(expert_surveys_items)

    expert_project_docs_items = _collect_filled_expert_project_docs(
        payload.get("expertProjectDocuments") or []
    )
    _validate_expert_project_documents(expert_project_docs_items)

    expert_estimate_data = expert_estimate_to_xml(payload.get("expertEstimate"))
    if expert_estimate_data:
        _validate_expert_estimate(expert_estimate_data)

    _validate_summary(summary)
    _validate_experts(experts)

    conclusion = ET.Element("Conclusion", {
        "xmlns:xsi": "http://www.w3.org/2001/XMLSchema-instance",
        "xsi:noNamespaceSchemaLocation": "conclusion-01-03.xsd",
        "ConclusionGUID": str(uuid.uuid4()).upper(),
        "SchemaVersion": "01.03",
    })

    expert_organization = ET.SubElement(conclusion, "ExpertOrganization")
    ET.SubElement(expert_organization, "OrgFullName").text = org_full_name
    ET.SubElement(expert_organization, "OrgOGRN").text = org_ogrn
    ET.SubElement(expert_organization, "OrgINN").text = org_inn
    ET.SubElement(expert_organization, "OrgKPP").text = org_kpp
    address = ET.SubElement(expert_organization, "Address")
    ET.SubElement(address, "Country").text = country
    ET.SubElement(address, "Region").text = region
    ET.SubElement(address, "City").text = city
    ET.SubElement(address, "Street").text = street
    ET.SubElement(address, "Building").text = building
    ET.SubElement(address, "Room").text = room

    approver_elem = ET.SubElement(conclusion, "Approver")
    ET.SubElement(approver_elem, "FamilyName").text = family_name
    ET.SubElement(approver_elem, "FirstName").text = first_name
    ET.SubElement(approver_elem, "SecondName").text = second_name
    ET.SubElement(approver_elem, "Position").text = position

    examination_object = ET.SubElement(conclusion, "ExaminationObject")
    _add_if_set(examination_object, "ExaminationForm", exam.get("examinationForm"))
    _add_if_set(examination_object, "ExaminationResult", exam.get("examinationResult"))
    _add_if_set(examination_object, "ExaminationObjectType", exam.get("examinationObjectType"))
    for exam_type in examination_types:
        ET.SubElement(examination_object, "ExaminationType").text = exam_type
    _add_if_set(examination_object, "ConstructionType", exam.get("constructionType"))
    _add_if_set(examination_object, "ExaminationStage", exam.get("examinationStage"))
    stage_note = (exam.get("examinationStageNote") or "").strip()
    if stage_note:
        ET.SubElement(examination_object, "ExaminationStageNote").text = stage_note
    ET.SubElement(examination_object, "Name").text = object_name
    _add_if_set(examination_object, "ProjectDocumentationIM", exam.get("projectDocumentationIM"))
    _add_if_set(examination_object, "EngineeringSurveysIM", exam.get("engineeringSurveysIM"))

    documents = ET.SubElement(conclusion, "Documents")
    output_files: list[str] = []

    for doc in documents_data:
        document = ET.SubElement(documents, "Document")
        ET.SubElement(document, "DocType").text = doc["doc_type"]
        ET.SubElement(document, "DocName").text = doc["doc_name"]
        if doc["doc_number"]:
            ET.SubElement(document, "DocNumber").text = doc["doc_number"]
        ET.SubElement(document, "DocDate").text = doc["doc_date"]
        if doc["doc_author"]:
            ET.SubElement(document, "DocIssueAuthor").text = doc["doc_author"]
        if doc["doc_changes"]:
            ET.SubElement(document, "DocChanges").text = doc["doc_changes"]

        file_elem = ET.SubElement(document, "File")
        ET.SubElement(file_elem, "FileName").text = doc["file_name"]
        ET.SubElement(file_elem, "FileFormat").text = doc["file_format"]
        ET.SubElement(file_elem, "FileChecksum").text = doc["file_checksum"]
        output_files.append(doc["file_path"])

        for sign in doc["sign_files"]:
            sign_elem = ET.SubElement(file_elem, "SignFile")
            ET.SubElement(sign_elem, "FileName").text = sign["file_name"]
            ET.SubElement(sign_elem, "FileFormat").text = sign["file_format"]
            ET.SubElement(sign_elem, "FileChecksum").text = sign["file_checksum"]
            output_files.append(sign["file_path"])

    core.append_previous_conclusions_xml(conclusion, previous_conclusions)
    core.append_previous_simple_conclusions(conclusion, previous_simple)

    if capital_object_data and core.is_capital_object_filled(capital_object_data):
        core.append_capital_object(conclusion, capital_object_data)

    ecology_elem = ET.SubElement(conclusion, "EcologyExpertise")
    ET.SubElement(ecology_elem, "NeedExpertise").text = need_expertise
    ecology_comment = (ecology.get("comment") or "").strip()
    if ecology_comment:
        ET.SubElement(ecology_elem, "Comment").text = ecology_comment

    cadastral_numbers = _validate_cadastral_numbers(payload.get("cadastralNumbers") or [])
    for number in cadastral_numbers:
        ET.SubElement(conclusion, "CadastralNumber").text = number

    core.append_declarant_xml(conclusion, declarant_data)

    if project_docs_parties:
        core.append_project_documents_parties_xml(conclusion, project_docs_parties)

    core.append_finance_xml(conclusion, finance_items)

    finance_comment = (payload.get("financeComment") or "").strip()
    if finance_comment:
        ET.SubElement(conclusion, "FinanceComment").text = finance_comment

    if estimated_cost_data and core.is_estimated_cost_filled(estimated_cost_data):
        core.append_estimated_cost_xml(conclusion, estimated_cost_data)

    if climate_data and core.is_climate_conditions_block_filled(climate_data):
        core.append_climate_conditions_xml(conclusion, climate_data)
    if climate_data and climate_data.get("note"):
        ET.SubElement(conclusion, "ClimateConditionsNote").text = climate_data["note"]

    if designer_items:
        core.append_designers_xml(conclusion, designer_items)

    if eepd_use_items:
        core.append_eepd_use_xml(conclusion, eepd_use_items)

    if survey_address_items:
        core.append_engineering_survey_addresses_xml(conclusion, survey_address_items)

    if engineering_survey_parties:
        core.append_engineering_survey_parties_xml(conclusion, engineering_survey_parties)

    if expert_surveys_items:
        core.append_expert_engineering_surveys_xml(conclusion, expert_surveys_items)

    if expert_project_docs_items:
        core.append_expert_project_documents_xml(conclusion, expert_project_docs_items)

    if expert_estimate_data and core.is_expert_estimate_filled(expert_estimate_data):
        core.append_expert_estimate_xml(conclusion, expert_estimate_data)

    core.append_summary_xml(conclusion, summary_to_xml(summary))
    core.append_experts_xml(conclusion, experts_to_xml(experts))

    xml_pretty = core.prettify(conclusion)
    xml_text = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<?xml-stylesheet type="text/xsl" href="conclusion-01-03.xsl" ?>\n'
    ) + xml_pretty
    lines = xml_text.splitlines()
    del lines[2]
    return "\n".join(lines), output_files


def render_conclusion_xml_string(payload: dict, upload_dir: str | Path) -> tuple[str, list[str]]:
    return build_conclusion_xml(payload, Path(upload_dir))
