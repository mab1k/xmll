"""Преобразование JSON payload (camelCase) в dict для append_* функций main.py."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.tk_stub import install as install_tk_stub

install_tk_stub()
import main as core

_ADDRESS_KEYS = [key for _, key in core.CAPITAL_OBJECT_ADDRESS_FIELDS]
_POST_ADDRESS_KEYS = [key for _, key in core.POST_ADDRESS_FIELDS]
_COMPLEX_COST_KEYS = [key for _, key in core.COMPLEX_ESTIMATED_COST_FIELDS]
_COMPLEX_COST_COMMENT_KEYS = [key for _, key in core.OPTIONAL_COMPLEX_COST_COMMENT_FIELDS]


def _strip(value) -> str:
    return (value or "").strip() if value is not None else ""


def _get(data: dict, *keys: str, default=""):
    for key in keys:
        if key in data and data[key] is not None:
            return data[key]
    return default


def _get_complex_field(data: dict, pascal_key: str) -> str:
    camel_key = pascal_key[0].lower() + pascal_key[1:] if pascal_key else pascal_key
    return _strip(_get(data, pascal_key, camel_key))


def address_to_xml(data: dict | None) -> dict:
    if not data:
        return {key: "" for key in _ADDRESS_KEYS}
    return {key: _strip(_get(data, key)) for key in _ADDRESS_KEYS}


def post_address_to_xml(data: dict | None) -> dict:
    if not data:
        return {key: "" for key in _POST_ADDRESS_KEYS}
    return {key: _strip(_get(data, key)) for key in _POST_ADDRESS_KEYS}


def entity_to_xml(data: dict | None) -> dict:
    """Организация / иностранная организация / ИП / физлицо."""
    if not data:
        return {"type": "organization"}

    entity_type = _get(data, "type", default="organization")
    email = _strip(_get(data, "email"))

    if entity_type == "organization":
        return {
            "type": entity_type,
            "org_full_name": _strip(_get(data, "orgFullName", "org_full_name")),
            "org_ogrn": _strip(_get(data, "orgOgrn", "org_ogrn")),
            "org_inn": _strip(_get(data, "orgInn", "org_inn")),
            "org_kpp": _strip(_get(data, "orgKpp", "org_kpp")),
            "email": email,
            "address": address_to_xml(_get(data, "address", default={})),
        }

    if entity_type == "foreign_organization":
        return {
            "type": entity_type,
            "org_full_name": _strip(_get(data, "orgFullName", "org_full_name")),
            "org_inn": _strip(_get(data, "orgInn", "org_inn")),
            "org_kpp": _strip(_get(data, "orgKpp", "org_kpp")),
            "email": email,
            "address": address_to_xml(_get(data, "address", default={})),
        }

    if entity_type == "ip":
        return {
            "type": entity_type,
            "family_name": _strip(_get(data, "familyName", "family_name")),
            "first_name": _strip(_get(data, "firstName", "first_name")),
            "second_name": _strip(_get(data, "secondName", "second_name")),
            "ogrnip": _strip(_get(data, "ogrnip")),
            "email": email,
            "post_address": post_address_to_xml(_get(data, "postAddress", "post_address", default={})),
        }

    return {
        "type": "person",
        "family_name": _strip(_get(data, "familyName", "family_name")),
        "first_name": _strip(_get(data, "firstName", "first_name")),
        "second_name": _strip(_get(data, "secondName", "second_name")),
        "snils": _strip(_get(data, "snils")),
        "email": email,
        "post_address": post_address_to_xml(_get(data, "postAddress", "post_address", default={})),
    }


def technical_customer_to_xml(data: dict | None) -> dict:
    entity = entity_to_xml(data)
    if entity["type"] == "person":
        entity["type"] = "organization"
    return entity


def mismatch_to_xml(data: dict) -> dict:
    return {
        "summary": _strip(_get(data, "summary")),
        "part": _strip(_get(data, "part")),
        "link": _strip(_get(data, "link")),
    }


def mismatch_extended_to_xml(data: dict) -> dict:
    result = mismatch_to_xml(data)
    result["expert_type"] = _strip(_get(data, "expertType", "expert_type"))
    return result


def tei_to_xml(data: dict) -> dict:
    return {
        "name": _strip(_get(data, "name")),
        "measure": _strip(_get(data, "measure")),
        "value": _strip(_get(data, "value")),
    }


def object_part_to_xml(data: dict) -> dict:
    addresses_raw = _get(data, "addresses", default=[]) or []
    tei_raw = _get(data, "tei", default=[]) or []
    return {
        "name": _strip(_get(data, "name")),
        "addresses": [address_to_xml(addr) for addr in addresses_raw if any(address_to_xml(addr).values())],
        "functions_class": _strip(_get(data, "functionsClass", "functions_class")),
        "tei": [tei_to_xml(item) for item in tei_raw if any(tei_to_xml(item).values())],
    }


def capital_object_to_xml(data: dict | None) -> dict | None:
    if not data:
        return None
    addresses_raw = _get(data, "addresses", default=[]) or []
    tei_raw = _get(data, "tei", default=[]) or []
    parts_raw = _get(data, "parts", default=[]) or []
    return {
        "name": _strip(_get(data, "name")),
        "addresses": [address_to_xml(addr) for addr in addresses_raw if any(address_to_xml(addr).values())],
        "type": _strip(_get(data, "type")),
        "functions_class": _strip(_get(data, "functionsClass", "functions_class")),
        "tei": [tei_to_xml(item) for item in tei_raw if any(tei_to_xml(item).values())],
        "parts": [object_part_to_xml(part) for part in parts_raw],
    }


def previous_conclusion_to_xml(data: dict) -> dict:
    return {
        "date": core.format_doc_date(_strip(_get(data, "date"))),
        "number": _strip(_get(data, "number")),
        "number_format": _get(data, "numberFormat", "number_format", default="egrz"),
        "object_type": _strip(_get(data, "objectType", "object_type")),
        "name": _strip(_get(data, "name")),
        "result": _strip(_get(data, "result")),
    }


def previous_simple_conclusion_to_xml(data: dict) -> dict:
    return {
        "date": core.format_doc_date(_strip(_get(data, "date"))),
        "number": _strip(_get(data, "number")),
        "object_type": _strip(_get(data, "objectType", "object_type")),
        "result": _strip(_get(data, "result")),
    }


def party_item_to_xml(data: dict) -> dict:
    party_type = _get(data, "partyType", "party_type", default="developer")
    entity_raw = _get(data, "entity", default={})
    if party_type == "technical_customer":
        entity = technical_customer_to_xml(entity_raw)
    else:
        entity = entity_to_xml(entity_raw)
    return {"party_type": party_type, "entity": entity}


def complex_cost_to_xml(data: dict | None) -> dict:
    if not data:
        data = {}
    result = {}
    for key in _COMPLEX_COST_KEYS + _COMPLEX_COST_COMMENT_KEYS:
        result[key] = _get_complex_field(data, key)
    return result


def estimated_cost_to_xml(data: dict | None) -> dict | None:
    if not data:
        return None
    return {
        "currency": _strip(_get(data, "currency")),
        "mode": _get(data, "mode", default="complete"),
        "complete_before": _strip(_get(data, "completeBefore", "complete_before")),
        "complete_post": _strip(_get(data, "completePost", "complete_post")),
        "complex_before": complex_cost_to_xml(_get(data, "complexBefore", "complex_before", default={})),
        "complex_post": complex_cost_to_xml(_get(data, "complexPost", "complex_post", default={})),
    }


def climate_to_xml(data: dict | None) -> dict | None:
    if not data:
        return None
    seismic_raw = _get(data, "seismicCalculated", "seismic_calculated")
    seismic_calculated = None
    if seismic_raw and _get(seismic_raw, "enabled", default=False):
        seismic_calculated = {
            "min": _strip(_get(seismic_raw, "min")),
            "max": _strip(_get(seismic_raw, "max")),
        }
    return {
        "climate_districts": [v for v in (_get(data, "climateDistricts", "climate_districts", default=[]) or []) if v],
        "geological_conditions": [
            v for v in (_get(data, "geologicalConditions", "geological_conditions", default=[]) or []) if v
        ],
        "wind_districts": [v for v in (_get(data, "windDistricts", "wind_districts", default=[]) or []) if v],
        "snow_districts": [v for v in (_get(data, "snowDistricts", "snow_districts", default=[]) or []) if v],
        "seismic_activities": [
            v for v in (_get(data, "seismicActivities", "seismic_activities", default=[]) or []) if v
        ],
        "seismic_calculated": seismic_calculated,
        "note": _strip(_get(data, "note")),
    }


def designer_to_xml(data: dict) -> dict:
    entity = entity_to_xml(data)
    entity["general"] = _strip(_get(data, "general"))
    return entity


def eepd_use_to_xml(data: dict) -> dict:
    return {
        "note": _strip(_get(data, "note")),
        "number": _strip(_get(data, "number")),
        "number_format": _get(data, "numberFormat", "number_format", default="egrz"),
        "date": core.format_doc_date(_strip(_get(data, "date"))),
    }


def engineering_survey_address_to_xml(data: dict) -> dict:
    return {
        "region": _strip(_get(data, "region")),
        "district": _strip(_get(data, "district")),
    }


def expert_engineering_surveys_to_xml(data: dict) -> dict:
    mismatches_raw = _get(data, "normsMismatches", "norms_mismatches", default=[]) or []
    norms_mismatches = []
    for m in mismatches_raw:
        converted = mismatch_to_xml(m)
        if core.is_mismatch_filled(converted):
            norms_mismatches.append(converted)
    return {
        "survey_type": _strip(_get(data, "surveyType", "survey_type")),
        "norms_mismatches": norms_mismatches,
    }


def expert_project_documents_to_xml(data: dict) -> dict:
    return {
        "expert_type": _strip(_get(data, "expertType", "expert_type")),
        "danger_solutions": _strip(_get(data, "dangerSolutions", "danger_solutions")),
        "engineering_survey_mismatches": [
            mismatch_to_xml(m)
            for m in (_get(data, "engineeringSurveyMismatches", "engineering_survey_mismatches", default=[]) or [])
            if core.is_mismatch_filled(mismatch_to_xml(m))
        ],
        "project_task_mismatches": [
            mismatch_to_xml(m)
            for m in (_get(data, "projectTaskMismatches", "project_task_mismatches", default=[]) or [])
            if core.is_mismatch_filled(mismatch_to_xml(m))
        ],
        "norms_mismatches": [
            mismatch_to_xml(m)
            for m in (_get(data, "normsMismatches", "norms_mismatches", default=[]) or [])
            if core.is_mismatch_filled(mismatch_to_xml(m))
        ],
        "danger_mismatch": _strip(_get(data, "dangerMismatch", "danger_mismatch")),
    }


def expert_estimate_to_xml(data: dict | None) -> dict | None:
    if not data:
        return None

    def _filled_mismatches(key_camel: str, key_snake: str) -> list[dict]:
        raw = _get(data, key_camel, key_snake, default=[]) or []
        return [mismatch_to_xml(m) for m in raw if core.is_mismatch_filled(mismatch_to_xml(m))]

    def _filled_extended(key_camel: str, key_snake: str) -> list[dict]:
        raw = _get(data, key_camel, key_snake, default=[]) or []
        converted = [mismatch_extended_to_xml(m) for m in raw]
        return [m for m in converted if core.is_mismatch_extended_filled(m)]

    return {
        "estimate_norms": _strip(_get(data, "estimateNorms", "estimate_norms")),
        "common_mismatches": _filled_mismatches("commonMismatches", "common_mismatches"),
        "full_calculation_mismatches": _filled_mismatches("fullCalculationMismatches", "full_calculation_mismatches"),
        "local_calculation_mismatches": _filled_mismatches("localCalculationMismatches", "local_calculation_mismatches"),
        "project_documents_mismatches": _filled_extended("projectDocumentsMismatches", "project_documents_mismatches"),
        "basic_mismatches": _filled_mismatches("basicMismatches", "basic_mismatches"),
    }


def finance_item_to_xml(item: dict) -> dict:
    entry = {
        "finance_type": _strip(_get(item, "financeType", "finance_type")),
        "budget_type": _strip(_get(item, "budgetType", "budget_type")),
        "finance_size": _strip(_get(item, "financeSize", "finance_size")),
        "owner": None,
    }
    owner = item.get("owner")
    if owner:
        owner_xml = technical_customer_to_xml(owner)
        if core.is_technical_customer_filled(owner_xml):
            entry["owner"] = owner_xml
    return entry


def declarant_to_xml(data: dict) -> dict:
    return entity_to_xml(data)


def experts_to_xml(experts: list[dict]) -> list[dict]:
    return [
        {
            "family_name": e["familyName"],
            "first_name": e["firstName"],
            "second_name": _strip(e.get("secondName")),
            "expert_type": e["expertType"],
            "expert_certificate": e["expertCertificate"],
            "certificate_begin_date": core.format_doc_date(e["certificateBeginDate"]),
            "certificate_end_date": core.format_doc_date(e["certificateEndDate"]),
        }
        for e in experts
    ]


def summary_to_xml(summary: dict) -> dict:
    pd = summary.get("examinationProjectDocumentsSummary") or {}
    return {
        "engineering_survey_summary": summary.get("engineeringSurveySummary") or "",
        "engineering_survey_summary_date": _strip(summary.get("engineeringSurveySummaryDate")),
        "engineering_survey_types": summary.get("engineeringSurveyTypes") or [],
        "project_documents_summary": summary.get("projectDocumentsSummary") or "",
        "project_documents_summary_date": _strip(summary.get("projectDocumentsSummaryDate")),
        "estimate_variant": summary.get("estimateVariant") or "standard",
        "estimate_norms_and_works_summary": summary.get("estimateNormsAndWorksSummary") or "",
        "estimate_summary": summary.get("estimateSummary") or "",
        "estimate_norms_and_works_summary_1315": _strip(summary.get("estimateNormsAndWorksSummary1315")),
        "estimate_summary_1315": _strip(summary.get("estimateSummary1315")),
        "examination_engineering_surveys_results_summary": summary.get("examinationEngineeringSurveysResultsSummary") or "",
        "examination_project_documents_summary": {
            "engineering_surveys_results": pd.get("engineeringSurveysResults") or "",
            "design_assignment": pd.get("designAssignment") or "",
            "technical_requirements": pd.get("technicalRequirements") or "",
        },
        "examination_estimate_variant": summary.get("examinationEstimateVariant") or "standard",
        "examination_estimate_summary": summary.get("examinationEstimateSummary") or "",
        "examination_estimate_summary_1315": _strip(summary.get("examinationEstimateSummary1315")),
    }


def filter_filled(items: list[dict], is_filled) -> list[dict]:
    return [item for item in items if is_filled(item)]
