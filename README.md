# TERRA-X: Autonomous Functional Analog Discovery Engine
### Reproducible, Uncertainty-Aware Geospatial Discovery for Moon & Mars Exploration
**NASA Space Apps Challenge 2026**

[![Acceptance Tests](https://img.shields.io/badge/Acceptance%20Gates-7%2F7%20PASSED-success)](tests/test_acceptance.py)
[![Unit Tests](https://img.shields.io/badge/Unit%20Tests-21%2F21%20PASSED-success)](tests/)
[![Data Contracts](https://img.shields.io/badge/Data%20Contracts-NASA%20%7C%20USGS%20%7C%20CDSE%20%7C%20PSA%20%7C%20JAXA-blue)](connectors/)
[![License](https://img.shields.io/badge/License-CC--BY--4.0-green.svg)](manifests/licenses.json)

---

## 1. System Overview & The Core Non-Negotiables
TERRA-X is **NOT** a visual-similarity map. Superficial visual resemblance between Earth and planetary surfaces is notoriously treacherous (e.g. wet quartz sand or rounded beach dunes appearing visually similar to regolith, yet possessing completely invalid bearing capacities and slip dynamics).

Instead, TERRA-X evaluates **an H3 hexagonal cell (Resolution 5/6) as an engineering TEST ARTICLE for a named exploration FUNCTION**:
- `MOBILITY`: Rover wheel traversability, sinkage $z/D$, micro-roughness obstacle clearance $h_{\text{rms}}/D$, and slope slip $\tan\theta/\tan\phi$.
- `CONSTRUCTION_ISRU`: Regolith excavation cutting forces $F/(\gamma d^3)$, bearing pressure $p/(\gamma B)$, and microwave/solar sintering.
- `LANDING_PAD_PSI`: Rocket plume-surface interaction (PSI), supersonic shear scour, and high-velocity crater blast ejecta.
- `HUMAN_OPS_THERMAL`: Extreme diurnal cycling $\Delta T / T_{\text{mean}}$, thermal inertia, and radiative cold-trap sinks.
- `PNT_DENIED_NAV`: Terrain-Relative Navigation (TRN) in deep permanent shadow and low-grazing-angle solar illumination.
- `ASTROBIO`: Extreme hyper-arid desiccation limits, cryptoendolithic preservation, and biosignature retention.

---

## 2. Mathematical Scoring Law: $AFI_f = M_f \times (1 - C_f) \times T_f$

Every candidate H3 cell is scored by the **Analog Fidelity Index** ($AFI_f \in [0, 1]$):
$$AFI_f = M_f \cdot (1 - C_f) \cdot T_f$$

1. **$M_f$ (Confidence-Weighted Wasserstein Match):**
   Derived from analytical optimal transport distance between Gaussian uncertainty distributions $\mathcal{N}(\mu_e, \tau_e^2)$ and $\mathcal{N}(\mu_t, \sigma_t^2)$:
   $$W_2^2(P_i, Q_i) = (\mu_{e, i} - \mu_{t, i})^2 + (\tau_{e, i} - \sigma_{t, i})^2$$
   $$M_f = \frac{\sum_i w_i \exp(-W_2(P_i, Q_i) / S_i)}{\sum_i w_i}, \quad w_i = \frac{1}{1 + \tau_{e, i}/S_i}$$

2. **$C_f$ (Earth-Added Confounder Severity):**
   Evaluates function-dependent Earth physical phenomena absent in vacuum/planetary environments:
   - Moisture capillary cohesion ($w$)
   - Vegetation biomass / root binding ($NDVI$)
   - Fluvial/aeolian grain rounding ($W_r$) vs jagged impact-fractured regolith
   - Atmospheric convective cooling vs radiative equilibrium
   - **Biological Sign Inversion Rule:** In engineering functions, biological presence is a confounder ($C > 0$). In `ASTROBIO`, biological extremophile presence is the **TARGET SIGNAL**, flipping the sign and reducing $C_f$!

3. **$T_f$ (Transferable Physics Fraction):**
   Portion of governing physics that can be transferred directly to flight hardware testing without invalidating operational assumptions.

4. **Missing Data Policy:** Strictly labeled **`UNCONSTRAINED`** in the Fidelity Ledger and **NEVER imputed**.

---

## 3. Gravity Bridges: $\gamma = \rho g$
**Never claim $1g == 1/6g$.** Granular soil mechanics, bearing capacity, and excavation resistance scale with effective unit weight $\gamma$:
- Moon: $\gamma_{\text{moon}} = 1520\,\text{kg/m}^3 \times 1.62\,\text{m/s}^2 \approx 2,462\,\text{N/m}^3$
- Earth: $\gamma_{\text{earth}} = 1520\,\text{kg/m}^3 \times 9.81\,\text{m/s}^2 \approx 14,911\,\text{N/m}^3$
- **Gravity Load Scale Factor:** $\gamma_{\text{earth}} / \gamma_{\text{moon}} \approx \mathbf{6.05 - 6.37\times}$!
- To match dimensionless bearing pressure $p/(\gamma B)$ or excavation force $F/(\gamma d^3)$, test rigs must apply $\approx 6\times$ ballast adjustment or use an inclined test ramp at angle $\alpha = \arcsin(1/6) = 9.6^\circ$.

---

## 4. Repository Architecture
```
TERRA-X/
├── api/
│   └── app.py                     # FastAPI REST service & STAC endpoints
├── connectors/
│   ├── base.py                    # Rate-limiting, retry-after & error handling
│   ├── license_engine.py          # Provenance, DOIs, checksums, export gatekeeper
│   ├── nasa_cmr.py                # NASA CMR (ECOSTRESS V003, EMIT, OPERA, HLS, MODIS)
│   ├── usgs_stac.py               # USGS LandsatLook STAC client (C2L2 SR/ST)
│   ├── cdse_stac.py               # Copernicus Data Space Ecosystem STAC v1 & GLO-30
│   ├── mars_psa.py                # ESA PSA EPN-TAP ADQL client for Mars Express HRSC
│   ├── asia_connectors.py         # JAXA (AW3D30 canopy correction), Himawari, ISRO PRADAN
│   ├── csa_connector.py           # CSA RCM / RADARSAT-1 open data
│   └── pds_ode.py                 # PDS ODE, USGS LOLA unscaling, PGDA 100 clones
├── harmonize/
│   ├── h3_grid.py                 # Pure-Python H3 Discrete Global Grid System (r5/r6/r7)
│   ├── dem_unscale.py             # Planetary DEM int16 unscaling (scale 0.5)
│   └── sensor_harmonizer.py       # Cross-sensor spread (S1 vs OPERA, GLO30 vs AW3D)
├── features/
│   ├── dimensionless.py           # Dimensionless scaling groups & gravity bridges
│   ├── confounders.py             # Earth confounder assessment & biological sign flip
│   └── geomorphology.py           # Slope, micro-roughness h_rms(D), horizon blocking
├── targets/
│   └── registry.py                # Planetary target catalogs (Moon South Pole, Mars Jezero)
├── engine/
│   ├── scoring.py                 # AFI = M*(1-C)*T & Fidelity Ledger
│   ├── monte_carlo.py             # 100-clone PGDA DEM ensemble ranker (p10, p50, p90, P(top10))
│   ├── novelty_mmr.py             # Distance penalty & Maximal Marginal Relevance (MMR)
│   ├── pareto.py                  # Multi-objective non-dominated Pareto frontier
│   ├── field_kit.py               # In-situ field assay upload & re-scoring
│   └── pipeline.py                # 7-stage autonomous discovery pipeline (S0 - S6)
├── data/
│   ├── candidate_catalog.py       # Global H3 candidate database (benchmarks & novel sites)
│   ├── export_stac_dataset.py     # Open STAC & Parquet dataset generator
│   ├── terrax_stac_collection.geojson
│   └── terrax_analog_catalog.parquet
├── manifests/
│   ├── golden_sites.json          # Held-out benchmark registry
│   ├── licenses.json              # License classification and export terms
│   ├── nasa_tech_gaps.json        # NASA STMD/ESDMD Technology Taxonomy
│   └── target_catalogs.json       # Lunar & Martian target reference states
├── web/
│   ├── index.html                 # Split-screen Earth<->Planet MapLibre workstation
│   ├── style.css                  # Mission control dark-mode aesthetic
│   └── app.js                     # Real-time what-if sliders, passport & recipe exporter
├── tests/
│   ├── test_acceptance.py         # 7 Non-negotiable acceptance test gates
│   ├── test_connectors.py         # Multi-agency API data contracts & guardrails
│   ├── test_dimensionless.py      # Dimensionless scaling laws & gravity bridges
│   └── test_scoring.py            # AFI equation & Fidelity Ledger enforcement
├── notebooks/
│   └── TERRA_X_Reproducible_Discovery.ipynb  # End-to-end reproducible walk-through
├── reports/
│   ├── METHODS_AND_VALIDATION_REPORT.md     # Full derivations & validation matrix
│   └── TEST_RECIPES_NASA_TECH_GAPS.md       # Operational flight hardware test recipes
└── run_app.py                     # One-click server launcher
```

---

## 5. Verification & Acceptance Gates

Execute all 21 unit and acceptance tests:
```bash
python -m unittest discover -s tests -v
```

### Acceptance Test Results
- **Gate 1 (Golden-Site Recall@50):** `PASSED` (Recall = 1.0 $\ge$ 0.80 for Atacama, Haughton, Death Valley).
- **Gate 2 (Leave-One-Continent-Out):** `PASSED` (Consistent spatial generalization across all continents).
- **Gate 3 (Cross-Sensor Spread):** `PASSED` (Quantified backscatter, DEM, and thermal uncertainties).
- **Gate 4 (Monte Carlo Interval Calibration):** `PASSED` (Monotonic rank percentiles $p_{10} \le p_{50} \le p_{90}$).
- **Gate 5 (Ablation Study Per Dimension):** `PASSED` (Measurable rank sensitivity to roughness, slope, moisture).
- **Gate 6 (Adversarial Looks-Alike Rejection):** `PASSED` (Daytona Beach and rounded dunes rejected with $AFI < 0.02$).
- **Gate 7 (Expert Blind Review vs Controls):** `PASSED` (Authentic basaltic/angular sites strictly outrank controls).

---

## 6. Running the System

### Launch Mission Control Web Application
```bash
python run_app.py
```
Open your browser at `http://127.0.0.1:8000` to interact with:
- **Split-Screen Globe View:** Earth analog candidate H3 hexagons $\longleftrightarrow$ Moon/Mars target surface hillshade radar.
- **Dynamic What-If Sliders:** Adjust Wheel Diameter $D$, Landing Pad $B$, Bearing Pressure $p$, and Duration with instant re-ranking.
- **Site Passport Drawer:** Interactive Subsystem Fidelity Ledger (`STRONG`, `PARTIAL`, `BREAKS`, `UNCONSTRAINED`).
- **Transferable Test Recipe Exporter:** Downloadable JSON & printable flight hardware testing protocol tied to NASA STMD gaps.
- **In-Situ Field Kit:** Live upload of shear-vane, cone penetrometer, and micro-grain assays.

