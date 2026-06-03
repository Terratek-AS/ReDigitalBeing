const $ = (id) => document.getElementById(id);

let deferredInstallPrompt = null;

function showToast(message) {
  const t = $("toast");
  if (!t) return;
  t.textContent = message;
  t.classList.remove("hidden");
  setTimeout(() => t.classList.add("hidden"), 2400);
}

async function api(path, options = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || JSON.stringify(data));
  return data;
}

function pretty(el, data) {
  if (!el) return;
  el.textContent = typeof data === "string" ? data : JSON.stringify(data, null, 2);
}

async function copyText(value, okMessage) {
  try {
    await navigator.clipboard.writeText(value);
    showToast(okMessage);
  } catch {
    showToast("Clipboard unavailable in this browser context.");
  }
}

function updateOnboardingStep(stepNumber) {
  const steps = document.querySelectorAll(".onboarding-bar .step");
  steps.forEach((step, idx) => {
    step.classList.toggle("done", idx < stepNumber);
  });
}

function setRolePanel(role) {
  const map = {
    tester: "dashboard-tester",
    observer: "dashboard-observer",
    researcher: "dashboard-researcher",
  };
  Object.values(map).forEach((id) => {
    const panel = $(id);
    if (panel) panel.classList.add("hidden");
  });
  const target = $(map[role]);
  if (target) {
    target.classList.remove("hidden");
    target.scrollIntoView({ behavior: "smooth", block: "start" });
  }
  updateOnboardingStep(2);
}

function getObserverNotes() {
  try {
    const raw = localStorage.getItem("roomzero_observer_notes");
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveObserverNotes(notes) {
  localStorage.setItem("roomzero_observer_notes", JSON.stringify(notes));
}

function refreshObserverOutput() {
  const notes = getObserverNotes();
  if (!notes.length) {
    pretty($("observer-output"), "No observation notes yet.");
    return;
  }
  pretty($("observer-output"), notes);
}

async function initHealthAndStatus() {
  try {
    const health = await api("/health");
    $("health-pill").textContent = `System ${health.status} • safe mode ${health.safe_mode ? "on" : "off"}`;
    $("status-system").textContent = health.status === "ok" ? "Online and responsive" : "Needs attention";

    const [jobs, memories, logs, feedbackStats] = await Promise.all([
      api("/research/jobs").catch(() => ({ count: 0 })),
      api("/memory/recent").catch(() => ({ count: 0 })),
      api("/logs/recent").catch(() => ({ count: 0 })),
      api("/feedback/stats").catch(() => ({})),
    ]);

    $("status-research").textContent =
      (jobs.count || 0) > 0 ? `${jobs.count} job(s) available` : "No jobs yet, ready to start";
    $("status-memory").textContent = `${memories.count || 0} memories • ${logs.count || 0} log entries`;
    const feedbackCount = feedbackStats.total_feedback_count || 0;
    $("status-feedback").textContent =
      feedbackCount > 0 ? `${feedbackCount} feedback item(s) captured` : "Ready to collect feedback";
  } catch {
    $("health-pill").textContent = "System appears offline";
    $("status-system").textContent = "Offline";
    $("status-research").textContent = "Unknown";
    $("status-memory").textContent = "Unknown";
    $("status-feedback").textContent = "Unknown";
  }
}

function setupPwaInstall() {
  window.addEventListener("beforeinstallprompt", (event) => {
    event.preventDefault();
    deferredInstallPrompt = event;
    const btn = $("btn-install-pwa");
    if (btn) btn.classList.remove("hidden");
  });

  const btn = $("btn-install-pwa");
  if (btn) {
    btn.onclick = async () => {
      if (!deferredInstallPrompt) {
        showToast("Install is available from your browser menu on this device.");
        return;
      }
      deferredInstallPrompt.prompt();
      await deferredInstallPrompt.userChoice;
      deferredInstallPrompt = null;
      btn.classList.add("hidden");
    };
  }

  if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/static/service-worker.js").catch(() => {
      // best-effort registration only
    });
  }
}

