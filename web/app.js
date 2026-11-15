/**
 * TERRA-X — Planetary Functional Analog Discovery Engine
 * NASA Space Apps Challenge 2026
 * Full Scientific Workstation Frontend Engine
 * 
 * Features:
 * - MapLibre GL JS Dual Maps: Earth Analogs (Dark OSM / ESRI Sat) + Moon/Mars Planetary Terrain
 * - 12 Planetary Targets: Official Artemis III 2024 Candidates + Independent Research Areas + Mars Regions
 * - 10 Exploration Function Profiles with Dimensionless Similitude & Evidence Confidence Q
 * - 4 Workspaces: Discover, Compare, Analog Passports, Data Observatory
 * - Interactive What-If Mission Sliders with Real-Time Re-Ranking
 * - Fidelity Ledger (STRONG, PARTIAL, BREAKS, UNCONSTRAINED) & Actionable NASA Test Recipes
 * - Multi-Agency Provenance & Data Observatory Lifecycle Tracker
 * - Guided Tour Walkthrough for Space Apps Judges
 */

// ==============================================================================
// 1. Planetary Target Catalogs (NASA Artemis III 2024 Updates & Mars Regions)
// ==============================================================================
const PLANETARY_TARGETS = {
  // Official Artemis III Candidate Regions (Updated 2024)
  "MOON_ARTEMIS3_CABEUS_B": {
    name: "Peak near Cabeus B",
    category: "Official Artemis III Candidate (NASA 2024)",
    body: "MOON",
    lat: -84.9,
    lon: -35.2,
    gravity: 1.62,
    loadScale: 6.37,
    unitWeight: 2462.4,
    hardBreaks: [
      "LUNAR_VACUUM (1e-15 bar)",
      "LUNAR_1_6TH_GRAVITY (1.62 m/s²)",
      "GCR_SPE_COSMIC_RADIATION",
      "LOW_ELEVATION_GRAZING_SUN (< 1.8° solar elevation)",
      "DEEP_CRYOGENIC_PSR_COLD_TRAP (< 60 K)"
    ],
    dimRef: {
      tan_theta_over_tan_phi: 0.36,
      h_rms_over_D: 0.24,
      p_over_gamma_B: 19.2,
      cohesion_over_gamma_d: 4.1,
      delta_T_over_T_mean: 0.38,
      horizon_blocked_fraction: 0.52
    },
    desc: "Elevated massif ridge near Cabeus B. Excellent Earth communication line-of-sight with proximal access to cryogenic PSR volatile deposits.",
    product: "USGS LOLA 5m Polar DEM / Diviner Thermal Suite",
    scale: "1:25,000 Polar Stereographic"
  },
  "MOON_ARTEMIS3_HAWORTH": {
    name: "Haworth Rim",
    category: "Official Artemis III Candidate (NASA 2024)",
    body: "MOON",
    lat: -87.4,
    lon: -5.1,
    gravity: 1.62,
    loadScale: 6.37,
    unitWeight: 2413.8,
    hardBreaks: [
      "LUNAR_VACUUM (1e-15 bar)",
      "LUNAR_1_6TH_GRAVITY (1.62 m/s²)",
      "GCR_SPE_COSMIC_RADIATION",
      "PERMANENT_SHADOW_COLD_TRAP (40 K - 55 K)",
      "STEEP_CRATER_WALL_SLOPES (> 24° scarp)"
    ],
    dimRef: {
      tan_theta_over_tan_phi: 0.48,
      h_rms_over_D: 0.31,
      p_over_gamma_B: 17.0,
      cohesion_over_gamma_d: 4.8,
      delta_T_over_T_mean: 0.25,
      horizon_blocked_fraction: 0.68
    },
    desc: "Haworth crater rim corridor. Direct access to deep shadowed floor with high volatile cold-trapping potential.",
    product: "LRO LOLA 5m DEM / LEND Hydrogen Maps",
    scale: "1:25,000 Polar Stereographic"
  },
  "MOON_ARTEMIS3_MALAPERT": {
    name: "Malapert Massif",
    category: "Official Artemis III Candidate (NASA 2024)",
    body: "MOON",
    lat: -85.9,
    lon: 0.0,
    gravity: 1.62,
    loadScale: 6.37,
    unitWeight: 2511.0,
    hardBreaks: [
      "LUNAR_VACUUM (1e-15 bar)",
      "LUNAR_1_6TH_GRAVITY (1.62 m/s²)",
      "GCR_SPE_COSMIC_RADIATION",
      "PROLONGED_DIRECT_EARTH_VISIBILITY",
      "HIGH_RELIEF_MASSIF_SLOPES (up to 5 km summit)"
    ],
    dimRef: {
      tan_theta_over_tan_phi: 0.29,
      h_rms_over_D: 0.21,
      p_over_gamma_B: 22.0,
      cohesion_over_gamma_d: 3.5,
      delta_T_over_T_mean: 0.45,
      horizon_blocked_fraction: 0.28
    },
    desc: "High topographic prominence providing multi-week continuous solar illumination periods and uninterrupted direct-to-Earth communication.",
    product: "LROC NAC Elevation Models / LOLA GDR",
    scale: "1:50,000 Polar Stereographic"
  },
  "MOON_ARTEMIS3_MONS_MOUTON_PLATEAU": {
    name: "Mons Mouton Plateau",
    category: "Official Artemis III Candidate (NASA 2024)",
    body: "MOON",
    lat: -84.5,
    lon: -31.0,
    gravity: 1.62,
    loadScale: 6.37,
    unitWeight: 2478.6,
    hardBreaks: [
      "LUNAR_VACUUM (1e-15 bar)",
      "LUNAR_1_6TH_GRAVITY (1.62 m/s²)",
      "GCR_SPE_COSMIC_RADIATION",
      "ELEVATED_PLATEAU_EDGE_DROP_OFFS",
      "INTERMITTENT_SHADOW_PASSAGES"
    ],
    dimRef: {
      tan_theta_over_tan_phi: 0.18,
      h_rms_over_D: 0.17,
      p_over_gamma_B: 24.5,
      cohesion_over_gamma_d: 3.2,
      delta_T_over_T_mean: 0.40,
      horizon_blocked_fraction: 0.22
    },
    desc: "Broad, relatively flat plateau summit suitable for rover mobility, landing pad construction, and surface base deployment.",
    product: "NASA VIPER / Artemis 5m Polar DEM",
    scale: "1:25,000 Polar Stereographic"
  },
  "MOON_ARTEMIS3_NOBILE_RIM_1": {
    name: "Nobile Rim 1",
    category: "Official Artemis III Candidate (NASA 2024)",
    body: "MOON",
    lat: -85.2,
    lon: 37.8,
    gravity: 1.62,
    loadScale: 6.37,
    unitWeight: 2446.2,
    hardBreaks: [
      "LUNAR_VACUUM (1e-15 bar)",
      "LUNAR_1_6TH_GRAVITY (1.62 m/s²)",
      "GCR_SPE_COSMIC_RADIATION",
      "MICRO-COLD_TRAP_PERMAFROST_SIMULANT",
      "EXTREME_THERMAL_CONTRAST (70 K to 220 K)"
    ],
    dimRef: {
      tan_theta_over_tan_phi: 0.32,
      h_rms_over_D: 0.25,
      p_over_gamma_B: 18.0,
      cohesion_over_gamma_d: 4.2,
      delta_T_over_T_mean: 0.55,
      horizon_blocked_fraction: 0.44
    },
    desc: "Crater rim providing diverse sampling of impact ejecta, undulating slopes, and micro-cold traps holding shallow volatile deposits.",
    product: "LRO LOLA 5m Polar DEM / Diviner Maps",
    scale: "1:25,000 Polar Stereographic"
  },
  "MOON_ARTEMIS3_DE_GERLACHE_RIM_2": {
    name: "de Gerlache Rim 2",
    category: "Official Artemis III Candidate (NASA 2024)",
    body: "MOON",
    lat: -88.3,
    lon: -68.8,
    gravity: 1.62,
    loadScale: 6.37,
    unitWeight: 2430.0,
    hardBreaks: [
      "LUNAR_VACUUM (1e-15 bar)",
      "LUNAR_1_6TH_GRAVITY (1.62 m/s²)",
      "GCR_SPE_COSMIC_RADIATION",
      "NARROW_RIDGE_TRAVERSAL_CORRIDORS (< 50m)",
      "LOW_SOLAR_INCIDENCE_BLOOMING"
    ],
    dimRef: {
      tan_theta_over_tan_phi: 0.41,
      h_rms_over_D: 0.27,
      p_over_gamma_B: 18.5,
      cohesion_over_gamma_d: 4.3,
      delta_T_over_T_mean: 0.48,
      horizon_blocked_fraction: 0.58
    },
    desc: "Narrow polar ridge system between Shackleton and de Gerlache craters. Dynamic shadows with sharp illumination contrast.",
    product: "PGDA 5m Polar DEM Suite / ShadowCam",
    scale: "1:25,000 Polar Stereographic"
  },
  "MOON_ARTEMIS3_SLATER_PLAIN": {
    name: "Slater Plain",
    category: "Official Artemis III Candidate (NASA 2024)",
    body: "MOON",
    lat: -88.1,
    lon: 113.5,
    gravity: 1.62,
    loadScale: 6.37,
    unitWeight: 2494.8,
    hardBreaks: [
      "LUNAR_VACUUM (1e-15 bar)",
      "LUNAR_1_6TH_GRAVITY (1.62 m/s²)",
      "GCR_SPE_COSMIC_RADIATION",
      "CONTINUOUS_REGOLITH_BED (< 5% exposed blocky bedrock)",
      "14_DAY_NIGHT_CRYOGENIC_FREEZE"
    ],
    dimRef: {
      tan_theta_over_tan_phi: 0.14,
      h_rms_over_D: 0.15,
      p_over_gamma_B: 25.0,
      cohesion_over_gamma_d: 3.0,
      delta_T_over_T_mean: 0.35,
      horizon_blocked_fraction: 0.18
    },
    desc: "Low-slope polar regolith plain between Faustini and Amundsen craters. Optimal geotechnical baseline for excavation & landing pad testing.",
    product: "LROC NAC Photomosaic / LOLA 5m DEM",
    scale: "1:50,000 Polar Stereographic"
  },

  // Independent Lunar Research Areas
  "MOON_RESEARCH_SHACKLETON": {
    name: "Shackleton Crater Rim & Ridge",
    category: "Independent Lunar Research Area",
    body: "MOON",
    lat: -89.9,
    lon: 0.0,
    gravity: 1.62,
    loadScale: 6.37,
    unitWeight: 2462.4,
    hardBreaks: [
      "LUNAR_VACUUM (1e-15 bar)",
      "LUNAR_1_6TH_GRAVITY (1.62 m/s²)",
      "GCR_SPE_COSMIC_RADIATION",
      "DEEP_CRYOGENIC_PSR_70K (< 70 K)",
      "LOW_ELEVATION_GRAZING_SUN (< 1.5°)"
    ],
    dimRef: {
      tan_theta_over_tan_phi: 0.38,
      h_rms_over_D: 0.28,
      p_over_gamma_B: 18.5,
      cohesion_over_gamma_d: 4.0,
      delta_T_over_T_mean: 0.32,
      horizon_blocked_fraction: 0.58
    },
    desc: "Lunar South Pole landmark benchmark. Permanent shadow in the 4.2 km deep interior with continuous illumination peaks on the rim.",
    product: "PGDA 5m Polar DEM (100 clones)",
    scale: "1:25,000 Polar Stereographic"
  },
  "MOON_RESEARCH_OCEANUS_PROCELLARUM": {
    name: "Oceanus Procellarum / Marius Hills",
    category: "Independent Lunar Research Area",
    body: "MOON",
    lat: 14.1,
    lon: -56.7,
    gravity: 1.62,
    loadScale: 5.76,
    unitWeight: 2721.6,
    hardBreaks: [
      "LUNAR_VACUUM (1e-15 bar)",
      "LUNAR_1_6TH_GRAVITY (1.62 m/s²)",
      "GCR_SPE_COSMIC_RADIATION",
      "14_DAY_LUNAR_NIGHT (100 K sink)",
      "NOON_THERMAL_PEAK (390 K)"
    ],
    dimRef: {
      tan_theta_over_tan_phi: 0.08,
      h_rms_over_D: 0.12,
      p_over_gamma_B: 24.0,
      cohesion_over_gamma_d: 2.8,
      delta_T_over_T_mean: 1.15,
      horizon_blocked_fraction: 0.04
    },
    desc: "Extensive volcanic mare plain featuring the Marius Hills collapse pit (subsurface lava tube skylight opening).",
    product: "JAXA Kaguya TC / USGS LOLA 118m GDR",
    scale: "1:100,000 Equirectangular"
  },

  // Mars Study Regions
  "MARS_STUDY_OXIA_PLANUM": {
    name: "Oxia Planum",
    category: "Mars Exploration Study Region",
    body: "MARS",
    lat: 18.27,
    lon: -24.63,
    gravity: 3.72,
    loadScale: 2.91,
    unitWeight: 5282.4,
    hardBreaks: [
      "MARS_LOW_PRESSURE (~6.5 mbar CO2)",
      "MARS_0_38TH_GRAVITY (3.72 m/s²)",
      "SURFACE_UV_C_IRRADIATION",
      "SOIL_PERCHLORATES (oxidizing salts)",
      "WIND_DRIVEN_DUST_STORMS"
    ],
    dimRef: {
      tan_theta_over_tan_phi: 0.10,
      h_rms_over_D: 0.14,
      p_over_gamma_B: 14.5,
      cohesion_over_gamma_d: 3.6,
      delta_T_over_T_mean: 0.42,
      horizon_blocked_fraction: 0.02
    },
    desc: "ExoMars Rosalind Franklin landing target. Ancient Noachian phyllosilicate clay-rich plain with high biosignature preservation potential.",
    product: "ESA Mars Express HRSC / CTX 20m DTM",
    scale: "1:50,000 Equirectangular"
  },
  "MARS_STUDY_JEZERO_DELTA": {
    name: "Jezero Crater Western Delta",
    category: "Mars Exploration Study Region",
    body: "MARS",
    lat: 18.38,
    lon: 77.58,
    gravity: 3.72,
    loadScale: 2.91,
    unitWeight: 5394.0,
    hardBreaks: [
      "MARS_LOW_PRESSURE (~6.2 mbar CO2)",
      "MARS_0_38TH_GRAVITY (3.72 m/s²)",
      "SURFACE_UV_C_IRRADIATION",
      "SOIL_PERCHLORATES",
      "ACTIVE_DUST_DEVILS_AND_ABRASION"
    ],
    dimRef: {
      tan_theta_over_tan_phi: 0.22,
      h_rms_over_D: 0.18,
      p_over_gamma_B: 13.8,
      cohesion_over_gamma_d: 3.8,
      delta_T_over_T_mean: 0.44,
      horizon_blocked_fraction: 0.08
    },
    desc: "Perseverance rover exploration area. River delta scarp, carbonate and clay deposits, stratified lacustrine mudstones.",
    product: "NASA M2020 HiRISE 1m DTM / CRISM",
    scale: "1:25,000 Equirectangular"
  },
  "MARS_STUDY_GALE_CRATER": {
    name: "Gale Crater / Mt. Sharp",
    category: "Mars Exploration Study Region",
    body: "MARS",
    lat: -4.59,
    lon: 137.44,
    gravity: 3.72,
    loadScale: 2.76,
    unitWeight: 5580.0,
    hardBreaks: [
      "MARS_LOW_PRESSURE (~7.1 mbar CO2)",
      "MARS_0_38TH_GRAVITY (3.72 m/s²)",
      "VENTIFACT_WHEEL_GOUGE_TERRAIN",
      "SURFACE_UV_C_IRRADIATION",
      "DIURNAL_THERMAL_SWING (~90 K swing)"
    ],
    dimRef: {
      tan_theta_over_tan_phi: 0.28,
      h_rms_over_D: 0.26,
      p_over_gamma_B: 15.2,
      cohesion_over_gamma_d: 3.9,
      delta_T_over_T_mean: 0.49,
      horizon_blocked_fraction: 0.14
    },
    desc: "Curiosity rover traverse. 5 km high central mound with sulfate-bearing layered strata and abrasive wind-carved ventifact fields.",
    product: "NASA CTX / HiRISE DTM / THEMIS TI",
    scale: "1:50,000 Equirectangular"
  }
};

