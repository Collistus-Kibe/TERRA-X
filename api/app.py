"""
TERRA-X FastAPI Geospatial Backend & STAC Service
Provides RESTful discovery, dynamic what-if parameter re-ranking,
Site Passport generation, NASA Test Recipe export, and Field-Kit re-scoring.
"""

# Compatibility patch for Starlette 1.8+ with FastAPI 0.115
import starlette.routing
_orig_router_init = starlette.routing.Router.__init__
def _compat_router_init(self, *args, **kwargs):
    kwargs.pop("on_startup", None)
    kwargs.pop("on_shutdown", None)
    return _orig_router_init(self, *args, **kwargs)
starlette.routing.Router.__init__ = _compat_router_init

from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel, Field
import json

from targets.registry import TargetRegistry
from engine.pipeline import TerraXPipeline
from engine.field_kit import FieldKitEngine
from connectors.license_engine import LicenseEngine, LicenseClass

app = FastAPI(
    title="TERRA-X Planetary Surface Systems Discovery API",
    description="Reproducible, uncertainty-aware Functional Analog discovery system for Moon & Mars exploration (NASA Space Apps 2026).",
    version="1.0.0",
)

# Enable CORS for MapLibre frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = TerraXPipeline()
target_reg = TargetRegistry()
license_eng = LicenseEngine()


class DiscoverRequest(BaseModel):
    target_id: str = Field(default="MOON_SOUTH_POLE_SHACKLETON", description="Target planetary site ID")
    function_profile: str = Field(default="MOBILITY", description="MOBILITY, CONSTRUCTION_ISRU, LANDING_PAD_PSI, HUMAN_OPS_THERMAL, PNT_DENIED_NAV, ASTROBIO")
    wheel_diameter_m: float = Field(default=0.50, ge=0.1, le=2.5, description="Rover wheel diameter in meters")
    contact_pressure_kpa: float = Field(default=25.0, ge=1.0, le=200.0, description="Contact/bearing pressure in kPa")
    footprint_width_m: float = Field(default=0.30, ge=0.05, le=5.0, description="Footprint/wheel width in meters")
    test_duration_days: int = Field(default=14, ge=1, le=180, description="Test campaign duration in days")
    top_k: int = Field(default=15, ge=1, le=50, description="Number of analog sites to retrieve")
    enforce_mmr: bool = Field(default=True, description="Enforce Maximal Marginal Relevance spatial diversity")


class FieldKitUploadRequest(BaseModel):
    cell_id: str
    target_id: str
    function_profile: str
    shear_vane: Optional[Dict[str, float]] = None
    penetrometer: Optional[Dict[str, float]] = None
    grain_photo_analysis: Optional[Dict[str, float]] = None
    xrf_xrd_mineralogy: Optional[Dict[str, Any]] = None


@app.get("/health")
def health_check() -> Dict[str, Any]:
    return {
        "status": "healthy",
        "service": "TERRA-X API",
        "version": "1.0.0",
        "engine": "AFI_f = M_f * (1 - C_f) * T_f",
        "gravity_bridges": "Active (gamma = rho * g)",
    }


@app.get("/api/targets")
def list_planetary_targets() -> Dict[str, Any]:
    """Returns available Moon and Mars target exploration sites."""
    return {"targets": target_reg.list_targets()}


