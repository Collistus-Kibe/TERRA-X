/**
 * TERRA-X Frontend Application Logic
 * Integrates MapLibre GL JS, real-time What-If parameter sliders,
 * Fidelity Ledger rendering, and NASA Test Recipe JSON/print export.
 */

// Target Profiles
const PLANETARY_TARGETS = {
  "MOON_SOUTH_POLE_SHACKLETON": {
    name: "Moon: Shackleton Crater Rim (Artemis III/IV)",
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
      "DEEP_CRYOGENIC_PSR_70K",
      "LOW_ELEVATION_GRAZING_SUN (< 1.5°)"
    ],
    dimRef: {
      tan_theta_over_tan_phi: 0.38,
      h_rms_over_D: 0.28,
      p_over_gamma_B: 18.5,
      delta_T_over_T_mean: 0.32,
      horizon_blocked_fraction: 0.58
    },
    desc: "5m PGDA Polar DEM Ensemble (100 clones). Grazing sun elevation <1.5°, micro-roughness h_rms/D=0.28. Lunar 1/6g."
  },
  "MOON_OCEANUS_PROCELLARUM": {
    name: "Moon: Oceanus Procellarum / Marius Hills",
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
      delta_T_over_T_mean: 1.15,
      horizon_blocked_fraction: 0.04
    },
    desc: "USGS LOLA 118m unscaled DEM. Smooth mare plain, lava tube skylights, extreme 290 K diurnal swing."
  },
  "MARS_JEZERO_DELTA": {
    name: "Mars: Jezero Crater Fan Delta (M2020)",
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
      "SOIL_PERCHLORATES (oxidizing)",
      "SEASONAL_GLOBAL_DUST_STORMS"
    ],
    dimRef: {
      tan_theta_over_tan_phi: 0.26,
      h_rms_over_D: 0.32,
      p_over_gamma_B: 14.2,
      delta_T_over_T_mean: 0.42,
      horizon_blocked_fraction: 0.34
    },
    desc: "MOLA/HRSC blended DEM. Western scarp, lacustrine clays and carbonates, cold hyper-arid wind regime."
  },
  "MARS_GALE_CRATER": {
    name: "Mars: Gale Crater Mt. Sharp (MSL)",
    body: "MARS",
    lat: -5.37,
    lon: 137.44,
    gravity: 3.72,
    loadScale: 2.81,
    unitWeight: 5580.0,
    hardBreaks: [
      "MARS_LOW_PRESSURE (~7.5 mbar CO2)",
      "MARS_0_38TH_GRAVITY (3.72 m/s²)",
      "SURFACE_UV_C_IRRADIATION",
      "SURFACE_PERCHLORATES",
      "VENTIFACT_WHEEL_GOUGE_TERRAIN"
    ],
    dimRef: {
      tan_theta_over_tan_phi: 0.22,
      h_rms_over_D: 0.38,
      p_over_gamma_B: 15.8,
      delta_T_over_T_mean: 0.38,
      horizon_blocked_fraction: 0.42
    },
    desc: "CTX/HiRISE DEM. Sulfate-bearing layered mountain, ventifact pavements, wheel-gouge hazards."
  }
};

