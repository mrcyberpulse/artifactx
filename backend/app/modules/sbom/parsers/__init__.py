"""Modular SBOM parser registry. Each format is an independent adapter."""
from app.modules.sbom.parsers.base import (
    BaseSBOMParser,
    ParsedComponent,
    ParsedDependency,
    ParsedSBOM,
    SBOMValidationError,
)
from app.modules.sbom.parsers.cyclonedx_json import CycloneDXJSONParser
from app.modules.sbom.parsers.cyclonedx_xml import CycloneDXXMLParser
from app.modules.sbom.parsers.spdx_json import SPDXJSONParser
from app.modules.sbom.parsers.spdx_tagvalue import SPDXTagValueParser

# First parser whose can_parse() returns True wins.
PARSERS: list[BaseSBOMParser] = [
    CycloneDXJSONParser(),
    SPDXJSONParser(),
    CycloneDXXMLParser(),
    SPDXTagValueParser(),
]


def detect_and_parse(content: bytes, filename: str) -> ParsedSBOM:
    for parser in PARSERS:
        if parser.can_parse(content, filename):
            return parser.parse(content)
    raise SBOMValidationError(
        f"Unsupported or unrecognised SBOM format for file {filename!r}. "
        "Supported: CycloneDX JSON/XML, SPDX JSON/Tag-Value."
    )
