/**
 * PhishGuard Frontend Application Logic
 */

document.addEventListener("DOMContentLoaded", () => {
  const scanForm = document.getElementById("scanForm");
  const urlInput = document.getElementById("urlInput");
  const btnScan = document.getElementById("btnScan");
  const btnText = document.getElementById("btnText");
  const btnSpinner = document.getElementById("btnSpinner");

  const loadingBox = document.getElementById("loadingBox");
  const errorBox = document.getElementById("errorBox");
  const errorMessage = document.getElementById("errorMessage");

  const resultContainer = document.getElementById("resultContainer");
  const resultHeader = document.getElementById("resultHeader");
  const resultIcon = document.getElementById("resultIcon");
  const resultTitle = document.getElementById("resultTitle");
  const resultSubtitle = document.getElementById("resultSubtitle");
  const resultScore = document.getElementById("resultScore");
  const resultScoreCaption = document.getElementById("resultScoreCaption");
  const resultUrl = document.getElementById("resultUrl");
  const reasonsList = document.getElementById("reasonsList");
  const resultDisclaimer = document.getElementById("resultDisclaimer");
  const modelVersionPill = document.getElementById("modelVersionPill");
  const headerVersionText = document.getElementById("headerVersionText");

  // Fetch model metadata on page load
  async function loadModelInfo() {
    try {
      const res = await fetch("/api/model-info");
      if (res.ok) {
        const data = await res.json();
        if (headerVersionText) {
          headerVersionText.textContent = `Model v${data.model_version} (${data.model_name})`;
        }
      }
    } catch (e) {
      console.warn("Could not load model info:", e);
    }
  }
  loadModelInfo();

  // Preset example chips
  const exampleChips = document.querySelectorAll(".example-chip");
  exampleChips.forEach((chip) => {
    chip.addEventListener("click", () => {
      const sampleUrl = chip.getAttribute("data-url");
      if (sampleUrl) {
        urlInput.value = sampleUrl;
        triggerScan(sampleUrl);
      }
    });
  });

  // Handle Form Submission
  scanForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const url = urlInput.value.trim();
    if (!url) {
      showError("Silakan masukkan URL yang ingin diperiksa.");
      return;
    }
    triggerScan(url);
  });

  async function triggerScan(url) {
    clearUI();
    setLoading(true);

    try {
      const response = await fetch("/api/check", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || `Terjadi kesalahan (HTTP ${response.status})`);
      }

      displayResult(data);
    } catch (err) {
      showError(err.message || "Gagal menghubungi server deteksi. Pastikan server API berjalan.");
    } finally {
      setLoading(false);
    }
  }

  function displayResult(data) {
    const risk = (data.risk_level || "low").toLowerCase();
    const scorePct = (data.score * 100).toFixed(1);

    // Reset header classes
    resultHeader.className = "result-header";

    if (risk === "high") {
      resultHeader.classList.add("risk-high");
      resultIcon.innerHTML = `
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
      `;
      resultTitle.textContent = "RISIKO TINGGI (BAHAYA PHISHING)";
      resultSubtitle.textContent = "Tautan ini memiliki karakteristik kuat sebagai situs penipuan / pencurian kredensial.";
      resultScore.textContent = `${scorePct}%`;
      resultScoreCaption.textContent = "Probabilitas Phishing";
    } else if (risk === "medium") {
      resultHeader.classList.add("risk-medium");
      resultIcon.innerHTML = `
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="12"/>
          <line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
      `;
      resultTitle.textContent = "RISIKO SEDANG (MENCURIGAKAN)";
      resultSubtitle.textContent = "Ditemukan beberapa indikator anomali pada struktur URL. Periksa keaslian domain secara teliti.";
      resultScore.textContent = `${scorePct}%`;
      resultScoreCaption.textContent = "Probabilitas Phishing";
    } else {
      resultHeader.classList.add("risk-low");
      resultIcon.innerHTML = `
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          <polyline points="9 12 11 14 15 10"/>
        </svg>
      `;
      resultTitle.textContent = "RISIKO RENDAH (TERLIHAT AMAN)";
      resultSubtitle.textContent = "Tidak ditemukan pola manipulasi nama domain atau kata kunci penipuan mencurigakan.";
      resultScore.textContent = `${scorePct}%`;
      resultScoreCaption.textContent = "Probabilitas Phishing";
    }

    // STRICT RULE: URL displayed as plaintext ONLY (NEVER as clickable <a> tag)
    resultUrl.textContent = data.url;

    // Populate reasons
    reasonsList.innerHTML = "";
    if (data.reasons && data.reasons.length > 0) {
      data.reasons.forEach((reason) => {
        const li = document.createElement("li");
        li.innerHTML = `
          <span class="reason-bullet">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <polyline points="9 18 15 12 9 6"/>
            </svg>
          </span>
          <span>${escapeHTML(reason)}</span>
        `;
        reasonsList.appendChild(li);
      });
    }

    resultDisclaimer.textContent = data.disclaimer || "Hasil ini perkiraan berbasis model machine learning, bukan jaminan.";
    if (modelVersionPill) {
      modelVersionPill.textContent = `Versi Model: ${data.model_version || "1.0.0"}`;
    }

    resultContainer.style.display = "block";
    resultContainer.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  function setLoading(isLoading) {
    btnScan.disabled = isLoading;
    if (isLoading) {
      btnText.style.display = "none";
      btnSpinner.style.display = "inline-block";
      loadingBox.style.display = "block";
    } else {
      btnText.style.display = "inline";
      btnSpinner.style.display = "none";
      loadingBox.style.display = "none";
    }
  }

  function showError(msg) {
    errorMessage.textContent = msg;
    errorBox.style.display = "flex";
  }

  function clearUI() {
    errorBox.style.display = "none";
    resultContainer.style.display = "none";
  }

  function escapeHTML(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
  }
});

