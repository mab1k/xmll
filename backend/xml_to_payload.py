"""Преобразование conclusion.xml в JSON-payload для API/билдера."""
from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

ADDRESS_TAGS = (
    "country",
    "region",
    "district",
    "city",
    "settlement",
    "street",
    "building",
    "room",
    "note",
)


def _text(parent: ET.Element | None, tag: str, default: str = "") -> str:
    if parent is None:
        return default
    elem = parent.find(tag)
    if elem is None or elem.text is None:
        return default
    return elem.text.strip()


def _texts(parent: ET.Element | None, tag: str) -> list[str]:
    if parent is None:
        return []
    return [(elem.text or "").strip() for elem in parent.findall(tag) if (elem.text or "").strip()]


def _parse_address(elem: ET.Element | None) -> dict:
    if elem is None:
        return {key: "" for key in ADDRESS_TAGS}
    return {key: _text(elem, key.capitalize() if key != "note" else "Note") for key in ADDRESS_TAGS}


def _parse_organization(parent: ET.Element | None) -> dict:
    org = parent.find("Organization") if parent is not None else None
    if org is None:
        return {"type": "organization"}
    return {
        "type": "organization",
        "orgFullName": _text(org, "OrgFullName"),
        "orgOgrn": _text(org, "OrgOGRN"),
        "orgInn": _text(org, "OrgINN"),
        "orgKpp": _text(org, "OrgKPP"),
        "email": _text(org, "Email"),
        "address": _parse_address(org.find("Address")),
    }


def _parse_declarant(declarant: ET.Element | None) -> dict:
    if declarant is None:
        return {"type": "organization"}
    if declarant.find("Organization") is not None:
        return _parse_organization(declarant)
    if declarant.find("ForeignOrganization") is not None:
        foreign = declarant.find("ForeignOrganization")
        return {
            "type": "foreign_organization",
            "orgFullName": _text(foreign, "OrgFullName"),
            "orgInn": _text(foreign, "OrgINN"),
            "orgKpp": _text(foreign, "OrgKPP"),
            "email": _text(foreign, "Email"),
            "address": _parse_address(foreign.find("Address")),
        }
    if declarant.find("IP") is not None:
        ip = declarant.find("IP")
        return {
            "type": "ip",
            "familyName": _text(ip, "FamilyName"),
            "firstName": _text(ip, "FirstName"),
            "secondName": _text(ip, "SecondName"),
            "ogrnip": _text(ip, "OGRNIP"),
            "email": _text(ip, "Email"),
            "postAddress": _parse_address(ip.find("PostAddress")),
        }
    person = declarant.find("Person")
    return {
        "type": "person",
        "familyName": _text(person, "FamilyName"),
        "firstName": _text(person, "FirstName"),
        "secondName": _text(person, "SecondName"),
        "snils": _text(person, "SNILS"),
        "email": _text(person, "Email"),
        "postAddress": _parse_address(person.find("PostAddress") if person is not None else None),
    }


def _parse_documents(documents: ET.Element | None) -> list[dict]:
    if documents is None:
        return []
    items = []
    for document in documents.findall("Document"):
        file_elem = document.find("File")
        sign_names = []
        if file_elem is not None:
            for sign in file_elem.findall("SignFile"):
                sign_name = _text(sign, "FileName")
                if sign_name:
                    sign_names.append(sign_name)
        items.append({
            "docType": _text(document, "DocType"),
            "docName": _text(document, "DocName"),
            "docNumber": _text(document, "DocNumber"),
            "docDate": _text(document, "DocDate"),
            "docChanges": _text(document, "DocChanges"),
            "docAuthor": _text(document, "DocIssueAuthor"),
            "fileName": _text(file_elem, "FileName"),
            "signFileNames": sign_names,
        })
    return items


def _parse_tei_list(parent: ET.Element | None) -> list[dict]:
    if parent is None:
        return []
    return [
        {
            "name": _text(tei, "Name"),
            "measure": _text(tei, "Measure"),
            "value": _text(tei, "Value"),
        }
        for tei in parent.findall("TEI")
    ]


def _parse_capital_object(obj: ET.Element | None) -> dict | None:
    if obj is None:
        return None
    addresses = [_parse_address(addr) for addr in obj.findall("Address")]
    parts = []
    for part in obj.findall("ObjectPart"):
        parts.append({
            "name": _text(part, "Name"),
            "addresses": [_parse_address(addr) for addr in part.findall("Address")],
            "functionsClass": _text(part, "FunctionsClass"),
            "tei": _parse_tei_list(part),
        })
    return {
        "name": _text(obj, "Name"),
        "addresses": addresses,
        "type": _text(obj, "Type"),
        "functionsClass": _text(obj, "FunctionsClass"),
        "tei": _parse_tei_list(obj),
        "parts": parts,
    }


