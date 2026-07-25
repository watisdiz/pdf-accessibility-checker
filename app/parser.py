from __future__ import annotations

from xml.etree import ElementTree

from app.errors import VeraPDFExecutionError
from app.models import ValidationIssue, ValidationResult, ValidationSummary


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _first_descendant(root: ElementTree.Element, name: str) -> ElementTree.Element | None:
    return next((element for element in root.iter() if _local_name(element.tag) == name), None)


def _children(element: ElementTree.Element, name: str) -> list[ElementTree.Element]:
    return [child for child in element if _local_name(child.tag) == name]


def _text(element: ElementTree.Element | None) -> str:
    if element is None:
        return ""
    return " ".join(part.strip() for part in element.itertext() if part.strip())


def _as_int(value: str | None) -> int:
    try:
        return int(value or 0)
    except ValueError:
        return 0


def _profile_name(raw_name: str | None) -> str:
    name = raw_name or ""
    if "PDF/UA-1" in name.upper():
        return "PDF/UA-1"
    return name or "PDF/UA-1"


def parse_verapdf_report(xml_text: str, duration_ms: int) -> ValidationResult:
    try:
        root = ElementTree.fromstring(xml_text)
    except ElementTree.ParseError as exc:
        raise VeraPDFExecutionError("veraPDF palautti virheellisen XML-raportin.") from exc

    validation = _first_descendant(root, "validationReport")
    if validation is None:
        raise VeraPDFExecutionError("veraPDF-raportista puuttuu validointitulos.")

    details = _first_descendant(validation, "details")
    if details is None:
        raise VeraPDFExecutionError("veraPDF-raportista puuttuu validoinnin yhteenveto.")

    issues: list[ValidationIssue] = []
    for rule in _children(details, "rule"):
        contexts: list[str] = []
        for check in _children(rule, "check"):
            context = _first_descendant(check, "context")
            context_text = _text(context)
            if context_text:
                contexts.append(context_text)

        issues.append(
            ValidationIssue(
                specification=rule.attrib.get("specification", ""),
                clause=rule.attrib.get("clause", ""),
                test_number=rule.attrib.get("testNumber", ""),
                description=_text(_first_descendant(rule, "description")),
                object=_text(_first_descendant(rule, "object")),
                occurrences=_as_int(rule.attrib.get("failedChecks")) or len(contexts),
                contexts=contexts,
            )
        )

    compliant = validation.attrib.get("isCompliant", "false").lower() == "true"
    return ValidationResult(
        status="compliant" if compliant else "non_compliant",
        profile=_profile_name(validation.attrib.get("profileName")),
        duration_ms=max(0, duration_ms),
        summary=ValidationSummary(
            passed_rules=_as_int(details.attrib.get("passedRules")),
            failed_rules=_as_int(details.attrib.get("failedRules")),
            passed_checks=_as_int(details.attrib.get("passedChecks")),
            failed_checks=_as_int(details.attrib.get("failedChecks")),
        ),
        issues=issues,
    )
