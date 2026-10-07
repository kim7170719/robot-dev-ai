const api = "/api/v1";

const demoRegistry = {
  hardware: [{
    id: "generic-diff-base",
    kind: "mobile-base",
    vendor: "Robot Dev AI",
    capability_ids: ["differential-drive"],
  }],
  drivers: [{
    id: "generic-diff-driver",
    hardware_id: "generic-diff-base",
    ros_distro: "jazzy",
  }],
  capabilities: [{
    id: "differential-drive",
    interface_ids: [],
    template_id: "differential-drive",
  }],
  packages: [{
    id: "diff-drive-controller",
    required_capability_ids: ["differential-drive"],
  }],
  compatibility: [{
    hardware_id: "generic-diff-base",
    package_id: "diff-drive-controller",
    status: "validated",
  }],
};

function showResult(id, value) {
  const output = document.querySelector(`#${id}`);
  output.replaceChildren();
  const pre = document.createElement("pre");
  pre.textContent = JSON.stringify(value, null, 2);
  output.append(pre);
}

async function request(path, options = {}) {
  const response = await fetch(`${api}${path}`, {
    headers: { "content-type": "application/json", ...(options.headers || {}) },
    ...options,
  });
  const body = await response.json().catch(() => ({ detail: "API returned no JSON" }));
  if (!response.ok) throw new Error(body.detail || `API error ${response.status}`);
  return body;
}

function bindAction(selector, resultId, handler) {
  document.querySelector(selector).addEventListener("click", async () => {
    try {
      showResult(resultId, await handler());
    } catch (error) {
      showResult(resultId, { error: error.message });
    }
  });
}

bindAction('[data-action="load-summary"]', "summary-result", () => request("/project/summary"));

document.querySelector("#requirement-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const natural_language = document.querySelector("#requirement-input").value;
  try {
    showResult("requirement-result", await request("/requirements/parse", {
      method: "POST", body: JSON.stringify({ natural_language }),
    }));
  } catch (error) {
    showResult("requirement-result", { error: error.message });
  }
});

bindAction('[data-action="resolve-configuration"]', "configuration-result", () => request("/compatibility/resolve", {
  method: "POST",
  body: JSON.stringify({
    registry: demoRegistry,
    request: {
      hardware_id: "generic-diff-base",
      specification: { capability_ids: ["differential-drive"] },
      ros_distro: "jazzy",
      target_platform: "ubuntu-x86-64",
    },
  }),
}));

bindAction('[data-action="preview-template"]', "configuration-result", () => request("/templates/preview", {
  method: "POST",
  body: JSON.stringify({
    registry: demoRegistry,
    request: {
      hardware_id: "generic-diff-base",
      capability_id: "differential-drive",
      values: { package_name: "demo_robot" },
    },
  }),
}));

bindAction('[data-action="runtime-snapshot"]', "runtime-result", () => request("/runtime/snapshot"));

bindAction('[data-action="validate-navigation"]', "validation-result", async () => {
  if (!document.querySelector("#validation-confirm").checked) {
    throw new Error("Confirm the fixed virtual validation before running it.");
  }
  return request("/validation/m4-navigation", {
    method: "POST", body: JSON.stringify({ confirmed: true }),
  });
});

bindAction('[data-action="propose-repair"]', "validation-result", () => request("/repairs/propose", {
  method: "POST",
  body: JSON.stringify({
    path: "src/demo_robot/package.xml",
    contents: '<package format="3">\n  <name>demo_robot</name>\n</package>\n',
    missing_dependency: "geometry_msgs",
  }),
}));