def _parse_finance_items(root: ET.Element) -> list[dict]:
    items = []
    for finance in root.findall("Finance"):
        item = {
            "financeType": _text(finance, "FinanceType"),
            "budgetType": _text(finance, "BudgetType"),
            "financeSize": _text(finance, "FinanceSize"),
            "owner": None,
        }
        owner = finance.find("FinanceOwner")
        if owner is not None:
            item["owner"] = _parse_organization(owner)
        items.append(item)
    return items


def _parse_estimated_cost(elem: ET.Element | None) -> dict | None:
    if elem is None:
        return None
    if elem.find("EstimatedComplexCostBefore") is not None or elem.find("EstimatedComplexCostPost") is not None:
        return {
            "currency": _text(elem, "Currency"),
            "mode": "complex",
            "complexBefore": _parse_complex_cost(elem.find("EstimatedComplexCostBefore")),
            "complexPost": _parse_complex_cost(elem.find("EstimatedComplexCostPost")),
        }
    return {
        "currency": _text(elem, "Currency"),
        "mode": "complete",
        "completeBefore": _text(elem, "EstimatedCompleteCostBefore"),
        "completePost": _text(elem, "EstimatedCompleteCostPost"),
    }


def _parse_complex_cost(elem: ET.Element | None) -> dict:
    if elem is None:
        return {}
    return {child.tag: (child.text or "").strip() for child in list(elem)}


def _parse_climate(elem: ET.Element | None) -> dict | None:
    if elem is None:
        return None
    calc = elem.find("SeismicActivityCalculatedValue")
    seismic_calculated = None
    if calc is not None:
        seismic_calculated = {
            "enabled": True,
            "min": _text(calc, "MinValue"),
            "max": _text(calc, "MaxValue"),
        }
    return {
        "climateDistricts": _texts(elem, "ClimateDistrict"),
        "geologicalConditions": _texts(elem, "GeologicalConditions"),
        "windDistricts": _texts(elem, "WindDistrict"),
        "snowDistricts": _texts(elem, "SnowDistrict"),
        "seismicActivities": _texts(elem, "SeismicActivity"),
        "seismicCalculated": seismic_calculated,
        "note": "",
    }


def _parse_designers(root: ET.Element) -> list[dict]:
    items = []
    for designer in root.findall("Designer"):
        entity = _parse_organization(designer)
        entity["general"] = designer.attrib.get("General", "")
        items.append(entity)
    return items


def _parse_party_blocks(root: ET.Element, developer_tag: str, customer_tag: str) -> list[dict]:
    parties = []
    for elem in root.findall(developer_tag):
        parties.append({"partyType": "developer", "entity": _parse_organization(elem)})
    for elem in root.findall(customer_tag):
        parties.append({"partyType": "technical_customer", "entity": _parse_organization(elem)})
    return parties


def _parse_survey_addresses(root: ET.Element) -> list[dict]:
    return [
        {
            "region": _text(item, "EngineeringSurveyRegion"),
            "district": _text(item, "EngineeringSurveyDistrict"),
        }
        for item in root.findall("EngineeringSurveyAddress")
    ]


def _parse_mismatches(parent: ET.Element | None, tag: str) -> list[dict]:
    if parent is None:
        return []
    mismatches = parent.find("Mismatches")
    if mismatches is None:
        return []
    return [
        {
            "summary": _text(item, "Summary"),
            "part": _text(item, "Part"),
            "link": _text(item, "Link"),
        }
        for item in mismatches.findall(tag)
    ]


def _parse_expert_estimate(elem: ET.Element | None) -> dict | None:
    if elem is None:
        return None
    mismatches = elem.find("Mismatches")
    return {
        "estimateNorms": _text(elem, "EstimateNorms"),
        "commonMismatches": _parse_mismatches(elem, "CommonMismatch"),
        "fullCalculationMismatches": _parse_mismatches(elem, "FullCalculationMismatch"),
        "localCalculationMismatches": _parse_mismatches(elem, "LocalCalculationMismatch"),
        "projectDocumentsMismatches": [
            {
                "summary": _text(item, "Summary"),
                "part": _text(item, "Part"),
                "link": _text(item, "Link"),
                "expertType": item.attrib.get("ExpertType", _text(item, "ExpertType")),
            }
            for item in (mismatches.findall("ProjectDocumentsMismatch") if mismatches is not None else [])
        ],
        "basicMismatches": _parse_mismatches(elem, "BasicMismatch"),
    }


