# TERRA-X: Transferable Test Recipes Manual
## Operations Tied to NASA Space Technology Mission Directorate (STMD) Gaps
**Document ID:** TERRAX-TR-2026-V1  
**Target Missions:** Artemis III/IV Lunar Surface, Commercial Lunar Payload Services (CLPS), Mars 2026+

---

## 1. NASA Technology Taxonomy Mapping

The TERRA-X engine automatically pairs each discovered H3 analog test article with a **Transferable Test Recipe** directly addressing NASA's named technology gaps:

```
+----------------------------------------------------------------------------------------------------+
| NASA TAXONOMY GAP   | TECH GAP TITLE                               | PRIMARY EXPLORATION FUNCTION  |
+---------------------+----------------------------------------------+-------------------------------+
| TX04.1              | Precision Landing & Hazard Avoidance in PSR  | PNT_DENIED_NAV                |
| TX06.2              | Regolith Dust Mitigation & Seal Integrity    | CONSTRUCTION_ISRU / MOBILITY  |
| TX07.1              | Cryogenic & High-ΔT Surface Mechanisms       | HUMAN_OPS_THERMAL             |
| TX03.3              | Autonomous Robotic Cable & Fluid Mating      | CONSTRUCTION_ISRU             |
| TX07.2              | Regolith Excavation & Beneficiation          | CONSTRUCTION_ISRU             |
| TX04.3              | Surface Mobility Traversability & Sinkage    | MOBILITY                      |
+---------------------+----------------------------------------------+-------------------------------+
```

---

## 2. Test Recipe Specification: TX04.1 Precision Landing & Hazard Avoidance in Shadow

### 2.1 Operational Context
Lunar South Pole exploration (e.g. Shackleton Crater Rim, Connecting Ridge) requires autonomous descent guidance and hazard avoidance in Permanently Shadowed Regions (PSRs) where sun elevation is grazing ($< 1.5^\circ$) or non-existent, and GNSS is absent.

### 2.2 Qualified Analog Sites
- **Primary Analog Article:** H3 Cell `86043644fffffff` (Haughton Impact Crater, Devon Island, Canada)
- **Topographic Match:** Crater rim geometry, horizon-blocked fraction $\text{HBF} = 0.58$, steep shadow contrast.

### 2.3 Flight Hardware Test Recipe
```json
{
  "test_recipe_id": "RECIPE-TX04.1-HAUGHTON-SHADOW-TRN",
  "nasa_tech_gap": "TX04.1 Precision Landing & Hazard Detection in PSR",
  "target_planetary_body": "MOON (South Pole)",
  "gravity_compensation_fixture": {
    "recommended_platform": "Autonomous Multirotor Drone or Aerial Tethered Gantry",
    "scaled_velocity_rule": "v_earth = v_moon * sqrt(g_earth / g_moon) = 2.46 * v_moon",
    "descent_rate_profile": "Constant deceleration 0.35 m/s² simulating lunar thruster control authority"
  },
  "illumination_and_environmental_conditioning": {
    "solar_elevation_window": "Conduct sorties exclusively when sun elevation is between 0.5° and 3.0° above horizon (polar equinox window) or under night conditions with collimated high-power floodlights mounted at ground level",
    "sensor_payload": [
      "Flash-LIDAR 1.5 um pulsed 3D imaging camera",
      "Doppler LIDAR 3-beam velocimeter",
      "High Dynamic Range (HDR) optical navigation camera with anti-blooming baffle"
    ]
  },
  "acceptance_criteria": {
    "hazard_detection_threshold": "Detect 0.3m boulders and 0.5m craters at 150m slant range with probability >= 99%",
    "state_estimation_drift": "< 0.1% distance traveled under GNSS-denied inertial/optical odometry"
  }
}
```

---

## 3. Test Recipe Specification: TX06.2 Dust Mitigation & Seal Protection

### 3.1 Operational Context
Lunar regolith particles are sub-20 $\mu\text{m}$, jagged, un-weathered, and electrostatically charged. Terrestrial sands with rounded grains (Wadell roundness $> 0.50$) fail to simulate seal abrasion and micro-clinging.

### 3.2 Qualified Analog Sites
- **Primary Analog Article:** H3 Cell `8644485afffffff` (Mauna Kea Basaltic Tephra Cone, Hawaii) & `867b4512fffffff` (Tibesti Caldera, Chad).
- **Material Match:** Unweathered glassy basaltic ash, Wadell roundness $W_r < 0.22$, zero moisture.

