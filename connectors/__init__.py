"""
TERRA-X Planetary Surface Systems & Geospatial Architecture
Connectors Package: Multi-Agency Earth & Planetary Observation Ingestion Pipeline
"""

from . import config  # Automatically loads .env into os.environ
from .license_engine import LicenseEngine, AssetRecord, LicenseClass
from .nasa_cmr import NASAConnector
from .usgs_stac import USGSLandsatConnector
from .cdse_stac import CDSEConnector
from .mars_psa import MarsPSAConnector
from .asia_connectors import JAXAConnector, HimawariConnector, ISROPRADANConnector
from .csa_connector import CSAConnector
from .pds_ode import PDSODEConnector

__all__ = [
    "LicenseEngine",
    "AssetRecord",
    "LicenseClass",
    "NASAConnector",
    "USGSLandsatConnector",
    "CDSEConnector",
    "MarsPSAConnector",
    "JAXAConnector",
    "HimawariConnector",
    "ISROPRADANConnector",
    "CSAConnector",
    "PDSODEConnector",
]