def _parse_summary(elem: ET.Element | None) -> dict:
    if elem is None:
        return {}
    exam = elem.find("ExaminationSummary")
    exam_pd = exam.find("ProjectDocumentsSummary") if exam is not None else None
    estimate_variant = "standard"
    estimate_1315 = _text(elem, "EstimateNormsAndWorksSummary1315") or _text(elem, "EstimateSummary1315")
    if estimate_1315:
        estimate_variant = "1315"
    exam_estimate_variant = "standard"
    if exam is not None and _text(exam, "EstimateSummary1315"):
        exam_estimate_variant = "1315"
    return {
        "engineeringSurveySummary": _text(elem, "EngineeringSurveySummary"),
        "engineeringSurveySummaryDate": _text(elem, "EngineeringSurveySummaryDate"),
        "engineeringSurveyTypes": _texts(elem, "EngineeringSurveyType"),
        "projectDocumentsSummary": _text(elem, "ProjectDocumentsSummary"),
        "projectDocumentsSummaryDate": _text(elem, "ProjectDocumentsSummaryDate"),
        "estimateVariant": estimate_variant,
        "estimateNormsAndWorksSummary": _text(elem, "EstimateNormsAndWorksSummary"),
        "estimateSummary": _text(elem, "EstimateSummary"),
        "estimateNormsAndWorksSummary1315": _text(elem, "EstimateNormsAndWorksSummary1315"),
        "estimateSummary1315": _text(elem, "EstimateSummary1315"),
        "examinationEngineeringSurveysResultsSummary": _text(exam, "EngineeringSurveysResultsSummary") if exam is not None else "",
        "examinationProjectDocumentsSummary": {
            "engineeringSurveysResults": _text(exam_pd, "ProjectDocumentationEngineeringSurveysResultsSummary"),
            "designAssignment": _text(exam_pd, "ProjectDocumentationDesignAssignmentSummary"),
            "technicalRequirements": _text(exam_pd, "ProjectDocumentationTechnicalRequirementsSummary"),
        },
        "examinationEstimateVariant": exam_estimate_variant,
        "examinationEstimateSummary": _text(exam, "EstimateSummary") if exam is not None else "",
        "examinationEstimateSummary1315": _text(exam, "EstimateSummary1315") if exam is not None else "",
    }


def _parse_experts(elem: ET.Element | None) -> list[dict]:
    if elem is None:
        return []
    return [
        {
            "familyName": _text(expert, "FamilyName"),
            "firstName": _text(expert, "FirstName"),
            "secondName": _text(expert, "SecondName"),
            "expertType": _text(expert, "ExpertType"),
            "expertCertificate": _text(expert, "ExpertCertificate"),
            "certificateBeginDate": _text(expert, "ExpertCertificateBeginDate"),
            "certificateEndDate": _text(expert, "ExpertCertificateEndDate"),
        }
        for expert in elem.findall("Expert")
    ]


def _ensure_expert_org_address(address: dict) -> dict:
    """В conclusion.xml адрес организации может быть только в Note — дополняем для валидации билдера."""
    result = dict(address)
    if result.get("note") and not any(result.get(key) for key in ("city", "street", "building", "room")):
        for key in ("city", "street", "building", "room"):
            if not result.get(key):
                result[key] = "-"
    if not result.get("country"):
        result["country"] = "Российская Федерация"
    return result