document.querySelectorAll("[data-open-role]").forEach((btn) => {
  btn.addEventListener("click", () => setRolePanel(btn.dataset.openRole));
});

$("btn-create-invite").onclick = async () => {
  try {
    const data = await api("/testers/invite", {
      method: "POST",
      body: JSON.stringify({ role: $("invite-role").value }),
    });
    pretty($("invite-output"), data);
    $("register-code").value = data.invite.invite_code;
    showToast("Invite created");
  } catch (e) {
    showToast(e.message);
  }
};

$("btn-register").onclick = async () => {
  try {
    const data = await api("/testers/register", {
      method: "POST",
      body: JSON.stringify({
        display_name: $("register-name").value,
        invite_code: $("register-code").value,
        consent_accepted: true,
      }),
    });
    pretty($("register-output"), data);
    $("chat-tester-id").value = data.tester.tester_id;
    $("fb-tester-id").value = data.tester.tester_id;
    showToast("Tester registered");
  } catch (e) {
    showToast(e.message);
  }
};

$("btn-chat").onclick = async () => {
  try {
    const payload = { message: $("chat-message").value };
    if ($("chat-tester-id").value) payload.tester_id = $("chat-tester-id").value;
    const data = await api("/chat", { method: "POST", body: JSON.stringify(payload) });
    pretty($("chat-output"), data);
  } catch (e) {
    showToast(e.message);
  }
};

$("btn-submit-feedback").onclick = async () => {
  try {
    const data = await api("/feedback/session", {
      method: "POST",
      body: JSON.stringify({
        tester_id: $("fb-tester-id").value,
        session_id: $("fb-session-id").value,
        realism_score: Number($("fb-realism").value),
        coherence_score: Number($("fb-coherence").value),
        memory_score: Number($("fb-memory").value),
        emotional_presence_score: Number($("fb-emotional").value),
        ethical_safety_score: Number($("fb-ethical").value),
        usefulness_score: Number($("fb-usefulness").value),
        uncanny_score: Number($("fb-uncanny").value),
        trust_score: Number($("fb-trust").value),
        free_text: $("fb-text").value,
        suggested_improvement: $("fb-improvement").value,
      }),
    });
    pretty($("feedback-output"), data);
    showToast("Feedback submitted");
    updateOnboardingStep(3);
    initHealthAndStatus();
  } catch (e) {
    showToast(e.message);
  }
};

$("btn-feedback-stats").onclick = async () => {
  try {
    const data = await api("/feedback/stats");
    pretty($("feedback-output"), data);
  } catch (e) {
    showToast(e.message);
  }
};

$("btn-save-observation").onclick = () => {
  const title = $("obs-title").value.trim();
  const tag = $("obs-tag").value.trim();
  const note = $("obs-note").value.trim();

  if (!title || !note) {
    showToast("Please provide both an observation title and note.");
    return;
  }

  const notes = getObserverNotes();
  notes.unshift({
    created_at: new Date().toISOString(),
    title,
    tag: tag || "general",
    note,
  });
  saveObserverNotes(notes);
  $("obs-title").value = "";
  $("obs-tag").value = "";
  $("obs-note").value = "";
  refreshObserverOutput();
  showToast("Observation saved on this device");
};

$("btn-clear-observations").onclick = () => {
  localStorage.removeItem("roomzero_observer_notes");
  refreshObserverOutput();
  showToast("Observer notes cleared");
};

$("btn-submit-rq").onclick = async () => {
  try {
    const data = await api("/research/questions", {
      method: "POST",
      body: JSON.stringify({
        question: $("rq-question").value,
        category: $("rq-category").value,
        submitted_by: $("rq-submitted-by").value || "ui_researcher",
        priority: 5,
        tags: ["ui"],
        linked_sources: [],
      }),
    });
    pretty($("rq-output"), data);
    showToast("Research question submitted");
    initHealthAndStatus();
  } catch (e) {
    showToast(e.message);
  }
};