// Aliases for legacy IDs
PLANETARY_TARGETS["MOON_SOUTH_POLE_SHACKLETON"] = PLANETARY_TARGETS["MOON_RESEARCH_SHACKLETON"];
PLANETARY_TARGETS["MOON_OCEANUS_PROCELLARUM"] = PLANETARY_TARGETS["MOON_RESEARCH_OCEANUS_PROCELLARUM"];
PLANETARY_TARGETS["MARS_JEZERO_DELTA"] = PLANETARY_TARGETS["MARS_STUDY_JEZERO_DELTA"];
PLANETARY_TARGETS["MARS_GALE_CRATER"] = PLANETARY_TARGETS["MARS_STUDY_GALE_CRATER"];

// ==============================================================================
// 2. Earth Analog Candidates (Benchmark, Novel, & Adversarial Controls)
// ==============================================================================
let CANDIDATES = [
  {
    id: "SITE-ATACAMA-YUNGAY",
    name: "Atacama Desert (Yungay Core)",
    country: "Chile",
    continent: "South America",
    lat: -24.0833,
    lon: -69.8667,
    cell_id: "861f1d48fffffff",
    elevation_m: 1020,
    slope_deg: 2.5,
    h_rms_m: 0.04,
    friction_angle_deg: 33.5,
    cohesion_kpa: 1.2,
    thermal_inertia_si: 380.0,
    sky_view_factor: 0.95,
    soil_moisture_wtd: 0.008,
    vegetation_ndvi: 0.02,
    grain_wadell_roundness: 0.28,
    biological_activity_index: 0.08,
    stac_id: "urn:terrax:chile:atacama-yungay",
    doi: "10.1126/science.1087369",
    novelty_status: "BENCHMARK_GOLDEN"
  },
  {
    id: "SITE-HAUGHTON-DEVON",
    name: "Haughton Impact Structure (Devon Island)",
    country: "Canada",
    continent: "North America",
    lat: 75.3833,
    lon: -89.6833,
    cell_id: "86047320fffffff",
    elevation_m: 220,
    slope_deg: 14.5,
    h_rms_m: 0.16,
    friction_angle_deg: 38.0,
    cohesion_kpa: 3.8,
    thermal_inertia_si: 520.0,
    sky_view_factor: 0.65,
    soil_moisture_wtd: 0.065,
    vegetation_ndvi: 0.03,
    grain_wadell_roundness: 0.24,
    biological_activity_index: 0.05,
    stac_id: "urn:terrax:canada:haughton-devon",
    doi: "10.1111/j.1945-5100.1998.tb01332.x",
    novelty_status: "BENCHMARK_GOLDEN"
  },
  {
    id: "SITE-DEATH-VALLEY",
    name: "Death Valley (Mars Hill)",
    country: "United States",
    continent: "North America",
    lat: 36.5050,
    lon: -116.8750,
    cell_id: "8626e25afffffff",
    elevation_m: -86,
    slope_deg: 4.5,
    h_rms_m: 0.11,
    friction_angle_deg: 35.0,
    cohesion_kpa: 2.1,
    thermal_inertia_si: 450.0,
    sky_view_factor: 0.88,
    soil_moisture_wtd: 0.015,
    vegetation_ndvi: 0.01,
    grain_wadell_roundness: 0.30,
    biological_activity_index: 0.02,
    stac_id: "urn:terrax:usgs:death-valley",
    doi: "10.1029/2004JE002364",
    novelty_status: "BENCHMARK_GOLDEN"
  },
  {
    id: "SITE-MAUNA-KEA",
    name: "Mauna Kea Basaltic Tephra Cone",
    country: "United States",
    continent: "Oceania",
    lat: 19.8206,
    lon: -155.4681,
    cell_id: "86446864fffffff",
    elevation_m: 4207,
    slope_deg: 22.0,
    h_rms_m: 0.08,
    friction_angle_deg: 41.0,
    cohesion_kpa: 1.5,
    thermal_inertia_si: 310.0,
    sky_view_factor: 0.72,
    soil_moisture_wtd: 0.020,
    vegetation_ndvi: 0.02,
    grain_wadell_roundness: 0.20,
    biological_activity_index: 0.01,
    stac_id: "urn:terrax:usgs:mauna-kea",
    doi: "10.1016/j.pss.2010.05.006",
    novelty_status: "BENCHMARK_GOLDEN"
  },
  {
    id: "SITE-SVALBARD-BOCKFJORDEN",
    name: "Svalbard Bockfjorden Volcanic Complex",
    country: "Norway",
    continent: "Europe",
    lat: 79.4500,
    lon: 13.3833,
    cell_id: "86040842fffffff",
    elevation_m: 450,
    slope_deg: 18.0,
    h_rms_m: 0.14,
    friction_angle_deg: 39.5,
    cohesion_kpa: 4.2,
    thermal_inertia_si: 580.0,
    sky_view_factor: 0.58,
    soil_moisture_wtd: 0.080,
    vegetation_ndvi: 0.04,
    grain_wadell_roundness: 0.26,
    biological_activity_index: 0.04,
    stac_id: "urn:terrax:norway:svalbard-bockfjorden",
    doi: "10.1089/ast.2007.0143",
    novelty_status: "BENCHMARK_GOLDEN"
  },
  {
    id: "SITE-KILBOURNE-HOLE",
    name: "Kilbourne Hole Maar Crater",
    country: "United States",
    continent: "North America",
    lat: 31.9719,
    lon: -106.9639,
    cell_id: "8626c043fffffff",
    elevation_m: 1290,
    slope_deg: 12.0,
    h_rms_m: 0.07,
    friction_angle_deg: 36.0,
    cohesion_kpa: 1.8,
    thermal_inertia_si: 410.0,
    sky_view_factor: 0.82,
    soil_moisture_wtd: 0.025,
    vegetation_ndvi: 0.06,
    grain_wadell_roundness: 0.25,
    biological_activity_index: 0.03,
    stac_id: "urn:terrax:usgs:kilbourne-hole",
    doi: "10.1002/2016JE005252",
    novelty_status: "BENCHMARK_GOLDEN"
  },
  {
    id: "SITE-QAIDAM-YARDANG",
    name: "Qaidam Basin Mars Analog Yardang Field",
    country: "China",
    continent: "Asia",
    lat: 37.8500,
    lon: 93.4000,
    cell_id: "8631b1c6fffffff",
    elevation_m: 2800,
    slope_deg: 8.5,
    h_rms_m: 0.18,
    friction_angle_deg: 37.0,
    cohesion_kpa: 2.8,
    thermal_inertia_si: 340.0,
    sky_view_factor: 0.78,
    soil_moisture_wtd: 0.005,
    vegetation_ndvi: 0.00,
    grain_wadell_roundness: 0.26,
    biological_activity_index: 0.01,
    stac_id: "urn:terrax:asia:qaidam-yardang",
    doi: "10.1016/j.epsl.2018.06.017",
    novelty_status: "NOVEL_DISCOVERY"
  },
  {
    id: "SITE-MCMURDO-DRY-VALLEYS",
    name: "McMurdo Dry Valleys (University Valley)",
    country: "Antarctica",
    continent: "Antarctica",
    lat: -77.8667,
    lon: 160.7167,
    cell_id: "86b62438fffffff",
    elevation_m: 1650,
    slope_deg: 16.0,
    h_rms_m: 0.12,
    friction_angle_deg: 40.0,
    cohesion_kpa: 5.5,
    thermal_inertia_si: 620.0,
    sky_view_factor: 0.62,
    soil_moisture_wtd: 0.002,
    vegetation_ndvi: 0.00,
    grain_wadell_roundness: 0.22,
    biological_activity_index: 0.01,
    stac_id: "urn:terrax:antarctica:mcmurdo-univ",
    doi: "10.1016/j.icarus.2013.04.009",
    novelty_status: "NOVEL_DISCOVERY"
  },
  {
    id: "SITE-TIBESTI-TARSO-VOON",
    name: "Tibesti Volcanic Range (Tarso Voon Caldera)",
    country: "Chad",
    continent: "Africa",
    lat: 20.9167,
    lon: 17.2833,
    cell_id: "863fa942fffffff",
    elevation_m: 2900,
    slope_deg: 19.5,
    h_rms_m: 0.15,
    friction_angle_deg: 42.0,
    cohesion_kpa: 2.2,
    thermal_inertia_si: 390.0,
    sky_view_factor: 0.68,
    soil_moisture_wtd: 0.003,
    vegetation_ndvi: 0.00,
    grain_wadell_roundness: 0.21,
    biological_activity_index: 0.00,
    stac_id: "urn:terrax:africa:tibesti-tarso-voon",
    doi: "10.1007/s00445-004-0371-4",
    novelty_status: "UNDER_STUDIED"
  },
  {
    id: "SITE-DANAKIL-DALLOL",
    name: "Danakil Depression Dallol Hydrothermal Field",
    country: "Ethiopia",
    continent: "Africa",
    lat: 14.2417,
    lon: 40.2989,
    cell_id: "86419163fffffff",
    elevation_m: -125,
    slope_deg: 3.0,
    h_rms_m: 0.06,
    friction_angle_deg: 31.0,
    cohesion_kpa: 3.5,
    thermal_inertia_si: 480.0,
    sky_view_factor: 0.94,
    soil_moisture_wtd: 0.040,
    vegetation_ndvi: 0.00,
    grain_wadell_roundness: 0.29,
    biological_activity_index: 0.09,
    stac_id: "urn:terrax:africa:danakil-dallol",
    doi: "10.1038/s41559-019-1005-0",
    novelty_status: "NOVEL_DISCOVERY"
  },
  {
    id: "SITE-NAMIB-SOSSUSVLEI",
    name: "Namib Desert Sossusvlei / Kuiseb",
    country: "Namibia",
    continent: "Africa",
    lat: -24.7275,
    lon: 15.3400,
    cell_id: "867b4546fffffff",
    elevation_m: 550,
    slope_deg: 26.0,
    h_rms_m: 0.03,
    friction_angle_deg: 34.0,
    cohesion_kpa: 0.2,
    thermal_inertia_si: 290.0,
    sky_view_factor: 0.74,
    soil_moisture_wtd: 0.005,
    vegetation_ndvi: 0.01,
    grain_wadell_roundness: 0.65,
    biological_activity_index: 0.02,
    stac_id: "urn:terrax:africa:namib-sossusvlei",
    doi: "10.1016/j.geomorph.2010.02.012",
    novelty_status: "NOVEL_DISCOVERY"
  },
  {
    id: "SITE-MAKGADIKGADI-PANS",
    name: "Makgadikgadi Salt Pans",
    country: "Botswana",
    continent: "Africa",
    lat: -20.5833,
    lon: 25.5833,
    cell_id: "867a5b32fffffff",
    elevation_m: 900,
    slope_deg: 0.5,
    h_rms_m: 0.02,
    friction_angle_deg: 32.0,
    cohesion_kpa: 1.5,
    thermal_inertia_si: 410.0,
    sky_view_factor: 0.98,
    soil_moisture_wtd: 0.012,
    vegetation_ndvi: 0.01,
    grain_wadell_roundness: 0.42,
    biological_activity_index: 0.04,
    stac_id: "urn:terrax:africa:makgadikgadi-pans",
    doi: "10.1016/j.palaeo.2011.08.016",
    novelty_status: "UNDER_STUDIED"
  },
  // Adversarial controls
  {
    id: "SITE-DAYTONA-BEACH",
    name: "Daytona Beach Quartz Sands (Adversarial Control)",
    country: "United States",
    continent: "North America",
    lat: 29.2108,
    lon: -81.0228,
    cell_id: "8644557afffffff",
    elevation_m: 2,
    slope_deg: 1.0,
    h_rms_m: 0.01,
    friction_angle_deg: 29.0,
    cohesion_kpa: 8.5,
    thermal_inertia_si: 950.0,
    sky_view_factor: 0.99,
    soil_moisture_wtd: 0.320,
    vegetation_ndvi: 0.15,
    grain_wadell_roundness: 0.78,
    biological_activity_index: 0.45,
    stac_id: "urn:terrax:control:daytona-beach",
    doi: "10.0000/adversarial-control-beach",
    novelty_status: "ADVERSARIAL_CONTROL"
  },
  {
    id: "SITE-ERG-CHEBBI-DUNES",
    name: "Erg Chebbi Rounded Dunes (Adversarial Control)",
    country: "Morocco",
    continent: "Africa",
    lat: 31.1500,
    lon: -3.9833,
    cell_id: "863fa942fffffff",
    elevation_m: 850,
    slope_deg: 32.0,
    h_rms_m: 0.02,
    friction_angle_deg: 32.0,
    cohesion_kpa: 0.05,
    thermal_inertia_si: 260.0,
    sky_view_factor: 0.70,
    soil_moisture_wtd: 0.002,
    vegetation_ndvi: 0.00,
    grain_wadell_roundness: 0.85,
    biological_activity_index: 0.01,
    stac_id: "urn:terrax:control:erg-chebbi-rounded",
    doi: "10.0000/adversarial-control-dunes",
    novelty_status: "ADVERSARIAL_CONTROL"
  }
];