def xml_to_payload(root: ET.Element) -> dict:
    org = root.find("ExpertOrganization")
    org_address = _parse_address(org.find("Address") if org is not None else None)
    exam = root.find("ExaminationObject")
    ecology = root.find("EcologyExpertise")

    payload = {
        "expertOrganization": {
            "orgFullName": _text(org, "OrgFullName"),
            "orgOgrn": _text(org, "OrgOGRN"),
            "orgInn": _text(org, "OrgINN"),
            "orgKpp": _text(org, "OrgKPP"),
            "address": _ensure_expert_org_address(org_address),
        },
        "approver": {
            "familyName": _text(root.find("Approver"), "FamilyName"),
            "firstName": _text(root.find("Approver"), "FirstName"),
            "secondName": _text(root.find("Approver"), "SecondName"),
            "position": _text(root.find("Approver"), "Position"),
        },
        "examinationObject": {
            "examinationForm": _text(exam, "ExaminationForm"),
            "examinationResult": _text(exam, "ExaminationResult"),
            "examinationObjectType": _text(exam, "ExaminationObjectType"),
            "examinationTypes": _texts(exam, "ExaminationType"),
            "constructionType": _text(exam, "ConstructionType"),
            "examinationStage": _text(exam, "ExaminationStage"),
            "examinationStageNote": _text(exam, "ExaminationStageNote"),
            "name": _text(exam, "Name"),
            "projectDocumentationIM": _text(exam, "ProjectDocumentationIM"),
            "engineeringSurveysIM": _text(exam, "EngineeringSurveysIM"),
        },
        "documents": _parse_documents(root.find("Documents")),
        "previousConclusions": [],
        "previousSimpleConclusions": [],
        "capitalObject": _parse_capital_object(root.find("Object")),
        "ecology": {
            "needExpertise": _text(ecology, "NeedExpertise"),
            "comment": _text(ecology, "Comment"),
        },
        "cadastralNumbers": _texts(root, "CadastralNumber"),
        "declarant": _parse_declarant(root.find("Declarant")),
        "projectDocumentsParties": _parse_party_blocks(
            root, "ProjectDocumentsDeveloper", "ProjectDocumentsTechnicalCustomer"
        ),
        "finance": _parse_finance_items(root),
        "financeComment": _text(root, "FinanceComment"),
        "estimatedCost": _parse_estimated_cost(root.find("EstimatedCost")),
        "climateConditions": _parse_climate(root.find("ClimateConditions")),
        "designers": _parse_designers(root),
        "eepdUse": [],
        "engineeringSurveyAddresses": _parse_survey_addresses(root),
        "engineeringSurveyParties": _parse_party_blocks(
            root, "EngineeringSurveyDeveloper", "EngineeringSurveyTechnicalCustomer"
        ),
        "expertEngineeringSurveys": [],
        "expertProjectDocuments": [],
        "expertEstimate": _parse_expert_estimate(root.find("ExpertEstimate")),
        "summary": _parse_summary(root.find("Summary")),
        "experts": _parse_experts(root.find("Experts")),
    }

    prev = root.find("PreviousConclusions")
    if prev is not None:
        for item in prev.findall("PreviousConclusion"):
            number_elem = item.find("Number")
            number_format = "egrz"
            number = ""
            if number_elem is not None:
                if number_elem.find("EGRZ") is not None:
                    number = _text(number_elem, "EGRZ")
                    number_format = "egrz"
                else:
                    number = _text(number_elem, "noEGRZ")
                    number_format = "noegrz"
            payload["previousConclusions"].append({
                "date": _text(item, "Date"),
                "number": number,
                "numberFormat": number_format,
                "objectType": _text(item, "ExaminationObjectType"),
                "name": _text(item, "Name"),
                "result": _text(item, "Result"),
            })

    prev_simple = root.find("PreviousSimpleConclusions")
    if prev_simple is not None:
        for item in prev_simple.findall("PreviousSimpleConclusion"):
            payload["previousSimpleConclusions"].append({
                "date": _text(item, "Date"),
                "number": _text(item, "Number"),
                "objectType": _text(item, "ExaminationObjectType"),
                "result": _text(item, "Result"),
            })

    for eepd in root.findall("EEPDUse"):
        number_elem = eepd.find("EEPDNumber")
        number_format = "egrz"
        number = ""
        if number_elem is not None:
            if number_elem.find("EGRZ") is not None:
                number = _text(number_elem, "EGRZ")
            else:
                number = _text(number_elem, "noEGRZ")
                number_format = "noegrz"
        payload["eepdUse"].append({
            "note": _text(eepd, "EEPDNote"),
            "number": number,
            "numberFormat": number_format,
            "date": _text(eepd, "EEPDDate"),
        })

    for block in root.findall("ExpertEngineeringSurveys"):
        payload["expertEngineeringSurveys"].append({
            "surveyType": block.attrib.get("EngineeringSurveyType", ""),
            "normsMismatches": _parse_mismatches(block, "NormsMismatch"),
        })

    for block in root.findall("ExpertProjectDocuments"):
        payload["expertProjectDocuments"].append({
            "expertType": block.attrib.get("ExpertType", ""),
            "dangerSolutions": _text(block, "DangerSolutions"),
            "engineeringSurveyMismatches": _parse_mismatches(block, "EngineeringSurveyMismatch"),
            "projectTaskMismatches": _parse_mismatches(block, "ProjectTaskMismatch"),
            "normsMismatches": _parse_mismatches(block, "NormsMismatch"),
            "dangerMismatch": _text(block.find("Mismatches"), "DangerMismatch"),
        })

    return payload


def load_payload_from_xml(path: str | Path) -> dict:
    root = ET.parse(path).getroot()
    return xml_to_payload(root)
