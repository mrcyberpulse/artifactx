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


class SPDXJSONParser(BaseSBOMParser):
    format_name = "spdx-json"

    def can_parse(self, content: bytes, filename: str) -> bool:
        if not filename.lower().endswith(".json"):
            return False
        try:
            doc = json.loads(content)
        except (json.JSONDecodeError, UnicodeDecodeError):
            return False
        return isinstance(doc, dict) and str(doc.get("spdxVersion", "")).startswith("SPDX-")

    def parse(self, content: bytes) -> ParsedSBOM:
        try:
            doc: dict[str, Any] = json.loads(content)
        except json.JSONDecodeError as exc:
            raise SBOMValidationError(f"Invalid JSON: {exc}") from exc

        spdx_version = doc.get("spdxVersion")
        if not spdx_version or not str(spdx_version).startswith("SPDX-"):
            raise SBOMValidationError("Not an SPDX document (missing/invalid spdxVersion)")

        packages = doc.get("packages") or []
        if not isinstance(packages, list) or not packages:
            raise SBOMValidationError("SPDX document contains no packages")

        components: list[ParsedComponent] = []
        for i, p in enumerate(packages):
            if not isinstance(p, dict) or not p.get("name"):
                raise SBOMValidationError(f"Package at index {i} is missing a name")
            components.append(self._parse_package(p))

        dependencies = self._parse_relationships(doc)

        return ParsedSBOM(
            format=self.format_name,
            spec_version=str(spdx_version),
            name=doc.get("name"),
            components=components,
            dependencies=dependencies,
            metadata={
                "spdxId": doc.get("SPDXID"),
                "created": (doc.get("creationInfo") or {}).get("created"),
                "documentNamespace": doc.get("documentNamespace"),
            },
        )

    def _parse_package(self, p: dict[str, Any]) -> ParsedComponent:
        purl: str | None = None
        external_refs: list[dict[str, Any]] = []
        for ref in p.get("externalRefs") or []:
            if isinstance(ref, dict):
                external_refs.append(ref)
                if ref.get("referenceType") == "purl" and not purl:
                    purl = ref.get("referenceLocator")

        sha256: str | None = None
        for checksum in p.get("checksums") or []:
            if isinstance(checksum, dict) and checksum.get("algorithm") == "SHA256":
                sha256 = checksum.get("checksumValue")
                break

        license_str = p.get("licenseDeclared") or p.get("licenseConcluded")
        if license_str and str(license_str).startswith("NOASSERTION"):
            license_str = None

        return ParsedComponent(
            name=p["name"],
            version=p.get("versionInfo"),
            purl=purl,
            ecosystem=ecosystem_from_purl(purl),
            supplier=p.get("supplier"),
            publisher=None,
            license=license_str,
            sha256=sha256,
            description=p.get("description"),
            component_type=p.get("primaryPackagePurpose"),
            sbom_ref=p.get("SPDXID"),
            external_references=external_refs,
            raw=p,
        )

    def _parse_relationships(self, doc: dict[str, Any]) -> list[ParsedDependency]:
        deps_map: dict[str, list[str]] = {}
        for rel in doc.get("relationships") or []:
            if not isinstance(rel, dict):
                continue
            rel_type = rel.get("relationshipType")
            if rel_type not in ("DEPENDS_ON", "DEPENDENCY_OF"):
                continue
            src, dst = rel.get("spdxElementId"), rel.get("relatedSpdxElement")
            if not src or not dst:
                continue
            if rel_type == "DEPENDENCY_OF":
                src, dst = dst, src
            deps_map.setdefault(src, []).append(dst)
        return [ParsedDependency(ref=k, depends_on=v) for k, v in deps_map.items()]