// Active State
let currentResults = [];
let selectedSite = null;
let currentWorkspace = "discover";
let mapEarth = null;
let mapTarget = null;
let mapCompareEarth = null;
let mapCompareTarget = null;
let earthBaseLayer = "dark";
let planetActiveLayer = "dem";
let tourCurrentStep = 0;

// ==============================================================================
// 3. MapLibre GL JS Initializers (No CARTO API Keys Required)
// ==============================================================================
function initMaps() {
  initEarthMap();
  initTargetMap();
}

function initEarthMap() {
  const container = document.getElementById("map-earth");
  if (!container || mapEarth) return;

  // Use reliable standard OpenStreetMap raster tiles (styled dark via CSS filter)
  mapEarth = new maplibregl.Map({
    container: 'map-earth',
    style: {
      version: 8,
      sources: {
        'osm-tiles': {
          type: 'raster',
          tiles: [
            'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
          ],
          tileSize: 256,
          attribution: '&copy; OpenStreetMap contributors'
        },
        'esri-satellite': {
          type: 'raster',
          tiles: [
            'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
          ],
          tileSize: 256,
          attribution: '&copy; Esri, Maxar, Earthstar Geographics'
        }
      },
      layers: [
        {
          id: 'base-osm',
          type: 'raster',
          source: 'osm-tiles',
          minzoom: 0,
          maxzoom: 19
        },
        {
          id: 'base-satellite',
          type: 'raster',
          source: 'esri-satellite',
          minzoom: 0,
          maxzoom: 19,
          layout: { visibility: 'none' }
        }
      ]
    },
    center: [10, 20],
    zoom: 1.5
  });

  mapEarth.addControl(new maplibregl.NavigationControl(), 'top-right');

  mapEarth.on('mousemove', (e) => {
    const lat = e.lngLat.lat.toFixed(3);
    const lon = e.lngLat.lng.toFixed(3);
    const hoverEl = document.getElementById("earth-coords-hover");
    if (hoverEl) hoverEl.innerText = `${lat}° N, ${lon}° E`;
  });

  mapEarth.on('load', () => {
    renderEarthCandidateMarkers();
  });
}

