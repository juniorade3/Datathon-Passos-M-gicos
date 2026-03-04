/* ============================================================
   Passos Mágicos — Frontend JavaScript
   Integração com API: POST /predict e GET /drift
   ============================================================ */

const API_BASE = window.location.origin;

// =====================================================================
//  DOM Elements
// =====================================================================
const form = document.getElementById('form-predicao');
const btnPredict = document.getElementById('btn-predict');
const cardResultado = document.getElementById('card-resultado');
const statusBadge = document.getElementById('status-badge');
const statusIcon = document.getElementById('status-icon');
const statusText = document.getElementById('status-text');
const probCircle = document.getElementById('prob-circle');
const probValue = document.getElementById('prob-value');
const detailClass = document.getElementById('detail-class');
const detailConfidence = document.getElementById('detail-confidence');
const driftTableBody = document.getElementById('drift-table-body');
const btnRefresh = document.getElementById('btn-refresh');

// Stats
const statTotal = document.getElementById('stat-total');
const statTaxaRisco = document.getElementById('stat-taxa-risco');
const statProbMedia = document.getElementById('stat-prob-media');
const statProbStd = document.getElementById('stat-prob-std');

// Tabs
const tabPredicao = document.getElementById('tab-predicao');
const tabMonitoramento = document.getElementById('tab-monitoramento');
const sectionPredicao = document.getElementById('section-predicao');
const sectionMonitoramento = document.getElementById('section-monitoramento');

// Toast
const toast = document.getElementById('toast');
const toastIcon = document.getElementById('toast-icon');
const toastMessage = document.getElementById('toast-message');

// =====================================================================
//  Tab Navigation
// =====================================================================
function switchTab(tab) {
    // Remove active from all
    document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(s => s.classList.remove('active'));

    if (tab === 'predicao') {
        tabPredicao.classList.add('active');
        sectionPredicao.classList.add('active');
    } else {
        tabMonitoramento.classList.add('active');
        sectionMonitoramento.classList.add('active');
        fetchDrift();
    }
}

tabPredicao.addEventListener('click', () => switchTab('predicao'));
tabMonitoramento.addEventListener('click', () => switchTab('monitoramento'));

// =====================================================================
//  Toast Notifications
// =====================================================================
let toastTimeout = null;

function showToast(message, icon = '✅', duration = 3500) {
    if (toastTimeout) clearTimeout(toastTimeout);
    toastIcon.textContent = icon;
    toastMessage.textContent = message;
    toast.classList.add('show');
    toastTimeout = setTimeout(() => {
        toast.classList.remove('show');
    }, duration);
}

// =====================================================================
//  Form Validation
// =====================================================================
function validateForm() {
    const inputs = form.querySelectorAll('input[required]');
    let valid = true;

    inputs.forEach(input => {
        const group = input.closest('.form-group');
        const val = parseFloat(input.value);

        if (input.value === '' || isNaN(val)) {
            group.classList.add('has-error');
            valid = false;
        } else if (val < parseFloat(input.min) || val > parseFloat(input.max)) {
            group.classList.add('has-error');
            valid = false;
        } else {
            group.classList.remove('has-error');
        }
    });

    return valid;
}

// Remove error on input
form.querySelectorAll('input').forEach(input => {
    input.addEventListener('input', () => {
        input.closest('.form-group').classList.remove('has-error');
    });
});

