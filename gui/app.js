const api = "/api/v1";
const translations = {
  zh: { "nav.overview": "概覽", "nav.design": "設計", "nav.build": "建置", "nav.run": "運行", "nav.diagnose": "診斷", "chrome.safety": "安全邊界啟用中", "landing.kicker": "設計、驗證、模擬", "landing.title": "讓第一台機器人<br>先在虛擬世界醒來。", "landing.summary": "從自然語言需求出發，建立具備 LiDAR、Camera 與導航能力的差速機器人；每個動作都先在可審閱的安全邊界內完成。", "landing.enter": "進入工作區", "landing.direct": "直接建立方案", "landing.status": "Virtual-first robot development", "overview.title": "從想法到機器人", "overview.summary": "先告訴我們你想做的機器人；我們會整理可行建議，確認後才會建立專案。", "overview.design": "開始規劃", "overview.runtime": "查看目前狀態", views: { landing: "首頁", dashboard: "概覽", requirement: "設計", configuration: "建置", runtime: "運行", validation: "診斷" } },
  en: { "nav.overview": "Overview", "nav.design": "Design", "nav.build": "Build", "nav.run": "Run", "nav.diagnose": "Diagnose", "chrome.safety": "Safety boundary active", "landing.kicker": "DESIGN · VALIDATE · SIMULATE", "landing.title": "Let your first robot<br>wake up virtually.", "landing.summary": "Start with a natural-language request and build a differential-drive robot with LiDAR, camera, and navigation—each action remains within a reviewable safety boundary.", "landing.enter": "Enter workspace", "landing.direct": "Create a design plan", "landing.status": "Virtual-first robot development", "overview.title": "From idea to robot", "overview.summary": "Tell us what you want to build. We will organise practical suggestions before anything is created.", "overview.design": "Start planning", "overview.runtime": "View current status", views: { landing: "Home", dashboard: "Overview", requirement: "Design", configuration: "Build", runtime: "Run", validation: "Diagnose" } },
};
let locale = localStorage.getItem("robot-dev-ai-locale") === "en" ? "en" : "zh";
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
    button.disabled = true; button.setAttribute("aria-busy", "true"); button.classList.add("is-working"); button.textContent = "處理中…";
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
async function refreshSimulationFrame() {
  if (frameRequestActive) return;
  frameRequestActive = true;
  document.querySelector(".camera-stage")?.classList.add("is-refreshing");
  try {
    const source = document.querySelector("#camera-source")?.value || "isaac";
    const frame = await request(`/simulation/frame?source=${source}`);
    const image = document.querySelector("#camera-frame");
    image.src = `data:image/png;base64,${frame.image_png_base64}`;
    image.hidden = false;
    document.querySelector("#camera-empty").hidden = true;
    setText("camera-label", `${frame.width} × ${frame.height} · live`);
    setText("camera-resolution", `${frame.width} × ${frame.height} RGB8`);
    setText("camera-topic", frame.source_topic);
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
document.querySelectorAll("[data-view-link]").forEach((link) => link.addEventListener("click", (event) => { event.preventDefault(); setView(link.dataset.viewLink); }));
document.querySelectorAll("[data-go]").forEach((button) => button.addEventListener("click", () => setView(button.dataset.go)));
document.querySelectorAll('[data-action="toggle-language"]').forEach((button) => button.addEventListener("click", () => { locale = locale === "zh" ? "en" : "zh"; localStorage.setItem("robot-dev-ai-locale", locale); applyLocale(); }));
bindAction('[data-action="load-summary"]', "summary-result", () => request("/project/summary"), "PROJECT SNAPSHOT");
document.querySelector('[data-action="refresh-simulation"]').addEventListener("click", refreshSimulation);
document.querySelector('[data-action="refresh-camera"]').addEventListener("click", refreshSimulationFrame);
document.querySelector("#camera-source").addEventListener("change", (event) => {
  const source = event.currentTarget.value;
  const webcam = source === "webcam";
  setText("camera-source-name", webcam ? "RealSense D455 · USB colour" : "Isaac Sim · M4 RGB camera");
  setText("camera-topic", webcam ? "/webcam/color/image_raw" : "/camera/image_raw");
  document.querySelectorAll("[data-camera-device]").forEach((card) => card.classList.toggle("active", card.dataset.cameraDevice === source));
  refreshSimulationFrame();
});
document.querySelector("#live-preview").addEventListener("change", (event) => { if (event.currentTarget.checked) refreshSimulationFrame(); });
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
refreshSimulation();
window.setInterval(() => { if (document.querySelector("#live-preview").checked) refreshSimulationFrame(); }, 1000);