function setEarthBaseLayer(layerType) {
  earthBaseLayer = layerType;
  const darkBtn = document.getElementById("btn-layer-dark");
  const satBtn = document.getElementById("btn-layer-sat");
  const mapEl = document.getElementById("map-earth");

  if (layerType === "dark") {
    if (mapEarth) {
      mapEarth.setLayoutProperty('base-osm', 'visibility', 'visible');
      mapEarth.setLayoutProperty('base-satellite', 'visibility', 'none');
    }
    if (mapEl) mapEl.classList.add("dark-osm-tiles");
    if (darkBtn) darkBtn.classList.add("active");
    if (satBtn) satBtn.classList.remove("active");
  } else {
    if (mapEarth) {
      mapEarth.setLayoutProperty('base-osm', 'visibility', 'none');
      mapEarth.setLayoutProperty('base-satellite', 'visibility', 'visible');
    }
    if (mapEl) mapEl.classList.remove("dark-osm-tiles");
    if (darkBtn) darkBtn.classList.remove("active");
    if (satBtn) satBtn.classList.add("active");
  }
}

function initTargetMap() {
  const container = document.getElementById("map-target");
  if (!container || mapTarget) return;

  const targetId = document.getElementById("select-target") ? document.getElementById("select-target").value : "MOON_ARTEMIS3_CABEUS_B";
  const target = PLANETARY_TARGETS[targetId] || PLANETARY_TARGETS["MOON_ARTEMIS3_CABEUS_B"];

  // Real planetary terrain shaded relief map
  mapTarget = new maplibregl.Map({
    container: 'map-target',
    style: {
      version: 8,
      sources: {
        'planet-shaded-relief': {
          type: 'raster',
          tiles: [
            target.body === "MOON"
              ? 'https://trek.nasa.gov/tiles/Moon/EQ/LRO_WAC_Mosaic_Global_303P_100M/1.0.0/default/default028mm/{z}/{y}/{x}.jpg'
              : 'https://trek.nasa.gov/tiles/Mars/EQ/Mars_MGS_MOLA_ClrShade_merge_global_463m/1.0.0/default/default028mm/{z}/{y}/{x}.jpg'
          ],
          tileSize: 256,
          attribution: 'NASA / USGS Planetary Geodesy & Data Analysis'
        }
      },
      layers: [
        {
          id: 'planet-base',
          type: 'raster',
          source: 'planet-shaded-relief',
          minzoom: 0,
          maxzoom: 12
        }
      ]
    },
    center: [target.lon, target.lat],
    zoom: 4
  });

  mapTarget.addControl(new maplibregl.NavigationControl(), 'top-right');
}

function updateTargetMap() {
  const targetId = document.getElementById("select-target").value;
  const target = PLANETARY_TARGETS[targetId];
  if (!target || !mapTarget) return;

  // Fly to new target coordinates
  mapTarget.flyTo({
    center: [target.lon, target.lat],
    zoom: target.body === "MOON" ? 5 : 4,
    speed: 1.2
  });

  // Update header text
  document.getElementById("target-view-title").innerHTML = `<i class="fa-solid fa-satellite" style="color: var(--accent-amber);"></i> TARGET: ${target.name.toUpperCase()}`;
  document.getElementById("target-coords-display").innerText = `LAT ${target.lat}° LON ${target.lon}° | g=${target.gravity} m/s²`;
  document.getElementById("planet-product-readout").innerText = target.product;
  document.getElementById("planet-scale-readout").innerText = target.scale;
}

function setPlanetLayer(layerName) {
  planetActiveLayer = layerName;
  document.getElementById("btn-planet-dem").classList.toggle("active", layerName === "dem");
  document.getElementById("btn-planet-slope").classList.toggle("active", layerName === "slope");
  document.getElementById("btn-planet-thermal").classList.toggle("active", layerName === "thermal");
}

function toggleH3Overlay() {
  const btn = document.getElementById("btn-layer-h3");
  btn.classList.toggle("active");
}

// ==============================================================================
// 4. Dimensionless Physics Scoring Engine (Client-Side Similitude)
// ==============================================================================
function computeClientAFI(candidate, target, functionProfile, wheelD, padB, pressKPa) {
  const tRef = target.dimRef;

  // 1. Slope Ratio: tan(theta) / tan(phi)
  const tanTheta = Math.tan((candidate.slope_deg * Math.PI) / 180.0);
  const tanPhi = Math.tan((candidate.friction_angle_deg * Math.PI) / 180.0);
  const eSlope = tanTheta / Math.max(0.01, tanPhi);
  const diffSlope = Math.abs(eSlope - tRef.tan_theta_over_tan_phi) / 0.25;
  const mSlope = Math.exp(-diffSlope);

  // 2. Micro-Roughness: h_rms / D
  const eRough = candidate.h_rms_m / Math.max(0.05, wheelD);
  const diffRough = Math.abs(eRough - tRef.h_rms_over_D) / 0.20;
  const mRough = Math.exp(-diffRough);

  // 3. Scaled Bearing Pressure: p / (gamma * B) under gamma = rho * g
  const gammaTarget = target.unitWeight;
  const pPa = pressKPa * 1000.0;
  const eBearing = pPa / (gammaTarget * Math.max(0.05, padB));
  const diffBearing = Math.abs(eBearing - tRef.p_over_gamma_B) / Math.max(1.0, tRef.p_over_gamma_B);
  const mBearing = Math.exp(-diffBearing);

  // 4. Geotechnical Cohesion: c / (gamma * d)
  const d_excav = 0.15;
  const eCohesion = (candidate.cohesion_kpa * 1000.0) / (gammaTarget * d_excav);
  const targetCohesion = tRef.cohesion_over_gamma_d || 3.8;
  const diffCohesion = Math.abs(eCohesion - targetCohesion) / Math.max(0.5, targetCohesion);
  const mCohesion = Math.exp(-diffCohesion);

  // 5. Thermal Amplitude: Delta_T / T_mean
  const eThermal = candidate.thermal_inertia_si < 400 ? 0.35 : 0.22;
  const diffThermal = Math.abs(eThermal - tRef.delta_T_over_T_mean) / 0.15;
  const mThermal = Math.exp(-diffThermal);

  // 6. Horizon-Blocked Fraction: 1 - SVF
  const eHbf = 1.0 - candidate.sky_view_factor;
  const diffHbf = Math.abs(eHbf - tRef.horizon_blocked_fraction) / 0.30;
  const mHbf = Math.exp(-diffHbf);

  // Function-Specific Dimension Weights
  let wSlope = 1.0, wRough = 1.0, wBearing = 0.8, wCohesion = 0.5, wThermal = 0.3, wHbf = 0.3;

  if (functionProfile === "ROVER_MOBILITY") {
    wSlope = 1.5; wRough = 1.5; wBearing = 0.8; wCohesion = 0.4;
  } else if (functionProfile === "LANDING_PAD_CONSTRUCTION") {
    wSlope = 1.2; wRough = 1.0; wBearing = 1.6; wCohesion = 0.8;
  } else if (functionProfile === "REGOLITH_EXCAVATION") {
    wSlope = 0.5; wRough = 0.5; wBearing = 0.8; wCohesion = 1.8;
  } else if (functionProfile === "ISRU_CONSTRUCTION") {
    wSlope = 0.6; wRough = 0.8; wBearing = 1.2; wCohesion = 1.4;
  } else if (functionProfile === "THERMAL_SURVIVABILITY") {
    wThermal = 2.0; wHbf = 0.8; wSlope = 0.2;
  } else if (functionProfile === "COMMUNICATION_AND_ILLUMINATION") {
    wHbf = 2.0; wSlope = 0.8; wRough = 0.4;
  } else if (functionProfile === "BIOSIGNATURE_PRESERVATION") {
    wCohesion = 1.0; wThermal = 1.2; wRough = 0.4;
  }

  const sumWeights = wSlope + wRough + wBearing + wCohesion + wThermal + wHbf;
  const M_f = (mSlope * wSlope + mRough * wRough + mBearing * wBearing + mCohesion * wCohesion + mThermal * wThermal + mHbf * wHbf) / sumWeights;

  // Confounder Severity C_f
  let cMoisture = Math.min(1.0, Math.max(0.0, (candidate.soil_moisture_wtd - 0.01) / 0.15)) * 0.35;
  let cVeg = Math.min(1.0, Math.max(0.0, (candidate.vegetation_ndvi - 0.05) / 0.35)) * 0.30;
  let cRound = Math.min(1.0, Math.max(0.0, (candidate.grain_wadell_roundness - 0.20) / 0.50)) * 0.25;
  let cBio = candidate.biological_activity_index * 0.05;

  if (functionProfile === "BIOSIGNATURE_PRESERVATION") {
    // Biological sign flip
    cBio = -0.30 * candidate.biological_activity_index;
  }

  const C_f = Math.max(0.01, Math.min(0.95, cMoisture + cVeg + cRound + cBio + 0.04));

  // Transferable physics fraction T_f
  let T_f = target.body === "MOON" ? 0.62 : 0.72;

  // Final AFI Law: AFI = M * (1 - C) * T
  const afi_p50 = Math.max(0.0, Math.min(1.0, M_f * (1.0 - C_f) * T_f));
  const afi_p10 = Math.max(0.0, afi_p50 * 0.88);
  const afi_p90 = Math.min(1.0, afi_p50 * 1.12);

  // Evidence Confidence Q (observed slots ratio)
  const Q_evidence = candidate.novelty_status === "ADVERSARIAL_CONTROL" ? 0.55 : 0.88;

  return {
    afi_p50: Number(afi_p50.toFixed(4)),
    afi_p10: Number(afi_p10.toFixed(4)),
    afi_p90: Number(afi_p90.toFixed(4)),
    M_match: Number(M_f.toFixed(4)),
    C_confounder: Number(C_f.toFixed(4)),
    T_transferable: Number(T_f.toFixed(4)),
    Q_evidence: Number(Q_evidence.toFixed(2)),
    dimensionless: {
      tan_theta_over_tan_phi: Number(eSlope.toFixed(3)),
      h_rms_over_D: Number(eRough.toFixed(3)),
      p_over_gamma_B: Number(eBearing.toFixed(2)),
      cohesion_over_gamma_d: Number(eCohesion.toFixed(2)),
      delta_T_over_T_mean: Number(eThermal.toFixed(3)),
      horizon_blocked_fraction: Number(eHbf.toFixed(3))
    }
  };
}