### 3.3 Conditioning & Execution Protocol
1. **Desiccation Bake-Out:** Test bed tephra must be baked at $120^\circ\text{C}$ under vacuum or nitrogen purge until gravimetric water content $w \le 0.005\%$. Capillary moisture falsifies cohesion!
2. **Triboelectric Charging:** Pass granular stream across insulating PTFE chutes to induce surface electrostatic charge density $\sigma \ge 10^{-5}\,\text{C/m}^2$.
3. **Hardware Test Articles:**
   - Active dynamic rotary seals (wheel hubs, drill chucks).
   - Electrical umbilical pin guide sleeves.
   - Suit fabric patch samples (Orthofabric with electrodynamic dust shield).

---

## 4. Test Recipe Specification: TX07.1 Extreme-Temperature Cryogenic Mechanisms (40K to 400K)

### 4.1 Operational Context
South pole crater floors sit in permanent cryogenic cold traps ($40\,\text{K} - 70\,\text{K}$), while equatorial mare plains swing from $100\,\text{K}$ to $390\,\text{K}$. Solid lubricants (e.g. $\text{MoS}_2$) experience severe friction spikes below $120\,\text{K}$.

### 4.2 Environmental Break & Testing Compensator
- **Hard Break Notice:** Open-air testing cannot reproduce $70\,\text{K}$ radiative equilibrium.
- **Transferable Procedure:** Test articles are mounted on a cryogenic cold-plate shroud inside a field-deployable portable vacuum chamber (TVAC interface), with soil simulant beds chilled by liquid nitrogen / helium coils to match the target thermal inertia ($I \approx 45 - 60\,\text{J}\cdot\text{m}^{-2}\cdot\text{K}^{-1}\cdot\text{s}^{-1/2}$).

---

## 5. Test Recipe Specification: TX03.3 Autonomous Robotic Cable & Fluid Mating in Regolith

### 5.1 Operational Context
Power distribution architectures for Moon bases (Fission Surface Power to habitats) require autonomous docking of 5 kV umbilical cables into connectors exposed to regolith dust.

### 5.2 Flight Hardware Test Recipe
```json
{
  "test_recipe_id": "RECIPE-TX03.3-CABLE-MATING",
  "nasa_tech_gap": "TX03.3 Autonomous Wet/Dry Cable & Fluid Mating in Contaminated Regolith",
  "test_article_site": "Central Namib Gravel Pavement (H3: 867a2134fffffff)",
  "gravity_compensation_fixture": {
    "fixture": "Gravity-counterbalance pantograph on robotic manipulator",
    "load_scaling": "Robot arm joints programmed with 1/6g inertia matrix (M_moon = 1/6 * M_earth normal force)"
  },
  "contamination_protocol": {
    "regolith_layer": "50mm uncompacted basaltic fines spread over connector receptacle face",
    "insertion_cycles": 100,
    "dielectric_isolation_test": "Continuous 5 kV DC insulation resistance measurement post-mating (> 100 GOhm required)"
  }
}
```

---

## 6. Test Recipe Specification: TX07.2 Regolith Excavation & Beneficiation

### 6.1 Dimensionless Cutting Force Law
Excavation cutting force $F$ scales with the dimensionless force group:
$$\Pi_{\text{excavation}} = \frac{F}{\gamma \cdot d^3}$$
where $d$ is tool cutting depth, and $\gamma = \rho g$.

Because lunar $\gamma_{\text{moon}} = \frac{1}{6.37} \gamma_{\text{earth}}$, **an excavator tested on Earth at $1g$ experiences over $6\times$ higher resisting force per unit depth than on the Moon**.

### 6.2 Mandatory Test Rig Configuration
- **Option A (Traction-Equated Ballast):** To prevent premature excavator track slip under Earth gravity, the vehicle chassis mass must be ballasted:
  $$M_{\text{earth, ballast}} = 6.37 \times M_{\text{flight}}$$
- **Option B (Inclined-Plane Test Bed):** Construct the regolith test trench on an inclined ramp tilted at:
  $$\alpha = \arcsin\left(\frac{g_{\text{moon}}}{g_{\text{earth}}}\right) = \arcsin\left(\frac{1.62}{9.81}\right) = 9.51^\circ$$
  The component of normal gravity acting into the bed precisely equals lunar gravity ($g_{\text{normal}} = 1.62\,\text{m/s}^2$).

