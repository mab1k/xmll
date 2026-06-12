"""Преобразование сохранённой формы в payload для conclusion_builder."""
from __future__ import annotations


def _strip_mismatch(item: dict) -> dict:
    return {
        "summary": item.get("summary", ""),
        "part": item.get("part", ""),
        "link": item.get("link", ""),
    }


def _strip_mismatch_extended(item: dict) -> dict:
    return {**_strip_mismatch(item), "expertType": item.get("expertType", "")}


def form_to_builder_payload(form: dict, files_by_id: dict | None = None) -> dict:
    files_by_id = files_by_id or {}

    documents = []
    for doc in form.get("documents", []):
        sign_names = list(doc.get("signFileNames") or [])
        sign_ids = list(doc.get("signStorageIds") or [])
        for idx, stored_id in enumerate(sign_ids):
            if stored_id and stored_id in files_by_id and idx < len(sign_names):
                sign_names[idx] = files_by_id[stored_id].original_name
        file_name = doc.get("fileName") or ""
        file_id = doc.get("fileStorageId")
        if file_id and file_id in files_by_id:
            file_name = files_by_id[file_id].original_name
        documents.append({
            "docType": doc.get("docType", ""),
            "docName": doc.get("docName", ""),
            "docNumber": doc.get("docNumber", ""),
            "docDate": doc.get("docDate", ""),
            "docChanges": doc.get("docChanges", ""),
            "docAuthor": doc.get("docAuthor", ""),
            "fileName": file_name,
            "signFileNames": [name for name in sign_names if name],
        })

    designers = []
    for designer in form.get("designers", []):
        item = dict(designer)
        item.pop("id", None)
        designers.append(item)

    return {
        "expertOrganization": form.get("expertOrganization") or {},
        "approver": form.get("approver") or {},
        "examinationObject": form.get("examinationObject") or {},
        "documents": documents,
        "previousConclusions": [
            {
                "date": item.get("date", ""),
                "number": item.get("number", ""),
                "numberFormat": item.get("numberFormat", "egrz"),
                "objectType": item.get("objectType", ""),
                "name": item.get("name", ""),
                "result": item.get("result", ""),
            }
            for item in form.get("previousConclusions", [])
        ],
        "previousSimpleConclusions": [
            {
                "date": item.get("date", ""),
                "number": item.get("number", ""),
                "objectType": item.get("objectType", ""),
                "result": item.get("result", ""),
            }
            for item in form.get("previousSimpleConclusions", [])
        ],
        "capitalObject": form.get("capitalObject"),
        "ecology": form.get("ecology") or {},
        "cadastralNumbers": [
            n.strip() for n in form.get("cadastralNumbers", []) if isinstance(n, str) and n.strip()
        ],
        "declarant": form.get("declarant") or {},
        "projectDocumentsParties": [
            {"partyType": p.get("partyType", ""), "entity": p.get("entity") or {}}
            for p in form.get("projectDocumentsParties", [])
        ],
        "finance": [
            {
                "financeType": item.get("financeType", ""),
                "budgetType": item.get("budgetType", ""),
                "financeSize": item.get("financeSize", ""),
                "owner": item.get("owner") or {},
            }
            for item in form.get("finance", [])
        ],
        "financeComment": form.get("financeComment", ""),
        "estimatedCost": form.get("estimatedCost"),
        "climateConditions": form.get("climateConditions"),
        "designers": designers,
        "eepdUse": [
            {
                "note": item.get("note", ""),
                "number": item.get("number", ""),
                "numberFormat": item.get("numberFormat", "egrz"),
                "date": item.get("date", ""),
            }
            for item in form.get("eepdUse", [])
        ],
        "engineeringSurveyAddresses": [
            {"region": item.get("region", ""), "district": item.get("district", "")}
            for item in form.get("engineeringSurveyAddresses", [])
        ],
        "engineeringSurveyParties": [
            {"partyType": p.get("partyType", ""), "entity": p.get("entity") or {}}
            for p in form.get("engineeringSurveyParties", [])
        ],
        "expertEngineeringSurveys": [
            {
                "surveyType": block.get("surveyType", ""),
                "normsMismatches": [_strip_mismatch(m) for m in block.get("normsMismatches", [])],
            }
            for block in form.get("expertEngineeringSurveys", [])
        ],
        "expertProjectDocuments": [
            {
                "expertType": block.get("expertType", ""),
                "dangerSolutions": block.get("dangerSolutions", ""),
                "engineeringSurveyMismatches": [
                    _strip_mismatch(m) for m in block.get("engineeringSurveyMismatches", [])
                ],
                "projectTaskMismatches": [
                    _strip_mismatch(m) for m in block.get("projectTaskMismatches", [])
                ],
                "normsMismatches": [_strip_mismatch(m) for m in block.get("normsMismatches", [])],
                "dangerMismatch": block.get("dangerMismatch", ""),
            }
            for block in form.get("expertProjectDocuments", [])
        ],
        "expertEstimate": {
            "estimateNorms": (form.get("expertEstimate") or {}).get("estimateNorms", ""),
            "commonMismatches": [
                _strip_mismatch(m)
                for m in (form.get("expertEstimate") or {}).get("commonMismatches", [])
            ],
            "fullCalculationMismatches": [
                _strip_mismatch(m)
                for m in (form.get("expertEstimate") or {}).get("fullCalculationMismatches", [])
            ],
            "localCalculationMismatches": [
                _strip_mismatch(m)
                for m in (form.get("expertEstimate") or {}).get("localCalculationMismatches", [])
            ],
            "projectDocumentsMismatches": [
                _strip_mismatch_extended(m)
                for m in (form.get("expertEstimate") or {}).get("projectDocumentsMismatches", [])
            ],
            "basicMismatches": [
                _strip_mismatch(m)
                for m in (form.get("expertEstimate") or {}).get("basicMismatches", [])
            ],
        },
        "summary": form.get("summary") or {},
        "experts": [
            {
                "familyName": e.get("familyName", ""),
                "firstName": e.get("firstName", ""),
                "secondName": e.get("secondName", ""),
                "expertType": e.get("expertType", ""),
                "expertCertificate": e.get("expertCertificate", ""),
                "certificateBeginDate": e.get("certificateBeginDate", ""),
                "certificateEndDate": e.get("certificateEndDate", ""),
            }
            for e in form.get("experts", [])
        ],
    }