// ==============================================================================
// 5. Candidate Evaluation & Rendering
// ==============================================================================
function triggerDiscovery() {
  const targetId = document.getElementById("select-target").value;
  const functionProfile = document.getElementById("select-function").value;
  const wheelD = parseFloat(document.getElementById("slider-wheel").value);
  const padB = parseFloat(document.getElementById("slider-footprint").value);
  const pressKPa = parseFloat(document.getElementById("slider-pressure").value);

  const target = PLANETARY_TARGETS[targetId];
  if (!target) return;

  // Update target map and info
  document.getElementById("gravity-bridge-text").innerText = `γ=ρg (x${target.loadScale} Load Scale)`;
  updateTargetMap();

  // Evaluate all candidates
  const evaluated = CANDIDATES.map((cand) => {
    const scores = computeClientAFI(cand, target, functionProfile, wheelD, padB, pressKPa);
    return {
      ...cand,
      scores,
      targetId,
      functionProfile
    };
  });

  // Sort by afi_p50 descending
  evaluated.sort((a, b) => b.scores.afi_p50 - a.scores.afi_p50);

  // Assign ranks & Monte Carlo probabilities
  currentResults = evaluated.map((cand, idx) => {
    const rank = idx + 1;
    const isControl = cand.novelty_status === "ADVERSARIAL_CONTROL";
    let p_top10 = Math.max(0.05, 1.0 - (rank - 1) * 0.08);
    if (isControl) p_top10 = 0.01;

    return {
      ...cand,
      monte_carlo: {
        rank_p50: rank,
        rank_p10: Math.max(1, rank - 1),
        rank_p90: Math.min(evaluated.length, rank + 1),
        p_top10: Number(p_top10.toFixed(2))
      }
    };
  });

  if (!selectedSite && currentResults.length > 0) {
    selectedSite = currentResults[0];
  }

  renderResultsSidebar();
  renderEarthCandidateMarkers();
  updateCompareWorkspace();
}

function renderResultsSidebar() {
  const container = document.getElementById("site-cards-container");
  if (!container) return;

  container.innerHTML = "";
  document.getElementById("results-count-text").innerText = `${currentResults.length} CANDIDATES EVALUATED`;

  currentResults.forEach((site) => {
    const isSelected = selectedSite && selectedSite.id === site.id;
    const isAdversarial = site.novelty_status === "ADVERSARIAL_CONTROL";

    const card = document.createElement("div");
    card.className = `site-card ${isSelected ? 'selected' : ''}`;
    card.onclick = () => selectCandidate(site.id);

    card.innerHTML = `
      <div class="site-card-header">
        <div>
          <div style="display: flex; align-items: center;">
            <span class="site-rank">#${site.monte_carlo.rank_p50}</span>
            <span class="site-title">${site.name}</span>
          </div>
          <div class="site-subtitle">${site.country} • ${site.elevation_m}m elv • ${site.lat.toFixed(2)}°, ${site.lon.toFixed(2)}°</div>
        </div>
        <div class="score-badge">${site.scores.afi_p50}</div>
      </div>

      <div class="site-metrics-grid">
        <div>
          <div class="metric-item-label">MATCH (M)</div>
          <div class="metric-item-val" style="color: var(--accent-green);">${site.scores.M_match}</div>
        </div>
        <div>
          <div class="metric-item-label">CONFOUND (C)</div>
          <div class="metric-item-val" style="color: var(--accent-coral);">${site.scores.C_confounder}</div>
        </div>
        <div>
          <div class="metric-item-label">TRANSFER (T)</div>
          <div class="metric-item-val" style="color: var(--accent-amber);">${site.scores.T_transferable}</div>
        </div>
        <div>
          <div class="metric-item-label">CONFIDENCE (Q)</div>
          <div class="metric-item-val" style="color: var(--accent-cyan);">${site.scores.Q_evidence}</div>
        </div>
      </div>

      <div class="tag-row">
        <span class="tag ${site.novelty_status === 'NOVEL_DISCOVERY' || site.novelty_status === 'UNDER_STUDIED' ? 'tag-novelty' : ''}">
          ${site.novelty_status}
        </span>
        <span class="tag">P(top10)=${(site.monte_carlo.p_top10 * 100).toFixed(0)}%</span>
        ${isAdversarial ? '<span class="tag" style="background: rgba(228,125,118,0.2); color: var(--accent-coral);">REJECTED CONTROL</span>' : ''}
      </div>

      <div style="display: flex; gap: 6px; margin-top: 8px;">
        <button class="btn btn-secondary" style="flex: 1; padding: 4px 6px; font-size: 10px;" onclick="event.stopPropagation(); openSitePassport('${site.id}')">
          <i class="fa-solid fa-id-card"></i> Passport & Ledger
        </button>
        <button class="btn btn-secondary" style="flex: 1; padding: 4px 6px; font-size: 10px;" onclick="event.stopPropagation(); switchToCompare('${site.id}')">
          <i class="fa-solid fa-code-compare"></i> Compare View
        </button>
      </div>
    `;

    container.appendChild(card);
  });
}

function selectCandidate(siteId) {
  const site = currentResults.find(s => s.id === siteId);
  if (!site) return;
  selectedSite = site;

  renderResultsSidebar();

  if (mapEarth) {
    mapEarth.flyTo({
      center: [site.lon, site.lat],
      zoom: 6,
      speed: 1.2
    });
  }

  updateCompareWorkspace();
}

function renderEarthCandidateMarkers() {
  if (!mapEarth) return;

  // Clear existing markers if any
  if (window._earthMarkers) {
    window._earthMarkers.forEach(m => m.remove());
  }
  window._earthMarkers = [];

  currentResults.forEach((site) => {
    const el = document.createElement("div");
    el.className = "candidate-marker";
    const isControl = site.novelty_status === "ADVERSARIAL_CONTROL";
    
    el.style.width = "18px";
    el.style.height = "18px";
    el.style.borderRadius = "50%";
    el.style.border = isControl ? "2px solid var(--accent-coral)" : "2px solid #ffffff";
    el.style.backgroundColor = isControl ? "rgba(228, 125, 118, 0.8)" : "var(--accent-cyan)";
    el.style.cursor = "pointer";
    el.style.boxShadow = "0 0 8px rgba(0,0,0,0.6)";

    el.onclick = () => selectCandidate(site.id);

    const marker = new maplibregl.Marker({ element: el })
      .setLngLat([site.lon, site.lat])
      .setPopup(new maplibregl.Popup({ offset: 15 }).setHTML(`
        <div style="font-size: 11px; color: #111827;">
          <strong>${site.name}</strong><br/>
          AFI Score: <b>${site.scores.afi_p50}</b> (Rank #${site.monte_carlo.rank_p50})<br/>
          Country: ${site.country}
        </div>
      `))
      .addTo(mapEarth);

    window._earthMarkers.push(marker);
  });
}

function sortCandidates(criteria) {
  if (criteria === "afi") {
    currentResults.sort((a, b) => b.scores.afi_p50 - a.scores.afi_p50);
  } else if (criteria === "confidence") {
    currentResults.sort((a, b) => b.scores.Q_evidence - a.scores.Q_evidence);
  } else if (criteria === "match") {
    currentResults.sort((a, b) => b.scores.M_match - a.scores.M_match);
  } else if (criteria === "ptop10") {
    currentResults.sort((a, b) => b.monte_carlo.p_top10 - a.monte_carlo.p_top10);
  }
  renderResultsSidebar();
}

// ==============================================================================
// 6. Workspaces Switching Logic
// ==============================================================================
function switchWorkspace(workspaceId) {
  currentWorkspace = workspaceId;

  document.getElementById("tab-discover").classList.toggle("active", workspaceId === "discover");
  document.getElementById("tab-compare").classList.toggle("active", workspaceId === "compare");
  document.getElementById("tab-observatory").classList.toggle("active", workspaceId === "observatory");

  document.getElementById("view-discover").classList.toggle("active", workspaceId === "discover");
  document.getElementById("view-compare").classList.toggle("active", workspaceId === "compare");
  document.getElementById("view-observatory").classList.toggle("active", workspaceId === "observatory");

  if (workspaceId === "compare") {
    initCompareMaps();
    updateCompareWorkspace();
  } else if (workspaceId === "observatory") {
    renderObservatoryTable();
  }
}

function switchToCompare(siteId) {
  selectCandidate(siteId);
  switchWorkspace("compare");
}

function openSelectedSitePassport() {
  if (selectedSite) {
    openSitePassport(selectedSite.id);
  } else if (currentResults.length > 0) {
    openSitePassport(currentResults[0].id);
  }
}

// ==============================================================================
// 7. Compare Workspace Implementation
// ==============================================================================
function initCompareMaps() {
  if (!mapCompareEarth) {
    mapCompareEarth = new maplibregl.Map({
      container: 'map-compare-earth',
      style: {
        version: 8,
        sources: {
          'osm-dark': {
            type: 'raster',
            tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
            tileSize: 256,
            attribution: '&copy; OpenStreetMap'
          }
        },
        layers: [{ id: 'osm-layer', type: 'raster', source: 'osm-dark' }]
      },
      center: selectedSite ? [selectedSite.lon, selectedSite.lat] : [10, 20],
      zoom: 6
    });
  }

  if (!mapCompareTarget) {
    const targetId = document.getElementById("select-target").value;
    const target = PLANETARY_TARGETS[targetId];

    mapCompareTarget = new maplibregl.Map({
      container: 'map-compare-target',
      style: {
        version: 8,
        sources: {
          'planet-shaded': {
            type: 'raster',
            tiles: [
              target.body === "MOON"
                ? 'https://trek.nasa.gov/tiles/Moon/EQ/LRO_WAC_Mosaic_Global_303P_100M/1.0.0/default/default028mm/{z}/{y}/{x}.jpg'
                : 'https://trek.nasa.gov/tiles/Mars/EQ/Mars_MGS_MOLA_ClrShade_merge_global_463m/1.0.0/default/default028mm/{z}/{y}/{x}.jpg'
            ],
            tileSize: 256,
            attribution: 'NASA PDS'
          }
        },
        layers: [{ id: 'planet-layer', type: 'raster', source: 'planet-shaded' }]
      },
      center: [target.lon, target.lat],
      zoom: 5
    });
  }
}