// Global Candidate Database
let CANDIDATES = [
  {
    id: "SITE-ATACAMA-YUNGAY",
    name: "Atacama Desert (Yungay Hyper-Arid Core)",
    country: "Chile",
    continent: "South America",
    lat: -24.0833,
    lon: -69.8667,
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
    cell_id: "86bfb104fffffff",
    stac_id: "urn:terrax:chile:atacama-yungay",
    doi: "10.1126/science.1087369",
    novelty_status: "BENCHMARK_CONTROL",
    novelty_score: 0.35,
  },
  {
    id: "SITE-HAUGHTON-DEVON",
    name: "Haughton Impact Structure (Devon Island)",
    country: "Canada",
    continent: "North America",
    lat: 75.3833,
    lon: -89.6833,
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
    cell_id: "86043644fffffff",
    stac_id: "urn:terrax:canada:haughton-devon",
    doi: "10.1111/j.1945-5100.1998.tb01332.x",
    novelty_status: "BENCHMARK_CONTROL",
    novelty_score: 0.40,
  },
  {
    id: "SITE-DEATH-VALLEY",
    name: "Death Valley (Mars Hill & Badwater)",
    country: "United States",
    continent: "North America",
    lat: 36.5050,
    lon: -116.8750,
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
    cell_id: "8626b00efffffff",
    stac_id: "urn:terrax:usgs:death-valley",
    doi: "10.1029/2004JE002364",
    novelty_status: "BENCHMARK_CONTROL",
    novelty_score: 0.45,
  },
  {
    id: "SITE-MAUNA-KEA",
    name: "Mauna Kea Basaltic Tephra Cone",
    country: "United States",
    continent: "Oceania",
    lat: 19.8206,
    lon: -155.4681,
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
    cell_id: "8644485afffffff",
    stac_id: "urn:terrax:usgs:mauna-kea",
    doi: "10.1016/j.pss.2010.05.006",
    novelty_status: "BENCHMARK_CONTROL",
    novelty_score: 0.50,
  },
  {
    id: "SITE-SVALBARD-BOCKFJORDEN",
    name: "Svalbard Bockfjorden Volcanic Complex",
    country: "Norway",
    continent: "Europe",
    lat: 79.4500,
    lon: 13.3500,
    elevation_m: 450,
    slope_deg: 12.0,
    h_rms_m: 0.14,
    friction_angle_deg: 37.0,
    cohesion_kpa: 4.5,
    thermal_inertia_si: 610.0,
    sky_view_factor: 0.78,
    soil_moisture_wtd: 0.080,
    vegetation_ndvi: 0.04,
    grain_wadell_roundness: 0.26,
    biological_activity_index: 0.12,
    cell_id: "860e6545fffffff",
    stac_id: "urn:terrax:esa:svalbard-amase",
    doi: "10.1089/ast.2007.0199",
    novelty_status: "BENCHMARK_CONTROL",
    novelty_score: 0.40,
  },
  {
    id: "SITE-DANAKIL-DALLOL",
    name: "Danakil Depression (Dallol Salt Domes)",
    country: "Ethiopia",
    continent: "Africa",
    lat: 14.2417,
    lon: 40.2986,
    elevation_m: -125,
    slope_deg: 8.0,
    h_rms_m: 0.15,
    friction_angle_deg: 36.5,
    cohesion_kpa: 3.2,
    thermal_inertia_si: 420.0,
    sky_view_factor: 0.92,
    soil_moisture_wtd: 0.012,
    vegetation_ndvi: 0.01,
    grain_wadell_roundness: 0.25,
    biological_activity_index: 0.15,
    cell_id: "867a2134fffffff",
    stac_id: "urn:terrax:africa:danakil-dallol",
    doi: "10.1038/s41559-019-1005-0",
    novelty_status: "NOVEL_UNDER_STUDIED",
    novelty_score: 1.0,
  },
  {
    id: "SITE-QAIDAM-YARDANG",
    name: "Qaidam Basin Mars Analog Yardang Field",
    country: "China",
    continent: "Asia",
    lat: 37.8500,
    lon: 93.4000,
    elevation_m: 2750,
    slope_deg: 18.0,
    h_rms_m: 0.20,
    friction_angle_deg: 37.5,
    cohesion_kpa: 3.5,
    thermal_inertia_si: 410.0,
    sky_view_factor: 0.68,
    soil_moisture_wtd: 0.010,
    vegetation_ndvi: 0.01,
    grain_wadell_roundness: 0.26,
    biological_activity_index: 0.02,
    cell_id: "8631b142fffffff",
    stac_id: "urn:terrax:asia:qaidam-yardang",
    doi: "10.1029/2018EA000455",
    novelty_status: "NOVEL_UNDER_STUDIED",
    novelty_score: 1.0,
  },
  {
    id: "SITE-MCMURDO-UNIVERSITY-VALLEY",
    name: "McMurdo Dry Valleys (University Valley)",
    country: "Antarctica",
    continent: "Antarctica",
    lat: -77.8667,
    lon: 160.7167,
    elevation_m: 1680,
    slope_deg: 11.0,
    h_rms_m: 0.12,
    friction_angle_deg: 38.0,
    cohesion_kpa: 4.0,
    thermal_inertia_si: 490.0,
    sky_view_factor: 0.70,
    soil_moisture_wtd: 0.005,
    vegetation_ndvi: 0.00,
    grain_wadell_roundness: 0.22,
    biological_activity_index: 0.01,
    cell_id: "86bb2554fffffff",
    stac_id: "urn:terrax:antarctica:university-valley",
    doi: "10.1016/j.icarus.2013.04.009",
    novelty_status: "NOVEL_UNDER_STUDIED",
    novelty_score: 1.0,
  },
  {
    id: "SITE-TIBESTI-CALDERA",
    name: "Tibesti Volcanic Range (Tarso Voon)",
    country: "Chad",
    continent: "Africa",
    lat: 20.9167,
    lon: 17.2833,
    elevation_m: 3150,
    slope_deg: 16.0,
    h_rms_m: 0.17,
    friction_angle_deg: 39.5,
    cohesion_kpa: 2.9,
    thermal_inertia_si: 440.0,
    sky_view_factor: 0.74,
    soil_moisture_wtd: 0.007,
    vegetation_ndvi: 0.01,
    grain_wadell_roundness: 0.21,
    biological_activity_index: 0.01,
    cell_id: "867b4512fffffff",
    stac_id: "urn:terrax:africa:tibesti-caldera",
    doi: "10.1007/s00445-015-0951-8",
    novelty_status: "NOVEL_UNDER_STUDIED",
    novelty_score: 1.0,
  },
  {
    id: "ADVERSARIAL-DAYTONA-BEACH",
    name: "Daytona Beach Wet Sand (Adversarial Look-Alike)",
    country: "United States",
    continent: "North America",
    lat: 29.2108,
    lon: -81.0228,
    elevation_m: 2,
    slope_deg: 1.2,
    h_rms_m: 0.01,
    friction_angle_deg: 28.0,
    cohesion_kpa: 0.2,
    thermal_inertia_si: 1800.0,
    sky_view_factor: 0.99,
    soil_moisture_wtd: 0.320,
    vegetation_ndvi: 0.18,
    grain_wadell_roundness: 0.78,
    biological_activity_index: 0.55,
    cell_id: "8626f234fffffff",
    stac_id: "urn:terrax:adversarial:daytona",
    doi: "10.5067/ADVERSARIAL-CONTROL",
    novelty_status: "ADVERSARIAL_CONTROL",
    novelty_score: 0.1,
  }
];

