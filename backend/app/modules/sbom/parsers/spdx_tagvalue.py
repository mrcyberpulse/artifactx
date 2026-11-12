from app.modules.sbom.parsers.base import BaseSBOMParser, ParsedComponent, ParsedDependency, ParsedSBOM, SBOMValidationError, ecosystem_from_purl

class SPDXTagValueParser(BaseSBOMParser):
    format_name = "spdx-tag-value"

    def can_parse(self, content: bytes, filename: str) -> bool:
        if not filename.lower().endswith((".spdx", ".txt")):
            return False
        try:
            text = content.decode("utf-8")
            return "SPDXVersion:" in text
        except UnicodeDecodeError:
            return False

    def parse(self, content: bytes) -> ParsedSBOM:
        text = content.decode("utf-8")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        
        components = []
        current_pkg = {}
        
        for line in lines:
            if line.startswith("PackageName:"):
                if current_pkg.get("name"):
                    components.append(self._build_comp(current_pkg))
                current_pkg = {"name": line.split(":", 1)[1].strip()}
            elif line.startswith("PackageVersion:") and current_pkg is not None:
                current_pkg["version"] = line.split(":", 1)[1].strip()
            elif line.startswith("PackageSupplier:") and current_pkg is not None:
                current_pkg["supplier"] = line.split(":", 1)[1].strip()

        if current_pkg.get("name"):
            components.append(self._build_comp(current_pkg))

        if not components:
            raise SBOMValidationError("SPDX tag-value contains no packages")

        return ParsedSBOM(
            format=self.format_name, spec_version="SPDX-2.3", name=None,
            components=components, dependencies=[], metadata={}
        )
        
    def _build_comp(self, pkg: dict) -> ParsedComponent:
        return ParsedComponent(
            name=pkg["name"],
            version=pkg.get("version"),
            supplier=pkg.get("supplier"),
            ecosystem=None,
            raw=pkg
        )
