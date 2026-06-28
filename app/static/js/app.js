(function () {
  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/static/service-worker.js").catch(() => {});
  }

  document.getElementById("theme-toggle")?.addEventListener("click", () => {
    document.documentElement.classList.toggle("dark");
  });

  const mobileSidebar = document.getElementById("mobile-sidebar");
  const openMobileSidebar = () => mobileSidebar?.classList.remove("hidden");
  const closeMobileSidebar = () => mobileSidebar?.classList.add("hidden");
  document.getElementById("mobile-sidebar-open")?.addEventListener("click", openMobileSidebar);
  document.getElementById("mobile-sidebar-close")?.addEventListener("click", closeMobileSidebar);
  document.getElementById("mobile-sidebar-backdrop")?.addEventListener("click", closeMobileSidebar);

  const search = document.getElementById("table-search");
  search?.addEventListener("input", () => {
    const term = search.value.toLowerCase();
    document.querySelectorAll("#transaction-table tr").forEach((row) => {
      row.hidden = !row.textContent.toLowerCase().includes(term);
    });
  });

  const dropZone = document.getElementById("drop-zone");
  if (dropZone) {
    ["dragenter", "dragover"].forEach((eventName) => dropZone.addEventListener(eventName, (event) => {
      event.preventDefault();
      dropZone.classList.add("is-dragging");
    }));
    ["dragleave", "drop"].forEach((eventName) => dropZone.addEventListener(eventName, () => dropZone.classList.remove("is-dragging")));
    dropZone.addEventListener("drop", (event) => {
      event.preventDefault();
      dropZone.querySelector("input").files = event.dataTransfer.files;
    });
  }

  let importRows = [];
  document.getElementById("import-form")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const preview = document.getElementById("import-preview");
    preview.textContent = "Parsing file...";
    const response = await fetch("/api/import/preview", { method: "POST", body: new FormData(event.currentTarget) });
    const payload = await response.json();
    if (!response.ok) {
      preview.textContent = payload.error || "Import failed.";
      return;
    }
    importRows = payload.transactions;
    preview.innerHTML = importRows.map((tx) => `<div class="flex justify-between border-b border-line py-3"><span><strong>${tx.merchant}</strong><br><small>${tx.occurred_on} · ${tx.source}</small></span><strong>Rp ${(tx.amount_cents / 100).toLocaleString("id-ID")}</strong></div>`).join("");
    document.getElementById("confirm-import").disabled = importRows.length === 0;
  });

  document.getElementById("confirm-import")?.addEventListener("click", async () => {
    const response = await fetch("/api/import/confirm", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ transactions: importRows }),
    });
    const payload = await response.json();
    document.getElementById("import-preview").textContent = `Saved ${payload.created || 0} imported transactions.`;
  });

  document.getElementById("receipt-form")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const result = document.getElementById("receipt-result");
    result.textContent = "Scanning receipt...";
    const response = await fetch("/api/receipt/scan", { method: "POST", body: new FormData(event.currentTarget) });
    const payload = await response.json();
    result.innerHTML = `
      <div class="grid gap-4">
        <label class="font-bold">Merchant<input id="receipt-merchant" class="mt-2 w-full rounded-2xl border-line" value="${payload.merchant || ""}"></label>
        <label class="font-bold">Amount<input id="receipt-amount" class="mt-2 w-full rounded-2xl border-line" type="number" value="${Math.round((payload.amount_cents || 0) / 100)}"></label>
        <label class="font-bold">Date<input id="receipt-date" class="mt-2 w-full rounded-2xl border-line" type="date" value="${payload.occurred_on || ""}"></label>
        <button id="save-receipt" class="rounded-full bg-primary py-3 font-extrabold text-white">Save transaction</button>
      </div>`;
    document.getElementById("save-receipt").addEventListener("click", async () => {
      await fetch("/api/receipt/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          merchant: document.getElementById("receipt-merchant").value,
          amount_cents: Number(document.getElementById("receipt-amount").value) * 100,
          occurred_on: document.getElementById("receipt-date").value,
          category: "Receipts",
        }),
      });
      result.textContent = "Receipt transaction saved.";
    });
  });

  document.getElementById("investment-form")?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(event.currentTarget).entries());
    const response = await fetch("/api/investment/project", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    const payload = await response.json();
    window.renderInvestmentChart?.(payload);
  });

  window.renderInvestmentChart = function (payload) {
    const canvas = document.getElementById("investmentChart");
    if (!canvas || !window.Chart) return;
    if (window.investmentChart) window.investmentChart.destroy();
    document.getElementById("investment-risk").textContent = payload.risk;
    window.investmentChart = new Chart(canvas, {
      type: "line",
      data: {
        labels: payload.projection.map((row) => `Year ${row.year}`),
        datasets: [{ label: payload.instrument, data: payload.projection.map((row) => Math.round(row.value_cents / 100)), borderColor: "#0F5C3F", backgroundColor: "rgba(46,204,113,.12)", fill: true, tension: 0.38 }],
      },
      options: { plugins: { legend: { display: false } }, scales: { y: { ticks: { callback: (value) => `Rp ${Number(value).toLocaleString("id-ID")}` } } } },
    });
  };

  document.getElementById("investment-form")?.dispatchEvent(new Event("submit"));
})();
