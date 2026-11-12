import defusedxml.ElementTree as ET
from app.modules.sbom.parsers.base import BaseSBOMParser, ParsedComponent, ParsedDependency, ParsedSBOM, SBOMValidationError, ecosystem_from_purl

class CycloneDXXMLParser(BaseSBOMParser):
    format_name = "cyclonedx-xml"

    def can_parse(self, content: bytes, filename: str) -> bool:
        if not filename.lower().endswith(".xml"):
            return False
        return b"<bom" in content and b"cyclonedx" in content

    def parse(self, content: bytes) -> ParsedSBOM:
        try:
            root = ET.fromstring(content)
        except ET.ParseError as exc:
            raise SBOMValidationError(f"Invalid XML: {exc}") from exc

        ns = {"cdx": "http://cyclonedx.org/schema/bom/1.4"} # Simplified namespace handling
        if root.tag.endswith("bom") is False:
            raise SBOMValidationError("Not a CycloneDX XML document")

        spec_version = root.attrib.get("version", "1.4")
        components = []
        
        for comp in root.findall(".//{*}component"):
            name = comp.findtext("{*}name")
            if not name:
                continue
            purl = comp.findtext("{*}purl")
            components.append(ParsedComponent(
                name=name,
                version=comp.findtext("{*}version"),
                purl=purl,
                ecosystem=ecosystem_from_purl(purl),
                component_type=comp.attrib.get("type"),
                raw={}
            ))

        if not components:
            raise SBOMValidationError("CycloneDX XML contains no components")

        return ParsedSBOM(
            format=self.format_name, spec_version=spec_version, name=None,
            components=components, dependencies=[], metadata={}
        )
