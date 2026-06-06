const $ = (id) => document.getElementById(id);

let deferredInstallPrompt = null;

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

function getSimulationFilters() {
  const source = ($("sim-filter-source")?.value || "").trim();
  const event_type = ($("sim-filter-event-type")?.value || "").trim();
  const agent_id = ($("sim-filter-agent-id")?.value || "").trim();
  const status = ($("sim-filter-status")?.value || "").trim();
  const severity = ($("sim-filter-severity")?.value || "").trim();
  const limit = ($("sim-filter-limit")?.value || "50").trim();

  const params = new URLSearchParams();
  if (source) params.set("source", source);
  if (event_type) params.set("event_type", event_type);
  if (agent_id) params.set("agent_id", agent_id);
  if (status) params.set("status", status);
  if (severity) params.set("severity", severity);
  if (limit) params.set("limit", limit);
  return params;
}

function renderSimulationSummary(summary) {
  const el = $("simulation-events-summary");
  if (!el) return;
  if (!summary || typeof summary !== "object") {
    el.textContent = "Summary unavailable.";
    return;
  }
  const text = [
    `total=${summary.total_events ?? 0}`,
    `by_source=${JSON.stringify(summary.by_source || {})}`,
    `by_event_type=${JSON.stringify(summary.by_event_type || {})}`,
    `by_status=${JSON.stringify(summary.by_status || {})}`,
    `by_severity=${JSON.stringify(summary.by_severity || {})}`,
  ].join(" • ");
  el.textContent = text;
}

function extractLinkageFromTrace(traceItem) {
  const metadata = traceItem && typeof traceItem === "object" ? traceItem.metadata || {} : {};
  const linkage = {};
  const keys = ["research_question_id", "scenario_id", "simulation_run_id", "observation_id"];
  keys.forEach((k) => {
    const value = metadata[k];
    if (value !== undefined && value !== null && String(value).trim() !== "") linkage[k] = value;
  });
  return linkage;
}

function setSimulationReviewNotesState(message) {
  const el = $("simulation-review-notes-state");
  if (el) el.textContent = message;
}

const REVIEW_NOTE_STATUSES = ["active", "resolved", "flagged", "archived"];

function escapeHtml(value) {
  const text = String(value ?? "");
  return text.replace(/[&<>"']/g, function (ch) {
    return "&#" + ch.charCodeAt(0) + ";";
  });
}

function getReviewNoteStatus(status) {
  const normalized = String(status || "").trim().toLowerCase();
  return REVIEW_NOTE_STATUSES.includes(normalized) ? normalized : "active";
}

function setSimulationReviewAuditState(message, stateClass = "") {
  const el = $("simulation-review-audit-state");
  if (!el) return;
  el.classList.remove("state-loading", "state-success", "state-error", "state-empty");
  if (stateClass) el.classList.add(stateClass);
  el.textContent = message;
}

function renderSimulationReviewAudit(items) {
  const container = $("simulation-review-audit-output");
  if (!container) return;
  container.innerHTML = "";

  if (!Array.isArray(items) || items.length === 0) {
    container.innerHTML = `<div class="audit-empty muted">No review audit entries for this event yet.</div>`;
    return;
  }

  items.forEach((entry) => {
    const row = document.createElement("article");
    row.className = "review-audit-item";
    row.innerHTML = `
      <div class="review-audit-head">
        <div class="review-audit-action">${escapeHtml(entry.action || "-")}</div>
        <div class="review-audit-time">${escapeHtml(entry.created_at || "-")}</div>
      </div>
      <div class="review-audit-meta">
        actor=${escapeHtml(entry.actor || "-")} • id=${escapeHtml(entry.id || "-")}
      </div>
      <div class="review-audit-detail">${escapeHtml(JSON.stringify(entry.details || {}))}</div>
    `;
    container.appendChild(row);
  });
}

async function loadSimulationReviewAudit(eventId) {
  if (!eventId) {
    setSimulationReviewAuditState("Select an event to load review audit.", "");
    renderSimulationReviewAudit([]);
    return;
  }

  setSimulationReviewAuditState("Loading review audit...", "state-loading");
  try {
    const data = await api(`/simulation/events/${eventId}/review-audit`);
    const count = data.count || 0;
    if (count === 0) {
      setSimulationReviewAuditState("No review audit entries yet.", "state-empty");
    } else {
      setSimulationReviewAuditState(`Review audit loaded: ${count}`, "state-success");
    }
    renderSimulationReviewAudit(data.items || []);
  } catch (e) {
    setSimulationReviewAuditState(`Failed to load review audit: ${e.message}`, "state-error");
    renderSimulationReviewAudit([]);
  }
}