@app.get("/api/functions")
def list_exploration_functions() -> Dict[str, Any]:
    """Returns the 10 exploration function profiles."""
    return {
        "profiles": [
            {
                "id": "ROVER_MOBILITY",
                "name": "Surface Mobility & Traversability",
                "governing_dimensionless_groups": ["tan(theta)/tan(phi)", "h_rms(D)/D", "z/D sinkage"],
                "gravity_scaling": "Load scale bridge x6.37 for Moon, x2.85 for Mars",
            },
            {
                "id": "LANDING_PAD_CONSTRUCTION",
                "name": "Plume-Surface Interaction (PSI) & Blast Ejecta",
                "governing_dimensionless_groups": ["tau_plume/(gamma*d50)", "p/(gamma*B)"],
                "gravity_scaling": "Ejecta trajectory and threshold Shields parameter",
            },
            {
                "id": "REGOLITH_EXCAVATION",
                "name": "Regolith Excavation & Cutting Shear Mechanics",
                "governing_dimensionless_groups": ["c/(gamma*d)", "F/(gamma*d^3)", "p/(gamma*B)"],
                "gravity_scaling": "Cutting resistance scales directly with effective unit weight gamma=rho*g",
            },
            {
                "id": "ISRU_CONSTRUCTION",
                "name": "Excavation, Beneficiation & Microwave Sintering",
                "governing_dimensionless_groups": ["F/(gamma*d^3)", "p/(gamma*B)", "c/(gamma*d)"],
                "gravity_scaling": "Cutting force scaled by unit weight gamma=rho*g",
            },
            {
                "id": "THERMAL_SURVIVABILITY",
                "name": "Extreme Diurnal Thermal Dynamics & Radiative Sink",
                "governing_dimensionless_groups": ["Delta_T / T_mean", "Thermal Inertia Ratio"],
                "gravity_scaling": "Atmosphere suppresses radiative swing (Hard Break)",
            },
            {
                "id": "DUST_AND_WIND",
                "name": "Aeolian Saltation & Electrostatic Levitation",
                "governing_dimensionless_groups": ["Froude Number", "Roughness Ratio h_rms/D", "Wadell Roundness"],
                "gravity_scaling": "Saltation threshold and trajectory scaled by reduced gravity",
            },
            {
                "id": "WATER_AND_ICE_RESOURCES",
                "name": "Cryo-adsorbed Volatiles & Micro-Cold Traps",
                "governing_dimensionless_groups": ["Sublimation Loss Ratio", "Water Activity a_w", "Delta_T / T_mean"],
                "gravity_scaling": "Vacuum sublimation and cryogenic cold trapping at <70 K",
            },
            {
                "id": "BIOSIGNATURE_PRESERVATION",
                "name": "Biosignature Preservation & Extreme Desiccation",
                "governing_dimensionless_groups": ["Water Activity a_w Ratio", "UV Dosage", "Preservation Index"],
                "gravity_scaling": "Biological presence sign flipped (treated as analog target signal)",
            },
            {
                "id": "SUBSURFACE_AND_LAVA_TUBES",
                "name": "Basalt Lava Tube Skylights & Structural Integrity",
                "governing_dimensionless_groups": ["Span-to-Thickness Ratio", "Lithostatic Stress / Cohesion"],
                "gravity_scaling": "Reduced gravity permits 6x wider stable lava tube spans",
            },
            {
                "id": "COMMUNICATION_AND_ILLUMINATION",
                "name": "Positioning, Nav & Timing Denied Terrain-Relative Nav",
                "governing_dimensionless_groups": ["Horizon-Blocked Fraction (1-SVF)", "Grazing Shadow Contrast"],
                "gravity_scaling": "Pure geometry & low-sun elevation optical tracking",
            },
        ]
    }


@app.get("/api/observatory")
def get_data_observatory() -> Dict[str, Any]:
    """Returns multi-agency dataset lifecycle statuses across NASA, ESA, JAXA, CSA, and USGS."""
    return {
        "datasets": [
            {
                "provider": "NASA LP DAAC",
                "mission": "ISS ECOSTRESS",
                "product": "ECO3LSTE V003 (C3998139651-LPCLOUD)",
                "spatial_resolution": "70 m",
                "temporal_extent": "2018 - Present",
                "lifecycle_state": "QA_VALIDATED",
                "live_status": "CONNECTED",
                "granules_ingested": 42,
                "documentation": "https://lpdaac.usgs.gov/products/eco3lstev003/",
            },
            {
                "provider": "NASA LP DAAC",
                "mission": "ISS EMIT",
                "product": "EMITL2BMIN V001 (Mineralogy)",
                "spatial_resolution": "60 m",
                "temporal_extent": "2022 - Present",
                "lifecycle_state": "QA_VALIDATED",
                "live_status": "CONNECTED",
                "granules_ingested": 18,
                "documentation": "https://lpdaac.usgs.gov/products/emitl2bminv001/",
            },
            {
                "provider": "NASA ASF DAAC",
                "mission": "OPERA (Sentinel-1)",
                "product": "OPERA_L2_RTC-S1_V1",
                "spatial_resolution": "30 m",
                "temporal_extent": "2023 - Present",
                "lifecycle_state": "PROCESSED",
                "live_status": "CONNECTED",
                "granules_ingested": 64,
                "documentation": "https://www.jpl.nasa.gov/go/opera",
            },
            {
                "provider": "EU Copernicus CDSE",
                "mission": "Copernicus DEM",
                "product": "COP-DEM GLO-30 (COG v1)",
                "spatial_resolution": "30 m",
                "temporal_extent": "Static (2020 ed.)",
                "lifecycle_state": "USED_IN_ANALYSIS",
                "live_status": "AUTHENTICATED",
                "granules_ingested": 96,
                "documentation": "https://dataspace.copernicus.eu",
            },
            {
                "provider": "USGS EROS",
                "mission": "Landsat 8/9",
                "product": "Landsat-C2L2-ST / SR",
                "spatial_resolution": "30 m",
                "temporal_extent": "2013 - Present",
                "lifecycle_state": "PROCESSED",
                "live_status": "AVAILABLE",
                "granules_ingested": 88,
                "documentation": "https://landsatlook.usgs.gov",
            },
            {
                "provider": "NASA PDS / PGDA",
                "mission": "LRO LOLA",
                "product": "LDEM_80S_5M (100 Clones Ensemble)",
                "spatial_resolution": "5 m",
                "temporal_extent": "2009 - 2024",
                "lifecycle_state": "USED_IN_ANALYSIS",
                "live_status": "CONNECTED",
                "granules_ingested": 100,
                "documentation": "https://pgda.gsfc.nasa.gov",
            },
            {
                "provider": "ESA PSA",
                "mission": "Mars Express",
                "product": "MEX_HRSC_DTM_V1",
                "spatial_resolution": "50 m",
                "temporal_extent": "2004 - 2024",
                "lifecycle_state": "QA_VALIDATED",
                "live_status": "CONNECTED",
                "granules_ingested": 26,
                "documentation": "https://psa.esa.int",
            },
            {
                "provider": "JAXA G-Portal",
                "mission": "ALOS PRISM",
                "product": "AW3D30 v3.2 DSM",
                "spatial_resolution": "30 m",
                "temporal_extent": "Static",
                "lifecycle_state": "PROCESSED",
                "live_status": "AVAILABLE",
                "granules_ingested": 35,
                "documentation": "https://gportal.jaxa.jp",
            },
        ]
    }



