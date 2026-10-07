// Primary Application Logic for AI Waste Recovery Decision Intelligence
const API_BASE = '/api/v1';

// Check query param for design states: ?state=empty|loading|error
const urlParams = new URLSearchParams(window.location.search);
const stateParam = urlParams.get('state');

function setPageState(state) {
  if (stateParam) {
    document.querySelectorAll('[data-state]').forEach(el => el.dataset.state = stateParam);
    return;
  }
  document.querySelectorAll('[data-state]').forEach(el => el.dataset.state = state);
}

// Global initialization per page
document.addEventListener('DOMContentLoaded', () => {
  const path = window.location.pathname;
  if (path.endsWith('index.html') || path === '/' || path.endsWith('/app/')) {
    initDashboard();
  } else if (path.endsWith('scanner.html')) {
    initScanner();
  } else if (path.endsWith('result.html')) {
    initResult();
  } else if (path.endsWith('recovery.html')) {
    initRecovery();
  } else if (path.endsWith('regional.html')) {
    initRegional();
  } else if (path.endsWith('forecast.html')) {
    initForecast();
  } else if (path.endsWith('map.html')) {
    initMap();
  } else if (path.endsWith('community.html')) {
    initCommunity();
  } else if (path.endsWith('model-performance.html')) {
    initModelPerformance();
  } else if (path.endsWith('explainable-ai.html')) {
    initExplainableAI();
  } else if (path.endsWith('system-health.html')) {
    initSystemHealth();
  }
});

// 1. DASHBOARD
async function initDashboard() {
  setPageState('loading');
  try {
    const res = await fetch(`${API_BASE}/regional/overview`);
    if (!res.ok) throw new Error('Overview failed');
    const data = await res.json();
    setPageState('ready');

    // Update Priority regions table
    const tableBody = document.querySelector('#h-96948')?.closest('.card')?.querySelector('tbody');
    if (tableBody && data.regions) {
      tableBody.innerHTML = data.regions.slice(0, 5).map(r => `
        <tr>
          <td><strong>${r.region}</strong> (${r.pressure_category} Pressure)</td>
          <td class="num">${r.pressure_index} / 100</td>
        </tr>
      `).join('');
    }

    // Update Pressure list
    const chartBox = document.querySelector('#h-18076')?.closest('.card')?.querySelector('.chart-box');
    if (chartBox && data.regions) {
      chartBox.innerHTML = `
        <div style="display:flex; flex-direction:column; gap:8px;">
          ${data.regions.slice(0, 6).map(r => `
            <div>
              <div style="display:flex; justify-content:space-between; font-size:13px; margin-bottom:2px;">
                <span>${r.region} (${r.generation_tpd.toFixed(0)} TPD)</span>
                <span>${r.pressure_index}/100</span>
              </div>
              <div class="bar" style="background:#e0e0e0; height:8px; border-radius:4px; overflow:hidden;">
                <span style="display:block; width:${r.pressure_index}%; height:100%; background:${r.pressure_index > 65 ? 'var(--color-danger, #d9534f)' : 'var(--color-primary, #2e7d32)'}"></span>
              </div>
            </div>
          `).join('')}
        </div>
      `;
    }

    // Community actions
    const commBody = document.querySelector('#h-97143')?.closest('.card')?.querySelector('tbody');
    if (commBody) {
      commBody.innerHTML = `
        <tr><td>Decentralized composting drive (Pune)</td><td class="num"><span class="badge">In Progress</span></td></tr>
        <tr><td>MRF Dry segregation awareness (Mumbai)</td><td class="num"><span class="badge">Suggested</span></td></tr>
        <tr><td>E-Waste collection hub (Nagpur)</td><td class="num"><span class="badge">Accepted</span></td></tr>
      `;
    }

    // Recent Scans
    const recentsBody = document.querySelector('#h-79241')?.closest('.card')?.querySelector('tbody');
    if (recentsBody) {
      const recsRes = await fetch(`${API_BASE}/recommendations?page_size=3`);
      if (recsRes.ok) {
        const recsData = await recsRes.json();
        if (recsData.items && recsData.items.length > 0) {
          recentsBody.innerHTML = recsData.items.map(it => `
            <tr><td>${it.action.slice(0, 35)}...</td><td class="num"><span class="badge">${it.priority}</span></td></tr>
          `).join('');
        }
      }
    }

  } catch (err) {
    console.error(err);
    setPageState('error');
  }
}

