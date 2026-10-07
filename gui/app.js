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
  document.querySelector(selector).addEventListener("click", async (event) => {
    const button = event.currentTarget; const original = button.innerHTML;
    button.disabled = true; button.textContent = "處理中…";
    try { showResult(resultId, await handler(), label); } catch (error) { showError(resultId, error); }
    finally { button.disabled = false; button.innerHTML = original; }
  });
}
document.querySelectorAll("[data-view-link]").forEach((link) => link.addEventListener("click", (event) => { event.preventDefault(); setView(link.dataset.viewLink); }));
document.querySelectorAll("[data-go]").forEach((button) => button.addEventListener("click", () => setView(button.dataset.go)));
bindAction('[data-action="load-summary"]', "summary-result", () => request("/project/summary"), "PROJECT SNAPSHOT");
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