@app.post("/api/discover")
def discover_analogs(req: DiscoverRequest) -> Dict[str, Any]:
    """
    Executes discovery pipeline with real-time what-if sliders.
    Returns ranked sites with Monte Carlo rank percentiles (p10/p50/p90) and P(top10).
    """
    try:
        results = pipeline.run_discovery_pipeline(
            target_id=req.target_id,
            function_profile=req.function_profile,
            wheel_diameter_m=req.wheel_diameter_m,
            contact_pressure_kpa=req.contact_pressure_kpa,
            footprint_width_m=req.footprint_width_m,
            test_duration_days=req.test_duration_days,
            top_k=req.top_k,
            enforce_mmr=req.enforce_mmr,
        )
        return results
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/passport/{cell_id}")
def get_site_passport(
    cell_id: str,
    target_id: str = "MOON_SOUTH_POLE_SHACKLETON",
    function_profile: str = "MOBILITY",
    wheel_diameter_m: float = 0.50,
) -> Dict[str, Any]:
    """Retrieves full Site Passport and Fidelity Ledger for a specific H3 cell."""
    target = target_reg.get_target(target_id)
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")

    # Match cell
    matched_cand = next((c for c in pipeline.all_candidates if c.get("cell_id") == cell_id or c.get("id") == cell_id), None)
    if not matched_cand:
        raise HTTPException(status_code=404, detail=f"Cell {cell_id} not found in candidate catalog")

    mc_result = pipeline.mc_ranker.run_ensemble_ranking(
        function_profile=function_profile,
        target=target,
        candidate_cells=[matched_cand],
        wheel_diameter_m=wheel_diameter_m,
    )[0]

    passport = pipeline.generate_site_passport(
        candidate_mc=mc_result,
        target=target,
        function_profile=function_profile,
        wheel_diameter_m=wheel_diameter_m,
        test_duration_days=14,
    )
    return passport


@app.get("/api/recipe/{cell_id}")
def export_test_recipe(
    cell_id: str,
    target_id: str = "MOON_SOUTH_POLE_SHACKLETON",
    function_profile: str = "MOBILITY",
    wheel_diameter_m: float = 0.50,
    test_duration_days: int = 14,
) -> Dict[str, Any]:
    """Exports transferable Test Recipe tied to named NASA technology gaps."""
    passport = get_site_passport(cell_id, target_id, function_profile, wheel_diameter_m)
    return passport.get("test_recipe", {})


@app.post("/api/field-kit/rescore")
def rescore_with_field_kit(payload: FieldKitUploadRequest) -> Dict[str, Any]:
    """Uploads in-situ field measurement data to upgrade Fidelity Ledger and re-score AFI."""
    target = target_reg.get_target(payload.target_id)
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")

    matched_cand = next((c for c in pipeline.all_candidates if c.get("cell_id") == payload.cell_id or c.get("id") == payload.cell_id), None)
    if not matched_cand:
        raise HTTPException(status_code=404, detail=f"Cell {payload.cell_id} not found")

    rescore_out = FieldKitEngine.re_score_with_field_kit(
        base_features=matched_cand,
        field_kit_payload=payload.dict(),
        target=target,
        function_profile=payload.function_profile,
    )
    return rescore_out


