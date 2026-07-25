from pathlib import Path
import xml.etree.ElementTree as ET


def test_verapdf_installer_configuration_is_valid_xml() -> None:
    root = ET.parse(Path("docker-install.xml")).getroot()

    assert root.tag == "AutomatedInstallation"
    assert root.find(".//installpath").text == "/opt/verapdf"

    cli_pack = root.find(".//pack[@name='veraPDF CLI']")
    assert cli_pack is not None
    assert cli_pack.attrib["selected"] == "true"
