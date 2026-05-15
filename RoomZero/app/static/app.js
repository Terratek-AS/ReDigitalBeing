const $ = (id) => document.getElementById(id);

function showToast(message) {
  const t = $("toast");
  t.textContent = message;
  t.classList.remove("hidden");
  setTimeout(() => t.classList.add("hidden"), 2200);
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

async function initHealth() {
  try {
    const h = await api("/health");
    $("health-pill").textContent = `API: ${h.status} • safe_mode=${h.safe_mode}`;
  } catch (e) {
    $("health-pill").textContent = `API offline`;
  }
}

$("btn-create-invite").onclick = async () => {
  try {
    const data = await api("/testers/invite", {
      method: "POST",
      body: JSON.stringify({ role: $("invite-role").value }),
    });
    pretty($("invite-output"), data);
    $("register-code").value = data.invite.invite_code;
    showToast("Invite created");
  } catch (e) { showToast(e.message); }
};

$("btn-register").onclick = async () => {
  try {
    const data = await api("/testers/register", {
      method: "POST",
      body: JSON.stringify({
        display_name: $("register-name").value,
        invite_code: $("register-code").value,
        consent_accepted: true
      }),
    });
    pretty($("register-output"), data);
    $("chat-tester-id").value = data.tester.tester_id;
    $("fb-tester-id").value = data.tester.tester_id;
    showToast("Tester registered");
  } catch (e) { showToast(e.message); }
};

$("btn-chat").onclick = async () => {
  try {
    const payload = { message: $("chat-message").value };
    if ($("chat-tester-id").value) payload.tester_id = $("chat-tester-id").value;
    const data = await api("/chat", { method: "POST", body: JSON.stringify(payload) });
    pretty($("chat-output"), data);
  } catch (e) { showToast(e.message); }
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
        linked_sources: []
      }),
    });
    pretty($("rq-output"), data);
    showToast("Research question submitted");
  } catch (e) { showToast(e.message); }
};

$("btn-list-rq").onclick = async () => {
  try {
    const data = await api("/research/questions");
    pretty($("rq-output"), data);
  } catch (e) { showToast(e.message); }
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
        notes: "Created from UI"
      }),
    });
    pretty($("job-output"), data);
    $("job-id").value = data.job.job_id;
    showToast("Job created");
  } catch (e) { showToast(e.message); }
};

$("btn-list-jobs").onclick = async () => {
  try {
    const data = await api("/research/jobs");
    pretty($("job-output"), data);
  } catch (e) { showToast(e.message); }
};

$("btn-run-job").onclick = async () => {
  try {
    const data = await api(`/research/jobs/${$("job-id").value}/run`, { method: "POST", body: "{}" });
    pretty($("job-output"), data);
    showToast("Job run complete");
  } catch (e) { showToast(e.message); }
};

$("btn-pause-job").onclick = async () => {
  try {
    const data = await api(`/research/jobs/${$("job-id").value}/pause`, { method: "POST", body: "{}" });
    pretty($("job-output"), data);
  } catch (e) { showToast(e.message); }
};

$("btn-activate-job").onclick = async () => {
  try {
    const data = await api(`/research/jobs/${$("job-id").value}/activate`, { method: "POST", body: "{}" });
    pretty($("job-output"), data);
  } catch (e) { showToast(e.message); }
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
        claimed_relevance: $("source-relevance").value
      }),
    });
    pretty($("source-output"), data);
    showToast("Source submitted");
  } catch (e) { showToast(e.message); }
};

$("btn-list-sources").onclick = async () => {
  try {
    const data = await api("/sources/queue");
    pretty($("source-output"), data);
  } catch (e) { showToast(e.message); }
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
        suggested_improvement: $("fb-improvement").value
      }),
    });
    pretty($("feedback-output"), data);
    showToast("Feedback submitted");
  } catch (e) { showToast(e.message); }
};

$("btn-feedback-stats").onclick = async () => {
  try {
    const data = await api("/feedback/stats");
    pretty($("feedback-output"), data);
  } catch (e) { showToast(e.message); }
};

$("btn-quick-health").onclick = async () => {
  try {
    const data = await api("/health");
    pretty($("quick-output"), data);
    showToast("Health check complete");
  } catch (e) { showToast(e.message); }
};

$("btn-quick-list-jobs").onclick = async () => {
  try {
    const data = await api("/research/jobs");
    pretty($("quick-output"), data);
  } catch (e) { showToast(e.message); }
};

$("btn-open-docs").onclick = () => {
  window.open("/docs", "_blank", "noopener");
};

$("btn-copy-install").onclick = () => {
  copyText(".\\install.ps1", "Copied install command");
};

$("btn-copy-run").onclick = () => {
  copyText(".\\run.ps1", "Copied run command");
};

$("btn-copy-build-installer").onclick = () => {
  copyText(".\\install.ps1 -WithBuilder && .\\build_installer.ps1", "Copied build-installer command");
};

$("btn-mobile-help").onclick = () => {
  const help = [
    "Mobile quick install / access:",
    "1) Start RoomZero locally (./run.ps1).",
    "2) Ensure phone and PC are on same Wi-Fi.",
    "3) Replace localhost with your PC LAN IP and open /ui on mobile.",
    "4) In mobile browser menu, choose 'Add to Home Screen'.",
    "5) Use home-screen shortcut for rapid tester sessions."
  ].join("\n");
  pretty($("quick-output"), help);
};

$("btn-copy-mobile-url").onclick = () => {
  copyText("http://127.0.0.1:8000/ui", "Copied local UI URL");
};

$("btn-quick-create-flow").onclick = async () => {
  try {
    const invite = await api("/testers/invite", {
      method: "POST",
      body: JSON.stringify({ role: "tester" }),
    });

    const tester = await api("/testers/register", {
      method: "POST",
      body: JSON.stringify({
        display_name: "quick-ui-tester",
        invite_code: invite.invite.invite_code,
        consent_accepted: true
      }),
    });

    $("chat-tester-id").value = tester.tester.tester_id;
    $("fb-tester-id").value = tester.tester.tester_id;
    $("register-code").value = invite.invite.invite_code;

    pretty($("quick-output"), { invite, tester });
    showToast("Quick tester flow complete");
  } catch (e) { showToast(e.message); }
};

initHealth();