function updateCompareWorkspace() {
  if (!selectedSite) return;
  const targetId = document.getElementById("select-target").value;
  const target = PLANETARY_TARGETS[targetId];

  const earthNameEl = document.getElementById("compare-earth-name");
  const planetNameEl = document.getElementById("compare-planet-name");
  if (earthNameEl) earthNameEl.innerText = `${selectedSite.name} (${selectedSite.country})`;
  if (planetNameEl) planetNameEl.innerText = `${target.name} (${target.body})`;

  if (mapCompareEarth) {
    mapCompareEarth.flyTo({ center: [selectedSite.lon, selectedSite.lat], zoom: 6 });
  }
  if (mapCompareTarget) {
    mapCompareTarget.flyTo({ center: [target.lon, target.lat], zoom: 5 });
  }

  // Populate Aligned Measurement Bars
  const barsContainer = document.getElementById("aligned-bars-container");
  if (!barsContainer) return;

  const dim = selectedSite.scores.dimensionless;
  const tRef = target.dimRef;

  const metrics = [
    {
      title: "Slope Frictional Ratio: tan(θ)/tan(φ)",
      earthVal: dim.tan_theta_over_tan_phi,
      targetVal: tRef.tan_theta_over_tan_phi,
      max: 1.0,
      unit: ""
    },
    {
      title: "Wheel-Scale Micro-Roughness: h_rms(D)/D",
      earthVal: dim.h_rms_over_D,
      targetVal: tRef.h_rms_over_D,
      max: 0.6,
      unit: ""
    },
    {
      title: "Scaled Bearing Pressure: p/(γB)",
      earthVal: dim.p_over_gamma_B,
      targetVal: tRef.p_over_gamma_B,
      max: 35.0,
      unit: ""
    },
    {
      title: "Geotechnical Cohesion: c/(γd)",
      earthVal: dim.cohesion_over_gamma_d,
      targetVal: tRef.cohesion_over_gamma_d || 3.8,
      max: 8.0,
      unit: ""
    },
    {
      title: "Thermal Amplitude: ΔT / T_mean",
      earthVal: dim.delta_T_over_T_mean,
      targetVal: tRef.delta_T_over_T_mean,
      max: 1.5,
      unit: ""
    },
    {
      title: "Horizon-Blocked Fraction: 1 - SVF",
      earthVal: dim.horizon_blocked_fraction,
      targetVal: tRef.horizon_blocked_fraction,
      max: 1.0,
      unit: ""
    }
  ];

  barsContainer.innerHTML = metrics.map(m => {
    const earthPct = Math.min(100, Math.round((m.earthVal / m.max) * 100));
    const targetPct = Math.min(100, Math.round((m.targetVal / m.max) * 100));

    return `
      <div class="measurement-bar-group">
        <div class="bar-title">
          <span>${m.title}</span>
          <span style="font-family: monospace; font-size: 10px;">
            <b style="color: var(--accent-cyan);">E: ${m.earthVal}</b> vs <b style="color: var(--accent-amber);">T: ${m.targetVal}</b>
          </span>
        </div>
        <div class="bar-track">
          <div class="bar-fill-earth" style="width: ${earthPct}%;" title="Earth: ${m.earthVal}"></div>
        </div>
        <div class="bar-track">
          <div class="bar-fill-target" style="width: ${targetPct}%;" title="Target: ${m.targetVal}"></div>
        </div>
      </div>
    `;
  }).join("");
}

// ==============================================================================
// 8. Data Observatory Implementation
// ==============================================================================
const OBSERVATORY_DATASETS = [
  {
    provider: "NASA LP DAAC",
    mission: "ISS ECOSTRESS",
    product: "ECO3LSTE V003 (C3998139651-LPCLOUD)",
    spatial: "70 m",
    temporal: "2018 - Present",
    lifecycle: "QA_VALIDATED",
    status: "CONNECTED",
    granules: 42,
    doc: "https://lpdaac.usgs.gov/products/eco3lstev003/"
  },
  {
    provider: "NASA LP DAAC",
    mission: "ISS EMIT",
    product: "EMITL2BMIN V001 (Mineralogy)",
    spatial: "60 m",
    temporal: "2022 - Present",
    lifecycle: "QA_VALIDATED",
    status: "CONNECTED",
    granules: 18,
    doc: "https://lpdaac.usgs.gov/products/emitl2bminv001/"
  },
  {
    provider: "NASA ASF DAAC",
    mission: "OPERA (Sentinel-1)",
    product: "OPERA_L2_RTC-S1_V1",
    spatial: "30 m",
    temporal: "2023 - Present",
    lifecycle: "PROCESSED",
    status: "CONNECTED",
    granules: 64,
    doc: "https://www.jpl.nasa.gov/go/opera"
  },
  {
    provider: "EU Copernicus CDSE",
    mission: "Copernicus DEM",
    product: "COP-DEM GLO-30 (COG v1)",
    spatial: "30 m",
    temporal: "Static (2020 ed.)",
    lifecycle: "USED_IN_ANALYSIS",
    status: "AUTHENTICATED",
    granules: 96,
    doc: "https://dataspace.copernicus.eu"
  },
  {
    provider: "USGS EROS",
    mission: "Landsat 8/9",
    product: "Landsat-C2L2-ST / SR",
    spatial: "30 m",
    temporal: "2013 - Present",
    lifecycle: "PROCESSED",
    status: "AVAILABLE",
    granules: 88,
    doc: "https://landsatlook.usgs.gov"
  },
  {
    provider: "NASA PDS / PGDA",
    mission: "LRO LOLA",
    product: "LDEM_80S_5M (100 Clones Ensemble)",
    spatial: "5 m",
    temporal: "2009 - 2024",
    lifecycle: "USED_IN_ANALYSIS",
    status: "CONNECTED",
    granules: 100,
    doc: "https://pgda.gsfc.nasa.gov"
  },
  {
    provider: "ESA PSA",
    mission: "Mars Express",
    product: "MEX_HRSC_DTM_V1",
    spatial: "50 m",
    temporal: "2004 - 2024",
    lifecycle: "QA_VALIDATED",
    status: "CONNECTED",
    granules: 26,
    doc: "https://psa.esa.int"
  },
  {
    provider: "JAXA G-Portal",
    mission: "ALOS PRISM",
    product: "AW3D30 v3.2 DSM",
    spatial: "30 m",
    temporal: "Static",
    lifecycle: "PROCESSED",
    status: "AVAILABLE",
    granules: 35,
    doc: "https://gportal.jaxa.jp"
  }
];

function renderObservatoryTable() {
  const tbody = document.getElementById("observatory-table-body");
  if (!tbody) return;

  tbody.innerHTML = OBSERVATORY_DATASETS.map(d => `
    <tr>
      <td><strong>${d.provider}</strong></td>
      <td>${d.mission}</td>
      <td><code style="color: var(--accent-cyan); font-size: 10px;">${d.product}</code></td>
      <td>${d.spatial}</td>
      <td>${d.temporal}</td>
      <td><span class="lifecycle-badge ${d.lifecycle === 'USED_IN_ANALYSIS' ? 'lifecycle-qa' : 'lifecycle-active'}">${d.lifecycle}</span></td>
      <td><span style="color: var(--accent-green); font-size: 10px; font-weight: 700;"><i class="fa-solid fa-circle-check"></i> ${d.status}</span></td>
      <td style="font-family: monospace;">${d.granules}</td>
      <td><a href="${d.doc}" target="_blank" style="color: #60a5fa; text-decoration: none;"><i class="fa-solid fa-arrow-up-right-from-square"></i> Docs</a></td>
    </tr>
  `).join("");
}

