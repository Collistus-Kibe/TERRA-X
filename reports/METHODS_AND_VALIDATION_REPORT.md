# TERRA-X: Methods & Validation Report
## Functional Planetary Analog Discovery Engine (NASA Space Apps 2026)
**Author:** TERRA-X Engineering Architecture & Planetary Surface Systems Team  
**Date:** November 2026  
**Status:** Validated & Acceptance Tests Passed (21/21 Unit & Integration Tests Green)

---

## 1. Executive Problem Statement
Visual appearance is a notoriously treacherous metric for planetary analog discovery. Terrestrial landscapes that superficially "look like" the Moon or Mars—such as coastal sand beaches, river sandbars, or agricultural desert dunes—invariably fail when used as test articles for flight hardware. They possess moisture capillary cohesion, rounded grains from fluvial or aeolian transport, organic biofilms, and are tested under standard Earth gravity ($1g$), leading to disastrously unrepresentative tractive effort, bearing sinkage, and thermal dynamics.

**TERRA-X** rejects visual-similarity mapping in favor of a rigorous **Functional Analog Discovery System**. Every candidate site is evaluated as an **H3 hexagonal cell** (Resolution 5/6 discrete global grid system) acting as a **test article** for a named exploration **function profile**.

---

## 2. Exploration Function Profiles & Dimensionless Physics Groups

To transcend raw parameter values and bridge disparate gravitational and planetary environments, TERRA-X evaluates **dimensionless similarity groups** derived from Buckingham $\Pi$ dimensional analysis.

### 2.1 Gravity Bridges: $\gamma = \rho g$
A core non-negotiable axiom of TERRA-X is: **Never claim $1g == 1/6g$**.
Granular soil mechanics, bearing capacity, and excavation forces scale with soil effective unit weight $\gamma$:
$$\gamma = \rho \cdot g$$

| Planetary Body | Surface Gravity $g$ | Regolith Density $\rho$ | Unit Weight $\gamma$ | Earth Load Scale Ratio $\gamma_{\text{earth}} / \gamma_{\text{target}}$ |
| :--- | :--- | :--- | :--- | :--- |
| **Earth** | $9.80665\,\text{m/s}^2$ | $1520\,\text{kg/m}^3$ | $14,911.2\,\text{N/m}^3$ | $1.00\times$ (Reference) |
| **Moon** | $1.62000\,\text{m/s}^2$ | $1520\,\text{kg/m}^3$ | $2,462.4\,\text{N/m}^3$ | **$6.05 - 6.37\times$** |
| **Mars** | $3.72076\,\text{m/s}^2$ | $1450\,\text{kg/m}^3$ | $5,394.0\,\text{N/m}^3$ | **$2.76 - 2.91\times$** |

### 2.2 Governing Dimensionless Groups per Function

```
+----------------------------------------------------------------------------------------------------+
| FUNCTION PROFILE    | GOVERNING DIMENSIONLESS GROUPS       | SCALING LAW / BRIDGE MECHANISM        |
+---------------------+--------------------------------------+---------------------------------------+
| MOBILITY            | tan(θ) / tan(φ)                      | Frictional slip angle of repose       |
|                     | h_rms(D_wheel) / D_wheel             | Obstacle micro-roughness scaling      |
|                     | z / D_wheel                          | Bekker-Wong sinkage ratio             |
+---------------------+--------------------------------------+---------------------------------------+
| CONSTRUCTION_ISRU   | F / (γ · d³)                         | Dimensionless excavation force group  |
|                     | p / (γ · B)                          | Bearing capacity scaled pressure      |
|                     | c / (γ · d)                          | Cohesion-to-gravity ratio             |
+---------------------+--------------------------------------+---------------------------------------+
| LANDING_PAD_PSI     | τ_plume / (γ · d50)                  | Plume shear scour Shields parameter   |
|                     | q_jet / (γ · h_bed)                  | Stagnation pressure scour ratio       |
+---------------------+--------------------------------------+---------------------------------------+
| HUMAN_OPS_THERMAL   | ΔT / T_mean                          | Diurnal thermal cycling amplitude     |
|                     | I_earth / I_target                   | Thermal inertia ratio                 |
+---------------------+--------------------------------------+---------------------------------------+
| PNT_DENIED_NAV      | Horizon-Blocked Fraction (1 - SVF)   | Topographic occlusion / Shadow relief |
|                     | Sun elevation / Grazing angle        | Optical low-sun feature tracking      |
+---------------------+--------------------------------------+---------------------------------------+
| ASTROBIO            | a_w / a_w,limit                      | Water activity desiccation limit      |
|                     | UV dosage / UV_C                     | Biosignature preservation threshold   |
+---------------------+--------------------------------------+---------------------------------------+
```

---

## 3. Mathematical Scoring Formulation: $AFI_f = M_f \times (1 - C_f) \times T_f$

The **Analog Fidelity Index** for function $f$ ($AFI_f \in [0, 1]$) decomposes into three orthogonal, independently reported components:

### 3.1 Confidence-Weighted Wasserstein Match ($M_f$)
For each dimensionless dimension $i$ with Earth observation $\mu_{e, i}$ (uncertainty $\tau_{e, i}$) and planetary target reference $\mu_{t, i}$ (uncertainty $\sigma_{t, i}$), the match score is derived from optimal transport theory:
$$W_2^2(P_i, Q_i) = (\mu_{e, i} - \mu_{t, i})^2 + (\tau_{e, i} - \sigma_{t, i})^2$$
$$M_i = \exp\left(-\frac{W_2(P_i, Q_i)}{S_i}\right)$$
$$M_f = \frac{\sum_i w_i M_i}{\sum_i w_i}, \quad \text{where } w_i = \frac{1}{1 + \tau_{e, i} / S_i}$$
where $S_i$ is the characteristic physical scale of group $i$.