// =====================================================================
//  Prediction API
// =====================================================================
async function submitPrediction(e) {
    e.preventDefault();

    if (!validateForm()) {
        showToast('Preencha todos os campos corretamente', '⚠️');
        return;
    }

    // Collect data
    const payload = {};
    const formData = new FormData(form);
    formData.forEach((value, key) => {
        payload[key] = parseFloat(value);
    });

    // Loading state
    btnPredict.classList.add('loading');
    btnPredict.disabled = true;

    try {
        const response = await fetch(`${API_BASE}/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || `Erro ${response.status}`);
        }

        const data = await response.json();
        displayResult(data);
        showToast('Análise realizada com sucesso!', '✅');

    } catch (error) {
        console.error('Erro na predição:', error);
        showToast(`Erro: ${error.message}`, '❌', 5000);
    } finally {
        btnPredict.classList.remove('loading');
        btnPredict.disabled = false;
    }
}

form.addEventListener('submit', submitPrediction);

// =====================================================================
//  Display Result
// =====================================================================
function displayResult(data) {
    // Show card with animation
    cardResultado.style.display = '';
    cardResultado.classList.remove('animate-in');
    void cardResultado.offsetWidth; // Force reflow
    cardResultado.classList.add('animate-in');

    const isRisco = data.previsao === 1;
    const prob = data.probabilidade_risco;
    const probPercent = Math.round(prob * 100);

    // Status badge
    statusBadge.className = `status-badge ${isRisco ? 'com-risco' : 'sem-risco'}`;
    statusIcon.textContent = isRisco ? '🚨' : '✅';
    statusText.textContent = data.status;
    statusText.style.color = isRisco ? 'var(--danger)' : 'var(--success)';

    // Probability ring
    const circumference = 2 * Math.PI * 54; // r=54
    const offset = circumference - (prob * circumference);
    probCircle.className = `prob-fill ${isRisco ? 'com-risco' : 'sem-risco'}`;
    // Animate from full offset (initially reset for animation)
    probCircle.style.strokeDashoffset = circumference;
    requestAnimationFrame(() => {
        requestAnimationFrame(() => {
            probCircle.style.strokeDashoffset = offset;
        });
    });

    // Animate percentage counter
    animateCounter(probValue, 0, probPercent, '%', 1000);

    // Details
    detailClass.textContent = data.status;
    detailClass.style.color = isRisco ? 'var(--danger)' : 'var(--success)';

    const confidence = isRisco ? prob : (1 - prob);
    const confPercent = Math.round(confidence * 100);
    detailConfidence.textContent = `${confPercent}%`;
    detailConfidence.style.color = confPercent >= 70 ? 'var(--success)' : confPercent >= 50 ? 'var(--warning)' : 'var(--danger)';

    // Scroll to result on mobile
    if (window.innerWidth < 900) {
        setTimeout(() => {
            cardResultado.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }, 200);
    }
}

// Animated counter
function animateCounter(element, from, to, suffix, duration) {
    const start = performance.now();
    function update(now) {
        const elapsed = now - start;
        const progress = Math.min(elapsed / duration, 1);
        // Ease out
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = Math.round(from + (to - from) * eased);
        element.textContent = `${current}${suffix}`;
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    requestAnimationFrame(update);
}

// =====================================================================
//  Drift / Monitoring
// =====================================================================
async function fetchDrift() {
    try {
        const response = await fetch(`${API_BASE}/drift`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        displayDrift(data);
    } catch (error) {
        console.error('Erro ao buscar drift:', error);
        showToast('Erro ao carregar dados de monitoramento', '❌');
    }
}

function displayDrift(data) {
    // Stats
    statTotal.textContent = data.total_predicoes ?? 0;

    if (data.total_predicoes === 0) {
        statTaxaRisco.textContent = '—';
        statProbMedia.textContent = '—';
        statProbStd.textContent = '—';
        driftTableBody.innerHTML = `
      <tr>
        <td colspan="6" class="empty-state">
          Nenhuma predição registrada ainda. Faça uma predição para ver os dados.
        </td>
      </tr>`;
        return;
    }

    statTaxaRisco.textContent = `${(data.taxa_risco * 100).toFixed(1)}%`;
    statProbMedia.textContent = `${(data.probabilidade_media_risco * 100).toFixed(1)}%`;
    statProbStd.textContent = data.probabilidade_std_risco?.toFixed(4) ?? '—';

    // Feature table
    if (!data.features) return;

    const featureLabels = {
        'Idade': 'Idade',
        'Ano ingresso': 'Ano Ingresso',
        'IAA': 'IAA (Auto Avaliação)',
        'IEG': 'IEG (Engajamento)',
        'IPS': 'IPS (Psicossocial)',
        'IDA': 'IDA (Desempenho)',
        'IPV': 'IPV (Ponto de Virada)',
        'Mat': 'Matemática',
        'Por': 'Português',
    };

    let rows = '';
    for (const [key, stats] of Object.entries(data.features)) {
        const label = featureLabels[key] || key;
        // Normalize bar: for scores 0-10 use max 10, for age/year use actual max
        let maxVal = 10;
        if (key === 'Idade') maxVal = 25;
        if (key === 'Ano ingresso') maxVal = 2030;

        let barWidth = 0;
        if (key === 'Ano ingresso') {
            barWidth = ((stats.media - 2000) / (2030 - 2000)) * 100;
        } else {
            barWidth = (stats.media / maxVal) * 100;
        }
        barWidth = Math.max(0, Math.min(100, barWidth));

        rows += `
      <tr>
        <td class="feature-name">${label}</td>
        <td>${stats.media.toFixed(2)}</td>
        <td>${stats.std.toFixed(2)}</td>
        <td>${stats.min.toFixed(2)}</td>
        <td>${stats.max.toFixed(2)}</td>
        <td>
          <div class="mini-bar">
            <div class="mini-bar-track">
              <div class="mini-bar-fill" style="width: ${barWidth}%"></div>
            </div>
            <span class="mini-bar-value">${stats.media.toFixed(1)}</span>
          </div>
        </td>
      </tr>`;
    }

    driftTableBody.innerHTML = rows;
}

// Refresh button
btnRefresh.addEventListener('click', () => {
    btnRefresh.classList.add('spinning');
    fetchDrift().finally(() => {
        setTimeout(() => btnRefresh.classList.remove('spinning'), 600);
    });
});

// =====================================================================
//  Init
// =====================================================================
// On page load, if on monitoring tab, fetch drift
document.addEventListener('DOMContentLoaded', () => {
    // Default tab is prediction, no fetch needed
});
