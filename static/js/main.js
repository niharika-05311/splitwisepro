/**
 * main.js
 * -------
 * Client-side logic for SplitWise Pro:
 *   - Sidebar toggle (mobile)
 *   - Chart.js dashboard charts
 *   - Balance bar chart (settlements page)
 *   - Auto-dismiss flash messages
 */

// ── Sidebar toggle ───────────────────────────────────────────────
(function () {
  const sidebar  = document.getElementById('sidebar');
  const overlay  = document.getElementById('sidebarOverlay');
  const hamburger= document.getElementById('hamburger');
  const closeBtn = document.getElementById('sidebarClose');

  function open()  { sidebar.classList.add('open');  overlay.classList.add('open');  }
  function close() { sidebar.classList.remove('open'); overlay.classList.remove('open'); }

  if (hamburger) hamburger.addEventListener('click', open);
  if (closeBtn)  closeBtn .addEventListener('click', close);
  if (overlay)   overlay  .addEventListener('click', close);
})();

// ── Auto-dismiss flash messages ───────────────────────────────────
setTimeout(() => {
  document.querySelectorAll('.flash').forEach(el => {
    el.style.transition = 'opacity 0.5s';
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 500);
  });
}, 4000);


// ── Chart defaults ────────────────────────────────────────────────
function applyChartDefaults() {
  // Shared Chart.js global defaults
  const defaults = {
    color: '#9aa0b4',
    font: { family: "'DM Sans', sans-serif", size: 12 },
  };
  if (typeof Chart !== 'undefined') {
    Chart.defaults.color = defaults.color;
    Chart.defaults.font  = defaults.font;
    Chart.defaults.plugins.legend.labels.boxWidth  = 10;
    Chart.defaults.plugins.legend.labels.padding   = 16;
    Chart.defaults.plugins.tooltip.backgroundColor = '#1a1e28';
    Chart.defaults.plugins.tooltip.borderColor     = '#252a38';
    Chart.defaults.plugins.tooltip.borderWidth     = 1;
    Chart.defaults.plugins.tooltip.padding         = 10;
    Chart.defaults.plugins.tooltip.titleColor      = '#e8eaf0';
    Chart.defaults.plugins.tooltip.bodyColor       = '#9aa0b4';
  }
}
applyChartDefaults();


// ── Dashboard charts ──────────────────────────────────────────────
/**
 * initDashboardCharts
 * @param {Array} categoryData  [{category, total}, ...]
 * @param {Array} userData      [{name, total}, ...]
 */
function initDashboardCharts(categoryData, userData) {
  if (typeof Chart === 'undefined') return;

  // Colour palette for slices / bars
  const PALETTE = [
    '#6c8ef0', '#2dd4bf', '#fbbf24',
    '#fb7185', '#a78bfa', '#4ade80',
    '#38bdf8', '#f97316',
  ];

  // 1. Doughnut — by category
  const catCtx = document.getElementById('categoryChart');
  if (catCtx && categoryData.length) {
    new Chart(catCtx, {
      type: 'doughnut',
      data: {
        labels: categoryData.map(d => d.category),
        datasets: [{
          data: categoryData.map(d => d.total),
          backgroundColor: PALETTE,
          borderColor: '#13161e',
          borderWidth: 3,
          hoverOffset: 6,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '68%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: { usePointStyle: true, pointStyle: 'circle' }
          },
          tooltip: {
            callbacks: {
              label: ctx => ` ₹${ctx.parsed.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`,
            }
          }
        }
      }
    });
  } else if (catCtx) {
    showEmptyChart(catCtx, 'No expenses yet');
  }

  // 2. Horizontal bar — per user
  const userCtx = document.getElementById('userChart');
  if (userCtx && userData.length) {
    new Chart(userCtx, {
      type: 'bar',
      data: {
        labels: userData.map(d => d.name),
        datasets: [{
          label: 'Total Paid (₹)',
          data: userData.map(d => d.total),
          backgroundColor: PALETTE.slice(0, userData.length).map(c => c + 'cc'),
          borderColor: PALETTE.slice(0, userData.length),
          borderWidth: 1.5,
          borderRadius: 5,
          borderSkipped: false,
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: 'y',
        plugins: { legend: { display: false } },
        scales: {
          x: {
            grid:  { color: '#252a38' },
            ticks: {
              callback: v => '₹' + v.toLocaleString('en-IN'),
            }
          },
          y: { grid: { display: false } }
        }
      }
    });
  } else if (userCtx) {
    showEmptyChart(userCtx, 'No data yet');
  }
}


// ── Balance chart (settlements page) ─────────────────────────────
/**
 * initBalanceChart
 * @param {Object} balanceData  {uid: {name, balance}, ...}
 */
function initBalanceChart(balanceData) {
  if (typeof Chart === 'undefined') return;

  const ctx = document.getElementById('balanceChart');
  if (!ctx) return;

  const entries = Object.values(balanceData);
  if (!entries.length) return;

  const labels = entries.map(e => e.name);
  const values = entries.map(e => e.balance);
  const colors = values.map(v =>
    v > 0  ? '#4ade8099' :
    v < 0  ? '#fb718599' :
             '#5c638099'
  );
  const borders = values.map(v =>
    v > 0  ? '#4ade80' :
    v < 0  ? '#fb7185' :
             '#5c6380'
  );

  new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [{
        label: 'Net Balance (₹)',
        data: values,
        backgroundColor: colors,
        borderColor: borders,
        borderWidth: 1.5,
        borderRadius: 5,
        borderSkipped: false,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { grid: { display: false } },
        y: {
          grid: { color: '#252a38' },
          ticks: { callback: v => '₹' + v.toLocaleString('en-IN') }
        }
      }
    }
  });
}


// ── Helper: empty chart placeholder ──────────────────────────────
function showEmptyChart(ctx, message) {
  // Draw centred text on canvas when no data exists
  const c  = ctx.getContext('2d');
  const w  = ctx.parentElement.offsetWidth  || 300;
  const h  = ctx.parentElement.offsetHeight || 240;
  ctx.width  = w;
  ctx.height = h;
  c.fillStyle = '#5c6380';
  c.font      = "14px 'DM Sans', sans-serif";
  c.textAlign = 'center';
  c.fillText(message, w / 2, h / 2);
}
