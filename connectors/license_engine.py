"""
TERRA-X License Engine & Asset Provenance Tracking
Ensures strict compliance with licensing constraints, data provenance, and export restrictions.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, List, Optional
import hashlib
import json
from pathlib import Path


class LicenseClass(str, Enum):
    OPEN_PUBLIC_DOMAIN = "OPEN_PUBLIC_DOMAIN"
    OPEN_CC_BY_4 = "OPEN_CC_BY_4"
    OPEN_ESA_FREE = "OPEN_ESA_FREE"
    RESEARCH_NON_COMMERCIAL = "RESEARCH_NON_COMMERCIAL"
    NON_PROFIT_OPERATIONAL = "NON_PROFIT_OPERATIONAL"
    RESTRICTED_MANUAL_AUTH = "RESTRICTED_MANUAL_AUTH"
    CANADIAN_OPEN_GOV = "CANADIAN_OPEN_GOV"


@dataclass
class AssetRecord:
    asset_id: str
    agency: str
    sensor_or_collection: str
    stac_id: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    checksum_sha256: Optional[str] = None
    license_class: LicenseClass = LicenseClass.OPEN_PUBLIC_DOMAIN
    commercial_export_allowed: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "asset_id": self.asset_id,
            "agency": self.agency,
            "sensor_or_collection": self.sensor_or_collection,
            "stac_id": self.stac_id,
            "doi": self.doi,
            "url": self.url,
            "checksum_sha256": self.checksum_sha256,
            "license_class": self.license_class.value,
            "commercial_export_allowed": self.commercial_export_allowed,
            "metadata": self.metadata,
        }


class LicenseEngine:
    """Audits asset provenance and applies export guardrails."""

    def __init__(self, config_path: Optional[Path] = None):
        if config_path is None:
            config_path = Path(__file__).resolve().parent.parent / "manifests" / "licenses.json"
        
        self.config_path = config_path
        self.license_rules = {}
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                self.config = json.load(f)
                self.license_rules = self.config.get("license_classes", {})
        else:
            self.config = {"guardrails": {"filter_restricted_exports": True}}

    def register_asset(
        self,
        asset_id: str,
        agency: str,
        collection: str,
        license_class: LicenseClass,
        stac_id: Optional[str] = None,
        doi: Optional[str] = None,
        url: Optional[str] = None,
        data_bytes: Optional[bytes] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AssetRecord:
        checksum = None
        if data_bytes:
            checksum = hashlib.sha256(data_bytes).hexdigest()
        
        rule = self.license_rules.get(license_class.value, {})
        export_allowed = rule.get("export_allowed", True)
        if license_class == LicenseClass.RESTRICTED_MANUAL_AUTH:
            export_allowed = False

        record = AssetRecord(
            asset_id=asset_id,
            agency=agency,
            sensor_or_collection=collection,
            stac_id=stac_id or f"urn:terrax:{agency.lower()}:{asset_id}",
            doi=doi,
            url=url,
            checksum_sha256=checksum,
            license_class=license_class,
            commercial_export_allowed=export_allowed,
            metadata=metadata or {},
        )
        return record

    def validate_for_export(self, assets: List[AssetRecord]) -> List[AssetRecord]:
        """Filters out restricted assets from export packages."""
        allowed = []
        for asset in assets:
            if asset.license_class == LicenseClass.RESTRICTED_MANUAL_AUTH:
                continue
            if not asset.commercial_export_allowed:
                continue
            allowed.append(asset)
        return allowed