@app.get("/api/stac/items")
def stac_items(
    target_id: str = "MOON_SOUTH_POLE_SHACKLETON",
    function_profile: str = "MOBILITY",
) -> Dict[str, Any]:
    """Returns STAC-compliant GeoJSON FeatureCollection of evaluated analog cells."""
    discovery = pipeline.run_discovery_pipeline(target_id=target_id, function_profile=function_profile, top_k=20)
    features = []

    for site in discovery["ranked_sites"]:
        cell_id = site["cell_id_h3_r6"]
        coords = H3Grid.cell_to_boundary(cell_id)

        feat = {
            "type": "Feature",
            "id": site["site_id"],
            "geometry": {
                "type": "Polygon",
                "coordinates": [coords],
            },
            "properties": {
                "title": site["site_name"],
                "cell_id_h3": cell_id,
                "afi_score_p50": site["scores"]["afi_p50"],
                "rank_p50": site["monte_carlo_rank"]["rank_p50"],
                "p_top10": site["monte_carlo_rank"]["p_top10"],
                "novelty_score": site["novelty"]["novelty_score"],
                "function_profile": function_profile,
                "target_body": site["planetary_target"]["body"],
                "hard_breaks": site["hard_breaks"],
                "stac_version": "1.0.0",
                "license": site["provenance"]["license_class"],
            },
            "links": [
                {"rel": "self", "href": f"/api/passport/{cell_id}"},
                {"rel": "recipe", "href": f"/api/recipe/{cell_id}"},
            ],
            "assets": {
                "passport": {"href": f"/api/passport/{cell_id}", "type": "application/json"},
                "recipe": {"href": f"/api/recipe/{cell_id}", "type": "application/json"},
            },
        }
        features.append(feat)

    return {
        "type": "FeatureCollection",
        "stac_version": "1.0.0",
        "description": "TERRA-X STAC Catalog for NASA Planetary Analog Discovery",
        "features": features,
    }


# ==============================================================================
# AI MISSION COPILOT & TOKEN EFFICIENCY ENDPOINTS
# ==============================================================================
from engine.ai_copilot import TerraXCopilot, AVAILABLE_MODELS

ai_copilot = TerraXCopilot()


class AISynthesisRequest(BaseModel):
    cell_id: str
    target_id: str = "MOON_SOUTH_POLE_SHACKLETON"
    function_profile: str = "MOBILITY"
    wheel_diameter_m: float = 0.50
    model: Optional[str] = None
    force_refresh: bool = False


class AIChatRequest(BaseModel):
    cell_id: str
    target_id: str = "MOON_SOUTH_POLE_SHACKLETON"
    function_profile: str = "MOBILITY"
    user_query: str
    wheel_diameter_m: float = 0.50
    model: Optional[str] = None


@app.get("/api/ai/models")
def get_ai_models() -> List[Dict[str, Any]]:
    """Returns available Meta AI models with token efficiency recommendations."""
    return AVAILABLE_MODELS


@app.post("/api/ai/synthesize")
def ai_synthesize_site(req: AISynthesisRequest) -> Dict[str, Any]:
    """Generates AI mission engineering synthesis with token caching."""
    passport = get_site_passport(
        cell_id=req.cell_id,
        target_id=req.target_id,
        function_profile=req.function_profile,
        wheel_diameter_m=req.wheel_diameter_m,
    )
    result = ai_copilot.generate_synthesis(
        site_passport=passport,
        model_override=req.model,
        force_refresh=req.force_refresh,
    )
    return result


@app.post("/api/ai/chat")
def ai_chat_site(req: AIChatRequest) -> Dict[str, Any]:
    """Conversational engineering consultation regarding test article suitability and mitigations."""
    passport = get_site_passport(
        cell_id=req.cell_id,
        target_id=req.target_id,
        function_profile=req.function_profile,
        wheel_diameter_m=req.wheel_diameter_m,
    )
    result = ai_copilot.generate_synthesis(
        site_passport=passport,
        user_query=req.user_query,
        model_override=req.model,
        force_refresh=True,
    )
    return result


@app.get("/api/ai/token-stats")
def ai_token_stats() -> Dict[str, Any]:
    """Returns token consumption, latency, and efficiency metrics."""
    return ai_copilot.tracker.get_stats()


