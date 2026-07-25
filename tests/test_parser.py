from app.parser import parse_verapdf_report


def test_parser_normalizes_non_compliant_report():
    payload = """<?xml version="1.0" encoding="utf-8"?>
    <report>
      <jobs>
        <job>
          <validationReport profileName="PDF/UA-1 validation profile" isCompliant="false">
            <details passedRules="85" failedRules="1" passedChecks="541" failedChecks="2">
              <rule specification="ISO 14289-1:2014" clause="7.1" testNumber="1" failedChecks="2">
                <description>The document shall be tagged.</description>
                <object>PDDocument</object>
                <check status="failed"><context>root/document[0]</context></check>
                <check status="failed"><context>root/document[1]</context></check>
              </rule>
            </details>
          </validationReport>
        </job>
      </jobs>
    </report>"""

    result = parse_verapdf_report(payload, duration_ms=1234)

    assert result.status == "non_compliant"
    assert result.profile == "PDF/UA-1"
    assert result.duration_ms == 1234
    assert result.summary.failed_rules == 1
    assert result.summary.failed_checks == 2
    assert len(result.issues) == 1
    assert result.issues[0].occurrences == 2
    assert result.issues[0].contexts == ["root/document[0]", "root/document[1]"]


def test_parser_normalizes_compliant_report():
    payload = """<report><jobs><job>
      <validationReport profileName="PDF/UA-1 validation profile" isCompliant="true">
        <details passedRules="86" failedRules="0" passedChecks="543" failedChecks="0" />
      </validationReport>
    </job></jobs></report>"""

    result = parse_verapdf_report(payload, duration_ms=400)

    assert result.status == "compliant"
    assert result.summary.failed_rules == 0
    assert result.issues == []