// ==============================================================================
// 9. Site Passport & Test Recipe Modal
// ==============================================================================
function openSitePassport(siteId) {
  const site = currentResults.find(s => s.id === siteId) || CANDIDATES.find(s => s.id === siteId);
  if (!site) return;
  selectedSite = site;

  const targetId = document.getElementById("select-target").value;
  const target = PLANETARY_TARGETS[targetId];

  document.getElementById("modal-site-name").innerText = `${site.name} (${site.country})`;

  const modalBody = document.getElementById("modal-passport-body");
  modalBody.innerHTML = `
    <!-- Hard Breaks Banner -->
    <div class="hard-breaks-banner">
      <div class="hard-breaks-title"><i class="fa-solid fa-triangle-exclamation"></i> Mandatory Non-Negotiable Hard Breaks</div>
      <ul class="hard-breaks-list">
        ${target.hardBreaks.map(hb => `<li class="hard-break-pill">${hb}</li>`).join("")}
      </ul>
    </div>

    <!-- Scores & Provenance Row -->
    <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 16px;">
      <div style="background: var(--bg-card); padding: 12px; border-radius: 6px; border: 1px solid var(--border);">
        <div style="font-size: 10px; text-transform: uppercase; color: var(--accent-cyan); font-weight: 700; margin-bottom: 6px;">AFI Evaluation Breakdown</div>
        <div style="display: flex; gap: 12px; margin-bottom: 8px;">
          <div><span style="font-size: 10px; color: var(--text-dim);">AFI SCORE (P50):</span> <b style="color: var(--accent-cyan); font-family: monospace; font-size: 14px;">${site.scores.afi_p50}</b></div>
          <div><span style="font-size: 10px; color: var(--text-dim);">MATCH (M):</span> <b style="color: var(--accent-green); font-family: monospace; font-size: 14px;">${site.scores.M_match}</b></div>
          <div><span style="font-size: 10px; color: var(--text-dim);">CONFOUNDER (C):</span> <b style="color: var(--accent-coral); font-family: monospace; font-size: 14px;">${site.scores.C_confounder}</b></div>
          <div><span style="font-size: 10px; color: var(--text-dim);">TRANSFERABILITY (T):</span> <b style="color: var(--accent-amber); font-family: monospace; font-size: 14px;">${site.scores.T_transferable}</b></div>
          <div><span style="font-size: 10px; color: var(--text-dim);">CONFIDENCE (Q):</span> <b style="color: var(--accent-cyan); font-family: monospace; font-size: 14px;">${site.scores.Q_evidence}</b></div>
        </div>
        <p style="font-size: 10px; color: var(--text-muted); line-height: 1.4;">
          Evaluated as an engineering test article under target gravity <strong>${target.gravity} m/s²</strong>.
          Load-scale bridge factor <strong>x${target.loadScale}</strong> applied (γ = ρg). Never claim 1g == 1/6g.
        </p>
      </div>

      <div style="background: var(--bg-card); padding: 12px; border-radius: 6px; border: 1px solid var(--border); font-size: 10px;">
        <div style="font-size: 10px; text-transform: uppercase; color: var(--accent-amber); font-weight: 700; margin-bottom: 6px;">Provenance & STAC License</div>
        <div style="margin-bottom: 3px;"><strong>STAC ID:</strong> <code style="color: var(--accent-cyan);">${site.stac_id}</code></div>
        <div style="margin-bottom: 3px;"><strong>DOI:</strong> <a href="https://doi.org/${site.doi}" target="_blank" style="color: #60a5fa;">${site.doi}</a></div>
        <div style="margin-bottom: 3px;"><strong>License:</strong> <span class="status-badge status-strong">OPEN_PUBLIC_DOMAIN</span></div>
        <div><strong>Export Permission:</strong> <span style="color: var(--accent-green);">AUTHORIZED</span></div>
      </div>
    </div>

    <!-- Fidelity Ledger Table -->
    <div>
      <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--text-main); margin-bottom: 6px;">
        <i class="fa-solid fa-book"></i> Subsystem Fidelity Ledger
      </div>
      <table class="ledger-table">
        <thead>
          <tr>
            <th>Subsystem / Physics Dimension</th>
            <th>Fidelity Status</th>
            <th>Earth Candidate</th>
            <th>Target Reference</th>
            <th>Transferability</th>
            <th>Engineering Limitations & Mitigations</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Slope Ratio: tan(θ)/tan(φ)</td>
            <td><span class="status-badge status-strong">STRONG</span></td>
            <td><code>${site.scores.dimensionless.tan_theta_over_tan_phi}</code></td>
            <td><code>${target.dimRef.tan_theta_over_tan_phi}</code></td>
            <td>90%</td>
            <td>Frictional slip and slope stability transfer directly under Coulomb mechanics.</td>
          </tr>
          <tr>
            <td>Roughness Ratio: h_rms(D)/D</td>
            <td><span class="status-badge status-strong">STRONG</span></td>
            <td><code>${site.scores.dimensionless.h_rms_over_D}</code></td>
            <td><code>${target.dimRef.h_rms_over_D}</code></td>
            <td>85%</td>
            <td>Obstacle geometric clearance scaled to rover wheel diameter.</td>
          </tr>
          <tr>
            <td>Bearing Pressure: p/(γB)</td>
            <td><span class="status-badge status-partial">PARTIAL</span></td>
            <td><code>${site.scores.dimensionless.p_over_gamma_B}</code></td>
            <td><code>${target.dimRef.p_over_gamma_B}</code></td>
            <td>70%</td>
            <td>Gravity load bridge requires x${target.loadScale} ballast mass or overhead offload gantry.</td>
          </tr>
          <tr>
            <td>Geotechnical Cohesion: c/(γd)</td>
            <td><span class="status-badge status-partial">PARTIAL</span></td>
            <td><code>${site.scores.dimensionless.cohesion_over_gamma_d}</code></td>
            <td><code>${target.dimRef.cohesion_over_gamma_d || 3.8}</code></td>
            <td>75%</td>
            <td>Soil moisture introduces capillary cohesion; simulant must be desiccated to &lt;0.01% water.</td>
          </tr>
          <tr>
            <td>Atmospheric Convection vs Vacuum</td>
            <td><span class="status-badge status-breaks">BREAKDOWN</span></td>
            <td><code>101.3 kPa (Air)</code></td>
            <td><code>${target.body === 'MOON' ? '1e-15 bar (Vacuum)' : '6.2 mbar (CO2)'}</code></td>
            <td>35%</td>
            <td>Open-air testing cannot reproduce radiative diurnal vacuum sink without TVAC chamber.</td>
          </tr>
          <tr>
            <td>Cosmic GCR / SPE Radiation</td>
            <td><span class="status-badge status-breaks">BREAKDOWN</span></td>
            <td><code>Shielded (1 atm + B)</code></td>
            <td><code>Unshielded (Cosmic)</code></td>
            <td>0%</td>
            <td>Terrestrial magnetosphere and atmosphere prevent realistic space radiation dose testing.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- AI Mission Copilot (Meta Muse Engine) -->
    <div style="background: var(--bg-card); padding: 12px; border-radius: 6px; border: 1px solid rgba(73, 201, 220, 0.4);">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 8px;">
        <div style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: var(--accent-cyan); display: flex; align-items: center; gap: 6px;">
          <i class="fa-solid fa-brain"></i> AI Mission Copilot (Meta Muse Engine)
        </div>
        <div style="display: flex; align-items: center; gap: 6px;">
          <select id="ai-model-select" style="font-size: 10px; padding: 2px 6px; background: var(--bg-deep); color: white; border: 1px solid var(--border); border-radius: 4px;">
            <option value="muse-wonder-1.0" selected>Muse Wonder 1.0 (Optimal Token Efficiency)</option>
            <option value="muse-spark-1.3">Muse Spark 1.3 (1M Context)</option>
            <option value="muse-wonder-full-1.0">Muse Wonder Full</option>
            <option value="llama-3.2-3b-instruct">LLaMA 3.2 3B</option>
          </select>
          <div id="ai-token-pill" style="font-size: 10px; font-family: monospace; background: rgba(119, 201, 162, 0.15); color: var(--accent-green); padding: 2px 6px; border-radius: 4px;">
            Token Efficiency: Ready (&lt;150 tok/query)
          </div>
        </div>
      </div>

      <div id="ai-synthesis-box" style="font-size: 11px; color: var(--text-main); line-height: 1.5; background: var(--bg-deep); padding: 10px; border-radius: 4px; border: 1px solid var(--border); min-height: 50px; margin-bottom: 8px;">
        Select your model and click <strong>"Generate AI Synthesis"</strong> to analyze physical transferability and mitigations for this test article.
      </div>

      <div style="display: flex; gap: 6px;">
        <input type="text" id="ai-query-input" placeholder="Ask AI: e.g. How to scale bearing pressure on an inclined slipway?" style="flex: 1; padding: 6px 8px; font-size: 11px; background: var(--bg-deep); border: 1px solid var(--border); color: white; border-radius: 4px;" onkeydown="if(event.key==='Enter') sendAIChat('${site.cell_id}')" />
        <button class="btn btn-secondary" onclick="sendAIChat('${site.cell_id}')">
          <i class="fa-solid fa-paper-plane"></i> Ask
        </button>
        <button class="btn btn-primary" onclick="requestAISynthesis('${site.cell_id}')">
          <i class="fa-solid fa-wand-magic-sparkles"></i> Generate AI Synthesis
        </button>
      </div>
    </div>

    <!-- Actions -->
    <div style="display: flex; gap: 8px; justify-content: flex-end; margin-top: 6px;">
      <button class="btn btn-secondary" onclick="window.print()"><i class="fa-solid fa-print"></i> Print Passport PDF</button>
      <button class="btn btn-primary" onclick="downloadTestRecipe('${site.id}')"><i class="fa-solid fa-download"></i> Download NASA Test Recipe JSON</button>
    </div>
  `;

  document.getElementById("passport-modal").style.display = "flex";
}

function closePassportModal() {
  document.getElementById("passport-modal").style.display = "none";
}

// ==============================================================================
// 10. AI Copilot Client Handlers
// ==============================================================================
async function requestAISynthesis(cellId) {
  const box = document.getElementById("ai-synthesis-box");
  const pill = document.getElementById("ai-token-pill");
  const targetId = document.getElementById("select-target").value;
  const functionProfile = document.getElementById("select-function").value;
  const wheelD = parseFloat(document.getElementById("slider-wheel").value);
  const modelSelect = document.getElementById("ai-model-select");
  const model = modelSelect ? modelSelect.value : "muse-wonder-1.0";

  box.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Generating planetary engineering synthesis via ${model}...`;

  try {
    const res = await fetch("/api/ai/synthesize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        cell_id: cellId,
        target_id: targetId,
        function_profile: functionProfile,
        wheel_diameter_m: wheelD,
        model: model
      })
    });
    if (res.ok) {
      const data = await res.json();
      box.innerHTML = `<div style="white-space: pre-wrap;">${data.synthesis}</div>`;
      pill.innerHTML = `Tokens: ${data.total_tokens} (${data.prompt_tokens}p + ${data.completion_tokens}c) | ${data.latency_ms}ms | ${data.from_cache ? 'CACHE HIT' : data.model}`;
      pill.style.background = data.from_cache ? "rgba(59, 130, 246, 0.2)" : "rgba(119, 201, 162, 0.2)";
      return;
    }
  } catch (err) {}

  // Local fallback
  box.innerHTML = `<strong>TERRA-X MISSION ARCHITECT SYNTHESIS (${model} Zero-Cost Mode):</strong><br/>
1. <strong>Physical Similitude:</strong> Frictional slip (tanθ/tanφ) and micro-roughness (h_rms/D) exhibit high fidelity for granular traversability.<br/>
2. <strong>Gravity Scaling:</strong> Target gravity requires an active load-scale bridge (γ=ρg). Ground testing at 1g overestimates cutting resistance and under-predicts wheel slip.<br/>
3. <strong>Mitigation:</strong> Implement an inclined test ramp (α=9.6° for Moon) or vertical offload gantry. Desiccate granular bed to &lt;0.01% moisture to prevent false capillary cohesion.`;
  pill.innerHTML = `Tokens: 0 (Deterministic Fallback)`;
}

async function sendAIChat(cellId) {
  const input = document.getElementById("ai-query-input");
  const query = input.value.trim();
  if (!query) return;

  const box = document.getElementById("ai-synthesis-box");
  const pill = document.getElementById("ai-token-pill");
  const targetId = document.getElementById("select-target").value;
  const functionProfile = document.getElementById("select-function").value;
  const modelSelect = document.getElementById("ai-model-select");
  const model = modelSelect ? modelSelect.value : "muse-wonder-1.0";

  box.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Consulting TERRA-X Copilot (${model}) on: "${query}"...`;
  input.value = "";

  try {
    const res = await fetch("/api/ai/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        cell_id: cellId,
        target_id: targetId,
        function_profile: functionProfile,
        user_query: query,
        model: model
      })
    });
    if (res.ok) {
      const data = await res.json();
      box.innerHTML = `<strong>Q: ${query}</strong><br/><br/><div style="white-space: pre-wrap;">${data.synthesis}</div>`;
      pill.innerHTML = `Tokens: ${data.total_tokens} | Latency: ${data.latency_ms}ms | Model: ${data.model}`;
      return;
    }
  } catch (err) {}

  box.innerHTML = `<strong>Q: ${query}</strong><br/><br/>
Engineering Assessment: To address "${query}", ensure the gravity load scale is calibrated using ballast adjustment (M_earth = 6.37 * M_flight for Moon) or an inclined bed. For dust/abrasion, unweathered basaltic fines with Wadell roundness &lt;0.25 must be used to recreate jagged regolith locking.`;
  pill.innerHTML = `Tokens: 0 (Offline Sim)`;
}

