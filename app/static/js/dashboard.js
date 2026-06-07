const activityGrid = document.getElementById("activity-grid");
const recentLogsBody = document.getElementById("recent-logs-body");

const summaryIds = {
  totalAnswered: document.getElementById("summary-total-answered"),
  done: document.getElementById("summary-done"),
  notDone: document.getElementById("summary-not-done"),
  postponed: document.getElementById("summary-postponed"),
  completionRate: document.getElementById("summary-completion-rate"),
  lastUpdated: document.getElementById("last-updated"),
};

let summaryChart;

const statusClassMap = {
  done: "status-done",
  not_done: "status-not_done",
  postponed: "status-postponed",
  sent: "status-sent",
  error: "status-error",
};

async function loadDashboard() {
  try {
    const response = await fetch("/api/dashboard/metrics");
    const data = await response.json();
    renderSummary(data.summary);
    renderSummaryChart(data.summary);
    renderActivities(data.activities || []);
    renderRecentLogs(data.recent_logs || []);
    summaryIds.lastUpdated.textContent = new Date().toLocaleString("pt-BR");
  } catch (_error) {
    summaryIds.lastUpdated.textContent = "Falha ao carregar dados";
    recentLogsBody.innerHTML =
      '<tr><td colspan="4" class="empty-state">Nao foi possivel carregar o dashboard.</td></tr>';
  }
}

function renderSummary(summary) {
  summaryIds.totalAnswered.textContent = summary.total_answered ?? 0;
  summaryIds.done.textContent = summary.done ?? 0;
  summaryIds.notDone.textContent = summary.not_done ?? 0;
  summaryIds.postponed.textContent = summary.postponed ?? 0;
  summaryIds.completionRate.textContent = `${formatPercentage(summary.completion_rate)}%`;
}

function renderSummaryChart(summary) {
  const ctx = document.getElementById("summary-doughnut-chart");
  const data = [summary.done ?? 0, summary.not_done ?? 0, summary.postponed ?? 0];
  if (summaryChart) {
    summaryChart.destroy();
  }
  summaryChart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: ["Feitos", "Nao feitos", "Adiados"],
      datasets: [
        {
          data,
          backgroundColor: ["#34d399", "#fb7185", "#fbbf24"],
          borderColor: "rgba(255,255,255,0.08)",
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          labels: {
            color: "#f4f7fb",
            font: { family: "Inter" },
          },
        },
      },
    },
  });
}

function renderActivities(activities) {
  activityGrid.innerHTML = "";

  if (!activities.length) {
    activityGrid.innerHTML =
      '<article class="activity-card glass-card"><p class="empty-state">Nenhuma atividade encontrada.</p></article>';
    return;
  }

  activities.forEach((activity, index) => {
    const card = document.createElement("article");
    card.className = "activity-card glass-card";
    card.innerHTML = `
      <div class="activity-header">
        <div>
          <p class="section-tag">Atividade ${String(index + 1).padStart(2, "0")}</p>
          <h3>${escapeHtml(activity.title)}</h3>
        </div>
        <span class="activity-rate">${formatPercentage(activity.completion_rate)}%</span>
      </div>
      <div class="activity-stats">
        <div><span>Feitos</span><strong>${activity.done ?? 0}</strong></div>
        <div><span>Nao feitos</span><strong>${activity.not_done ?? 0}</strong></div>
        <div><span>Adiados</span><strong>${activity.postponed ?? 0}</strong></div>
      </div>
      <div class="chart-wrapper">
        <canvas id="activity-chart-${index}"></canvas>
      </div>
    `;
    activityGrid.appendChild(card);

    const ctx = card.querySelector("canvas");
    new Chart(ctx, {
      type: "bar",
      data: {
        labels: ["Feitos", "Nao feitos", "Adiados"],
        datasets: [
          {
            data: [activity.done ?? 0, activity.not_done ?? 0, activity.postponed ?? 0],
            backgroundColor: ["#34d399", "#fb7185", "#fbbf24"],
            borderRadius: 10,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: { ticks: { color: "#9eb0c7" }, grid: { display: false } },
          y: {
            beginAtZero: true,
            ticks: { color: "#9eb0c7", precision: 0 },
            grid: { color: "rgba(255,255,255,0.08)" },
          },
        },
        plugins: { legend: { display: false } },
      },
    });
  });
}

function renderRecentLogs(logs) {
  if (!logs.length) {
    recentLogsBody.innerHTML =
      '<tr><td colspan="4" class="empty-state">Nenhum log recente encontrado.</td></tr>';
    return;
  }

  recentLogsBody.innerHTML = logs
    .map(
      (log) => `
      <tr>
        <td>${escapeHtml(log.title)}</td>
        <td><span class="status-pill ${statusClassMap[log.status] ?? "status-sent"}">${escapeHtml(log.status)}</span></td>
        <td>${escapeHtml(formatDateTime(log.created_at))}</td>
        <td>${escapeHtml(log.message || "-")}</td>
      </tr>
    `
    )
    .join("");
}

function formatPercentage(value) {
  return Number(value ?? 0).toFixed(2).replace(/\.00$/, "");
}

function formatDateTime(value) {
  if (!value) return "";
  return new Date(value).toLocaleString("pt-BR");
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

loadDashboard();
