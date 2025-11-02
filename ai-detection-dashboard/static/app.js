// Fixed AI Detection & Evidence System JS Core
// NOTE: This version ensures JSON.parse issues are avoided and UI behavior is consistent

(() => {
  const data = {
    detectionTypes: [
      { id: "deepfake", name: "Deepfake Detection", description: "Detects manipulated content.", supported_formats: ["MP4", "JPG"], icon: "fas fa-video" },
      { id: "object", name: "Object Detection", description: "Identifies objects in media.", supported_formats: ["JPG", "PNG"], icon: "fas fa-eye" },
      { id: "fraud", name: "Fraud Detection", description: "Flags financial fraud.", supported_formats: ["CSV", "PDF"], icon: "fas fa-exclamation-triangle" }
    ],
    statistics: { total_detections: 0, deepfake_detections: 0, object_detections: 0, fraud_detections: 0, reports_generated: 0 },
    sampleDetections: [],
    evidenceReports: [],
    chartData: {
      activity_timeline: { labels: [], detections: [], reports: [] },
      detection_distribution: { labels: ["Deepfake", "Object", "Fraud"], data: [0, 0, 0] }
    }
  };

  let selectedFile = null;

  function formatConfidence(c) { return `${(c * 100).toFixed(1)}%`; }
  function formatDate(iso) { return new Date(iso).toLocaleString(); }
  function randomId() { return Math.random().toString(36).slice(2, 10); }

  function renderStats() {
    const grid = document.getElementById("statsGrid");
    if (!grid) return;
    const stats = [
      { label: "Total Detections", value: data.statistics.total_detections, icon: "fas fa-search" },
      { label: "Deepfake", value: data.statistics.deepfake_detections, icon: "fas fa-video" },
      { label: "Object", value: data.statistics.object_detections, icon: "fas fa-eye" },
      { label: "Fraud", value: data.statistics.fraud_detections, icon: "fas fa-exclamation-triangle" }
    ];
    grid.innerHTML = stats.map(s => `
      <div class="stat-card">
        <div><i class="${s.icon}"></i> <span>${s.value}</span></div>
        <div>${s.label}</div>
      </div>`).join('');
  }

  function renderDetectionsTable() {
    const tbody = document.querySelector("#detectionsTable tbody");
    if (!tbody) return;
    tbody.innerHTML = "";
    data.sampleDetections.forEach(d => {
      const reportExists = data.evidenceReports.some(r => r.detection_id === d.id);
      const row = tbody.insertRow();
      row.innerHTML = `
        <td>${d.id}</td><td>${d.type}</td><td>${d.filename}</td>
        <td>${formatConfidence(d.confidence)}</td><td>${formatDate(d.timestamp)}</td>
        <td><button class="action-btn" data-id="${d.id}" data-action="${reportExists ? "view" : "generate"}">${reportExists ? "View" : "Generate"}</button></td>`;
    });
  }

  function renderReportsTable() {
    const tbody = document.querySelector("#reportsTable tbody");
    if (!tbody) return;
    tbody.innerHTML = "";
    data.evidenceReports.forEach(r => {
      const row = tbody.insertRow();
      row.innerHTML = `
        <td>${r.id}</td><td>${r.type}</td><td>${formatDate(r.generated_at)}</td>
        <td>${r.status}</td><td><button class="download-btn" data-url="${r.pdfBlobUrl}">Download</button></td>`;
    });
  }

  function simulateAnalysis(type, file) {
    const progress = document.getElementById("progressBar");
    const result = document.getElementById("analysisResult");
    progress.value = 0;
    result.innerHTML = "";
    progress.classList.remove("hidden");

    let interval = setInterval(() => {
      progress.value += 10;
      if (progress.value >= 100) {
        clearInterval(interval);
        progress.classList.add("hidden");

        const detection = {
          id: Date.now(),
          type,
          filename: file.name,
          confidence: Math.random() * 0.3 + 0.7,
          timestamp: new Date().toISOString()
        };

        data.sampleDetections.unshift(detection);
        data.statistics.total_detections++;
        data.statistics[`${type}_detections`]++;

        renderStats();
        renderDetectionsTable();
        showAnalysisResult(detection);
      }
    }, 150);
  }

  function showAnalysisResult(det) {
    const el = document.getElementById("analysisResult");
    if (!el) return;
    el.innerHTML = `
      <div><strong>ID:</strong> ${det.id}</div>
      <div><strong>Type:</strong> ${det.type}</div>
      <div><strong>Confidence:</strong> ${formatConfidence(det.confidence)}</div>
      <button id="genReport">Generate Report</button>`;
    document.getElementById("genReport").onclick = () => generateReport(det);
  }

  function generateReport(detection) {
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();
    const reportId = `EVD-${randomId().toUpperCase()}`;

    doc.text("AI Detection Report", 10, 10);
    doc.text(`ID: ${detection.id}`, 10, 20);
    doc.text(`Type: ${detection.type}`, 10, 30);
    doc.text(`Confidence: ${formatConfidence(detection.confidence)}`, 10, 40);
    doc.text(`Timestamp: ${formatDate(detection.timestamp)}`, 10, 50);

    const blob = doc.output("blob");
    const url = URL.createObjectURL(blob);

    data.evidenceReports.unshift({ id: reportId, detection_id: detection.id, generated_at: new Date().toISOString(), type: detection.type, status: "verified", pdfBlobUrl: url });
    data.statistics.reports_generated++;

    renderReportsTable();
    renderDetectionsTable();
    window.open(url);
  }

  function initUI() {
    const select = document.getElementById("detectionType");
    const input = document.getElementById("fileInput");
    const btn = document.getElementById("analyzeBtn");
    if (!select || !input || !btn) return;

    data.detectionTypes.forEach(d => {
      const opt = document.createElement("option");
      opt.value = d.id;
      opt.textContent = d.name;
      select.appendChild(opt);
    });

    input.addEventListener("change", e => {
      selectedFile = e.target.files[0];
      btn.disabled = !(selectedFile && select.value);
    });
    select.addEventListener("change", () => {
      btn.disabled = !(selectedFile && select.value);
    });
    btn.addEventListener("click", () => {
      simulateAnalysis(select.value, selectedFile);
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    renderStats();
    renderDetectionsTable();
    renderReportsTable();
    initUI();

    // Secret hotkey: Shift+Alt+Enter to show author name
   document.addEventListener("keydown", function(e) {
  if (e.shiftKey && e.altKey && (e.key === "Enter" || e.code === "Enter")) {
    alert("Author: Akshat Jasrotia\nGithub: akshatjasrotia85");
  }
});

    document.body.addEventListener("click", e => {
      if (e.target.classList.contains("action-btn")) {
        const id = +e.target.dataset.id;
        const det = data.sampleDetections.find(d => d.id === id);
        if (!det) return;
        if (e.target.dataset.action === "generate") generateReport(det);
        else {
          const rep = data.evidenceReports.find(r => r.detection_id === det.id);
          if (rep) window.open(rep.pdfBlobUrl);
        }
      }

      if (e.target.classList.contains("download-btn")) {
        const url = e.target.dataset.url;
        if (url) window.open(url);
      }
    });
  });
})();