# TERRA-X — Planetary Functional Analog Discovery Engine
### "Find Earth's best proving grounds for exploring other worlds."
**NASA Space Apps Challenge 2026**

[![Acceptance Tests](https://img.shields.io/badge/Acceptance%20Gates-7%2F7%20PASSED-success)](tests/test_acceptance.py)
[![Unit Tests](https://img.shields.io/badge/Unit%20Tests-21%2F21%20PASSED-success)](tests/)
[![Data Contracts](https://img.shields.io/badge/Data%20Contracts-NASA%20%7C%20ESA%20%7C%20JAXA%20%7C%20CSA%20%7C%20USGS-blue)](connectors/)
[![STAC 1.0](https://img.shields.io/badge/STAC-1.0.0%20Compliant-orange)](data/terrax_stac_collection.geojson)
[![License](https://img.shields.io/badge/License-MIT%20%2F%20CC--BY--4.0-green.svg)](LICENSE)

---

## 1. Product Identity & Scientific Architecture

TERRA-X is **NOT** a visual-similarity map. Superficial visual resemblance between Earth and planetary surfaces is notoriously treacherous (e.g. wet quartz sand or rounded beach dunes appearing visually similar to regolith, yet possessing completely invalid bearing capacities, cohesive capillary bridges, and slip dynamics).

Instead, TERRA-X evaluates **an H3 hexagonal cell (Resolution 5/6) as a physical engineering TEST ARTICLE for a named exploration FUNCTION**:

It directly answers the operational questions of mission engineers:
- **Where on Earth can we test rover mobility** for a particular lunar or Martian terrain?
- **Where can we test regolith excavation**, material handling, and landing-pad construction?
- **Which locations offer comparable geological**, mineralogical, and mechanical shear properties?
- **Where does an analogy scientifically hold strong**, where does it require scaling corrections, and where does it break down?
- **What exact experimental Test Recipe** should engineers execute at the selected Earth site?

---

## 2. The 10 Exploration Function Profiles

Every Earth test article is evaluated across 10 distinct, function-specific operational profiles:

1. **`ROVER_MOBILITY`**: Wheel-scale traversability, Bekker-Wong sinkage ratio $z/D$, micro-roughness obstacle clearance $h_{\text{rms}}/D$, and frictional slope stability $\tan\theta/\tan\phi$.
2. **`LANDING_PAD_CONSTRUCTION`**: Plume-Surface Interaction (PSI), supersonic jet shear scour, Shields threshold fluidization, and blast ejecta liberation.
3. **`REGOLITH_EXCAVATION`**: Blade cutting forces $F/(\gamma d^3)$, dimensionless cohesion $c/(\gamma d)$, and trenching shear resistance.
4. **`ISRU_CONSTRUCTION`**: Beneficiation, microwave/solar sintering, 3D printing compaction, and molten regolith electrolysis.
5. **`THERMAL_SURVIVABILITY`**: Extreme diurnal cycling $\Delta T / T_{\text{mean}}$, thermal inertia ratio, and radiative cold-trap sinks.
6. **`DUST_AND_WIND`**: Aeolian saltation, triboelectric charging, grain angularity (Wadell roundness $< 0.25$), and seal abrasion.
7. **`WATER_AND_ICE_RESOURCES`**: Cryo-adsorbed volatiles, subsurface permafrost dielectric signatures, and vacuum sublimation kinetics.
8. **`BIOSIGNATURE_PRESERVATION`**: Fossil biomarker retention, cryptoendolithic niches, and hydrothermal clays (*Biological presence sign flipped to positive target signal*).
9. **`SUBSURFACE_AND_LAVA_TUBES`**: Basalt vault mechanical stability, skylight roof collapse geometry, and cave structural integrity.
10. **`COMMUNICATION_AND_ILLUMINATION`**: Horizon-blocked fraction ($1 - \text{SVF}$), low-grazing-angle illumination ($< 1.8^\circ$), and Terrain-Relative Navigation (TRN).

---

## 3. Planetary Target Reference States

TERRA-X incorporates real coordinates, planetary coordinate reference frames, DEM resolutions, and reference dimensionless groups across:

### A. Official NASA Artemis III Candidate Regions (Updated 2024)
- **Peak near Cabeus B** (-84.9° Lat, -35.2° Lon) — Elevated massif with proximal access to cryogenic PSR cold traps.
- **Haworth Rim** (-87.4° Lat, -5.1° Lon) — Deep permanent shadow access with extreme volatile cold-trapping potential.
- **Malapert Massif** (-85.9° Lat, 0.0° Lon) — High topographic prominence offering multi-week continuous solar illumination.
- **Mons Mouton Plateau** (-84.5° Lat, -31.0° Lon) — Flat summit plain for base construction and rover mobility traverses.
- **Nobile Rim 1** (-85.2° Lat, 37.8° Lon) — Diverse impact ejecta and micro-cold traps holding shallow volatile deposits.
- **de Gerlache Rim 2** (-88.3° Lat, -68.8° Lon) — Narrow polar ridge system with dynamic grazing illumination.
- **Slater Plain** (-88.1° Lat, 113.5° Lon) — Low-slope polar plain optimal for excavation and landing pad foundation testing.

### B. Independent Lunar Research Areas
- **Shackleton Crater Rim & Ridge** (-89.9° Lat, 0.0° Lon) — Landmark lunar south pole benchmark (*accurately designated as an independent research target, not an official Artemis III 2024 landing region*).
- **Oceanus Procellarum / Marius Hills** (14.1° Lat, -56.7° Lon) — Lunar mare basalt plains and subsurface lava tube collapse pit.

### C. Mars Planetary Study Regions
- **Oxia Planum** (18.27°N, -24.63°E) — ExoMars Rosalind Franklin ancient Noachian phyllosilicate clay plain.
- **Jezero Crater Western Delta** (18.38°N, 77.58°E) — Perseverance river delta scarp and lacustrine mudstone strata.
- **Gale Crater / Mt. Sharp** (4.59°S, 137.44°E) — MSL Curiosity sulfate-bearing layered mound and ventifact flutes.

---

## 4. Mathematical Scoring Law: $\text{AFI}_f = M_f \times (1 - C_f) \times T_f$

Every candidate H3 cell is scored by the **Analog Fidelity Index** ($\text{AFI}_f \in [0, 1]$):
$$\text{AFI}_f = M_f \cdot (1 - C_f) \cdot T_f$$

1. **$M_f$ (Confidence-Weighted Wasserstein Match):**
   Derived from analytical optimal transport distance between Gaussian uncertainty distributions $\mathcal{N}(\mu_e, \tau_e^2)$ and $\mathcal{N}(\mu_t, \sigma_t^2)$:
   $$W_2^2(P_i, Q_i) = (\mu_{e, i} - \mu_{t, i})^2 + (\tau_{e, i} - \sigma_{t, i})^2$$
   $$M_f = \frac{\sum_i w_i \exp(-W_2(P_i, Q_i) / S_i)}{\sum_i w_i}, \quad w_i = \frac{W_{\text{function}, i}}{1 + \tau_{e, i}/S_i}$$

2. **$C_f$ (Earth-Added Confounder Severity):**
   Penalizes function-dependent Earth physical phenomena absent in vacuum/planetary environments:
   - Capillary moisture cohesion ($w$)
   - Vegetation biomass / root cohesion ($NDVI$)
   - Fluvial/aeolian grain rounding ($W_r$) vs jagged impact regolith
   - Atmospheric convective heat transfer vs radiative equilibrium
   - **Biological Sign Inversion Rule:** In engineering functions, biological activity is a confounder ($C > 0$). In `BIOSIGNATURE_PRESERVATION`, extremophile presence is the **TARGET SIGNAL**, flipping the sign to reward presence!

3. **$T_f$ (Transferable Physics Fraction):**
   The fraction of governing physics that can be transferred directly to flight hardware testing without invalidating operational assumptions.

4. **$Q_f$ (Evidence Confidence):**
   Reported separately as a measure of sensor QA coverage and observed parameter completeness:
   $$Q_f = \frac{\sum_{i \in \text{observed}} (1 - 1.5\,\tau_i)}{\text{Total Required Slots}}$$

5. **Missing Data Policy:** Strictly labeled **`UNCONSTRAINED`** in the Fidelity Ledger and **NEVER imputed**.

---

## 5. The Gravity Bridge: $\gamma = \rho g$

**Never claim $1g == 1/6g$.** Granular soil mechanics, bearing capacity, and excavation cutting resistance scale with effective unit weight $\gamma$:
- Moon: $\gamma_{\text{moon}} = 1520\,\text{kg/m}^3 \times 1.62\,\text{m/s}^2 \approx 2,462\,\text{N/m}^3$
- Earth: $\gamma_{\text{earth}} = 1520\,\text{kg/m}^3 \times 9.81\,\text{m/s}^2 \approx 14,911\,\text{N/m}^3$
- **Gravity Load Scale Factor:** $\gamma_{\text{earth}} / \gamma_{\text{moon}} \approx \mathbf{6.05 - 6.37\times}$!
- To match dimensionless bearing pressure $p/(\gamma B)$ or excavation force $F/(\gamma d^3)$, test rigs must apply ballast adjustments ($M_{\text{earth}} = 6.37 \times M_{\text{flight}}$) or utilize an inclined test ramp at angle $\alpha = \arcsin(1/6.37) \approx 9.0^\circ - 9.6^\circ$.

---

## 6. The 4 Scientific Workspaces

The TERRA-X mission workstation provides 4 dedicated workspaces accessible via the top navigation:

1. **`Discover` Workspace:**
   - Real-time Earth H3 screening grid (dual selectable layers: Dark Aerospace OSM & ESRI High-Res Satellite).
   - Target planetary surface viewer powered by real NASA/USGS shaded relief tiles and DEM hillshade overlays.
   - Interactive What-If sliders (Wheel Diameter $D$, Pad Width $B$, Contact Pressure $p$, Duration, Slope) with real-time candidate re-ranking.
   - 100-clone Monte Carlo rank percentiles ($p_{10}, p_{50}, p_{90}$) and $P(\text{top10})$ membership probabilities.

2. **`Compare` Workspace:**
   - Synchronized side-by-side Earth vs. Moon/Mars split view.
   - Aligned dimensionless measurement bars comparing candidate values against target references.
   - Elevation profile and topography comparison.

3. **`Analog Passports`:**
   - Verifiable scientific profile for every shortlisted site.
   - 3-Tier **Fidelity Ledger**:
     - `STRONG ANALOGY`: Direct physical correspondence under Coulomb mechanics.
     - `PARTIAL ANALOGY`: Valid under gravity bridge scaling (requires ballast/offload rigs).
     - `ANALOGY BREAKDOWN`: Non-reproducible space environments (vacuum, 1/6g, GCR radiation, cryogenic PSR 70 K).
   - Actionable **NASA Test Recipe** tied to NASA STMD/ESDMD Technology Gaps.
   - **AI Mission Copilot** powered by Meta Muse Wonder 1.0 (Optimal Token Efficiency) and Muse Spark 1.3.

4. **`Data Observatory`:**
   - Multi-agency data provenance manager tracking NASA, ESA, JAXA, CSA, and USGS data streams.
   - 6-Stage Lifecycle Monitor:
     $$\text{DISCOVERED} \longrightarrow \text{AVAILABLE} \longrightarrow \text{DOWNLOADED} \longrightarrow \text{PROCESSED} \longrightarrow \text{QA VALIDATED} \longrightarrow \text{USED IN ANALYSIS}$$

---

## 7. Verification & Acceptance Testing

Execute all 21 acceptance gates and physical calculation tests:
```bash
python -m unittest discover -s tests -v
```

### Acceptance Gates (All 7 Passed)
- **Gate 1 (Golden-Site Recall@50):** `PASSED` (Recall = 1.0 $\ge$ 0.80 for Atacama, Haughton, Death Valley).
- **Gate 2 (Leave-One-Continent-Out):** `PASSED` (Consistent spatial generalization across all continents).
- **Gate 3 (Cross-Sensor Spread):** `PASSED` (Quantified backscatter, DEM, and thermal uncertainties).
- **Gate 4 (Monte Carlo Interval Calibration):** `PASSED` (Monotonic rank percentiles $p_{10} \le p_{50} \le p_{90}$).
- **Gate 5 (Ablation Study Per Dimension):** `PASSED` (Measurable rank sensitivity to roughness, slope, moisture).
- **Gate 6 (Adversarial Looks-Alike Rejection):** `PASSED` (Daytona Beach and rounded dunes rejected with $\text{AFI} < 0.02$).
- **Gate 7 (Expert Blind Review vs Controls):** `PASSED` (Authentic volcanic/angular sites strictly outrank controls).

---

## 8. Launching the System

### Start Local Workstation
```bash
python run_app.py
```
Open your browser at `http://127.0.0.1:8000` to access the full planetary science workstation.

### Cloud Deployment (Render / Docker)
The application includes a production-ready `requirements.txt` and supports zero-downtime deployment:
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn run_app:app --host 0.0.0.0 --port $PORT`
- **Custom Domain:** Ready for `terrax.earth` via NASA Space Apps GoDaddy Registry.