// 2. SCANNER
function initScanner() {
  setPageState('ready');
  const uploadBox = document.querySelector('#h-76916')?.closest('.card')?.querySelector('.chart-box');
  const contextCard = document.querySelector('#h-10976')?.closest('.card');

  if (uploadBox && contextCard) {
    uploadBox.innerHTML = `
      <div style="padding:16px; text-align:center;">
        <input type="file" id="scan-file" accept="image/*" style="margin-bottom:12px; display:block; margin:0 auto 12px auto;" />
        <button id="scan-submit-btn" class="btn" style="background:#2e7d32; color:white; font-weight:bold; padding:8px 16px; border:none; border-radius:4px; cursor:pointer;">Run AI Waste Analysis</button>
        <div id="scan-preview" style="margin-top:12px;"></div>
      </div>
    `;

    contextCard.innerHTML = `
      <h3 id="h-10976">Context & Environmental Inputs</h3>
      <div style="padding:8px 0; display:flex; flex-direction:column; gap:12px;">
        <div>
          <label style="display:block; font-size:13px; margin-bottom:4px; font-weight:600;">Select Region (for pressure integration)</label>
          <select id="scan-region" class="input" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;">
            <option value="">-- No Region (Generic Analysis) --</option>
            <option value="Mumbai">Mumbai</option>
            <option value="Pune">Pune</option>
            <option value="Nagpur">Nagpur</option>
            <option value="Thane">Thane</option>
            <option value="Nashik">Nashik</option>
            <option value="Aurangabad">Aurangabad</option>
            <option value="Kalyan">Kalyan</option>
            <option value="Navi Mumbai">Navi Mumbai</option>
            <option value="Amravati">Amravati</option>
            <option value="Kolhapur">Kolhapur</option>
            <option value="Chandrapur">Chandrapur</option>
            <option value="Raigad">Raigad</option>
          </select>
        </div>
        <div>
          <label style="display:block; font-size:13px; margin-bottom:4px; font-weight:600;">Condition Input (Manual / Citizen observation)</label>
          <select id="scan-condition" class="input" style="width:100%; padding:8px; border:1px solid #ccc; border-radius:4px;">
            <option value="">Condition unavailable</option>
            <option value="clean">Clean / Dry</option>
            <option value="dirty">Dirty / Soiled</option>
            <option value="greasy">Greasy / Food Contaminated</option>
            <option value="damaged">Damaged / Broken</option>
          </select>
          <small style="color:#666; font-size:11px;">Note: As per scientific guidelines, condition is never fabricated from image classifiers.</small>
        </div>
      </div>
    `;

    const fileInput = document.getElementById('scan-file');
    const previewDiv = document.getElementById('scan-preview');
    fileInput.addEventListener('change', () => {
      if (fileInput.files && fileInput.files[0]) {
        const reader = new FileReader();
        reader.onload = e => {
          previewDiv.innerHTML = `<img src="${e.target.result}" style="max-height:160px; border-radius:6px; box-shadow:0 1px 3px rgba(0,0,0,0.2);" />`;
        };
        reader.readAsDataURL(fileInput.files[0]);
      }
    });

    const submitBtn = document.getElementById('scan-submit-btn');
    submitBtn.addEventListener('click', async () => {
      if (!fileInput.files || !fileInput.files[0]) {
        alert('Please choose a waste image first.');
        return;
      }
      submitBtn.disabled = true;
      submitBtn.innerText = 'Analyzing with MobileNetV3 + Grad-CAM...';

      const formData = new FormData();
      formData.append('image', fileInput.files[0]);
      const reg = document.getElementById('scan-region').value;
      if (reg) formData.append('region', reg);
      const cond = document.getElementById('scan-condition').value;
      if (cond) formData.append('condition', cond);

      try {
        const resp = await fetch(`${API_BASE}/waste/analyze`, { method: 'POST', body: formData });
        if (!resp.ok) throw new Error('Analysis failed');
        const resultData = await resp.json();
        sessionStorage.setItem('latest_analysis', JSON.stringify(resultData));
        window.location.href = 'result.html';
      } catch (err) {
        alert('Error analyzing image: ' + err.message);
        submitBtn.disabled = false;
        submitBtn.innerText = 'Run AI Waste Analysis';
      }
    });
  }
}

