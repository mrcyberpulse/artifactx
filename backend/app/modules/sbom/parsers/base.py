from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


class SBOMValidationError(ValueError):
    """Raised when an SBOM document fails validation."""


@dataclass
class ParsedComponent:
    name: str
    version: str | None = None
    purl: str | None = None
    ecosystem: str | None = None
    supplier: str | None = None
    publisher: str | None = None
    license: str | None = None
    sha256: str | None = None
    description: str | None = None
    component_type: str | None = None
    sbom_ref: str | None = None
    external_references: list[dict[str, Any]] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class ParsedDependency:
    ref: str
    depends_on: list[str] = field(default_factory=list)


@dataclass
class ParsedSBOM:
    format: str
    spec_version: str | None
    name: str | None
    components: list[ParsedComponent]
    dependencies: list[ParsedDependency]
    metadata: dict[str, Any] = field(default_factory=dict)


def ecosystem_from_purl(purl: str | None) -> str | None:
    if not purl or not purl.startswith("pkg:"):
        return None
    body = purl[len("pkg:"):]
    # pkg:npm/foo@1.0.0  →  npm
    head = body.split("/", 1)[0]
    return head.split("@", 1)[0] or None


class BaseSBOMParser(ABC):
    format_name: str = "unknown"

    @abstractmethod
    def can_parse(self, content: bytes, filename: str) -> bool:
        """Cheap sniffing — does this parser think it can handle the content?"""

    @abstractmethod
    def parse(self, content: bytes) -> ParsedSBOM:
        """Parse bytes into a ParsedSBOM. Raises SBOMValidationError on failure."""
