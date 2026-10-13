const api = "/api/v1";
const translations = {
  zh: { "nav.overview": "概覽", "nav.design": "設計", "nav.build": "建置", "nav.run": "運行", "nav.diagnose": "診斷", "nav.evidence": "證據", "nav.registry": "元件庫", "chrome.safety": "安全邊界啟用中", "landing.kicker": "設計、驗證、模擬", "landing.title": "讓第一台機器人<br>先在虛擬世界醒來。", "landing.summary": "從自然語言需求出發，建立具備 LiDAR、Camera 與導航能力的差速機器人；每個動作都先在可審閱的安全邊界內完成。", "landing.enter": "進入工作區", "landing.direct": "直接建立方案", "landing.status": "Virtual-first robot development", "overview.title": "從想法到機器人", "overview.summary": "先告訴我們你想做的機器人；我們會整理可行建議，確認後才會建立專案。", "overview.design": "開始規劃", "overview.runtime": "查看目前狀態", views: { landing: "首頁", dashboard: "概覽", requirement: "設計", configuration: "建置", runtime: "運行", validation: "診斷", evidence: "證據", registry: "元件庫" } },
  en: { "nav.overview": "Overview", "nav.design": "Design", "nav.build": "Build", "nav.run": "Run", "nav.diagnose": "Diagnose", "nav.evidence": "Evidence", "nav.registry": "Registry", "chrome.safety": "Safety boundary active", "landing.kicker": "DESIGN · VALIDATE · SIMULATE", "landing.title": "Let your first robot<br>wake up virtually.", "landing.summary": "Start with a natural-language request and build a differential-drive robot with LiDAR, camera, and navigation—each action remains within a reviewable safety boundary.", "landing.enter": "Enter workspace", "landing.direct": "Create a design plan", "landing.status": "Virtual-first robot development", "overview.title": "From idea to robot", "overview.summary": "Tell us what you want to build. We will organise practical suggestions before anything is created.", "overview.design": "Start planning", "overview.runtime": "View current status", views: { landing: "Home", dashboard: "Overview", requirement: "Design", configuration: "Build", runtime: "Run", validation: "Diagnose", evidence: "Evidence", registry: "Registry" } },
};
let locale = localStorage.getItem("robot-dev-ai-locale") === "en" ? "en" : "zh";
const staticEnglish = new Map([
  ["跳至主要內容", "Skip to main content"], ["主要工作流", "Main workflow"], ["M14 視圖", "M14 views"],
  ["從想法到機器人", "From idea to robot"], ["下一步，從方案開始", "Start with a plan"],
  ["說說你想做什麼", "Describe what you want"], ["用簡單描述告訴我們你需要的機器人", "Tell us what you need in plain language"],
  ["確認建議內容", "Review the suggestions"], ["查看推薦內容後，再決定是否建立專案", "Review the suggestions before deciding to create a project"],
  ["在模擬中查看", "Check in simulation"], ["確認機器人、導航與感測器是否正常", "Check that the robot, navigation, and sensors are available"],
  ["模擬系統狀態", "Simulation status"], ["重新檢查模擬系統", "Check simulation again"], ["連線服務", "Available services"], ["資料通道", "Data channels"], ["位置關係", "Robot positions"],
  ["告訴我們你想做的機器人", "Tell us about your robot"], ["用日常語言描述你的想法；我們會先整理建議，讓你看過再決定下一步。", "Describe your idea in everyday language. We will suggest options for you to review before the next step."],
  ["你希望機器人做什麼？", "What would you like the robot to do?"], ["產生建議", "Show suggestions"], ["確認推薦內容", "Review the suggestions"], ["查看模擬狀態", "Check simulation status"], ["遇到問題時再來這裡", "Get help when something needs attention"],
  ["導航功能測試", "Test navigation"], ["開始檢查", "Start check"], ["查看修正建議", "View suggested fixes"], ["驗證資料的真實範圍", "What the evidence actually shows"],
  ["重新讀取證據", "Reload evidence"], ["證據覆蓋範圍", "Evidence coverage"], ["矛盾與待審查資料", "Conflicts and pending reviews"],
  ["元件來源與使用狀態", "Component sources and status"], ["顯示類型", "Show"], ["全部元件", "All components"], ["硬體", "Hardware"], ["驅動程式", "Drivers"], ["轉接層", "Adapters"], ["整合範本", "Templates"], ["來源審查結果", "Source review"], ["查看來源審查", "Review source"], ["預覽安全測試計畫", "Preview safe test plan"],
]);
const originalStaticText = new WeakMap();
function localizeStaticText() {
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let node;
  while ((node = walker.nextNode())) {
    if (!originalStaticText.has(node)) originalStaticText.set(node, node.nodeValue);
    const original = originalStaticText.get(node); const trimmed = original.trim();
    if (locale === "en" && staticEnglish.has(trimmed)) node.nodeValue = original.replace(trimmed, staticEnglish.get(trimmed));
    else node.nodeValue = original;
  }
  document.querySelectorAll("[aria-label]").forEach((node) => {
    if (!node.dataset.originalAriaLabel) node.dataset.originalAriaLabel = node.getAttribute("aria-label");
    const original = node.dataset.originalAriaLabel;
    node.setAttribute("aria-label", locale === "en" && staticEnglish.has(original) ? staticEnglish.get(original) : original);
  });
}
function uiText(value) { return locale === "en" ? (staticEnglish.get(String(value)) || value) : value; }
function applyLocale() {
  const copy = translations[locale];
  document.documentElement.lang = locale === "zh" ? "zh-Hant" : "en";
  document.querySelectorAll("[data-i18n]").forEach((node) => { node.textContent = copy[node.dataset.i18n] || node.textContent; });
  document.querySelectorAll("[data-i18n-html]").forEach((node) => { node.innerHTML = copy[node.dataset.i18nHtml] || node.innerHTML; });
  document.querySelectorAll(".language-current").forEach((node) => { node.textContent = locale === "zh" ? "中" : "EN"; });
  document.querySelectorAll(".language-alternate").forEach((node) => { node.textContent = locale === "zh" ? "EN" : "中"; });
  document.querySelectorAll('[data-action="toggle-language"]').forEach((button) => button.setAttribute("aria-label", locale === "zh" ? "Switch interface language to English" : "切換介面語言為中文"));
  const active = document.querySelector("[data-view].active")?.id;
  const viewTitle = document.querySelector("#view-title");
  if (active && viewTitle) viewTitle.textContent = copy.views[active];
  localizeStaticText();
}
const demoRegistry = { hardware: [{ id: "generic-diff-base", kind: "mobile-base", vendor: "Robot Dev AI", capability_ids: ["differential-drive"] }], drivers: [{ id: "generic-diff-driver", hardware_id: "generic-diff-base", ros_distro: "jazzy" }], capabilities: [{ id: "differential-drive", interface_ids: [], template_id: "differential-drive" }], packages: [{ id: "diff-drive-controller", required_capability_ids: ["differential-drive"] }], compatibility: [{ hardware_id: "generic-diff-base", package_id: "diff-drive-controller", status: "validated" }] };