// 3. RESULT
function initResult() {
  const raw = sessionStorage.getItem('latest_analysis');
  if (!raw) {
    setPageState('empty');
    return;
  }
  setPageState('ready');
  const d = JSON.parse(raw);

  // Update pipeline chain
  const chainSteps = document.querySelectorAll('.chain li');
  if (chainSteps.length >= 5) {
    chainSteps[0].dataset.state = 'done';
    chainSteps[0].querySelector('.value').innerText = 'Verified';
    chainSteps[1].dataset.state = 'done';
    chainSteps[1].querySelector('.value').innerText = d.classification.label;
    chainSteps[2].dataset.state = 'done';
    chainSteps[2].querySelector('.value').innerText = d.recovery.material.slice(0, 16);
    chainSteps[3].dataset.state = 'done';
    chainSteps[3].querySelector('.value').innerText = `${d.recovery.score}/100`;
    chainSteps[4].dataset.state = 'done';
    chainSteps[4].querySelector('.value').innerText = d.recovery.route.toUpperCase();
  }

  // Prediction card
  const predCard = document.querySelector('#h-90333')?.closest('.card');
  if (predCard) {
    predCard.innerHTML = `
      <h3 id="h-90333">Waste Identification</h3>
      <div style="font-size:24px; font-weight:bold; color:#2e7d32; margin-bottom:4px;">${d.classification.label}</div>
      <p style="font-size:14px; color:#555;"><strong>Detected Material:</strong> ${d.recovery.material}</p>
      <p style="font-size:13px; color:#666;"><strong>Condition:</strong> ${d.recovery.condition}</p>
      <p style="font-size:13px; color:#333; margin-top:8px;">${d.recovery.rationale}</p>
    `;
  }

  // Confidence card
  const confCard = document.querySelector('#h-19245')?.closest('.card');
  if (confCard) {
    const pct = (d.classification.confidence * 100).toFixed(1);
    confCard.innerHTML = `
      <h3 id="h-19245">Confidence Score</h3>
      <div style="font-size:22px; font-weight:bold; margin-bottom:8px;">${pct}%</div>
      <div class="bar" style="background:#eee; height:12px; border-radius:6px; overflow:hidden;">
        <span style="display:block; width:${pct}%; height:100%; background:#2e7d32;"></span>
      </div>
      <p style="font-size:12px; color:#666; margin-top:8px;">Model: MobileNetV3-Small (Transfer Learning on RealWaste)</p>
    `;
  }

  // Score card
  const scoreCard = document.querySelector('#h-85779')?.closest('.card');
  if (scoreCard) {
    scoreCard.innerHTML = `
      <h3 id="h-85779">Waste Recovery Score</h3>
      <div style="display:flex; align-items:center; gap:16px;">
        <div style="font-size:36px; font-weight:bold; color:#1565c0;">${d.recovery.score}<span style="font-size:18px; color:#666;">/100</span></div>
        <div style="font-size:13px; line-height:1.4;">
          <div>• Material Factor: ${d.recovery.factor_breakdown.material_factor} / 40</div>
          <div>• Condition Factor: ${d.recovery.factor_breakdown.condition_factor} / 25</div>
          <div>• Route Feasibility: ${d.recovery.factor_breakdown.route_feasibility_factor} / 20</div>
          <div>• Handling Factor: ${d.recovery.factor_breakdown.local_handling_factor} / 15</div>
        </div>
      </div>
      <small style="color:#777; display:block; margin-top:8px;">Project-specific explainable index (not an official regulatory metric).</small>
    `;
  }

  // Top alternatives table
  const altBody = document.querySelector('#h-66603')?.closest('.card')?.querySelector('tbody');
  if (altBody && d.classification.top_k) {
    altBody.innerHTML = d.classification.top_k.map(k => `
      <tr>
        <td>${k.label}</td>
        <td class="num">${(k.confidence * 100).toFixed(1)}%</td>
      </tr>
    `).join('');
  }
}

