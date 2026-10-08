import * as THREE from "three";

const host = document.querySelector("#hero-robot-3d");
const canvas = document.querySelector("#hero-robot-canvas");
const status = document.querySelector(".humanoid-pose");

if (host && canvas && window.WebGLRenderingContext) {
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, canvas, powerPreference: "high-performance" });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.12;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.domElement.setAttribute("role", "img");
  renderer.domElement.setAttribute("aria-label", "原創三維人形機器人，以獨立外置肩軸執行掃描、招手與移動展示。");

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(27, 1, .1, 40);
  camera.position.set(3.1, 1.0, 11.6);
  camera.lookAt(0, .45, 0);

  const key = new THREE.DirectionalLight(0xffffff, 4.6);
  key.position.set(3.5, 5.4, 4.5);
  key.castShadow = true;
  key.shadow.mapSize.set(1024, 1024);
  scene.add(key);
  scene.add(new THREE.HemisphereLight(0xaacbff, 0x05080e, 2.1));
  const rim = new THREE.DirectionalLight(0x75b7ff, 2.15);
  rim.position.set(-4, 3.6, -2.4);
  scene.add(rim);
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(16, 16), new THREE.ShadowMaterial({ color: 0x000000, opacity: .34 }));
  floor.rotation.x = -Math.PI / 2;
  floor.position.y = -2.04;
  floor.receiveShadow = true;
  scene.add(floor);

  const pearl = new THREE.MeshPhysicalMaterial({ color: 0xe7eef7, metalness: .31, roughness: .22, clearcoat: .64, clearcoatRoughness: .11 });
  const silver = new THREE.MeshPhysicalMaterial({ color: 0x9cacbf, metalness: .55, roughness: .25, clearcoat: .36 });
  const graphite = new THREE.MeshPhysicalMaterial({ color: 0x07101a, metalness: .78, roughness: .19, clearcoat: .5, clearcoatRoughness: .08 });
  const visor = new THREE.MeshPhysicalMaterial({ color: 0x01050a, metalness: .84, roughness: .06, clearcoat: 1, clearcoatRoughness: .03 });
  const signal = new THREE.MeshStandardMaterial({ color: 0xb7f4ff, emissive: 0x128cff, emissiveIntensity: 2.6, roughness: .24 });
  const robot = new THREE.Group();
  robot.rotation.y = -.3;
  scene.add(robot);

  const setShadow = (node) => { node.castShadow = true; node.receiveShadow = true; return node; };
  const mesh = (geometry, material, position = [0, 0, 0], scale = [1, 1, 1]) => {
    const node = setShadow(new THREE.Mesh(geometry, material));
    node.position.set(...position);
    node.scale.set(...scale);
    return node;
  };
  const sphere = (material, position, scale) => mesh(new THREE.SphereGeometry(1, 28, 20), material, position, scale);
  const capsule = (radius, length, material, position) => mesh(new THREE.CapsuleGeometry(radius, length, 8, 20), material, position);
  const roundedRect = (width, height, radius) => {
    const x = -width / 2;
    const y = -height / 2;
    const r = Math.min(radius, width / 2, height / 2);
    const shape = new THREE.Shape();
    shape.moveTo(x + r, y);
    shape.lineTo(x + width - r, y);
    shape.quadraticCurveTo(x + width, y, x + width, y + r);
    shape.lineTo(x + width, y + height - r);
    shape.quadraticCurveTo(x + width, y + height, x + width - r, y + height);
    shape.lineTo(x + r, y + height);
    shape.quadraticCurveTo(x, y + height, x, y + height - r);
    shape.lineTo(x, y + r);
    shape.quadraticCurveTo(x, y, x + r, y);
    return shape;
  };
  const shell = (width, height, depth, radius, material, position) => {
    const geometry = new THREE.ExtrudeGeometry(roundedRect(width, height, radius), {
      depth,
      bevelEnabled: true,
      bevelSegments: 3,
      bevelSize: Math.min(radius * .45, .06),
      bevelThickness: Math.min(depth * .18, .06),
      curveSegments: 16,
    });
    geometry.translate(0, 0, -depth / 2);
    return mesh(geometry, material, position);
  };

  // Original hard-surface silhouette: slim torso, external shoulder yokes, and recessed technical seams.
  const pelvis = new THREE.Group();
  pelvis.position.set(0, .12, 0);
  robot.add(pelvis);
  pelvis.add(shell(.94, .34, .52, .15, graphite, [0, 0, 0]));
  pelvis.add(shell(.62, .12, .035, .05, silver, [0, .02, .282]));
  robot.add(capsule(.23, .22, graphite, [0, .52, 0]));
  robot.add(shell(1.28, 1.08, .58, .25, pearl, [0, 1.23, 0]));
  robot.add(shell(.76, .58, .045, .19, graphite, [0, 1.25, .32]));
  robot.add(shell(.42, .035, .02, .01, signal, [0, 1.49, .355]));
  robot.add(shell(.48, .12, .38, .05, graphite, [0, 1.89, 0]));

  const head = new THREE.Group();
  head.position.set(0, 2.27, .02);
  robot.add(head);
  head.add(shell(1.02, .56, .65, .22, pearl, [0, 0, 0]));
  head.add(shell(.76, .2, .04, .09, visor, [0, -.02, .355]));
  head.add(shell(.59, .024, .014, .01, signal, [0, -.02, .388]));
  head.add(shell(.66, .075, .08, .03, silver, [0, .31, .02]));

  function makeArm(side) {
    const shoulder = new THREE.Group();
    shoulder.position.set(side * .91, 1.59, 0);
    robot.add(shoulder);
    shoulder.add(sphere(graphite, [0, 0, 0], [.205, .205, .205]));
    shoulder.add(shell(.31, .25, .44, .12, pearl, [side * .1, -.015, .01]));
    const upper = new THREE.Group();
    upper.position.set(0, -.19, 0);
    shoulder.add(upper);
    upper.add(capsule(.155, .55, pearl, [0, -.38, 0]));
    upper.add(sphere(graphite, [0, -.76, 0], [.14, .14, .14]));
    const forearm = new THREE.Group();
    forearm.position.set(0, -.79, 0);
    upper.add(forearm);
    forearm.add(capsule(.14, .5, silver, [0, -.34, 0]));
    forearm.add(shell(.23, .29, .2, .08, pearl, [0, -.76, .02]));
    return { shoulder, forearm };
  }
  const leftArm = makeArm(-1);
  const rightArm = makeArm(1);

  function makeLeg(side) {
    const hip = new THREE.Group();
    hip.position.set(side * .34, -.02, 0);
    pelvis.add(hip);
    hip.add(sphere(graphite, [0, 0, 0], [.18, .18, .18]));
    const thigh = new THREE.Group();
    thigh.position.set(0, -.18, 0);
    hip.add(thigh);
    thigh.add(shell(.31, .72, .34, .12, pearl, [0, -.39, 0]));
    thigh.add(sphere(graphite, [0, -.8, 0], [.17, .145, .17]));
    const shin = new THREE.Group();
    shin.position.set(0, -.84, 0);
    thigh.add(shin);
    shin.add(shell(.29, .67, .32, .1, silver, [0, -.38, .01]));
    shin.add(shell(.36, .16, .67, .08, pearl, [0, -.8, .16]));
    return { hip, shin };
  }
  const leftLeg = makeLeg(-1);
  const rightLeg = makeLeg(1);

  const labels = ["SYSTEM READY", "ENVIRONMENT SCAN", "FRIENDLY WAVE", "ACKNOWLEDGED", "MOBILITY CHECK", "READY STANCE"];
  const state = { headYaw: 0, headPitch: 0, leftArm: -.04, rightArm: .04, leftElbow: 0, rightElbow: 0, leftLeg: 0, rightLeg: 0, body: 0 };
  const target = { ...state };
  const clock = new THREE.Clock();
  let pose = 0;
  let started = 0;
  const active = () => document.body.classList.contains("is-landing") && !document.body.classList.contains("humanoid-motion-paused") && !document.hidden && !reducedMotion;
  const setPose = (now) => {
    const seconds = (now - started) / 1000;
    const rhythm = Math.sin(seconds * 3.4);
    Object.assign(target, { headYaw: 0, headPitch: 0, leftArm: -.04, rightArm: .04, leftElbow: 0, rightElbow: 0, leftLeg: 0, rightLeg: 0, body: 0 });
    if (pose === 1) target.headYaw = rhythm * .35;
    if (pose === 2) { target.rightArm = .94 + rhythm * .14; target.rightElbow = -.62; }
    if (pose === 3) target.headPitch = Math.sin(seconds * 4.2) * .13;
    if (pose === 4) { target.leftLeg = rhythm * .24; target.rightLeg = -rhythm * .24; target.leftArm = -rhythm * .13; target.rightArm = rhythm * .13; target.body = rhythm * .028; }
    if (pose === 5) { target.leftArm = -.13; target.rightArm = .13; target.body = .018; }
  };
  const resize = () => {
    const { width, height } = host.getBoundingClientRect();
    if (!width || !height) return;
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  };
  new ResizeObserver(resize).observe(host);
  resize();
  host.classList.add("is-ready");

  function render(now) {
    requestAnimationFrame(render);
    const delta = Math.min(clock.getDelta(), .05);
    if (active()) {
      if (!started) started = now;
      if (now - started > 3600) {
        pose = (pose + 1) % labels.length;
        started = now;
        if (status) status.textContent = labels[pose];
      }
      setPose(now);
      Object.keys(state).forEach((key) => { state[key] = THREE.MathUtils.damp(state[key], target[key], 5.5, delta); });
      head.rotation.set(state.headPitch, state.headYaw, 0);
      leftArm.shoulder.rotation.z = state.leftArm;
      rightArm.shoulder.rotation.z = state.rightArm;
      leftArm.forearm.rotation.z = state.leftElbow;
      rightArm.forearm.rotation.z = state.rightElbow;
      leftLeg.hip.rotation.x = state.leftLeg;
      rightLeg.hip.rotation.x = state.rightLeg;
      robot.rotation.z = state.body;
      robot.rotation.y = -.3 + Math.sin(now / 5400) * .03;
    }
    renderer.render(scene, camera);
  }
  requestAnimationFrame(render);
}