function showResult(id, value, label = "API EVIDENCE") {
  const output = document.querySelector(`#${id}`);
  const error = Boolean(value?.error);
  output.replaceChildren();
  const card = document.createElement("article");
  card.className = `result-card${error ? " is-error" : ""}`;
  const header = document.createElement("header");
  header.append(document.createTextNode(label));
  const state = document.createElement("span");
  state.textContent = error ? "ACTION NEEDED" : "EVIDENCE READY";
  header.append(state);
  const pre = document.createElement("pre");
  pre.textContent = JSON.stringify(value, null, 2);
  card.append(header, pre);
  output.append(card);
}
async function request(path, options = {}) {
  const response = await fetch(`${api}${path}`, { headers: { "content-type": "application/json", ...(options.headers || {}) }, ...options });
  const body = await response.json().catch(() => ({ detail: "API did not return JSON evidence." }));
  if (!response.ok) throw new Error(body.detail || `API error ${response.status}`);
  return body;
}
function showError(id, error) { showResult(id, { error: error.message }, "API RESPONSE"); }
function showDesignPlan(plan) {
  const output = document.querySelector("#requirement-result"); output.replaceChildren();
  const card = document.createElement("article"); card.className = "design-plan card";
  const packages = plan.resolution?.package_ids || []; const templates = plan.templates || [];
  card.innerHTML = `<header><div><p class="eyebrow">VALIDATED DESIGN PLAN</p><h2>${plan.status}</h2></div><span class="pill">${plan.resolution?.status || "blocked"}</span></header><div class="design-plan-grid"><section><small>CAPABILITIES</small><div class="chip-row">${plan.requirements.specification.capability_ids.map((item) => `<span>${item}</span>`).join("")}</div></section><section><small>RECOMMENDED PACKAGES</small><ul>${packages.map((item) => `<li>${item}</li>`).join("")}</ul></section><section><small>TEMPLATE PREVIEWS</small><ul>${templates.map((item) => `<li>${item.template_id} · ${Object.keys(item.files).length} files</li>`).join("")}</ul></section></div><p class="design-plan-note">Preview only — no workspace has been generated. Continue to Build only after reviewing this plan.</p>`;
  output.append(card);
}
const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