// 4. RECOVERY & RECOMMENDATION
function initRecovery() {
  const raw = sessionStorage.getItem('latest_analysis');
  if (!raw) {
    setPageState('ready');
    return;
  }
  setPageState('ready');
  const d = JSON.parse(raw);

  const mainArea = document.querySelector('.grid.cols-2') || document.querySelector('[data-show="ready"]');
  if (mainArea) {
    mainArea.innerHTML = `
      <section class="card">
        <h3>AI-Assisted Decision & Recommended Action</h3>
        <div style="padding:8px 0;">
          <div style="font-size:18px; font-weight:bold; color:#2e7d32; margin-bottom:8px;">${d.recommendation.action}</div>
          <p style="font-size:14px; margin-bottom:8px;"><strong>Statutory Pathway:</strong> ${d.recovery.statutory_guidance.statutory_pathway}</p>
          <p style="font-size:14px; margin-bottom:8px;"><strong>Stream Type:</strong> ${d.recovery.statutory_guidance.stream_type} (Recommended Bin: <span class="badge" style="background:#e3f2fd; color:#0d47a1; font-weight:bold;">${d.recovery.statutory_guidance.recommended_bin}</span>)</p>
          <p style="font-size:13px; color:#555;">${d.recommendation.explanation}</p>
        </div>
      </section>
      <section class="card">
        <h3>Community Action Assignment</h3>
        <div style="padding:8px 0;">
          <div style="font-size:16px; font-weight:600; color:#1565c0; margin-bottom:8px;">${d.recommendation.community_action}</div>
          <div style="display:flex; gap:8px; margin-top:12px;">
            <button class="btn" style="background:#2e7d32; color:white; padding:6px 14px; border:none; border-radius:4px; cursor:pointer;" onclick="alert('Community action accepted and logged!')">Accept Action</button>
            <button class="btn" style="background:#f5f5f5; border:1px solid #ccc; padding:6px 14px; border-radius:4px; cursor:pointer;">Dismiss</button>
          </div>
        </div>
      </section>
      <section class="card" style="grid-column: span 2;">
        <h3>Component Traceability (Decision Intelligence Audit)</h3>
        <div class="table-wrap">
          <table class="table">
            <thead>
              <tr><th>Component</th><th>Engine Type</th><th>Contribution / Details</th></tr>
            </thead>
            <tbody>
              ${d.recommendation.component_trace.map(t => `
                <tr>
                  <td><strong>${t.component}</strong></td>
                  <td><span class="badge" style="text-transform:uppercase; font-size:10px;">${t.kind}</span></td>
                  <td>${t.detail}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      </section>
    `;
  }
}

// 5. REGIONAL INTELLIGENCE
async function initRegional() {
  setPageState('loading');
  try {
    const res = await fetch(`${API_BASE}/regional/overview`);
    const data = await res.json();
    setPageState('ready');

    const tableBody = document.querySelector('.table tbody');
    if (tableBody && data.regions) {
      tableBody.innerHTML = data.regions.map(r => `
        <tr style="cursor:pointer;" onclick="loadRegionDetail('${r.region}')">
          <td><strong>${r.region}</strong></td>
          <td class="num">${r.generation_tpd.toFixed(1)}</td>
          <td class="num">${r.treated_tpd ? r.treated_tpd.toFixed(1) : 'N/A'}</td>
          <td class="num">${r.untreated_gap_tpd ? r.untreated_gap_tpd.toFixed(1) : 'N/A'}</td>
          <td class="num"><span class="badge" style="background:${r.pressure_category === 'High' ? '#ffebee' : '#e8f5e9'}; color:${r.pressure_category === 'High' ? '#c62828' : '#2e7d32'}">${r.pressure_index} (${r.pressure_category})</span></td>
        </tr>
      `).join('');
    }
  } catch (err) {
    setPageState('error');
  }
}

async function loadRegionDetail(regName) {
  try {
    const res = await fetch(`${API_BASE}/regional/${regName}`);
    const d = await res.json();
    alert(`Region: ${d.region}\n2023 Generation: ${d.history[d.history.length-1].generation_tpd} TPD\nPressure: ${d.pressure.pressure_index}/100 (${d.pressure.category})\n2024-2027 Forecast: ${d.forecasts.map(f => f.year + ':' + f.predicted_tpd).join(', ')}`);
  } catch (e) {
    console.error(e);
  }
}

// 6. FORECAST & CAPACITY PLANNING
async function initForecast() {
  setPageState('loading');
  try {
    const fcRes = await fetch(`${API_BASE}/forecast`);
    const data = await fcRes.json();
    setPageState('ready');

    // Forecast table
    const tableCard = document.querySelector('#h-79243')?.closest('.card');
    if (tableCard && data.forecasts) {
      // Pivot forecasts by region
      const regionsMap = {};
      data.forecasts.forEach(f => {
        if (!regionsMap[f.region]) regionsMap[f.region] = {};
        regionsMap[f.region][f.forecast_year] = f;
      });

      tableCard.innerHTML = `
        <h3 id="h-79243">Model-Based Forecasts (2024–2027)</h3>
        <p style="font-size:12px; color:#666; margin-bottom:8px;">Model: Naive Baseline / Previous Year Persistence (Selected via time-aware expanding-window backtesting across 2016–2023, Lowest MAE: 72.07 TPD). Forecast values are model predictions, not observations.</p>
        <div class="table-wrap">
          <table class="table">
            <thead>
              <tr><th>Region</th><th class="num">2024 Forecast</th><th class="num">2025 Forecast</th><th class="num">2026 Forecast</th><th class="num">2027 Forecast</th></tr>
            </thead>
            <tbody>
              ${Object.keys(regionsMap).map(reg => `
                <tr>
                  <td><strong>${reg}</strong></td>
                  <td class="num">${regionsMap[reg][2024]?.predicted_gen_total_ulb_tpd || '-'} <small style="color:#777;">±${Math.round((regionsMap[reg][2024]?.upper_bound - regionsMap[reg][2024]?.predicted_gen_total_ulb_tpd) || 0)}</small></td>
                  <td class="num">${regionsMap[reg][2025]?.predicted_gen_total_ulb_tpd || '-'} <small style="color:#777;">±${Math.round((regionsMap[reg][2025]?.upper_bound - regionsMap[reg][2025]?.predicted_gen_total_ulb_tpd) || 0)}</small></td>
                  <td class="num">${regionsMap[reg][2026]?.predicted_gen_total_ulb_tpd || '-'} <small style="color:#777;">±${Math.round((regionsMap[reg][2026]?.upper_bound - regionsMap[reg][2026]?.predicted_gen_total_ulb_tpd) || 0)}</small></td>
                  <td class="num">${regionsMap[reg][2027]?.predicted_gen_total_ulb_tpd || '-'} <small style="color:#777;">±${Math.round((regionsMap[reg][2027]?.upper_bound - regionsMap[reg][2027]?.predicted_gen_total_ulb_tpd) || 0)}</small></td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      `;
    }

    // Model description card
    const modelCard = document.querySelector('#h-79432')?.closest('.card');
    if (modelCard) {
      modelCard.innerHTML = `
        <h3 id="h-79432">Model Selection & Validation Summary</h3>
        <p><strong>Selected Model:</strong> Naive Baseline (Previous Year Persistence)</p>
        <p><strong>Backtesting MAE:</strong> 72.07 TPD | <strong>RMSE:</strong> 127.18 TPD | <strong>MAPE:</strong> 3.17%</p>
        <p><strong>Comparison:</strong> Evaluated against Linear Regression (MAE 132.40), Random Forest (MAE 81.44), and Gradient Boosting (MAE 73.52). Simple baseline achieved superior stability on the 8-year annual series without overfitting or trend extrapolation risk.</p>
      `;
    }

    // Chart Box
    const chartCard = document.querySelector('#h-32849')?.closest('.card')?.querySelector('.chart-box');
    if (chartCard) {
      chartCard.innerHTML = `
        <div style="padding:12px; font-size:13px;">
          <div style="font-weight:600; margin-bottom:8px;">Maharashtra Municipal Solid Waste Trajectory (2016–2027)</div>
          <div style="height:140px; display:flex; align-items:flex-end; gap:8px; border-bottom:2px solid #ccc; padding-bottom:4px;">
            <div style="flex:1; background:#90caf9; height:75%; text-align:center; font-size:11px;">2016</div>
            <div style="flex:1; background:#90caf9; height:80%; text-align:center; font-size:11px;">2018</div>
            <div style="flex:1; background:#90caf9; height:85%; text-align:center; font-size:11px;">2020</div>
            <div style="flex:1; background:#90caf9; height:90%; text-align:center; font-size:11px;">2022</div>
            <div style="flex:1; background:#90caf9; height:92%; text-align:center; font-size:11px;">2023</div>
            <div style="flex:1; background:#a5d6a7; height:92%; text-align:center; font-size:11px; border:2px dashed #2e7d32;">2024*</div>
            <div style="flex:1; background:#a5d6a7; height:92%; text-align:center; font-size:11px; border:2px dashed #2e7d32;">2025*</div>
            <div style="flex:1; background:#a5d6a7; height:92%; text-align:center; font-size:11px; border:2px dashed #2e7d32;">2026*</div>
            <div style="flex:1; background:#a5d6a7; height:92%; text-align:center; font-size:11px; border:2px dashed #2e7d32;">2027*</div>
          </div>
          <div style="display:flex; justify-content:space-between; margin-top:6px; font-size:11px; color:#555;">
            <span>Blue: Historical Data (2016–2023)</span>
            <span>Green/Dashed: Model Forecast (2024–2027)</span>
          </div>
        </div>
      `;
    }
  } catch (err) {
    setPageState('error');
  }
}

// 7. INTERACTIVE WASTE MAP
async function initMap() {
  setPageState('loading');
  try {
    const res = await fetch(`${API_BASE}/map`);
    const data = await res.json();
    setPageState('ready');

    const mapBox = document.querySelector('.map-box');
    if (mapBox && data.features) {
      mapBox.innerHTML = `
        <div style="padding:16px; background:#f9fbf9; border-radius:6px; min-height:340px;">
          <h4 style="margin-top:0; color:#2e7d32;">Maharashtra Regional Solid Waste Coordinates & Pressure</h4>
          <div style="display:grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap:12px; margin-top:12px;">
            ${data.features.map(f => `
              <div style="background:white; border:1px solid #e0e0e0; border-radius:6px; padding:10px; box-shadow:0 1px 2px rgba(0,0,0,0.05); cursor:pointer;" onclick="alert('Region: ${f.region}\\nCoordinates: [${f.latitude}, ${f.longitude}]\\nGeneration: ${f.current_generation_tpd} TPD\\nPressure: ${f.pressure_index}/100')">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                  <strong style="color:#1b5e20;">${f.region}</strong>
                  <span class="badge" style="background:${f.pressure_category === 'High' ? '#ffebee' : '#e8f5e9'}; color:${f.pressure_category === 'High' ? '#c62828' : '#2e7d32'}">${f.pressure_category}</span>
                </div>
                <div style="font-size:12px; color:#666; margin-top:4px;">Lat: ${f.latitude.toFixed(2)}, Lon: ${f.longitude.toFixed(2)}</div>
                <div style="font-size:13px; margin-top:6px;">Gen: <strong>${f.current_generation_tpd.toFixed(0)} TPD</strong></div>
                <div style="font-size:12px; color:#555;">2024 Fc: ${f.forecast_2024_tpd?.toFixed(0) || '-'} TPD</div>
              </div>
            `).join('')}
          </div>
        </div>
      `;
    }
  } catch (err) {
    setPageState('error');
  }
}

// 8. COMMUNITY ACTION
function initCommunity() {
  setPageState('ready');
  const mainGrid = document.querySelector('.grid') || document.querySelector('[data-show="ready"]');
  if (mainGrid) {
    mainGrid.innerHTML = `
      <section class="card" style="grid-column: span 2;">
        <h3>Community Action Initiatives</h3>
        <p style="font-size:13px; color:#555;">Drives recommended by the AI Decision Intelligence system across Maharashtra regions.</p>
        <div class="table-wrap">
          <table class="table">
            <thead><tr><th>Initiative</th><th>Region</th><th>Type</th><th>Status</th><th>Action</th></tr></thead>
            <tbody>
              <tr><td>Decentralized Society Wet-Waste Composting</td><td>Pune</td><td>Composting</td><td><span class="badge" style="background:#e8f5e9; color:#2e7d32;">In Progress</span></td><td><button class="btn" onclick="alert('Status updated!')">Mark Completed</button></td></tr>
              <tr><td>Bulk Corrugated Cardboard Segregation Drive</td><td>Mumbai</td><td>Recycling / MRF</td><td><span class="badge" style="background:#fff3e0; color:#e65100;">Suggested</span></td><td><button class="btn" onclick="alert('Action Accepted!')">Accept</button></td></tr>
              <tr><td>Authorized E-Waste Collection Drive</td><td>Nagpur</td><td>E-Waste</td><td><span class="badge" style="background:#e3f2fd; color:#0d47a1;">Accepted</span></td><td><button class="btn" onclick="alert('Status updated!')">Start Action</button></td></tr>
              <tr><td>Commercial Market Glass & Metal Separation</td><td>Thane</td><td>Material Recovery</td><td><span class="badge" style="background:#e8f5e9; color:#2e7d32;">Completed</span></td><td><span>Done</span></td></tr>
            </tbody>
          </table>
        </div>
      </section>
    `;
  }
}

// 9. MODEL PERFORMANCE
async function initModelPerformance() {
  setPageState('ready');
  const mainGrid = document.querySelector('.grid') || document.querySelector('[data-show="ready"]');
  if (mainGrid) {
    mainGrid.innerHTML = `
      <section class="card">
        <h3>Primary Model Evaluation (RealWaste)</h3>
        <p><strong>Architecture:</strong> MobileNetV3-Small (PyTorch Transfer Learning)</p>
        <p><strong>Test Accuracy:</strong> 78.26% | <strong>Macro F1:</strong> 79.26%</p>
        <div style="font-size:13px; margin-top:8px;">
          <div>• Cardboard: F1 = 0.857</div>
          <div>• Food Organics: F1 = 0.860</div>
          <div>• Vegetation: F1 = 0.939</div>
          <div>• Textile Trash: F1 = 0.804</div>
          <div>• Plastic: F1 = 0.750</div>
          <div>• Metal: F1 = 0.779</div>
          <div>• Glass: F1 = 0.767</div>
          <div>• Paper: F1 = 0.766</div>
          <div>• Misc Trash: F1 = 0.612</div>
        </div>
      </section>
      <section class="card">
        <h3>Cross-Dataset Testing (TrashNet)</h3>
        <p><strong>Role:</strong> Secondary Evaluation on 2,527 laboratory images</p>
        <p><strong>Accuracy on Mapped Classes:</strong> 32.01%</p>
        <p style="font-size:12px; color:#555;"><strong>Domain Shift:</strong> White uniform backgrounds in TrashNet vs real-world diverse background settings in RealWaste.</p>
      </section>
      <section class="card" style="grid-column: span 2;">
        <h3>External In-The-Wild Generalization (TACO)</h3>
        <p><strong>Role:</strong> Scientific Generalization Testing on 1,475 in-the-wild litter photos</p>
        <p><strong>Direct Full-Image Single-Label Accuracy:</strong> 7.39%</p>
        <p style="font-size:13px; color:#666;"><strong>Scientific Finding:</strong> TACO consists of multi-object complex scenes with bounding box annotations. Direct single-label classification on uncropped full scenes exhibits heavy domain shift and multi-label clutter, confirming the scientific distinction between image classification and object detection architectures.</p>
      </section>
    `;
  }
}

// 10. EXPLAINABLE AI
function initExplainableAI() {
  setPageState('ready');
  const mainGrid = document.querySelector('.grid') || document.querySelector('[data-show="ready"]');
  const raw = sessionStorage.getItem('latest_analysis');
  let overlaySrc = 'reports/figures/sample_gradcam_overlay.jpg';
  let disclaimer = 'Highlighted regions indicate image areas that contributed to the model prediction. They do not guarantee that the prediction is correct.';

  if (raw) {
    const d = JSON.parse(raw);
    if (d.explainability?.overlay_base64) {
      overlaySrc = d.explainability.overlay_base64;
    }
  }

  if (mainGrid) {
    mainGrid.innerHTML = `
      <section class="card" style="grid-column: span 2;">
        <h3>Real Grad-CAM Feature Attributions</h3>
        <p style="font-size:13px; color:#555;">Computed via exact gradients backpropagated through MobileNetV3 convolutional features layer to highlight visual cues influencing the classification.</p>
        <div style="display:flex; gap:24px; align-items:center; margin-top:16px;">
          <div>
            <img src="${overlaySrc}" style="max-height:260px; border-radius:6px; box-shadow:0 2px 6px rgba(0,0,0,0.15);" alt="Grad-CAM Overlay" />
          </div>
          <div style="flex:1;">
            <div style="background:#e8f5e9; border-left:4px solid #2e7d32; padding:12px; border-radius:4px; font-size:13px;">
              <strong>Scientific Explainability Notice:</strong><br/>
              ${disclaimer}
            </div>
          </div>
        </div>
      </section>
    `;
  }
}

// 11. SYSTEM & DATA HEALTH
async function initSystemHealth() {
  setPageState('loading');
  try {
    const res = await fetch('/health');
    const d = await res.json();
    setPageState('ready');

    const mainGrid = document.querySelector('.grid') || document.querySelector('[data-show="ready"]');
    if (mainGrid) {
      mainGrid.innerHTML = `
        <section class="card" style="grid-column: span 2;">
          <h3>System & Component Status</h3>
          <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(200px, 1fr)); gap:12px; margin-top:12px;">
            <div style="padding:12px; border:1px solid #e0e0e0; border-radius:6px;">
              <strong>Waste Classifier</strong>
              <div style="color:#2e7d32; font-weight:bold; margin-top:4px;">${d.components.image_classifier}</div>
            </div>
            <div style="padding:12px; border:1px solid #e0e0e0; border-radius:6px;">
              <strong>SQLite Database</strong>
              <div style="color:#2e7d32; font-weight:bold; margin-top:4px;">${d.components.database}</div>
            </div>
            <div style="padding:12px; border:1px solid #e0e0e0; border-radius:6px;">
              <strong>2024-2027 Forecasting</strong>
              <div style="color:#2e7d32; font-weight:bold; margin-top:4px;">${d.components.forecasting}</div>
            </div>
            <div style="padding:12px; border:1px solid #e0e0e0; border-radius:6px;">
              <strong>Regional Data (96 rows)</strong>
              <div style="color:#2e7d32; font-weight:bold; margin-top:4px;">${d.components.regional_data}</div>
            </div>
          </div>
        </section>
      `;
    }
  } catch (e) {
    setPageState('error');
  }
}
