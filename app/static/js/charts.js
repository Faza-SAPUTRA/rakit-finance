(async function () {
  const chartIds = ["spendingChart", "portfolioChart", "riskGauge"];
  if (!chartIds.some((id) => document.getElementById(id))) return;
  if (!window.Chart) return;

  const response = await fetch("/api/analytics/charts");
  if (!response.ok) return;
  const payload = await response.json();
  const colors = ["#0F5C3F", "#2ECC71", "#8FD5B0", "#0A0A0A", "#8A9A92"];

  const spending = document.getElementById("spendingChart");
  if (spending) {
    new Chart(spending, {
      type: "doughnut",
      data: { labels: payload.spending.labels, datasets: [{ data: payload.spending.values, backgroundColor: colors, borderWidth: 0 }] },
      options: { plugins: { legend: { position: "bottom" } }, cutout: "68%" },
    });
  }

  const portfolio = document.getElementById("portfolioChart");
  if (portfolio) {
    new Chart(portfolio, {
      type: "doughnut",
      data: { labels: payload.portfolio.labels, datasets: [{ data: payload.portfolio.values, backgroundColor: colors.slice(0, 3), borderWidth: 0 }] },
      options: { plugins: { legend: { position: "bottom" } }, cutout: "62%" },
    });
  }

  const gauge = document.getElementById("riskGauge");
  if (gauge) {
    const score = payload.risk.score;
    document.getElementById("risk-score").textContent = score;
    new Chart(gauge, {
      type: "doughnut",
      data: { labels: ["Risk", "Buffer"], datasets: [{ data: [score, 100 - score], backgroundColor: ["#0F5C3F", "#E1E3E2"], borderWidth: 0 }] },
      options: { rotation: -90, circumference: 180, cutout: "75%", plugins: { legend: { display: false } } },
    });
  }
})();

