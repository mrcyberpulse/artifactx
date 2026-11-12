from __future__ import annotations

import json
from typing import Any

from app.modules.sbom.parsers.base import (
    BaseSBOMParser,
    ParsedComponent,
    ParsedDependency,
    ParsedSBOM,
    SBOMValidationError,
    ecosystem_from_purl,
)

SUPPORTED_SPEC_VERSIONS = {"1.0", "1.1", "1.2", "1.3", "1.4", "1.5", "1.6"}


class CycloneDXJSONParser(BaseSBOMParser):
    format_name = "cyclonedx-json"

    def can_parse(self, content: bytes, filename: str) -> bool:
        if not filename.lower().endswith((".json", ".cdx", ".bom")):
            return False
        try:
            doc = json.loads(content)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return False
        return isinstance(doc, dict) and doc.get("bomFormat") == "CycloneDX"

    def parse(self, content: bytes) -> ParsedSBOM:
        try:
            doc: dict[str, Any] = json.loads(content)
        except json.JSONDecodeError as exc:
            raise SBOMValidationError(f"Invalid JSON: {exc}") from exc

        if doc.get("bomFormat") != "CycloneDX":
            raise SBOMValidationError("Not a CycloneDX document (bomFormat != 'CycloneDX')")

        spec_version = doc.get("specVersion")
        if spec_version not in SUPPORTED_SPEC_VERSIONS:
            raise SBOMValidationError(
                f"Unsupported CycloneDX specVersion: {spec_version!r}. "
                f"Supported: {sorted(SUPPORTED_SPEC_VERSIONS)}"
            )

        raw_components = doc.get("components") or []
        if not isinstance(raw_components, list) or not raw_components:
            raise SBOMValidationError("CycloneDX document contains no components")

        components: list[ParsedComponent] = []
        for i, c in enumerate(raw_components):
            if not isinstance(c, dict) or not c.get("name"):
                raise SBOMValidationError(f"Component at index {i} is missing a name")
            components.append(self._parse_component(c))

        dependencies: list[ParsedDependency] = []
        for dep in doc.get("dependencies") or []:
            if not isinstance(dep, dict) or not dep.get("ref"):
                continue
            dependencies.append(
                ParsedDependency(ref=dep["ref"], depends_on=list(dep.get("dependsOn") or []))
            )

        return ParsedSBOM(
            format=self.format_name,
            spec_version=spec_version,
            name=(doc.get("metadata") or {}).get("component", {}).get("name"),
            components=components,
            dependencies=dependencies,
            metadata={
                "serialNumber": doc.get("serialNumber"),
                "timestamp": (doc.get("metadata") or {}).get("timestamp"),
            },
        )

    def _parse_component(self, c: dict[str, Any]) -> ParsedComponent:
        license_str: str | None = None
        lic_list = c.get("licenses") or []
        if isinstance(lic_list, list):
            parts = []
            for entry in lic_list:
                if not isinstance(entry, dict):
                    continue
                lic = entry.get("license") or {}
                parts.append(lic.get("id") or lic.get("name") or "")
            license_str = ", ".join(p for p in parts if p) or None

        sha256: str | None = None
        for h in c.get("hashes") or []:
            if isinstance(h, dict) and h.get("alg") == "SHA-256":
                sha256 = h.get("content")
                break

        purl = c.get("purl")
        return ParsedComponent(
            name=c["name"],
            version=c.get("version"),
            purl=purl,
            ecosystem=ecosystem_from_purl(purl),
            supplier=(c.get("supplier") or {}).get("name"),
            publisher=c.get("publisher"),
            license=license_str,
            sha256=sha256,
            description=c.get("description"),
            component_type=c.get("type"),
            sbom_ref=c.get("bom-ref"),
            external_references=list(c.get("externalReferences") or []),
            raw=c,
        )
