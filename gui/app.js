const api = "/api/v1";
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
function setView(id) {
  document.querySelectorAll("[data-view]").forEach((view) => view.classList.toggle("active", view.id === id));
  document.querySelectorAll("[data-view-link]").forEach((link) => link.classList.toggle("active", link.dataset.viewLink === id));
  document.querySelector("#view-title").textContent = document.querySelector(`#${id} h1, #${id} h2`)?.textContent || id;
  history.replaceState(null, "", `#${id}`);
  window.scrollTo({ top: 0, behavior: "smooth" });
}
function bindAction(selector, resultId, handler, label) {
  const target = document.querySelector(selector);
  if (!target) return;
  target.addEventListener("click", async (event) => {
    const button = event.currentTarget; const original = button.innerHTML;
    button.disabled = true; button.textContent = "處理中…";
    try { showResult(resultId, await handler(), label); } catch (error) { showError(resultId, error); }
    finally { button.disabled = false; button.innerHTML = original; }
  });
}
function setText(id, text) { document.querySelector(`#${id}`).textContent = text; }
function setTimeline(stage, state, text) {
  const row = document.querySelector(`[data-stage="${stage}"]`);
  row.dataset.state = state;
  row.querySelector("span").textContent = text;
}
function updateSimulation(snapshot) {
  const commands = Object.values(snapshot.commands);
  const complete = commands.length > 0 && commands.every((command) => command.exit_code === 0) && snapshot.nodes.length > 0;
  const partial = !complete && snapshot.nodes.length > 0;
  const state = complete ? "healthy" : partial ? "partial" : "unavailable";
  setText("simulation-status", complete ? "Online" : partial ? "Partial" : "Unavailable");
  setText("simulation-detail", complete ? `${snapshot.nodes.length} nodes detected` : partial ? `${snapshot.nodes.length} nodes; some evidence timed out` : "Read command evidence for details");
  setText("health-label", complete ? "Simulation runtime is fully observable" : partial ? "Simulation graph is partially observable" : "Runtime evidence is unavailable");
  document.querySelector("#health-dot").dataset.state = state;
  setText("runtime-nodes", snapshot.nodes.length);
  setText("runtime-topics", Object.keys(snapshot.topic_types).length);
  setText("runtime-tf", snapshot.tf_edges.length);
  setTimeline("runtime", complete ? "passed" : partial ? "partial" : "blocked", complete ? "Observed" : partial ? "Partial" : "Unavailable");
  return complete;
}
async function refreshSimulation() {
  try {
    return updateSimulation(await request("/runtime/snapshot"));
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
bindAction('[data-action="load-summary"]', "summary-result", () => request("/project/summary"), "PROJECT SNAPSHOT");
document.querySelector('[data-action="refresh-simulation"]').addEventListener("click", refreshSimulation);
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
  try { showResult("requirement-result", await request("/requirements/parse", { method: "POST", body: JSON.stringify({ natural_language: document.querySelector("#requirement-input").value }) }), "STRUCTURED REQUIREMENT"); }
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
if (document.querySelector(`#${initial}[data-view]`)) setView(initial);
refreshSimulation();