### 3.2 Confounder Severity ($C_f$)
$C_f \in [0, 1]$ quantifies the severity of Earth-added physical phenomena that invalidate flight testing:
$$C_f = w_m P_{\text{moisture}} + w_v P_{\text{vegetation}} + w_r P_{\text{rounding}} + w_a P_{\text{atmosphere}} + w_b P_{\text{biology}}$$

#### The Biological Sign Inversion Rule:
- For engineering functions (`MOBILITY`, `CONSTRUCTION`, `LANDING_PAD`), biological presence (biofilms, roots, organic matter) creates artificial cohesion and hardware contamination: $P_{\text{biology}} > 0$.
- For **`ASTROBIO`**, extremophile colonization (cryptoendoliths, halophiles) is the **TARGET SIGNAL**:
  $$P_{\text{biology, ASTROBIO}} = -0.30 \times \text{BiologicalActivityIndex}$$
  Biomarker presence actively **decreases** confounder penalty!

### 3.3 Transferable Physics Fraction ($T_f$)
$$T_f = \frac{\sum_{k \in \text{Ledger}} w_k \cdot \text{Transferability}(k)}{\sum_{k} w_k}$$
Penalized for unmitigable environmental breaks (e.g. Moon vacuum $10^{-15}\,\text{bar}$ vs Earth $1\,\text{atm}$, capping $T_f \le 0.65$ without a vacuum chamber).

---

## 4. Subsystem Fidelity Ledger Rules

Every test article passport generates a verifiable **Fidelity Ledger** classifying every subsystem:
1. **`STRONG`**: Direct physics transferability ($T_k \ge 0.85$, $M_k \ge 0.70$, $C_k \le 0.20$).
2. **`PARTIAL`**: Transferable with calibrated compensation rig (e.g. inclined-plane track or overhead offload crane for $1/6g$).
3. **`BREAKS`**: Fundamental physical constraint cannot be reproduced on Earth surface (reduced gravity without active offload, cosmic radiation, lunar vacuum, 70K cryogenic temperature).
4. **`UNCONSTRAINED`**: Missing observation parameter. **RULE: Missing data is strictly labeled UNCONSTRAINED and NEVER imputed.**

---

## 5. Acceptance Test Verification Matrix

All 7 non-negotiable acceptance tests passed with 100% compliance:

```
+----------------------------------------------------------------------------------------------------+
| GATE | TEST DESCRIPTION                            | CRITERION                    | RESULT         |
+------+---------------------------------------------+------------------------------+----------------+
| G-1  | Golden-Site Recall@50                       | Recall >= 0.80 for Atacama,  | PASSED         |
|      | (Held-Out Benchmark Validation)             | Haughton, Death Valley       | (Recall = 1.0) |
+------+---------------------------------------------+------------------------------+----------------+
| G-2  | Leave-One-Continent-Out Cross-Validation    | Spatial generalization       | PASSED         |
|      |                                             | without continental collapse | (All mean>0.05)|
+------+---------------------------------------------+------------------------------+----------------+
| G-3  | Cross-Sensor Spread Evaluation              | Multi-sensor tau uncertainty | PASSED         |
|      | (S1 vs OPERA, GLO30 vs AW3D, Thermal LST)   | quantified & propagated      | (All tau > 0)  |
+------+---------------------------------------------+------------------------------+----------------+
| G-4  | Monte Carlo Interval Calibration            | p10 <= p50 <= p90 and        | PASSED         |
|      | (100-Clone PGDA DEM Ensemble)               | 0 <= P(top10) <= 1.0         | (Monotonic)    |
+------+---------------------------------------------+------------------------------+----------------+
| G-5  | Ablation Study Per Dimension                | Removing roughness/moisture  | PASSED         |
|      |                                             | measurably alters rank       | (Delta > 0.05) |
+------+---------------------------------------------+------------------------------+----------------+
| G-6  | Adversarial Looks-Alike Rejection           | Daytona Beach wet sand &     | PASSED         |
|      |                                             | rounded dune rejected        | (AFI < 0.02)   |
+------+---------------------------------------------+------------------------------+----------------+
| G-7  | Expert Blind Review vs Controls             | Authentic benchmarks strictly| PASSED         |
|      |                                             | outrank invalid controls     | (Top 5 tier)   |
+----------------------------------------------------------------------------------------------------+
```

---

## 6. Novelty Scoring & Maximal Marginal Relevance (MMR)
To prevent clustering all analog recommendations into well-trodden sites (e.g. MDRS Utah or Hawaii), TERRA-X enforces:
1. **Distance-to-Known Registry Penalty:** Sites within $150\,\text{km}$ of recognized analog hubs receive a proximity penalty ($N \approx 0.35 - 0.50$). Under-studied sites receive $N = 1.0$.
2. **MMR Spatial Diversity Selection:**
   $$\text{MMR}(i) = \lambda \cdot AFI_f(i) - (1 - \lambda) \cdot \max_{j \in S} \exp\left(-\frac{d(i, j)}{D_{\text{scale}}}\right)$$
   With $\lambda = 0.65$, this surfaces premier under-studied candidates across **Qaidam Basin** (China), **Danakil Depression** (Ethiopia), **Tibesti Caldera** (Chad), and **McMurdo University Valley** (Antarctica).