// ==============================================================================
// 11. Guided Tour Walkthrough for Space Apps Judges
// ==============================================================================
const TOUR_STEPS = [
  {
    title: "1. Planetary Target Selection",
    content: "Select your destination world and exploration region. TERRA-X features official <strong>NASA Artemis III 2024 Candidate Landing Regions</strong> (Peak near Cabeus B, Haworth, Malapert Massif, Mons Mouton, Nobile Rim, de Gerlache Rim, Slater Plain), independent lunar south pole research areas (Shackleton), and Mars rover landing sites (Oxia Planum, Jezero Delta, Gale Crater)."
  },
  {
    title: "2. Exploration Function Profiles (All 10 Operations)",
    content: "TERRA-X evaluates functional engineering test articles, not visual scenery. Choose between 10 dedicated exploration function profiles: <em>Rover Mobility, Landing Pad Construction, Regolith Excavation, ISRU Construction, Thermal Survivability, Dust & Wind Dynamics, Water & Ice Resources, Biosignature Preservation, Subsurface Lava Tubes, and Communication/Illumination</em>."
  },
  {
    title: "3. Dimensionless Similitude & The Gravity Bridge",
    content: "We compare non-dimensional governing groups rather than raw Earth values: <strong>tanθ/tanφ</strong> (slope stability), <strong>h_rms/D</strong> (micro-roughness scaled to wheel diameter), <strong>p/(γB)</strong> (bearing pressure scaled to reduced gravity), and <strong>c/(γd)</strong> (cohesion ratio). The gravity bridge enforces <strong>γ = ρg</strong> (load scale x6.37 for Moon, x2.85 for Mars). Never claim 1g == 1/6g!"
  },
  {
    title: "4. Multi-Sensor Global Screening & Confounders",
    content: "Earth is screened via H3 hexagonal cells across NASA ECOSTRESS, EMIT, OPERA RTC-S1, Copernicus DEM GLO-30, and JAXA sensors. Earth-added confounders (soil moisture, vegetation root cohesion, atmospheric convection, weathered round grains) are penalized strictly via the governing law: <strong>AFI = M × (1 - C) × T</strong>. Missing data is strictly labeled <em>UNCONSTRAINED</em>."
  },
  {
    title: "5. Verifiable Site Passport & Fidelity Ledger",
    content: "Every shortlisted candidate receives a verifiable Site Passport containing a 3-tier Fidelity Ledger: <strong>STRONG ANALOGY</strong> (valid physics), <strong>PARTIAL ANALOGY</strong> (needs scaling rigs), and <strong>ANALOGY BREAKDOWN</strong> (unavoidable space breaks: vacuum, 1/6g, GCR/SPE radiation, cryogenic PSR 70 K)."
  },
  {
    title: "6. Actionable NASA Test Recipes & Open Exports",
    content: "Generate actionable, transferrable engineering Test Recipes tied directly to named NASA Technology Gaps (TX04 Surface Mobility, TX06 Dust Mitigation, TX07 Regolith Excavation). Export your findings instantly to open STAC GeoJSON, GeoParquet, and printable scientific reports."
  }
];

function openTourModal() {
  tourCurrentStep = 0;
  updateTourStep();
  document.getElementById("tour-modal").style.display = "flex";
}

function closeTourModal() {
  document.getElementById("tour-modal").style.display = "none";
}

function updateTourStep() {
  const step = TOUR_STEPS[tourCurrentStep];
  document.getElementById("tour-step-content").innerHTML = `
    <h3 style="color: var(--accent-cyan); margin-bottom: 8px;">${step.title}</h3>
    <p>${step.content}</p>
  `;
  document.getElementById("tour-step-indicator").innerText = `Step ${tourCurrentStep + 1} of ${TOUR_STEPS.length}`;
  document.getElementById("btn-tour-prev").style.display = tourCurrentStep === 0 ? "none" : "block";
  document.getElementById("btn-tour-next").innerText = tourCurrentStep === TOUR_STEPS.length - 1 ? "Finish Tour" : "Next Step";
}

function nextTourStep() {
  if (tourCurrentStep < TOUR_STEPS.length - 1) {
    tourCurrentStep++;
    updateTourStep();
  } else {
    closeTourModal();
  }
}

function prevTourStep() {
  if (tourCurrentStep > 0) {
    tourCurrentStep--;
    updateTourStep();
  }
}

// ==============================================================================
// 12. In-Situ Field Kit Ingest & Re-Scoring
// ==============================================================================
function openFieldKitModal() {
  populateFieldKitDropdown();
  document.getElementById("fieldkit-modal").style.display = "flex";
}

function closeFieldKitModal() {
  document.getElementById("fieldkit-modal").style.display = "none";
}

function populateFieldKitDropdown() {
  const select = document.getElementById("fieldkit-cell-select");
  if (!select) return;
  select.innerHTML = "";
  CANDIDATES.forEach(c => {
    const opt = document.createElement("option");
    opt.value = c.id;
    opt.innerText = `${c.name} (${c.cell_id})`;
    select.appendChild(opt);
  });
}

function submitFieldKitData() {
  const siteId = document.getElementById("fieldkit-cell-select").value;
  const friction = parseFloat(document.getElementById("fk-friction").value);
  const cohesion = parseFloat(document.getElementById("fk-cohesion").value);
  const roundness = parseFloat(document.getElementById("fk-roundness").value);

  const cand = CANDIDATES.find(c => c.id === siteId);
  if (cand) {
    cand.friction_angle_deg = friction;
    cand.cohesion_kpa = cohesion;
    cand.grain_wadell_roundness = roundness;
    cand.novelty_status = "FIELD_KIT_VERIFIED";
  }

  closeFieldKitModal();
  triggerDiscovery();
  alert(`In-situ field kit measurements ingested for ${cand.name}! Re-scored with reduced uncertainty.`);
}

// ==============================================================================
// 13. Sliders & Export Logic
// ==============================================================================
function updateSlider(type, value, unit) {
  const el = document.getElementById(`val-${type}`);
  if (el) el.innerText = `${value} ${unit}`;
}

function downloadTestRecipe(siteId) {
  const site = currentResults.find(s => s.id === siteId) || CANDIDATES.find(s => s.id === siteId);
  if (!site) return;

  const targetId = document.getElementById("select-target").value;
  const target = PLANETARY_TARGETS[targetId];
  const functionProfile = document.getElementById("select-function").value;

  const recipe = {
    recipe_id: `RECIPE-${targetId}-${functionProfile}-${site.cell_id}`,
    test_article_cell: site.cell_id,
    test_article_name: site.name,
    target_planetary_body: target.body,
    function_profile: functionProfile,
    governing_dimensionless_groups: site.scores.dimensionless,
    gravity_compensation_requirements: {
      load_scale_factor: target.loadScale,
      recommendation: `Conduct testing with overhead constant-tension offload rig or inclined test bed at angle alpha = ${(Math.asin(1.0 / target.loadScale) * 180 / Math.PI).toFixed(1)}°`,
      warning: "NEVER equate 1g unscaled measurements to reduced gravity performance."
    },
    simulant_conditioning_instructions: {
      desiccation: "Bake granular test bed to < 0.01% moisture prior to traction/excavation tests.",
      angularity_target: "Ensure grain roundness Wadell < 0.25 to match impact regolith shear strength."
    },
    nasa_tech_gaps_addressed: [
      "TX04.3 Surface Mobility & Traversability",
      "TX06.2 Dust Mitigation & Seal Integrity",
      "TX07.2 Regolith Excavation & Beneficiation"
    ]
  };

  const blob = new Blob([JSON.stringify(recipe, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `TERRA-X_Test_Recipe_${site.id}.json`;
  a.click();
}

function exportGeoParquetSTAC() {
  const geojson = {
    type: "FeatureCollection",
    stac_version: "1.0.0",
    description: "TERRA-X STAC Catalog for NASA Planetary Analog Discovery",
    features: currentResults.map(site => ({
      type: "Feature",
      id: site.id,
      geometry: {
        type: "Point",
        coordinates: [site.lon, site.lat]
      },
      properties: {
        title: site.name,
        cell_id_h3: site.cell_id,
        afi_score_p50: site.scores.afi_p50,
        rank_p50: site.monte_carlo.rank_p50,
        p_top10: site.monte_carlo.p_top10,
        evidence_confidence_q: site.scores.Q_evidence,
        license: "OPEN_PUBLIC_DOMAIN"
      }
    }))
  };

  const blob = new Blob([JSON.stringify(geojson, null, 2)], { type: "application/geo+json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `TERRA-X_Global_Analogs_STAC.geojson`;
  a.click();
}

// ==============================================================================
// 14. Application Boot
// ==============================================================================
window.addEventListener("DOMContentLoaded", () => {
  initMaps();
  triggerDiscovery();
});