$("btn-list-rq").onclick = async () => {
  try {
    const data = await api("/research/questions");
    pretty($("rq-output"), data);
  } catch (e) {
    showToast(e.message);
  }
};

$("btn-create-job").onclick = async () => {
  try {
    const topic = $("job-topic").value;
    const data = await api("/research/jobs", {
      method: "POST",
      body: JSON.stringify({
        name: `Manual Research Job: ${topic}`,
        topic,
        category: "other",
        query: topic,
        schedule: "manual",
        created_by: "ui_admin",
        notes: "Created from UI",
      }),
    });
    pretty($("job-output"), data);
    $("job-id").value = data.job.job_id;
    showToast("Job created");
    initHealthAndStatus();
  } catch (e) {
    showToast(e.message);
  }
};

$("btn-list-jobs").onclick = async () => {
  try {
    const data = await api("/research/jobs");
    pretty($("job-output"), data);
  } catch (e) {
    showToast(e.message);
  }
};

$("btn-run-job").onclick = async () => {
  try {
    const data = await api(`/research/jobs/${$("job-id").value}/run`, { method: "POST", body: "{}" });
    pretty($("job-output"), data);
    showToast("Job run complete");
  } catch (e) {
    showToast(e.message);
  }
};

$("btn-pause-job").onclick = async () => {
  try {
    const data = await api(`/research/jobs/${$("job-id").value}/pause`, { method: "POST", body: "{}" });
    pretty($("job-output"), data);
  } catch (e) {
    showToast(e.message);
  }
};

$("btn-activate-job").onclick = async () => {
  try {
    const data = await api(`/research/jobs/${$("job-id").value}/activate`, { method: "POST", body: "{}" });
    pretty($("job-output"), data);
  } catch (e) {
    showToast(e.message);
  }
};

$("btn-submit-source").onclick = async () => {
  try {
    const data = await api("/sources/submit", {
      method: "POST",
      body: JSON.stringify({
        url_or_reference: $("source-url").value,
        title: $("source-title").value,
        submitted_by: $("source-by").value || "ui_researcher",
        category: $("source-category").value,
        claimed_relevance: $("source-relevance").value,
      }),
    });
    pretty($("source-output"), data);
    showToast("Source submitted");
  } catch (e) {
    showToast(e.message);
  }
};

$("btn-list-sources").onclick = async () => {
  try {
    const data = await api("/sources/queue");
    pretty($("source-output"), data);
  } catch (e) {
    showToast(e.message);
  }
};

$("btn-quick-health").onclick = async () => {
  try {
    const data = await api("/health");
    pretty($("quick-output"), data);
    showToast("Health check complete");
    initHealthAndStatus();
  } catch (e) {
    showToast(e.message);
  }
};

$("btn-open-docs").onclick = () => window.open("/docs", "_blank", "noopener");

$("btn-copy-install").onclick = () => copyText(".\\install.ps1", "Copied install command");
$("btn-copy-run").onclick = () => copyText(".\\run.ps1", "Copied run command");
$("btn-copy-build-installer").onclick = () =>
  copyText(".\\install.ps1 -WithBuilder && .\\build_installer.ps1", "Copied build-installer command");
$("btn-copy-mobile-url").onclick = () => copyText("http://127.0.0.1:8000/ui", "Copied local UI URL");

$("btn-mobile-help").onclick = () => {
  const help = [
    "Mobile install (PWA):",
    "1) Start RoomZero locally using .\\run.ps1",
    "2) Open /ui from your phone on the same Wi-Fi (use your PC LAN IP)",
    "3) In mobile browser menu, tap 'Add to Home Screen'",
    "4) Launch RoomZero from home screen like an app",
    "",
    "Android APK path (next stage):",
    "- Wrap current UI with Capacitor and point to hosted/local API",
    "- Keep PWA as baseline for this release",
  ].join("\n");
  pretty($("quick-output"), help);
};

refreshObserverOutput();
setRolePanel("tester");
setupPwaInstall();
initHealthAndStatus();