async function updateSimulationReviewNoteStatus(eventId, noteId, status) {
  if (!eventId || !noteId) return;
  const safeStatus = getReviewNoteStatus(status);
  setSimulationReviewNotesState(`Updating note ${noteId} -> ${safeStatus}...`);
  try {
    await api(`/simulation/events/${eventId}/review-notes/${noteId}`, {
      method: "PATCH",
      body: JSON.stringify({ status: safeStatus }),
    });
    setSimulationReviewNotesState(`Review note ${noteId} updated to ${safeStatus}.`);
    await Promise.all([loadSimulationReviewNotes(eventId), loadSimulationReviewAudit(eventId)]);
  } catch (e) {
    setSimulationReviewNotesState(`Failed to update review note ${noteId}: ${e.message}`);
  }
}

function renderSimulationReviewNotes(items) {
  const container = $("simulation-review-notes-output");
  const eventId = ($("simulation-selected-event-id")?.value || "").trim();
  if (!container) return;
  container.innerHTML = "";

  if (!Array.isArray(items) || items.length === 0) {
    container.innerHTML = `<div class="muted">No review notes for this event yet.</div>`;
    return;
  }

  items.forEach((note) => {
    const noteId = note.id || "";
    const status = getReviewNoteStatus(note.status);
    const row = document.createElement("article");
    row.className = `review-note-item status-${status}${status === "archived" ? " is-archived" : ""}`;
    row.innerHTML = `
      <div class="review-note-head">
        <div class="review-note-id">${escapeHtml(noteId || "-")}</div>
        <div class="review-note-time">${escapeHtml(note.created_at || "-")}</div>
      </div>
      <div class="review-note-meta">
        reviewer=${escapeHtml(note.reviewer_id || "-")}
        <span class="review-note-status-badge status-${status}">${escapeHtml(status)}</span>
      </div>
      <div class="review-note-text">${escapeHtml(note.note_text || "")}</div>
      <div class="review-note-actions" data-note-id="${escapeHtml(noteId)}">
        <span class="review-note-actions-label">Set status:</span>
        <button class="btn-secondary btn-note-status" data-status="active" ${status === "active" ? "disabled" : ""}>Mark active</button>
        <button class="btn-secondary btn-note-status" data-status="resolved" ${status === "resolved" ? "disabled" : ""}>Mark resolved</button>
        <button class="btn-secondary btn-note-status" data-status="flagged" ${status === "flagged" ? "disabled" : ""}>Mark flagged</button>
        <button class="btn-secondary btn-note-status btn-note-archive" data-status="archived" ${status === "archived" ? "disabled" : ""}>Archive</button>
      </div>
    `;
    container.appendChild(row);
  });

  container.querySelectorAll(".btn-note-status").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const targetStatus = btn.getAttribute("data-status");
      const wrapper = btn.closest(".review-note-actions");
      const noteId = wrapper ? wrapper.getAttribute("data-note-id") : "";
      if (!eventId || !noteId || !targetStatus) return;
      await updateSimulationReviewNoteStatus(eventId, noteId, targetStatus);
    });
  });
}

async function loadSimulationReviewNotes(eventId) {
  const selected = $("simulation-selected-event-id");
  if (selected) selected.value = eventId || "";

  if (!eventId) {
    setSimulationReviewNotesState("Select an event to load review notes.");
    renderSimulationReviewNotes([]);
    await loadSimulationReviewAudit("");
    return;
  }

  setSimulationReviewNotesState("Loading review notes...");
  try {
    const data = await api(`/simulation/events/${eventId}/review-notes`);
    setSimulationReviewNotesState(`Review notes loaded: ${data.count || 0}`);
    renderSimulationReviewNotes(data.items || []);
  } catch (e) {
    setSimulationReviewNotesState(`Failed to load review notes: ${e.message}`);
    renderSimulationReviewNotes([]);
  }
}

