"""Тесты сборки conclusion.xml на данных из conclusion.xml."""
from __future__ import annotations

import glob
import shutil
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.conclusion_builder import ValidationError, render_conclusion_xml_string
from backend.xml_to_payload import load_payload_from_xml

CONCLUSION_XML = ROOT / "conclusion.xml"
SKIP_REASON = "Файл conclusion.xml не найден в корне проекта"


def _find_stub_files() -> tuple[Path, Path]:
    pdf_candidates = [
        ROOT / "2.pdf",
        ROOT / "1774366449_3.pdf",
    ]
    pdf_source = next((p for p in pdf_candidates if p.is_file()), None)
    if pdf_source is None:
        raise FileNotFoundError("Не найден stub PDF (2.pdf или 1774366449_3.pdf)")

    sig_matches = glob.glob(str(ROOT / "*.sig"))
    if not sig_matches:
        raise FileNotFoundError("Не найден файл .sig в корне проекта")
    return pdf_source, Path(sig_matches[0])


def normalize_payload_for_build(payload: dict) -> dict:
    """Дополняет payload данными, обязательными для сборщика, но отсутствующими в EGRZ XML."""
    normalized = dict(payload)
    documents = []
    for doc in payload.get("documents", []):
        item = dict(doc)
        if not (item.get("docDate") or "").strip():
            item["docDate"] = "2020-01-01"
        documents.append(item)
    normalized["documents"] = documents
    return normalized


def prepare_upload_dir(payload: dict, upload_dir: Path) -> None:
    """Копирует stub-файлы под именами из payload.documents."""
    pdf_source, sig_source = _find_stub_files()
    upload_dir.mkdir(parents=True, exist_ok=True)

    for doc in payload.get("documents", []):
        file_name = doc.get("fileName")
        if file_name:
            shutil.copy2(pdf_source, upload_dir / file_name)
        for sign_name in doc.get("signFileNames") or []:
            shutil.copy2(sig_source, upload_dir / sign_name)


def normalize_xml_tree(xml_text: str, *, ignore_tags: set[str] | None = None) -> list[tuple[str, str]]:
    """Плоское представление XML для сравнения (путь тега → текст)."""
    ignore_tags = ignore_tags or set()
    root = ET.fromstring(xml_text.split("?>", 2)[-1].lstrip())
    items: list[tuple[str, str]] = []

    def walk(elem: ET.Element, path: str) -> None:
        if elem.tag in ignore_tags or path.endswith("/ConclusionGUID"):
            return
        text = (elem.text or "").strip()
        if text and not list(elem):
            items.append((path, text))
        for child in elem:
            walk(child, f"{path}/{child.tag}")

    walk(root, root.tag)
    return sorted(items)


@pytest.fixture(scope="module")
def source_payload() -> dict:
    if not CONCLUSION_XML.is_file():
        pytest.skip(SKIP_REASON)
    return load_payload_from_xml(CONCLUSION_XML)


@pytest.fixture(scope="module")
def buildable_payload(source_payload: dict) -> dict:
    return normalize_payload_for_build(source_payload)


@pytest.fixture(scope="module")
def source_root() -> ET.Element:
    if not CONCLUSION_XML.is_file():
        pytest.skip(SKIP_REASON)
    return ET.parse(CONCLUSION_XML).getroot()


class TestXmlToPayload:
    def test_parse_key_sections(self, source_payload: dict) -> None:
        assert source_payload["expertOrganization"]["orgInn"] == "1234567890"
        assert source_payload["examinationObject"]["examinationObjectType"] == "2"
        assert len(source_payload["examinationObject"]["examinationTypes"]) == 2
        assert len(source_payload["documents"]) == 20
        assert len(source_payload["experts"]) == 1
        assert source_payload["ecology"]["needExpertise"] == "да"
        assert len(source_payload["cadastralNumbers"]) == 1
        assert source_payload["declarant"]["orgInn"] == "1243124235"
        assert len(source_payload["designers"]) == 1
        assert source_payload["capitalObject"]["functionsClass"] == "01.02.001.001"

    def test_parse_finance_and_climate(self, source_payload: dict) -> None:
        assert source_payload["finance"][0]["financeType"] == "1"
        assert source_payload["climateConditions"]["climateDistricts"] == ["II"]
        assert source_payload["estimatedCost"]["mode"] == "complex"

    def test_parse_summary(self, source_payload: dict) -> None:
        summary = source_payload["summary"]
        assert "соответствует требованиям технических регламентов" in summary["projectDocumentsSummary"]
        pd = summary["examinationProjectDocumentsSummary"]
        assert pd["designAssignment"]


class TestBuildFromPayload:
    def test_build_without_validation_error(self, buildable_payload: dict) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            prepare_upload_dir(buildable_payload, Path(tmp))
            xml_text, output_files = render_conclusion_xml_string(buildable_payload, tmp)

        assert xml_text.startswith('<?xml version="1.0" encoding="UTF-8"?>')
        assert "conclusion-01-03.xsd" in xml_text
        assert len(output_files) > 0

        root = ET.fromstring(xml_text.split("?>", 2)[-1].lstrip())
        assert root.find("ExpertOrganization/OrgINN").text == "1234567890"
        assert len(root.findall("Documents/Document")) == 20
        assert len(root.findall("Experts/Expert")) == 1
        assert root.find("EcologyExpertise/NeedExpertise").text == "да"

    def test_roundtrip_core_fields(self, buildable_payload: dict, source_root: ET.Element) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            prepare_upload_dir(buildable_payload, Path(tmp))
            built_xml, _ = render_conclusion_xml_string(buildable_payload, tmp)

        with open(CONCLUSION_XML, encoding="utf-8") as f:
            source_xml = f.read()

        ignore = {"FileChecksum", "ConclusionGUID", "SchemaLink"}
        source_items = normalize_xml_tree(source_xml, ignore_tags=ignore)
        built_items = normalize_xml_tree(built_xml, ignore_tags=ignore)

        source_map = dict(source_items)
        built_map = dict(built_items)

        compare_paths = [
            "Conclusion/ExpertOrganization/OrgFullName",
            "Conclusion/ExpertOrganization/OrgINN",
            "Conclusion/Approver/FamilyName",
            "Conclusion/ExaminationObject/ExaminationObjectType",
            "Conclusion/ExaminationObject/Name",
            "Conclusion/Declarant/Organization/OrgINN",
            "Conclusion/Object/FunctionsClass",
            "Conclusion/Summary/ProjectDocumentsSummary",
        ]
        for path in compare_paths:
            assert path in source_map, f"В исходном XML нет {path}"
            assert path in built_map, f"В собранном XML нет {path}"
            assert built_map[path] == source_map[path], f"Расхождение в {path}"

        built_root = ET.fromstring(built_xml.split("?>", 2)[-1].lstrip())
        assert len(source_root.findall("Documents/Document")) == len(
            built_root.findall("Documents/Document")
        )

    def test_missing_documents_raises(self, source_payload: dict) -> None:
        payload = dict(source_payload)
        payload["documents"] = []
        with tempfile.TemporaryDirectory() as tmp:
            with pytest.raises(ValidationError, match="Добавьте хотя бы один документ"):
                render_conclusion_xml_string(payload, tmp)