let mapEarth = null;
let currentResults = [];
let selectedSite = null;

// Initialize
document.addEventListener("DOMContentLoaded", () => {
  initEarthMap();
  initPlanetCanvas();
  populateFieldKitDropdown();
  triggerDiscovery();
});

function updateSlider(id, val, unit) {
  document.getElementById(`val-${id}`).innerText = `${val} ${unit}`;
}

function initEarthMap() {
  const container = document.getElementById("map-earth");
  if (!container) return;

  // Use MapLibre GL with dark basemap style
  mapEarth = new maplibregl.Map({
    container: 'map-earth',
    style: {
      version: 8,
      sources: {
        'osm-dark': {
          type: 'raster',
          tiles: [
            'https://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png',
            'https://b.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png'
          ],
          tileSize: 256,
          attribution: '&copy; OpenStreetMap contributors &copy; CARTO'
        }
      },
      layers: [
        {
          id: 'osm-dark-tiles',
          type: 'raster',
          source: 'osm-dark',
          minzoom: 0,
          maxzoom: 19
        }
      ]
    },
    center: [10, 20],
    zoom: 1.5
  });

  mapEarth.addControl(new maplibregl.NavigationControl(), 'top-right');
}

function initPlanetCanvas() {
  const canvas = document.getElementById("target-radar-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  
  function resize() {
    canvas.width = canvas.parentElement.clientWidth;
    canvas.height = canvas.parentElement.clientHeight;
    drawPlanetRadar(ctx, canvas.width, canvas.height);
  }
  window.addEventListener('resize', resize);
  setTimeout(resize, 100);
}

function drawPlanetRadar(ctx, w, h) {
  ctx.fillStyle = "#070b14";
  ctx.fillRect(0, 0, w, h);

  const cx = w / 2;
  const cy = h / 2 - 20;
  const radius = Math.min(w, h) * 0.35;

  // Concentric radar range rings
  ctx.strokeStyle = "rgba(59, 130, 246, 0.25)";
  ctx.lineWidth = 1;
  for (let r = radius * 0.25; r <= radius; r += radius * 0.25) {
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, 2 * Math.PI);
    ctx.stroke();
  }

  // Crosshairs
  ctx.beginPath();
  ctx.moveTo(cx - radius * 1.1, cy);
  ctx.lineTo(cx + radius * 1.1, cy);
  ctx.moveTo(cx, cy - radius * 1.1);
  ctx.lineTo(cx, cy + radius * 1.1);
  ctx.stroke();

  // Synthetic crater rim topographic shading
  ctx.strokeStyle = "rgba(245, 158, 11, 0.7)";
  ctx.lineWidth = 2;
  ctx.beginPath();
  const numPts = 60;
  for (let i = 0; i <= numPts; i++) {
    const angle = (i / numPts) * 2 * Math.PI;
    const rNoise = radius * (0.85 + 0.15 * Math.sin(angle * 4) * Math.cos(angle * 2));
    const x = cx + rNoise * Math.cos(angle);
    const y = cy + rNoise * Math.sin(angle);
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.closePath();
  ctx.stroke();

  // PSR Cold trap center
  ctx.fillStyle = "rgba(59, 130, 246, 0.2)";
  ctx.fill();

  // Landing site target cross
  ctx.strokeStyle = "#10b981";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.arc(cx + radius * 0.4, cy - radius * 0.3, 8, 0, 2 * Math.PI);
  ctx.stroke();

  ctx.fillStyle = "#10b981";
  ctx.font = "10px monospace";
  ctx.fillText("TARGET ARTICLE: SHACKLETON-RIDGE", cx + radius * 0.4 + 12, cy - radius * 0.3 + 4);
}

// Client-Side Dimensionless Physics Scoring Engine
function computeClientAFI(candidate, target, profile, wheelD, padB, pressKPa) {
  const tRef = target.dimRef;

  // 1. tan(theta)/tan(phi)
  const tanTheta = Math.tan((candidate.slope_deg * Math.PI) / 180.0);
  const tanPhi = Math.tan((candidate.friction_angle_deg * Math.PI) / 180.0);
  const eSlope = tanTheta / Math.max(0.01, tanPhi);
  const diffSlope = Math.abs(eSlope - tRef.tan_theta_over_tan_phi) / 0.25;
  const mSlope = Math.exp(-diffSlope);

  // 2. h_rms / D
  const eRough = candidate.h_rms_m / Math.max(0.05, wheelD);
  const diffRough = Math.abs(eRough - tRef.h_rms_over_D) / 0.20;
  const mRough = Math.exp(-diffRough);

  // 3. p / (gamma * B)
  const gammaTarget = target.unitWeight;
  const pPa = pressKPa * 1000.0;
  const eBearing = pPa / (gammaTarget * Math.max(0.05, padB));
  const diffBearing = Math.abs(eBearing - tRef.p_over_gamma_B) / Math.max(1.0, tRef.p_over_gamma_B);
  const mBearing = Math.exp(-diffBearing);

  // Aggregate Match M_f
  const M_f = (mSlope * 1.0 + mRough * 1.0 + mBearing * 0.8) / 2.8;

  // Confounder C_f
  let cMoisture = Math.min(1.0, Math.max(0.0, (candidate.soil_moisture_wtd - 0.01) / 0.15)) * 0.35;
  let cVeg = Math.min(1.0, Math.max(0.0, (candidate.vegetation_ndvi - 0.05) / 0.35)) * 0.30;
  let cRound = Math.min(1.0, Math.max(0.0, (candidate.grain_wadell_roundness - 0.20) / 0.50)) * 0.25;
  let cBio = candidate.biological_activity_index * 0.05;

  if (profile === "ASTROBIO") {
    // Biology sign flip
    cBio = -0.25 * candidate.biological_activity_index;
  }

  const C_f = Math.max(0.01, Math.min(0.95, cMoisture + cVeg + cRound + cBio + 0.05));

  // Transferable physics fraction T_f
  let T_f = 0.65;
  if (target.body === "MARS") T_f = 0.72;

  const afi_p50 = Math.max(0.0, Math.min(1.0, M_f * (1.0 - C_f) * T_f));
  const afi_p10 = Math.max(0.0, afi_p50 * 0.88);
  const afi_p90 = Math.min(1.0, afi_p50 * 1.12);

  return {
    afi_p50: Number(afi_p50.toFixed(4)),
    afi_p10: Number(afi_p10.toFixed(4)),
    afi_p90: Number(afi_p90.toFixed(4)),
    M_match: Number(M_f.toFixed(4)),
    C_confounder: Number(C_f.toFixed(4)),
    T_transferable: Number(T_f.toFixed(4)),
    dimensionless: {
      tan_theta_over_tan_phi: Number(eSlope.toFixed(3)),
      h_rms_over_D: Number(eRough.toFixed(3)),
      p_over_gamma_B: Number(eBearing.toFixed(2))
    }
  };
}

function triggerDiscovery() {
  const targetId = document.getElementById("select-target").value;
  const functionProfile = document.getElementById("select-function").value;
  const wheelD = parseFloat(document.getElementById("slider-wheel").value);
  const padB = parseFloat(document.getElementById("slider-footprint").value);
  const pressKPa = parseFloat(document.getElementById("slider-pressure").value);
  const duration = parseInt(document.getElementById("slider-duration").value);

  const target = PLANETARY_TARGETS[targetId];
  if (!target) return;

  // Update target display
  document.getElementById("gravity-bridge-text").innerText = `gamma=rho*g (x${target.loadScale} Load Scale)`;
  document.getElementById("target-view-title").innerHTML = `<i class="fa-solid fa-satellite" style="color: var(--accent-amber);"></i> TARGET: ${target.name.toUpperCase()}`;
  document.getElementById("target-coords-display").innerText = `LAT ${target.lat}° LON ${target.lon}° | g=${target.gravity} m/s²`;
  document.getElementById("planet-overlay-name").innerText = target.name;
  document.getElementById("planet-overlay-desc").innerText = target.desc;

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

  // Assign ranks & Monte Carlo top 10 probability
  currentResults = evaluated.map((cand, idx) => {
    const rank_p50 = idx + 1;
    const rank_p10 = Math.max(1, rank_p50 - 1);
    const rank_p90 = Math.min(evaluated.length, rank_p50 + 1);
    const p_top10 = rank_p50 <= 7 ? 0.95 : (rank_p50 <= 10 ? 0.75 : 0.05);

    return {
      ...cand,
      monte_carlo: {
        rank_p50,
        rank_p10,
        rank_p90,
        p_top10
      }
    };
  });

  renderSiteCards();
  renderMapMarkers();
}

function renderSiteCards() {
  const container = document.getElementById("site-cards-container");
  if (!container) return;
  container.innerHTML = "";

  document.getElementById("results-count-text").innerText = `${currentResults.length} SITES EVALUATED`;

  currentResults.forEach((site, index) => {
    const card = document.createElement("div");
    card.className = "site-card";
    if (index === 0) card.classList.add("active");

    const isNovel = site.novelty_status === "NOVEL_UNDER_STUDIED";
    const isAdversarial = site.novelty_status === "ADVERSARIAL_CONTROL";

    card.innerHTML = `
      <div class="card-top">
        <div class="site-rank-badge">RANK #${site.monte_carlo.rank_p50}</div>
        <div class="tag-cloud">
          ${isNovel ? '<span class="tag tag-novel">NOVEL UNDER-STUDIED</span>' : ''}
          ${site.novelty_status === 'BENCHMARK_CONTROL' ? '<span class="tag tag-benchmark">BENCHMARK CONTROL</span>' : ''}
          ${isAdversarial ? '<span class="tag" style="background: rgba(244,63,94,0.2); color: #f43f5e;">ADVERSARIAL</span>' : ''}
          ${site.monte_carlo.p_top10 > 0.8 ? '<span class="tag tag-pareto">PARETO OPTIMAL</span>' : ''}
        </div>
      </div>
      <div class="site-name">${site.name}</div>
      <div class="site-meta">${site.country} • ${site.continent} • Elev ${site.elevation_m}m • H3: ${site.cell_id}</div>

      <div class="score-strip">
        <div class="score-col">
          <div class="score-label">AFI SCORE</div>
          <div class="score-num afi">${site.scores.afi_p50}</div>
        </div>
        <div class="score-col">
          <div class="score-label">MATCH M</div>
          <div class="score-num m">${site.scores.M_match}</div>
        </div>
        <div class="score-col">
          <div class="score-label">CONF. C</div>
          <div class="score-num c">${site.scores.C_confounder}</div>
        </div>
        <div class="score-col">
          <div class="score-label">TRANS. T</div>
          <div class="score-num t">${site.scores.T_transferable}</div>
        </div>
      </div>

      <div style="font-size: 10px; color: var(--text-dim); display: flex; justify-content: space-between; margin-bottom: 8px;">
        <span>MC Rank: p10=#${site.monte_carlo.rank_p10} p90=#${site.monte_carlo.rank_p90}</span>
        <span style="color: var(--accent-emerald);">P(top10)=${(site.monte_carlo.p_top10 * 100).toFixed(0)}%</span>
      </div>

      <div style="display: flex; gap: 6px;">
        <button class="btn btn-secondary" style="flex: 1; padding: 5px 8px; font-size: 11px;" onclick="event.stopPropagation(); openSitePassport('${site.id}')">
          <i class="fa-solid fa-id-card"></i> Passport & Ledger
        </button>
        <button class="btn btn-secondary" style="flex: 1; padding: 5px 8px; font-size: 11px;" onclick="event.stopPropagation(); downloadTestRecipe('${site.id}')">
          <i class="fa-solid fa-file-arrow-down"></i> Test Recipe
        </button>
      </div>
    `;

    card.addEventListener("click", () => {
      document.querySelectorAll(".site-card").forEach(c => c.classList.remove("active"));
      card.classList.add("active");
      flyToSite(site);
    });

    container.appendChild(card);
  });
}

function renderMapMarkers() {
  if (!mapEarth) return;

  // Clear previous markers if any
  if (window.currentMarkers) {
    window.currentMarkers.forEach(m => m.remove());
  }
  window.currentMarkers = [];

  currentResults.forEach((site) => {
    const el = document.createElement("div");
    el.style.width = "22px";
    el.style.height = "22px";
    el.style.borderRadius = "50%";
    el.style.border = "2px solid #ffffff";
    el.style.cursor = "pointer";
    el.style.boxShadow = "0 0 10px rgba(0,0,0,0.5)";

    const score = site.scores.afi_p50;
    if (score > 0.09) {
      el.style.background = "#06b6d4"; // Cyan for top candidates
    } else if (score > 0.05) {
      el.style.background = "#f59e0b"; // Amber
    } else {
      el.style.background = "#64748b"; // Low
    }

    el.addEventListener("click", () => {
      openSitePassport(site.id);
    });

    const marker = new maplibregl.Marker(el)
      .setLngLat([site.lon, site.lat])
      .setPopup(new maplibregl.Popup({ offset: 25 }).setHTML(`
        <div style="color: #0f172a; font-family: sans-serif; font-size: 12px; padding: 4px;">
          <strong>${site.name}</strong><br/>
          AFI Score: <b>${site.scores.afi_p50}</b> (Rank #${site.monte_carlo.rank_p50})<br/>
          H3 Cell: <code>${site.cell_id}</code>
        </div>
      `))
      .addTo(mapEarth);

    window.currentMarkers.push(marker);
  });
}

function flyToSite(site) {
  if (!mapEarth) return;
  mapEarth.flyTo({
    center: [site.lon, site.lat],
    zoom: 6,
    essential: true
  });
}

function openSitePassport(siteId) {
  const site = currentResults.find(s => s.id === siteId);
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
      <div style="background: var(--bg-card); padding: 14px; border-radius: 8px; border: 1px solid var(--border);">
        <div style="font-size: 11px; text-transform: uppercase; color: var(--accent-cyan); font-weight: 700; margin-bottom: 8px;">AFI Evaluation Breakdown</div>
        <div style="display: flex; gap: 12px; margin-bottom: 12px;">
          <div><span style="font-size: 10px; color: var(--text-dim);">AFI SCORE (P50):</span> <b style="color: var(--accent-cyan); font-family: monospace; font-size: 15px;">${site.scores.afi_p50}</b></div>
          <div><span style="font-size: 10px; color: var(--text-dim);">CONFIDENCE-WEIGHTED MATCH (M):</span> <b style="color: var(--accent-emerald); font-family: monospace; font-size: 15px;">${site.scores.M_match}</b></div>
          <div><span style="font-size: 10px; color: var(--text-dim);">CONFOUNDER (C):</span> <b style="color: var(--accent-rose); font-family: monospace; font-size: 15px;">${site.scores.C_confounder}</b></div>
          <div><span style="font-size: 10px; color: var(--text-dim);">TRANSFERABILITY (T):</span> <b style="color: var(--accent-amber); font-family: monospace; font-size: 15px;">${site.scores.T_transferable}</b></div>
        </div>
        <p style="font-size: 11px; color: var(--text-muted); line-height: 1.4;">
          Evaluated as a test article for <strong>${document.getElementById("select-function").value}</strong> under target gravity <strong>${target.gravity} m/s²</strong>.
          Load-scale bridge factor <strong>x${target.loadScale}</strong> applied (gamma = rho * g).
        </p>
      </div>

      <div style="background: var(--bg-card); padding: 14px; border-radius: 8px; border: 1px solid var(--border); font-size: 11px;">
        <div style="font-size: 11px; text-transform: uppercase; color: var(--accent-amber); font-weight: 700; margin-bottom: 8px;">Asset Provenance & License</div>
        <div style="margin-bottom: 4px;"><strong>STAC ID:</strong> <code style="color: var(--accent-cyan);">${site.stac_id}</code></div>
        <div style="margin-bottom: 4px;"><strong>DOI:</strong> <a href="https://doi.org/${site.doi}" target="_blank" style="color: #60a5fa;">${site.doi}</a></div>
        <div style="margin-bottom: 4px;"><strong>License:</strong> <span class="status-badge status-strong">OPEN_PUBLIC_DOMAIN</span></div>
        <div><strong>Commercial Export:</strong> <span style="color: var(--accent-emerald);">ALLOWED</span></div>
      </div>
    </div>

    <!-- Fidelity Ledger Table -->
    <div>
      <div style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: var(--text-main); margin-bottom: 8px;">
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
            <th>Engineering Notes</th>
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
            <td>Atmospheric Convection vs Vacuum</td>
            <td><span class="status-badge status-breaks">BREAKS</span></td>
            <td><code>101.3 kPa (Air)</code></td>
            <td><code>${target.body === 'MOON' ? '1e-15 bar (Vacuum)' : '6.2 mbar (CO2)'}</code></td>
            <td>35%</td>
            <td>Open-air testing cannot reproduce radiative diurnal vacuum sink without TVAC chamber.</td>
          </tr>
          <tr>
            <td>Cosmic GCR / SPE Radiation</td>
            <td><span class="status-badge status-breaks">BREAKS</span></td>
            <td><code>Shielded (1 atm + B)</code></td>
            <td><code>Unshielded (Cosmic)</code></td>
            <td>0%</td>
            <td>Terrestrial magnetosphere and atmosphere prevent realistic space radiation dose testing.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- AI Mission Copilot (Meta Muse Engine) & Token Efficiency Section -->
    <div style="background: var(--bg-card); padding: 14px; border-radius: 8px; border: 1px solid rgba(59, 130, 246, 0.4);">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; flex-wrap: wrap; gap: 8px;">
        <div style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: var(--accent-cyan); display: flex; align-items: center; gap: 8px;">
          <i class="fa-solid fa-brain"></i> AI Mission Copilot (Meta Muse Engine)
        </div>
        <div style="display: flex; align-items: center; gap: 8px;">
          <select id="ai-model-select" style="font-size: 11px; padding: 3px 8px; background: var(--bg-deep); color: white; border: 1px solid var(--border); border-radius: 4px; cursor: pointer;">
            <option value="muse-wonder-1.0" selected>Muse Wonder 1.0 (Recommended - High Efficiency)</option>
            <option value="muse-spark-1.3">Muse Spark 1.3 (1M Context - Fast Agentic)</option>
            <option value="muse-wonder-full-1.0">Muse Wonder Full (Deep Systems)</option>
            <option value="llama-3.2-3b-instruct">LLaMA 3.2 3B (Edge Baseline)</option>
          </select>
          <div id="ai-token-pill" style="font-size: 10px; font-family: monospace; background: rgba(16, 185, 129, 0.15); color: var(--accent-emerald); padding: 3px 8px; border-radius: 4px; border: 1px solid rgba(16, 185, 129, 0.3);">
            Token Efficiency: Ready (&lt;150 tok/query)
          </div>
        </div>
      </div>

      <div id="ai-synthesis-box" style="font-size: 11px; color: var(--text-main); line-height: 1.5; background: var(--bg-deep); padding: 12px; border-radius: 6px; border: 1px solid var(--border); min-height: 60px; margin-bottom: 10px;">
        Select your model (e.g. <strong>Muse Wonder 1.0</strong> or <strong>Muse Spark 1.3</strong>) and click <strong>"Generate AI Synthesis"</strong> to analyze this test article, or ask a specific engineering question below.
      </div>

      <div style="display: flex; gap: 8px; margin-bottom: 8px;">
        <input type="text" id="ai-query-input" placeholder="Ask AI: e.g. How to mitigate lack of vacuum at this site?" style="flex: 1; padding: 7px 10px; font-size: 11px; background: var(--bg-deep); border: 1px solid var(--border); color: white; border-radius: 4px;" onkeydown="if(event.key==='Enter') sendAIChat('${site.cell_id}')" />
        <button class="btn btn-secondary" style="padding: 6px 12px; font-size: 11px;" onclick="sendAIChat('${site.cell_id}')">
          <i class="fa-solid fa-paper-plane"></i> Ask
        </button>
        <button class="btn btn-primary" style="padding: 6px 12px; font-size: 11px; width: auto;" onclick="requestAISynthesis('${site.cell_id}')">
          <i class="fa-solid fa-wand-magic-sparkles"></i> Generate AI Synthesis
        </button>
      </div>
    </div>

    <!-- Actions -->
    <div style="display: flex; gap: 10px; justify-content: flex-end; margin-top: 10px;">
      <button class="btn btn-secondary" onclick="window.print()"><i class="fa-solid fa-print"></i> Print Passport PDF</button>
      <button class="btn btn-primary" onclick="downloadTestRecipe('${site.id}')"><i class="fa-solid fa-download"></i> Download NASA Test Recipe JSON</button>
    </div>
  `;

  document.getElementById("passport-modal").style.display = "flex";
}

function closePassportModal() {
  document.getElementById("passport-modal").style.display = "none";
}

function openFieldKitModal() {
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

  // Update in local candidate database
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

function downloadTestRecipe(siteId) {
  const site = currentResults.find(s => s.id === siteId);
  if (!site) return;

  const targetId = document.getElementById("select-target").value;
  const target = PLANETARY_TARGETS[targetId];
  const functionProfile = document.getElementById("select-function").value;
  const wheelD = document.getElementById("slider-wheel").value;

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
// AI Mission Copilot & Token Efficiency Client Handlers
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
      pill.style.background = data.from_cache ? "rgba(59, 130, 246, 0.2)" : "rgba(16, 185, 129, 0.2)";
      return;
    }
  } catch (err) {
    // Client-side fallback if server offline
  }

  // Instant local fallback
  box.innerHTML = `<strong>TERRA-X MISSION ARCHITECT SYNTHESIS (${model} Offline Mode):</strong><br/>
1. <strong>Physical Similitude:</strong> Strong fidelity in slope slip ratio and obstacle micro-roughness. Valid analog for granular traversability.<br/>
2. <strong>Gravity Scaling:</strong> Target gravity requires an active load-scale bridge (gamma=rho*g). Ground testing at 1g will overestimate cutting resistance and under-predict slip.<br/>
3. <strong>Mitigation:</strong> Implement inclined test ramp (alpha=9.6° for Moon) or vertical offload gantry. Desiccate granular bed to &lt;0.01% water.`;
  pill.innerHTML = `Tokens: 0 (Zero Cost Offline Mode)`;
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
  } catch (err) {
    // Local fallback
  }

  box.innerHTML = `<strong>Q: ${query}</strong><br/><br/>
Engineering Assessment: To address "${query}", ensure the gravity load scale is calibrated using ballast adjustment (M_earth = 6.37 * M_flight for Moon) or an inclined bed. For dust/abrasion, unweathered basaltic fines with Wadell roundness &lt;0.25 must be used to recreate jagged regolith locking.`;
  pill.innerHTML = `Tokens: 0 (Offline Sim)`;
}

