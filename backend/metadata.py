"""Справочники для веб-интерфейса."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.tk_stub import install as install_tk_stub

install_tk_stub()

from climate_options import (
    CLIMATE_DISTRICT_OPTIONS,
    GEOLOGICAL_CONDITIONS_OPTIONS,
    SEISMIC_ACTIVITY_OPTIONS,
    SNOW_DISTRICT_OPTIONS,
    WIND_DISTRICT_OPTIONS,
)
from doc_types import DOC_TYPE_LABELS, DOC_TYPE_OPTIONS
from engineering_survey_options import ENGINEERING_SURVEY_TYPE_OPTIONS
from expert_type_options import EXPERT_TYPE_OPTIONS
from region_options import REGION_RF_OPTIONS
from summary_options import (
    ENGINEERING_SURVEY_SUMMARY_OPTIONS,
    ENGINEERING_SURVEYS_RESULTS_SUMMARY_OPTIONS,
    ESTIMATE_NORMS_AND_WORKS_SUMMARY_OPTIONS,
    ESTIMATE_VALIDATION_SUMMARY_OPTIONS,
    PROJECT_DOCS_DESIGN_ASSIGNMENT_OPTIONS,
    PROJECT_DOCS_ENGINEERING_SURVEYS_RESULTS_OPTIONS,
    PROJECT_DOCS_TECHNICAL_REQUIREMENTS_OPTIONS,
    PROJECT_DOCUMENTS_SUMMARY_OPTIONS,
)
import main as core


def _dict_options(options: dict) -> list[dict]:
    return [{"label": label, "value": value} for label, value in options.items() if value]


def _tuple_options(options: list[tuple]) -> list[dict]:
    return [{"label": label, "value": value} for value, label in options]


def get_all_options() -> dict:
    return {
        "examinationForm": _dict_options(core.EXAMINATION_FORM_OPTIONS),
        "examinationResult": _dict_options(core.EXAMINATION_RESULT_OPTIONS),
        "examinationObjectType": _dict_options(core.EXAMINATION_OBJECT_TYPE_OPTIONS),
        "examinationType": _dict_options(core.EXAMINATION_TYPE_OPTIONS),
        "constructionType": _dict_options(core.CONSTRUCTION_TYPE_OPTIONS),
        "examinationStage": _dict_options(core.EXAMINATION_STAGE_OPTIONS),
        "im": _dict_options(core.IM_OPTIONS),
        "capitalObjectType": _dict_options(core.CAPITAL_OBJECT_TYPE_OPTIONS),
        "docType": [{"label": label, "value": DOC_TYPE_OPTIONS[label]} for label in DOC_TYPE_LABELS],
        "declarantType": _tuple_options(core.DECLARANT_TYPE_OPTIONS),
        "technicalCustomerType": _tuple_options(core.TECHNICAL_CUSTOMER_TYPE_OPTIONS),
        "designerType": _tuple_options(core.DESIGNER_TYPE_OPTIONS),
        "financeType": _dict_options(core.FINANCE_TYPE_OPTIONS),
        "budgetType": _dict_options(core.BUDGET_TYPE_OPTIONS),
        "climateDistrict": _dict_options(CLIMATE_DISTRICT_OPTIONS),
        "geologicalConditions": _dict_options(GEOLOGICAL_CONDITIONS_OPTIONS),
        "windDistrict": _dict_options(WIND_DISTRICT_OPTIONS),
        "snowDistrict": _dict_options(SNOW_DISTRICT_OPTIONS),
        "seismicActivity": _dict_options(SEISMIC_ACTIVITY_OPTIONS),
        "engineeringSurveyType": _dict_options(ENGINEERING_SURVEY_TYPE_OPTIONS),
        "expertType": _dict_options(EXPERT_TYPE_OPTIONS),
        "regionRf": _dict_options(REGION_RF_OPTIONS),
        "engineeringSurveySummary": _dict_options(ENGINEERING_SURVEY_SUMMARY_OPTIONS),
        "projectDocumentsSummary": _dict_options(PROJECT_DOCUMENTS_SUMMARY_OPTIONS),
        "engineeringSurveysResultsSummary": _dict_options(ENGINEERING_SURVEYS_RESULTS_SUMMARY_OPTIONS),
        "projectDocsEngineeringSurveysResults": _dict_options(PROJECT_DOCS_ENGINEERING_SURVEYS_RESULTS_OPTIONS),
        "projectDocsDesignAssignment": _dict_options(PROJECT_DOCS_DESIGN_ASSIGNMENT_OPTIONS),
        "projectDocsTechnicalRequirements": _dict_options(PROJECT_DOCS_TECHNICAL_REQUIREMENTS_OPTIONS),
        "estimateNormsAndWorksSummary": _dict_options(ESTIMATE_NORMS_AND_WORKS_SUMMARY_OPTIONS),
        "estimateValidationSummary": _dict_options(ESTIMATE_VALIDATION_SUMMARY_OPTIONS),
        "estimatedCostMode": _tuple_options(core.ESTIMATED_COST_MODE_OPTIONS),
        "complexCostFields": [
            {"label": label, "key": key}
            for label, key in core.COMPLEX_ESTIMATED_COST_FIELDS
        ],
        "complexCostCommentFields": [
            {"label": label, "key": key}
            for label, key in core.OPTIONAL_COMPLEX_COST_COMMENT_FIELDS
        ],
        "addressFields": [{"label": label, "key": key} for label, key in core.CAPITAL_OBJECT_ADDRESS_FIELDS],
        "postAddressFields": [{"label": label, "key": key} for label, key in core.POST_ADDRESS_FIELDS],
    }