function renderSimulationEvents(items) {
  const container = $("simulation-events-output");
  if (!container) return;
  container.innerHTML = "";

  if (!Array.isArray(items) || items.length === 0) {
    container.innerHTML = `<div class="muted">No simulation events match current filters.</div>`;
    return;
  }

  items.forEach((eventItem) => {
    const row = document.createElement("article");
    row.className = "event-item";
    row.innerHTML = `
      <div class="event-item-head">
        <div class="event-item-id">${eventItem.event_id || "-"}</div>
        <div class="event-item-time">${eventItem.created_at || "-"}</div>
      </div>
      <div class="event-item-meta">
        <span class="badge source">source: ${eventItem.source || "-"}</span>
        <span class="badge type">type: ${eventItem.event_type || "-"}</span>
        <span class="badge status">status: ${eventItem.status || "-"}</span>
        <span class="badge severity">severity: ${eventItem.severity || "-"}</span>
      </div>
      <div class="event-item-summary">
        agent=${eventItem.agent_id || "-"} • protocol=${eventItem.protocol_version || "-"} •
        transport=${eventItem.transport || "-"} • schema=${eventItem.schema_version || "-"}
      </div>
      <div class="event-item-summary">
        payload_summary=${JSON.stringify(eventItem.payload_summary || {})}
      </div>
      <div class="event-item-summary">
        risk_summary=${JSON.stringify(eventItem.risk_summary || {})}
      </div>
      <div class="event-item-actions">
        <button class="btn-secondary btn-event-trace" data-event-id="${eventItem.event_id || ""}">Trace</button>
        <button class="btn-secondary btn-event-select" data-event-id="${eventItem.event_id || ""}">Select</button>
      </div>
    `;
    container.appendChild(row);
  });

  container.querySelectorAll(".btn-event-trace").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const eventId = btn.getAttribute("data-event-id");
      if (!eventId) return;
      try {
        const traces = await api(`/simulation/events/${eventId}/traces`);
        const first = Array.isArray(traces.items) ? traces.items[0] : null;
        const linkage = extractLinkageFromTrace(first);
        if (Object.keys(linkage).length > 0) {
          pretty($("simulation-event-detail"), { trace: traces, linkage });
        } else {
          pretty($("simulation-event-detail"), traces);
        }
      } catch (e) {
        pretty($("simulation-event-detail"), { error: e.message });
      }
    });
  });

  container.querySelectorAll(".btn-event-select").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const eventId = btn.getAttribute("data-event-id");
      if (!eventId) return;
      await Promise.all([loadSimulationReviewNotes(eventId), loadSimulationReviewAudit(eventId)]);
    });
  });
}

async function addSimulationReviewNote() {
  const eventId = ($("simulation-selected-event-id")?.value || "").trim();
  const noteText = ($("simulation-review-note-text")?.value || "").trim();
  const reviewerId = ($("simulation-reviewer-id")?.value || "").trim();

  if (!eventId) {
    setSimulationReviewNotesState("Select an event before adding a review note.");
    return;
  }
  if (!noteText) {
    setSimulationReviewNotesState("Review note cannot be empty.");
    return;
  }

  try {
    setSimulationReviewNotesState("Submitting review note...");
    await api(`/simulation/events/${eventId}/review-notes`, {
      method: "POST",
      body: JSON.stringify({
        note_text: noteText,
        reviewer_id: reviewerId || undefined,
      }),
    });
    $("simulation-review-note-text").value = "";
    setSimulationReviewNotesState("Review note created.");
    await Promise.all([loadSimulationReviewNotes(eventId), loadSimulationReviewAudit(eventId)]);
  } catch (e) {
    setSimulationReviewNotesState(`Failed to create review note: ${e.message}`);
  }
}

async function loadSimulationEvents() {
  const params = getSimulationFilters();
  const query = params.toString();
  const eventsPath = query ? `/simulation/events?${query}` : "/simulation/events";
  const summaryPath = query ? `/simulation/events/summary?${query}` : "/simulation/events/summary";

  try {
    const [data, summary] = await Promise.all([api(eventsPath), api(summaryPath)]);
    renderSimulationEvents(data.items || []);
    renderSimulationSummary(summary);
    pretty($("simulation-event-detail"), { count: data.count || 0, note: "Select Trace on an event row." });
  } catch (e) {
    renderSimulationEvents([]);
    renderSimulationSummary({ total_events: 0 });
    pretty($("simulation-event-detail"), { error: e.message });
    const container = $("simulation-events-output");
    if (container) container.innerHTML = `<div class="muted">Failed to load simulation events: ${e.message}</div>`;
  }
}

const btnSimulationEvents = $("btn-list-simulation-events");
if (btnSimulationEvents) {
  btnSimulationEvents.onclick = loadSimulationEvents;
}

const btnAddReviewNote = $("btn-add-simulation-review-note");
if (btnAddReviewNote) {
  btnAddReviewNote.onclick = addSimulationReviewNote;
}

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
loadSimulationEvents();