function activateView(id) {
  document.querySelectorAll("[data-view]").forEach((view) => view.classList.toggle("active", view.id === id));
  document.querySelectorAll("[data-view-link]").forEach((link) => link.classList.toggle("active", link.dataset.viewLink === id));
  document.body.classList.toggle("is-landing", id === "landing");
  document.body.classList.toggle("is-control", id === "dashboard");
  syncHumanoidMotion(id === "landing");
  const viewTitle = document.querySelector("#view-title");
  if (viewTitle) viewTitle.textContent = translations[locale].views[id] || id;
  history.replaceState(null, "", `#${id}`);
  window.scrollTo({ top: 0, behavior: reducedMotion ? "auto" : "smooth" });
}
function syncHumanoidMotion(shouldRun) {
  document.body.classList.toggle("humanoid-motion-paused", !shouldRun || reducedMotion || document.hidden);
}
document.addEventListener("visibilitychange", () => syncHumanoidMotion(document.visibilityState === "visible" && document.body.classList.contains("is-landing")));
function setView(id) {
  if (!reducedMotion && document.startViewTransition) {
    document.startViewTransition(() => activateView(id));
  } else {
    activateView(id);
  }
}
function bindAction(selector, resultId, handler, label) {
  const target = document.querySelector(selector);
  if (!target) return;
  target.addEventListener("click", async (event) => {
    const button = event.currentTarget; const original = button.innerHTML;
    button.disabled = true; button.setAttribute("aria-busy", "true"); button.classList.add("is-working"); button.textContent = locale === "en" ? "Working…" : "處理中…";
    try { showResult(resultId, await handler(), label); } catch (error) { showError(resultId, error); }
    finally { button.disabled = false; button.removeAttribute("aria-busy"); button.classList.remove("is-working"); button.innerHTML = original; }
  });
}
function setText(id, text) {
  const target = document.querySelector(`#${id}`);
  if (!target || target.textContent === String(text)) return;
  target.textContent = text;
  if (!reducedMotion && target.closest(".metric, .health-indicator, .run-timeline")) {
    const surface = target.closest(".metric, .health-indicator, .run-timeline li");
    surface.classList.remove("is-updated");
    requestAnimationFrame(() => surface.classList.add("is-updated"));
    window.setTimeout(() => surface.classList.remove("is-updated"), 620);
  }
}
function setTimeline(stage, state, text) {
  const row = document.querySelector(`[data-stage="${stage}"]`);
  if (!row) return;
  row.dataset.state = state;
  row.querySelector("span").textContent = text;
}
function updateSimulation(snapshot) {
  const labels = locale === "zh" ? { online: "正常", partial: "部分資料可讀", unavailable: "目前無法讀取", onlineDetail: "個服務可正常讀取", partialDetail: "個服務可讀取，部分資料逾時", unavailableDetail: "請查看下方系統訊息", healthy: "模擬系統資料完整", partialHealth: "模擬系統只有部分資料", unavailableHealth: "目前無法讀取模擬系統", observed: "已讀取", partialTimeline: "部分可讀", unavailableTimeline: "無法讀取" } : { online: "Ready", partial: "Partially available", unavailable: "Unavailable", onlineDetail: "services are available", partialDetail: "services are available; some data timed out", unavailableDetail: "See the system message below", healthy: "Simulation data is available", partialHealth: "Only part of the simulation data is available", unavailableHealth: "Simulation data is unavailable", observed: "Available", partialTimeline: "Partial", unavailableTimeline: "Unavailable" };
  const commands = Object.values(snapshot.commands);
  const complete = commands.length > 0 && commands.every((command) => command.exit_code === 0) && snapshot.nodes.length > 0;
  const partial = !complete && snapshot.nodes.length > 0;
  const state = complete ? "healthy" : partial ? "partial" : "unavailable";
  setText("simulation-status", complete ? labels.online : partial ? labels.partial : labels.unavailable);
  setText("simulation-detail", complete ? `${snapshot.nodes.length} ${labels.onlineDetail}` : partial ? `${snapshot.nodes.length} ${labels.partialDetail}` : labels.unavailableDetail);
  setText("health-label", complete ? labels.healthy : partial ? labels.partialHealth : labels.unavailableHealth);
  document.querySelector("#health-dot").dataset.state = state;
  setText("runtime-nodes", snapshot.nodes.length);
  setText("runtime-topics", Object.keys(snapshot.topic_types).length);
  setText("runtime-tf", snapshot.tf_edges.length);
  setTimeline("runtime", complete ? "passed" : partial ? "partial" : "blocked", complete ? labels.observed : partial ? labels.partialTimeline : labels.unavailableTimeline);
  return complete;
}
function drawSimulationMap(frame) {
  const canvas = document.querySelector("#simulation-map");
  const context = canvas.getContext("2d");
  const { width, height } = canvas;
  context.clearRect(0, 0, width, height);
  context.fillStyle = "#091827";
  context.fillRect(0, 0, width, height);
  context.strokeStyle = "#29465c";
  context.lineWidth = 1;
  for (let x = 20; x < width; x += 48) { context.beginPath(); context.moveTo(x, 0); context.lineTo(x, height); context.stroke(); }
  for (let y = 18; y < height; y += 48) { context.beginPath(); context.moveTo(0, y); context.lineTo(width, y); context.stroke(); }
  context.strokeStyle = "#7693a2";
  context.lineWidth = 3;
  context.strokeRect(24, 22, width - 48, height - 44);
  context.fillStyle = "#29465c";
  context.fillRect(width * .62, height * .37, 70, 44);
  const scale = 52;
  const robotX = Math.max(42, Math.min(width - 42, width / 2 + frame.x_m * scale));
  const robotY = Math.max(40, Math.min(height - 40, height / 2 - frame.y_m * scale));
  context.save();
  context.translate(robotX, robotY);
  context.rotate(-frame.yaw_rad);
  context.fillStyle = "#59e1b4";
  context.strokeStyle = "#d9fff0";
  context.lineWidth = 2;
  context.beginPath(); context.moveTo(24, 0); context.lineTo(-16, -15); context.lineTo(-16, 15); context.closePath(); context.fill(); context.stroke();
  context.fillStyle = "#07111f";
  context.fillRect(-9, -22, 18, 6);
  context.restore();
  context.fillStyle = "#9db4bf";
  context.font = "11px system-ui";
  context.fillText("M4 virtual room · 1 grid = 1 m", 32, height - 12);
}
let frameRequestActive = false;
let mjpegActive = false;
function stopMjpegPreview() {
  if (!mjpegActive) return;
  const image = document.querySelector("#camera-frame");
  image.onload = null;
  image.onerror = null;
  image.removeAttribute("src");
  delete image.dataset.streamReady;
  mjpegActive = false;
}
function startMjpegPreview() {
  if (mjpegActive || !document.querySelector("#live-preview").checked) return;
  const image = document.querySelector("#camera-frame");
  const empty = document.querySelector("#camera-empty");
  mjpegActive = true;
  document.querySelector(".camera-stage")?.classList.add("is-refreshing");
  setText("camera-label", "Connecting live stream…");
  setText("camera-resolution", "MJPEG stream");
  setText("live-preview-label", "Live · MJPEG");
  image.onload = () => {
    if (image.dataset.streamReady) return;
    image.dataset.streamReady = "true";
    image.hidden = false;
    empty.hidden = true;
    setText("camera-label", `${image.naturalWidth} × ${image.naturalHeight} · live stream`);
    setText("camera-resolution", `${image.naturalWidth} × ${image.naturalHeight} MJPEG`);
    document.querySelector(".camera-stage")?.classList.remove("is-refreshing");
  };
  image.onerror = () => {
    stopMjpegPreview();
    image.hidden = true;
    empty.hidden = false;
    setText("camera-label", "Live stream unavailable");
    setText("camera-resolution", "No stream");
    setText("live-preview-label", "Live · off");
    document.querySelector(".camera-stage")?.classList.remove("is-refreshing");
  };
  image.src = "/api/v1/simulation/stream?source=webcam";
}
async function refreshSimulationFrame() {
  if (frameRequestActive) return;
  const source = document.querySelector("#camera-source")?.value || "isaac";
  if (source === "webcam") {
    startMjpegPreview();
    return;
  }
  stopMjpegPreview();
  frameRequestActive = true;
  document.querySelector(".camera-stage")?.classList.add("is-refreshing");
  try {
    const frame = await request(`/simulation/frame?source=${source}`);
    const image = document.querySelector("#camera-frame");
    image.src = `data:image/png;base64,${frame.image_png_base64}`;
    image.hidden = false;
    document.querySelector("#camera-empty").hidden = true;
    setText("camera-label", `${frame.width} × ${frame.height} · live`);
    setText("camera-resolution", `${frame.width} × ${frame.height} RGB8`);
    setText("camera-topic", frame.source_topic);
    setText("live-preview-label", "Live · 1s");
    setText("pose-label", frame.pose_available === false ? "Camera live · simulation pose unavailable" : `x ${frame.x_m.toFixed(2)} m · y ${frame.y_m.toFixed(2)} m · ${frame.yaw_rad.toFixed(2)} rad`);
    drawSimulationMap(frame);
  } catch (error) {
    setText("camera-label", "Camera unavailable");
    setText("camera-resolution", "No frame");
    document.querySelector("#camera-frame").hidden = true;
    document.querySelector("#camera-empty").hidden = false;
    setText("pose-label", error.message);
  } finally {
    frameRequestActive = false;
    document.querySelector(".camera-stage")?.classList.remove("is-refreshing");
  }
}
async function refreshSimulation() {
  try {
    const result = updateSimulation(await request("/runtime/snapshot"));
    refreshSimulationFrame();
    return result;
  } catch (error) {
    setText("simulation-status", "Unavailable");
    setText("simulation-detail", error.message);
    setText("health-label", "Could not collect runtime evidence");
    document.querySelector("#health-dot").dataset.state = "unavailable";
    setTimeline("runtime", "blocked", "Unavailable");
    return false;
  }
}
function updateFullRun(run) {
  const pipeline = run.pipeline;
  const buildPassed = pipeline.build_diagnosis?.category === "build-succeeded";
  setText("pipeline-status", pipeline.status);
  setText("pipeline-detail", run.workspace_lifecycle.replace("-", " "));
  setText("build-status", buildPassed ? "Succeeded" : "Blocked");
  setText("build-detail", buildPassed ? "Restricted package build passed" : (pipeline.issues?.[0] || "See run evidence"));
  setTimeline("requirements", "passed", "Passed");
  setTimeline("compatibility", pipeline.resolution?.compatible ? "passed" : "blocked", pipeline.resolution?.compatible ? "Passed" : "Blocked");
  setTimeline("generation", pipeline.templates.length ? "passed" : "blocked", pipeline.templates.length ? "Cleaned" : "Skipped");
  setTimeline("build", buildPassed ? "passed" : "blocked", buildPassed ? "Passed" : "Blocked");
  updateSimulation(run.runtime);
  if (run.validation) {
    setTimeline("validation", run.validation.status === "pass" ? "passed" : "blocked", run.validation.status);
  } else {
    setTimeline("validation", "", "Not requested");
  }
  setText("run-phase", pipeline.status.toUpperCase());
}
function renderEvidence(summary) {
  const target = document.querySelector("#evidence-summary");
  const record = summary.records[0];
  document.querySelector("#evidence-level").textContent = record?.evidence_level || "—";
  target.replaceChildren();
  if (!record) { target.textContent = "No recorded evidence."; return; }
  target.innerHTML = `<article><small>EVIDENCE LEVEL</small><strong>${record.evidence_level}</strong><p>${record.status.toUpperCase()} · trust ${record.source_trust}</p></article><article><small>RECORDED ENVIRONMENT</small><strong>${record.environment.os}</strong><p>${record.environment.ros_distro} · ${record.environment.cpu_arch}</p></article><article><small>PROVENANCE</small><strong>${record.provenance}</strong><p>${summary.coverage_levels.join(" · ")} coverage${summary.conflict_record_ids.length ? " · conflict recorded" : ""}</p></article>`;
  const pending = document.querySelector("#community-review-count");
  if (pending) pending.textContent = summary.pending_community_submission_ids.length ? (locale === "en" ? `${summary.pending_community_submission_ids.length} community reports need human review.` : `有 ${summary.pending_community_submission_ids.length} 筆社群資料等待人工確認。`) : (locale === "en" ? "No community reports waiting for review." : "目前沒有等待確認的社群資料。");
}
function renderEvidenceSnapshot(snapshot) {
  const target = document.querySelector("#evidence-snapshot");
  if (target) target.textContent = `${snapshot.snapshot_id.slice(0, 12)}… · ${snapshot.evidence_record_count} records`;
}
function appendEvidenceCell(row, value) {
  const cell = document.createElement("td");
  cell.textContent = value;
  row.append(cell);
}
function renderEvidenceOverview(overview) {
  const matrix = document.querySelector("#evidence-matrix");
  const count = document.querySelector("#evidence-matrix-count");
  matrix.replaceChildren();
  count.textContent = locale === "en" ? `${overview.coverage_matrix.length} known components` : `${overview.coverage_matrix.length} 個已知元件`;
  if (!overview.coverage_matrix.length) {
    const row = document.createElement("tr"); const cell = document.createElement("td");
    cell.colSpan = 4; cell.textContent = locale === "en" ? "No components are available to show." : "目前沒有可顯示的元件。"; row.append(cell); matrix.append(row);
  }
  overview.coverage_matrix.forEach((item) => {
    const row = document.createElement("tr");
    appendEvidenceCell(row, item.component_id);
    appendEvidenceCell(row, item.coverage_levels.join(" · ") || (locale === "en" ? "No record yet" : "尚無記錄"));
    appendEvidenceCell(row, String(item.record_count));
    const notices = [];
    if (item.conflict_record_ids.length) notices.push(locale === "en" ? "Results disagree" : "同一環境的結果不同");
    if (item.pending_community_submission_ids.length) notices.push(locale === "en" ? `${item.pending_community_submission_ids.length} waiting for review` : `${item.pending_community_submission_ids.length} 筆等待確認`);
    appendEvidenceCell(row, notices.join(locale === "en" ? "; " : "；") || (locale === "en" ? "None" : "沒有"));
    matrix.append(row);
  });
  const conflicts = document.querySelector("#evidence-conflicts");
  conflicts.replaceChildren();
  if (!overview.conflicts.length) {
    conflicts.textContent = locale === "en" ? "No results disagree in the same environment." : "目前沒有同一環境下互相矛盾的結果。";
  } else {
    overview.conflicts.forEach((conflict) => {
      const item = document.createElement("p");
      item.textContent = `${conflict.component_id}：${conflict.record_ids.join("、")}`;
      conflicts.append(item);
    });
  }
  const references = document.querySelector("#reference-robot-list");
  references.replaceChildren();
  if (!overview.reference_robots.length) {
    references.textContent = locale === "en" ? "No reference robot has been defined." : "尚未設定參考機器人。";
  }
  overview.reference_robots.forEach((reference) => {
    const item = document.createElement("article");
    const title = document.createElement("strong"); title.textContent = reference.display_name;
    const state = document.createElement("span"); state.textContent = reference.state === "planned" ? (locale === "en" ? "Planned — not verified yet" : "正在規劃，尚未實際驗證") : (locale === "en" ? "Evidence is available" : "已有對應資料");
    const detail = document.createElement("p"); detail.textContent = `${locale === "en" ? "Components" : "包含元件"}：${reference.component_ids.join(" · ")} · ${reference.provenance}`;
    item.append(title, state, detail); references.append(item);
  });
}
async function loadEvidenceViews() {
  const [summary, overview, snapshot] = await Promise.all([
    request("/evidence/generic-diff-base"), request("/evidence/overview"), request("/evidence/snapshot"),
  ]);
  renderEvidence(summary); renderEvidenceOverview(overview); renderEvidenceSnapshot(snapshot);
}
let registryCatalog = null;
function registryText(value) { return String(value || "—").replaceAll("-", " "); }
function renderSourceReview(review) {
  const target = document.querySelector("#source-review-result");
  target.replaceChildren();
  const title = document.createElement("strong");
  title.textContent = review.disposition === "sandbox-only" ? (locale === "en" ? "Can be checked in a safe test environment" : "目前只能在安全測試環境中檢查") : review.disposition === "blocked" ? (locale === "en" ? "This source is blocked" : "這個來源目前不能使用") : (locale === "en" ? "Information only" : "目前只能查看資料");
  const detail = document.createElement("p");
  detail.textContent = review.reasons.join(" ");
  target.append(title, detail);
}
async function reviewSource(sourceId) {
  try { renderSourceReview(await request(`/registry/sources/${sourceId}/review`)); }
  catch (error) { document.querySelector("#source-review-result").textContent = error.message; }
}
async function previewOnboarding(component) {
  const source = registryCatalog?.sources.find((item) => item.id === component.source_id);
  if (!source) return;
  const target = document.querySelector("#source-review-result");
  target.textContent = locale === "en" ? "Preparing a safe test plan…" : "正在準備安全測試計畫…";
  try {
    const plan = await request("/registry/onboarding/preview", { method: "POST", body: JSON.stringify({ component, source, requested_by: "local-operator" }) });
    target.replaceChildren();
    const title = document.createElement("strong");
    title.textContent = plan.status === "blocked" ? (locale === "en" ? "A safe test plan cannot be made for this source" : "這個來源目前不能建立安全測試計畫") : (locale === "en" ? "Safe test plan needs your confirmation" : "安全測試計畫等待你的確認");
    const detail = document.createElement("p");
    detail.textContent = plan.status === "blocked" ? plan.source_review.reasons.join(" ") : `預定步驟：${plan.sandbox_steps.join(" → ")}。目前沒有任何執行權限。`;
    target.append(title, detail);
    if (plan.status !== "blocked") {
      const authorize = document.createElement("button");
      authorize.type = "button"; authorize.className = "secondary"; authorize.textContent = locale === "en" ? "Record confirmation (do not run)" : "記錄確認（不執行）";
      authorize.addEventListener("click", async () => {
        authorize.disabled = true;
        try {
          const result = await request("/registry/onboarding/authorize-sandbox", { method: "POST", body: JSON.stringify({ transaction_id: plan.id, confirmed: true }) });
          title.textContent = "已記錄 sandbox runner 授權";
          detail.textContent = `${result.audit_record.recorded_at} 已寫入審計紀錄；主機沒有執行任何來源程式。`;
          authorize.remove();
        } catch (error) { detail.textContent = error.message; authorize.disabled = false; }
      });
      target.append(authorize);
    }
  } catch (error) { target.textContent = error.message; }
}
function renderRegistry() {
  const target = document.querySelector("#registry-catalog");
  if (!registryCatalog) return;
  const filter = document.querySelector("#registry-filter").value;
  const sources = new Map(registryCatalog.sources.map((source) => [source.id, source]));
  const components = registryCatalog.components.filter((component) => filter === "all" || component.kind === filter);
  target.replaceChildren();
  if (!components.length) { target.textContent = locale === "en" ? "No components match this filter." : "沒有符合這個篩選條件的元件。"; return; }
  components.forEach((component) => {
    const source = sources.get(component.source_id);
    const article = document.createElement("article"); article.className = "registry-row";
    const identity = document.createElement("div");
    const title = document.createElement("h2"); title.textContent = component.display_name;
    const meta = document.createElement("p"); meta.textContent = `${registryText(component.kind)} · ${registryText(component.version)}`;
    identity.append(title, meta);
    const state = document.createElement("span"); state.className = `lifecycle lifecycle-${component.lifecycle}`; state.textContent = registryText(component.lifecycle);
    const provenance = document.createElement("div"); provenance.className = "registry-source";
    provenance.textContent = `${source?.trust_level || "—"} trust · ${source?.license?.spdx || "license pending"}`;
    const actions = document.createElement("div"); actions.className = "registry-actions";
    const button = document.createElement("button"); button.type = "button"; button.className = "secondary"; button.textContent = locale === "en" ? "Review source" : "查看來源說明"; button.addEventListener("click", () => reviewSource(component.source_id));
    const preview = document.createElement("button"); preview.type = "button"; preview.className = "secondary"; preview.textContent = locale === "en" ? "Preview safe test plan" : "預覽安全測試計畫"; preview.addEventListener("click", () => previewOnboarding(component));
    actions.append(button, preview);
    article.append(identity, state, provenance, actions); target.append(article);
  });
}
async function loadRegistry() {
  try { registryCatalog = await request("/registry/management"); renderRegistry(); if (registryCatalog.components[0]) reviewSource(registryCatalog.components[0].source_id); }
  catch (error) { document.querySelector("#registry-catalog").textContent = error.message; }
}
async function loadSandboxReadiness() {
  try {
    const readiness = await request("/registry/sandbox/readiness");
    const title = document.querySelector("#sandbox-readiness");
    const detail = document.querySelector("#sandbox-readiness-detail");
    title.textContent = readiness.status === "available" ? `Sandbox runner：${readiness.runner} 可供測試` : readiness.status === "blocked" ? "Sandbox runner：已阻擋" : "Sandbox runner：尚未設定";
    detail.textContent = readiness.status === "available" ? "已偵測到 runner；仍需人工確認與隔離 self-test 通過後才能執行。" : readiness.issues.join(" ");
  } catch (error) { document.querySelector("#sandbox-readiness-detail").textContent = error.message; }
}
document.querySelectorAll("[data-view-link]").forEach((link) => link.addEventListener("click", (event) => { event.preventDefault(); setView(link.dataset.viewLink); }));
document.querySelectorAll("[data-go]").forEach((button) => button.addEventListener("click", () => setView(button.dataset.go)));
document.querySelectorAll('[data-action="toggle-language"]').forEach((button) => button.addEventListener("click", () => { locale = locale === "zh" ? "en" : "zh"; localStorage.setItem("robot-dev-ai-locale", locale); applyLocale(); }));
bindAction('[data-action="load-summary"]', "summary-result", () => request("/project/summary"), "PROJECT SNAPSHOT");
document.querySelector('[data-action="load-evidence"]').addEventListener("click", async () => {
  try { await loadEvidenceViews(); }
  catch (error) { document.querySelector("#evidence-summary").textContent = error.message; }
});
document.querySelector("#registry-filter")?.addEventListener("change", renderRegistry);
document.querySelector('[data-action="refresh-simulation"]').addEventListener("click", refreshSimulation);
document.querySelector('[data-action="refresh-camera"]').addEventListener("click", () => {
  if (document.querySelector("#camera-source").value === "webcam") stopMjpegPreview();
  refreshSimulationFrame();
});
document.querySelector("#camera-source").addEventListener("change", (event) => {
  const source = event.currentTarget.value;
  const webcam = source === "webcam";
  setText("camera-source-name", webcam ? "RealSense D455 · USB colour" : "Isaac Sim · M4 RGB camera");
  setText("camera-topic", webcam ? "/webcam/color/image_raw" : "/camera/image_raw");
  document.querySelectorAll("[data-camera-device]").forEach((card) => card.classList.toggle("active", card.dataset.cameraDevice === source));
  stopMjpegPreview();
  refreshSimulationFrame();
});
document.querySelector("#live-preview").addEventListener("change", (event) => {
  if (event.currentTarget.checked) refreshSimulationFrame();
  else stopMjpegPreview();
});
bindAction('[data-action="full-run"]', "full-run-result", async () => {
  const result = await request("/mvp/full-run", {
    method: "POST",
    body: JSON.stringify({
      natural_language: "我要建立一台 NVIDIA 差速機器車，LiDAR + Camera，能自主導航。",
      confirmed: true,
      include_validation: document.querySelector("#full-run-validation").checked,
    }),
  });
  updateFullRun(result);
  return result;
}, "FULL RUN EVIDENCE");
document.querySelector("#requirement-form").addEventListener("submit", async (event) => {
  event.preventDefault(); const button = event.currentTarget.querySelector("button[type=submit]"); button.disabled = true;
  try { showDesignPlan(await request("/design/plan", { method: "POST", body: JSON.stringify({ natural_language: document.querySelector("#requirement-input").value }) })); }
  catch (error) { showError("requirement-result", error); } finally { button.disabled = false; }
});
bindAction('[data-action="resolve-configuration"]', "configuration-result", () => request("/compatibility/resolve", { method: "POST", body: JSON.stringify({ registry: demoRegistry, request: { hardware_id: "generic-diff-base", specification: { capability_ids: ["differential-drive"] }, ros_distro: "jazzy", target_platform: "ubuntu-x86-64" } }) }), "COMPATIBILITY EVIDENCE");
bindAction('[data-action="preview-template"]', "configuration-result", () => request("/templates/preview", { method: "POST", body: JSON.stringify({ registry: demoRegistry, request: { hardware_id: "generic-diff-base", capability_id: "differential-drive", values: { package_name: "demo_robot", base_frame: "base_link", cmd_vel_topic: "/cmd_vel", wheel_radius_m: "0.05", wheel_separation_m: "0.30" } } }) }), "TEMPLATE PREVIEW");
bindAction('[data-action="runtime-snapshot"]', "runtime-result", () => request("/runtime/snapshot"), "READ-ONLY RUNTIME SNAPSHOT");
bindAction('[data-action="validate-navigation"]', "validation-result", async () => {
  if (!document.querySelector("#validation-confirm").checked) throw new Error("請先確認固定的 virtual navigation validation。");
  return request("/validation/m4-navigation", { method: "POST", body: JSON.stringify({ confirmed: true }) });
}, "FIXED SCENARIO VALIDATION");
bindAction('[data-action="propose-repair"]', "validation-result", () => request("/repairs/propose", { method: "POST", body: JSON.stringify({ path: "src/demo_robot/package.xml", contents: '<package format="3">\n  <name>demo_robot</name>\n</package>\n', missing_dependency: "geometry_msgs" }) }), "REPAIR PROPOSAL · REVIEW ONLY");
const initial = location.hash.slice(1);
const initialView = initial ? document.getElementById(initial) : null;
if (initialView?.matches("[data-view]")) {
  activateView(initial);
} else activateView("landing");
applyLocale();
loadEvidenceViews().catch((error) => { document.querySelector("#evidence-summary").textContent = error.message; });
loadRegistry();
loadSandboxReadiness();
refreshSimulation();
window.setInterval(() => {
  if (document.querySelector("#live-preview").checked && document.querySelector("#camera-source").value !== "webcam") refreshSimulationFrame();
}, 1000);
