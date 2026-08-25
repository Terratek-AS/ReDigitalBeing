const $ = (id) => document.getElementById(id);

let deferredInstallPrompt = null;
const adminState = {
  users: [],
  invitations: [],
  questions: [],
  scenarios: [],
  runs: [],
  audit: [],
};

function getConfiguredApiBaseUrl() {
  const fallback = "http://127.0.0.1:8000";
  const configured = window.ROOMZERO_CONFIG && window.ROOMZERO_CONFIG.API_BASE_URL;
  const base = (configured || fallback).trim().replace(/\/+$/, "");
  return base || fallback;
}

const API_BASE_URL = getConfiguredApiBaseUrl();

function toApiUrl(path) {
  if (/^https?:\/\//i.test(path)) return path;
  if (!path.startsWith("/")) return `${API_BASE_URL}/${path}`;
  return `${API_BASE_URL}${path}`;
}

function getUiBaseUrl() {
  return API_BASE_URL;
}

function escapeHtml(value) {
  const text = String(value ?? "");
  return text.replace(/[&<>"']/g, (ch) => `&#${ch.charCodeAt(0)};`);
}

function showToast(message) {
  const t = $("toast");
  if (!t) return;
  t.textContent = message;
  t.classList.remove("hidden");
  setTimeout(() => t.classList.add("hidden"), 2400);
}

async function api(path, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...(options.headers || {}),
  };

  const res = await fetch(toApiUrl(path), {
    ...options,
    headers,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || JSON.stringify(data));
  return data;
}

function pretty(el, data) {
  if (!el) return;
  el.textContent = typeof data === "string" ? data : JSON.stringify(data, null, 2);
}

function getAdminActorId() {
  return ($("admin-actor-id")?.value || "").trim();
}

function requireAdminActorId() {
  const actorId = getAdminActorId();
  if (!actorId) throw new Error("Enter a valid admin or reviewer actor ID first.");
  return actorId;
}

function splitCsv(value) {
  return String(value || "")
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function formatDate(value) {
  if (!value) return "Not set";
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? String(value) : parsed.toLocaleString();
}

function safeStateClass(value) {
  const allowed = new Set(["approved", "running", "completed"]);
  return allowed.has(value) ? `state-${value}` : "";
}

function safeRiskClass(value) {
  return value === "high" || value === "critical" ? `risk-${value}` : "";
}

function renderAdminEmpty(targetId, message) {
  const target = $(targetId);
  if (target) target.innerHTML = `<div class="empty-state">${escapeHtml(message)}</div>`;
}

function renderAdminInvitations(items) {
  const target = $("admin-invitations-list");
  if (!target) return;
  if (!items.length) {
    renderAdminEmpty("admin-invitations-list", "No platform invitations yet.");
    return;
  }
  target.innerHTML = items.slice(0, 12).map((item) => `
    <article class="admin-list-item">
      <div class="item-meta">
        <span class="state-badge ${item.active ? "state-approved" : ""}">${item.active ? "active" : "used / inactive"}</span>
        <span>${escapeHtml(item.role)}</span>
      </div>
      <h4>${escapeHtml(item.invite_code)}</h4>
      <p class="muted small">Expires ${escapeHtml(formatDate(item.expires_at))}</p>
      ${item.accepted_by ? `<p class="muted small">Accepted by ${escapeHtml(item.accepted_by)}</p>` : ""}
    </article>
  `).join("");
}

function renderAdminUsers(items) {
  const target = $("admin-users-list");
  if (!target) return;
  if (!items.length) {
    renderAdminEmpty("admin-users-list", "No platform users registered.");
    return;
  }
  target.innerHTML = items.slice(0, 20).map((item) => `
    <article class="admin-list-item">
      <div class="item-meta">
        <span class="state-badge ${Number(item.active) === 1 ? "state-approved" : ""}">${Number(item.active) === 1 ? "active" : "inactive"}</span>
        <span>${escapeHtml(item.role)}</span>
      </div>
      <h4>${escapeHtml(item.display_name)}</h4>
      <p class="muted small">${escapeHtml(item.id)} • joined ${escapeHtml(formatDate(item.created_at))}</p>
    </article>
  `).join("");
}

function renderAdminQuestions(items) {
  const target = $("admin-questions-list");
  if (!target) return;
  if (!items.length) {
    renderAdminEmpty("admin-questions-list", "No questions match the selected filters.");
    return;
  }
  target.innerHTML = items.map((item) => `
    <article class="admin-list-item">
      <div class="item-meta">
        <span class="state-badge ${safeStateClass(item.status)}">${escapeHtml(item.status)}</span>
        <span class="risk-badge ${safeRiskClass(item.risk_level)}">${escapeHtml(item.risk_level || "low")} risk</span>
        <span>Priority ${escapeHtml(item.priority ?? 5)}</span>
        <span>${escapeHtml(item.category)}</span>
      </div>
      <h4>${escapeHtml(item.title)}</h4>
      <p class="muted">${escapeHtml(item.description)}</p>
      <p class="muted small">Author ${escapeHtml(item.author)} • ${escapeHtml(formatDate(item.created_at))}</p>
      <div class="item-actions">
        <button data-question-action="approve" data-question-id="${escapeHtml(item.id)}">Approve</button>
        <button class="btn-secondary" data-question-action="review" data-question-id="${escapeHtml(item.id)}">Needs review</button>
        <button class="btn-danger" data-question-action="reject" data-question-id="${escapeHtml(item.id)}">Reject</button>
        <button class="btn-secondary" data-question-action="archive" data-question-id="${escapeHtml(item.id)}">Archive</button>
        ${item.status === "approved" ? `<button class="btn-secondary" data-question-action="scenario" data-question-id="${escapeHtml(item.id)}">Use in scenario</button>` : ""}
      </div>
    </article>
  `).join("");
}

function renderAdminScenarios(items) {
  const target = $("admin-scenarios-list");
  if (!target) return;
  if (!items.length) {
    renderAdminEmpty("admin-scenarios-list", "No scenarios have been created.");
    return;
  }
  target.innerHTML = items.map((item) => `
    <article class="admin-list-item">
      <div class="item-meta">
        <span class="state-badge ${safeStateClass(item.approval_status)}">${escapeHtml(item.approval_status)}</span>
        <span class="risk-badge ${safeRiskClass(item.risk_level)}">${escapeHtml(item.risk_level)} risk</span>
        <span>${escapeHtml(item.status)}</span>
      </div>
      <h4>${escapeHtml(item.purpose)}</h4>
      <p class="muted small">${escapeHtml(item.agent_type)} • ${escapeHtml(item.environment)}</p>
      <div class="item-actions">
        ${item.approval_status !== "approved" ? `<button data-scenario-action="approve" data-scenario-id="${escapeHtml(item.id)}">Approve scenario</button>` : `<button data-scenario-action="start" data-scenario-id="${escapeHtml(item.id)}">Start controlled run</button>`}
      </div>
    </article>
  `).join("");
}

function renderAdminRuns(items) {
  const target = $("admin-runs-list");
  if (!target) return;
  if (!items.length) {
    renderAdminEmpty("admin-runs-list", "No simulation runs recorded.");
    return;
  }
  target.innerHTML = items.map((item) => `
    <article class="admin-list-item">
      <div class="item-meta">
        <span class="state-badge ${safeStateClass(item.status)}">${escapeHtml(item.status)}</span>
        <span>Run ${escapeHtml(item.run_number)}</span>
      </div>
      <h4>${escapeHtml(item.id)}</h4>
      <p class="muted small">Scenario ${escapeHtml(item.scenario_id)} • ${escapeHtml(formatDate(item.created_at))}</p>
      <div class="item-actions">
        <button class="btn-secondary" data-run-action="observe" data-run-id="${escapeHtml(item.id)}">View observations</button>
        ${item.status === "running" ? `<button data-run-action="complete" data-run-id="${escapeHtml(item.id)}">Complete run</button>` : ""}
      </div>
    </article>
  `).join("");
}

function renderAdminAudit(items) {
  const target = $("admin-audit-list");
  if (!target) return;
  if (!items.length) {
    renderAdminEmpty("admin-audit-list", "No audit activity recorded.");
    return;
  }
  target.innerHTML = items.slice(0, 30).map((item) => `
    <article class="admin-list-item">
      <div class="item-meta"><span>${escapeHtml(formatDate(item.created_at))}</span><span>${escapeHtml(item.actor_id)}</span></div>
      <h4>${escapeHtml(item.action)}</h4>
      <p class="muted small">${escapeHtml(item.target_type)} • ${escapeHtml(item.target_id)}</p>
    </article>
  `).join("");
}

function updateAdminSummary() {
  const openInvites = adminState.invitations.filter((item) => Number(item.active) === 1).length;
  const needsReview = adminState.questions.filter(
    (item) => item.status === "proposed" || item.approval_status === "needs_review"
  ).length;
  $("admin-kpi-users").textContent = adminState.users.length;
  $("admin-kpi-invitations").textContent = openInvites;
  $("admin-kpi-review").textContent = needsReview;
  $("admin-kpi-scenarios").textContent = adminState.scenarios.length;
  $("admin-kpi-runs").textContent = adminState.runs.length;
}

async function loadAdminQuestions() {
  const actorId = requireAdminActorId();
  const params = new URLSearchParams({ actor_id: actorId });
  const status = $("admin-question-status").value;
  const risk = $("admin-question-risk").value;
  if (status) params.set("status", status);
  if (risk) params.set("risk_level", risk);
  const data = await api(`/platform/research/questions?${params}`);
  adminState.questions = data.items || [];
  renderAdminQuestions(adminState.questions);
  updateAdminSummary();
}

async function loadAdminDashboard() {
  const actorId = requireAdminActorId();
  $("admin-scope-note").textContent = "Loading governed platform data…";
  const encodedActor = encodeURIComponent(actorId);
  const [users, invitations, questions, scenarios, runs, audit] = await Promise.all([
    api(`/platform/users?actor_id=${encodedActor}`),
    api(`/platform/invitations?actor_id=${encodedActor}`),
    api(`/platform/research/questions?actor_id=${encodedActor}`),
    api(`/platform/scenarios?actor_id=${encodedActor}`),
    api(`/platform/runs?actor_id=${encodedActor}`),
    api("/platform/audit", { method: "POST", body: JSON.stringify({ actor_id: actorId }) }),
  ]);
  adminState.users = users.items || [];
  adminState.invitations = invitations.items || [];
  adminState.questions = questions.items || [];
  adminState.scenarios = scenarios.items || [];
  adminState.runs = runs.items || [];
  adminState.audit = audit.items || [];
  renderAdminInvitations(adminState.invitations);
  renderAdminUsers(adminState.users);
  renderAdminQuestions(adminState.questions);
  renderAdminScenarios(adminState.scenarios);
  renderAdminRuns(adminState.runs);
  renderAdminAudit(adminState.audit);
  updateAdminSummary();
  $("admin-scope-note").textContent = `Authorized workspace loaded for ${actorId}.`;
}

async function refreshAdminArea() {
  try {
    await loadAdminDashboard();
    showToast("Admin workspace refreshed");
  } catch (error) {
    $("admin-scope-note").textContent = error.message;
    showToast(error.message);
  }
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
    admin: "dashboard-admin",
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

function getEventReviewNotes() {
  try {
    const raw = localStorage.getItem("roomzero_event_review_notes");
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function saveEventReviewNotes(notes) {
  localStorage.setItem("roomzero_event_review_notes", JSON.stringify(notes));
}

function renderReviewAuditAction() {
  const actionEl = $("review-audit-action");
  const statusEl = $("review-audit-status");
  if (!actionEl || !statusEl) return;

  const prompt =
    "auditAction: Review code for readability, quality, and issues (see below for action prompt) output safely.";
  actionEl.innerHTML = `<code>${escapeHtml(prompt)}</code>`;
  statusEl.textContent = "active";
}

function refreshSimulationEvents() {
  const el = $("simulation-events-output");
  if (!el) return;

  api("/ws/unreal/observations")
    .then((data) => {
      pretty(el, data);
    })
    .catch(() => {
      pretty(el, "Simulation events unavailable.");
    });
}

function refreshEventReviewNotes() {
  const notes = getEventReviewNotes();
  if (!notes.length) {
    pretty($("event-review-notes-output"), "No event review notes yet.");
    return;
  }
  pretty($("event-review-notes-output"), notes);
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

function updateInstallState(message) {
  const el = $("install-state");
  if (el) el.textContent = message;
}

function isStandaloneDisplay() {
  return window.matchMedia("(display-mode: standalone)").matches || window.navigator.standalone === true;
}

function setupPwaInstall() {
  const btn = $("btn-install-pwa");

  if (isStandaloneDisplay()) {
    if (btn) btn.classList.add("hidden");
    updateInstallState("RoomZero is installed on this device.");
  } else {
    updateInstallState("Tip: Install RoomZero for one-tap launch from your home screen.");
  }

  window.addEventListener("beforeinstallprompt", (event) => {
    event.preventDefault();
    deferredInstallPrompt = event;
    if (btn) btn.classList.remove("hidden");
    updateInstallState("Install is available now.");
  });

  window.addEventListener("appinstalled", () => {
    deferredInstallPrompt = null;
    if (btn) btn.classList.add("hidden");
    updateInstallState("RoomZero installed successfully.");
    showToast("RoomZero installed");
  });

  if (btn) {
    btn.onclick = async () => {
      if (!deferredInstallPrompt) {
        showToast("Use your browser menu and choose 'Add to Home screen' if install is not shown.");
        return;
      }
      deferredInstallPrompt.prompt();
      await deferredInstallPrompt.userChoice;
      deferredInstallPrompt = null;
      btn.classList.add("hidden");
    };
  }

  if ("serviceWorker" in navigator) {
    const swUrl = (() => {
      if (window.location.protocol === "http:" || window.location.protocol === "https:") {
        return new URL("./service-worker.js", window.location.href).toString();
      }
      return "/static/service-worker.js";
    })();

    navigator.serviceWorker
      .register(swUrl)
      .then(() => updateInstallState("Offline support enabled (service worker active)."))
      .catch(() => {
        updateInstallState("Install works, but offline support could not be enabled in this browser.");
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

$("btn-save-event-review-note").onclick = () => {
  const input = $("event-review-note-input");
  if (!input) return;
  const note = input.value.trim();

  if (!note) {
    showToast("Please enter an event review note.");
    return;
  }

  const notes = getEventReviewNotes();
  notes.unshift({
    created_at: new Date().toISOString(),
    note,
  });
  saveEventReviewNotes(notes);
  input.value = "";
  refreshEventReviewNotes();
  showToast("Event review note saved");
};

$("btn-clear-event-review-notes").onclick = () => {
  localStorage.removeItem("roomzero_event_review_notes");
  refreshEventReviewNotes();
  showToast("Event review notes cleared");
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

$("btn-admin-save-actor").onclick = async () => {
  const actorId = getAdminActorId();
  if (!actorId) {
    showToast("Enter an actor ID first.");
    return;
  }
  localStorage.setItem("roomzero_admin_actor_id", actorId);
  await refreshAdminArea();
};

$("btn-admin-refresh").onclick = refreshAdminArea;
$("btn-admin-export").onclick = async () => {
  try {
    const actorId = requireAdminActorId();
    await loadAdminDashboard();
    const observationPairs = await Promise.all(
      adminState.runs.map(async (run) => {
        const data = await api(
          `/platform/runs/${encodeURIComponent(run.id)}/observations?actor_id=${encodeURIComponent(actorId)}`
        );
        return [run.id, data.items || []];
      })
    );
    const snapshot = {
      exported_at: new Date().toISOString(),
      schema: "roomzero.research-export.v1",
      users: adminState.users,
      invitations: adminState.invitations,
      research_questions: adminState.questions,
      simulation_scenarios: adminState.scenarios,
      simulation_runs: adminState.runs,
      observations_by_run: Object.fromEntries(observationPairs),
      audit_logs: adminState.audit,
    };
    const blob = new Blob([JSON.stringify(snapshot, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `roomzero-research-${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    URL.revokeObjectURL(url);
    showToast("Research snapshot exported");
  } catch (error) {
    showToast(error.message);
  }
};
$("btn-admin-filter-questions").onclick = async () => {
  try {
    await loadAdminQuestions();
    showToast("Research queue filtered");
  } catch (error) {
    showToast(error.message);
  }
};

$("btn-admin-create-invite").onclick = async () => {
  try {
    const actorId = requireAdminActorId();
    const data = await api("/platform/invitations", {
      method: "POST",
      body: JSON.stringify({
        actor_id: actorId,
        role: $("admin-invite-role").value,
        expires_in_hours: Number($("admin-invite-hours").value || 72),
      }),
    });
    showToast(`Invite ${data.invitation.invite_code} created`);
    await loadAdminDashboard();
  } catch (error) {
    showToast(error.message);
  }
};

$("admin-questions-list").onclick = async (event) => {
  const button = event.target.closest("button[data-question-action]");
  if (!button) return;
  const questionId = button.dataset.questionId;
  const action = button.dataset.questionAction;
  if (action === "scenario") {
    $("admin-scenario-question-id").value = questionId;
    $("admin-scenario-purpose").focus();
    showToast("Question selected for scenario builder");
    return;
  }
  try {
    const actorId = requireAdminActorId();
    const reviewerNotes = $("admin-review-notes").value.trim();
    if (action === "review") {
      await api(`/platform/research/questions/${encodeURIComponent(questionId)}/review`, {
        method: "PATCH",
        body: JSON.stringify({
          actor_id: actorId,
          approval_status: "needs_review",
          reviewer_notes: reviewerNotes || "Returned for further ethical review.",
        }),
      });
    } else {
      await api(`/platform/research/questions/${encodeURIComponent(questionId)}/${action}`, {
        method: "POST",
        body: JSON.stringify({ actor_id: actorId, reviewer_notes: reviewerNotes || null }),
      });
    }
    const actionLabels = { approve: "approved", review: "returned for review", reject: "rejected", archive: "archived" };
    showToast(`Question ${actionLabels[action] || "updated"}`);
    await loadAdminDashboard();
  } catch (error) {
    showToast(error.message);
  }
};

$("btn-admin-convert-scenario").onclick = async () => {
  try {
    const actorId = requireAdminActorId();
    const questionId = $("admin-scenario-question-id").value.trim();
    if (!questionId) throw new Error("Select an approved research question first.");
    const purpose = $("admin-scenario-purpose").value.trim();
    if (!purpose) throw new Error("Describe the scenario purpose.");
    const metrics = splitCsv($("admin-scenario-metrics").value);
    const constraints = splitCsv($("admin-scenario-constraints").value);
    await api(`/platform/research/questions/${encodeURIComponent(questionId)}/convert-scenario`, {
      method: "POST",
      body: JSON.stringify({
        actor_id: actorId,
        purpose,
        agent_type: $("admin-scenario-agent").value.trim() || "Eir",
        environment: $("admin-scenario-environment").value.trim() || "Local synthetic chamber",
        variables: [],
        metrics,
        ethical_constraints: constraints,
        environment_conditions: "Controlled local research environment.",
        input_variables: [],
        expected_observations: [],
        metrics_to_collect: metrics,
        result_summary: "Not run yet.",
        status: "draft",
        risk_level: $("admin-scenario-risk").value,
        possible_harm: "Requires human review before execution.",
        mitigation_notes: constraints.join("; "),
        human_oversight_required: true,
        approval_status: "pending",
        reviewer_notes: $("admin-review-notes").value.trim(),
      }),
    });
    showToast("Draft scenario created");
    await loadAdminDashboard();
  } catch (error) {
    showToast(error.message);
  }
};

$("btn-admin-refresh-scenarios").onclick = refreshAdminArea;
$("btn-admin-refresh-runs").onclick = refreshAdminArea;

$("admin-scenarios-list").onclick = async (event) => {
  const button = event.target.closest("button[data-scenario-action]");
  if (!button) return;
  const scenarioId = button.dataset.scenarioId;
  const action = button.dataset.scenarioAction;
  try {
    const actorId = requireAdminActorId();
    if (action === "approve") {
      await api(`/platform/scenarios/${encodeURIComponent(scenarioId)}`, {
        method: "PATCH",
        body: JSON.stringify({
          actor_id: actorId,
          status: "ready_for_test",
          approval_status: "approved",
          reviewer_notes: $("admin-review-notes").value.trim() || "Approved in M4.2 admin console.",
        }),
      });
      showToast("Scenario approved for controlled testing");
    } else if (action === "start") {
      const created = await api(`/platform/scenarios/${encodeURIComponent(scenarioId)}/runs`, {
        method: "POST",
        body: JSON.stringify({ actor_id: actorId, input_snapshot: { source: "m4.2-admin-ui" } }),
      });
      await api(`/platform/runs/${encodeURIComponent(created.run.id)}`, {
        method: "PATCH",
        body: JSON.stringify({ actor_id: actorId, status: "running", metrics: {}, result_summary: "" }),
      });
      showToast(`Run ${created.run.run_number} started`);
    }
    await loadAdminDashboard();
  } catch (error) {
    showToast(error.message);
  }
};

$("admin-runs-list").onclick = async (event) => {
  const button = event.target.closest("button[data-run-action]");
  if (!button) return;
  const runId = button.dataset.runId;
  const action = button.dataset.runAction;
  try {
    const actorId = requireAdminActorId();
    if (action === "observe") {
      const data = await api(
        `/platform/runs/${encodeURIComponent(runId)}/observations?actor_id=${encodeURIComponent(actorId)}`
      );
      pretty($("admin-run-observations"), data);
    } else if (action === "complete") {
      await api(`/platform/runs/${encodeURIComponent(runId)}`, {
        method: "PATCH",
        body: JSON.stringify({
          actor_id: actorId,
          status: "completed",
          metrics: {},
          result_summary: "Completed from M4.2 admin console; review observations before conclusions.",
        }),
      });
      showToast("Simulation run completed");
      await loadAdminDashboard();
    }
  } catch (error) {
    showToast(error.message);
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

const quickLinkDocs = $("quick-link-docs");
if (quickLinkDocs) quickLinkDocs.href = toApiUrl("/docs");

const quickLinkHealth = $("quick-link-health");
if (quickLinkHealth) quickLinkHealth.href = toApiUrl("/health");

$("btn-open-docs").onclick = () => window.open(toApiUrl("/docs"), "_blank", "noopener");

$("btn-copy-install").onclick = () => copyText(".\\install.ps1", "Copied install command");
$("btn-copy-run").onclick = () => copyText(".\\run.ps1", "Copied run command");
$("btn-copy-build-installer").onclick = () =>
  copyText(".\\install.ps1 -WithBuilder && .\\build_installer.ps1", "Copied build-installer command");
$("btn-copy-mobile-url").onclick = () => copyText(`${getUiBaseUrl()}/ui`, "Copied UI URL");

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
refreshEventReviewNotes();
refreshSimulationEvents();
renderReviewAuditAction();
renderAdminEmpty("admin-invitations-list", "Enter an authorized actor ID to load invitations.");
renderAdminEmpty("admin-users-list", "Enter an authorized actor ID to load users.");
renderAdminEmpty("admin-questions-list", "Enter an authorized actor ID to load the review queue.");
renderAdminEmpty("admin-scenarios-list", "Enter an authorized actor ID to load scenarios.");
renderAdminEmpty("admin-runs-list", "Enter an authorized actor ID to load runs.");
renderAdminEmpty("admin-audit-list", "Enter an authorized actor ID to load audit activity.");
const savedAdminActorId = localStorage.getItem("roomzero_admin_actor_id");
if (savedAdminActorId) $("admin-actor-id").value = savedAdminActorId;
setRolePanel("tester");
setupPwaInstall();
initHealthAndStatus();
