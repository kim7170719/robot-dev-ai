import * as THREE from "three";

const host = document.querySelector("#hero-robot-3d");
const canvas = document.querySelector("#hero-robot-canvas");
const status = document.querySelector(".humanoid-pose");

if (host && canvas && window.WebGLRenderingContext) {
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, canvas, powerPreference: "high-performance" });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.domElement.setAttribute("role", "img");
  renderer.domElement.setAttribute("aria-label", "原創三維人形機器人，以外置肩軸執行掃描、招手與移動展示。");

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(26, 1, .1, 40);
  camera.position.set(2.95, .86, 11.7);
  camera.lookAt(0, .38, 0);
  const key = new THREE.DirectionalLight(0xf6f9ff, 4.8);
  key.position.set(3.5, 5.5, 4.5);
  key.castShadow = true;
  key.shadow.mapSize.set(1024, 1024);
  scene.add(key);
  scene.add(new THREE.HemisphereLight(0x9fc8ff, 0x04070c, 2.15));
  const rim = new THREE.DirectionalLight(0x58a9ff, 2.4);
  rim.position.set(-4, 3.5, -2);
  scene.add(rim);
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(16, 16), new THREE.ShadowMaterial({ color: 0x000000, opacity: .35 }));
  floor.rotation.x = -Math.PI / 2;
  floor.position.y = -1.93;
  floor.receiveShadow = true;
  scene.add(floor);

  const ceramic = new THREE.MeshPhysicalMaterial({ color: 0xe4ebf5, metalness: .34, roughness: .24, clearcoat: .6, clearcoatRoughness: .12 });
  const ceramicDark = new THREE.MeshPhysicalMaterial({ color: 0xaebdd0, metalness: .48, roughness: .26, clearcoat: .48 });
  const graphite = new THREE.MeshPhysicalMaterial({ color: 0x090f18, metalness: .72, roughness: .21, clearcoat: .32 });
  const visor = new THREE.MeshPhysicalMaterial({ color: 0x02060d, metalness: .82, roughness: .08, clearcoat: .92, clearcoatRoughness: .06 });
  const cyan = new THREE.MeshStandardMaterial({ color: 0xa8eeff, emissive: 0x138dff, emissiveIntensity: 3.2, roughness: .22 });
  const robot = new THREE.Group();
  robot.rotation.y = -.31;
  scene.add(robot);
  const sphere = new THREE.SphereGeometry(1, 28, 20);
  const joint = new THREE.SphereGeometry(1, 20, 16);
  const capsule = new THREE.CapsuleGeometry(.5, 1, 8, 18);
  const mesh = (geometry, material, position, scale = [1, 1, 1]) => {
    const node = new THREE.Mesh(geometry, material);
    node.position.set(...position);
    node.scale.set(...scale);
    node.castShadow = true;
    node.receiveShadow = true;
    return node;
  };
  const orb = (material, position, scale) => mesh(sphere, material, position, scale);
  const tube = (material, position, scale) => mesh(capsule, material, position, scale);
  const box = (size, material, position, scale = [1, 1, 1]) => mesh(new THREE.BoxGeometry(...size), material, position, scale);
  const plate = (points, depth, material, position) => {
    const profile = new THREE.Shape();
    profile.moveTo(...points[0]);
    points.slice(1).forEach((point) => profile.lineTo(...point));
    profile.closePath();
    return mesh(new THREE.ExtrudeGeometry(profile, { depth, bevelEnabled: true, bevelSize: .055, bevelThickness: .05, bevelSegments: 2, curveSegments: 12 }), material, position);
  };

  // A broad faceted thorax and a narrow waist deliberately replace the former toy-like sphere stack.
  robot.add(plate([[-.78, -.46], [.78, -.46], [.61, .56], [.34, .7], [-.34, .7], [-.61, .56]], .5, ceramic, [0, 1.04, -.25]));
  robot.add(orb(graphite, [0, 1.18, .285], [.36, .42, .065]));
  robot.add(box([.5, .04, .025], cyan, [0, 1.46, .365]));
  robot.add(tube(graphite, [0, .5, .01], [.38, .34, .3]));
  robot.add(orb(ceramicDark, [-.37, .09, -.02], [.31, .24, .29]));
  robot.add(orb(ceramicDark, [.37, .09, -.02], [.31, .24, .29]));
  robot.add(orb(graphite, [0, 1.91, 0], [.22, .16, .18]));

  const head = new THREE.Group();
  head.position.set(0, 2.28, .03);
  robot.add(head);
  head.add(orb(ceramic, [0, 0, 0], [.66, .4, .48]));
  head.add(orb(visor, [0, -.02, .45], [.55, .18, .075]));
  head.add(box([.64, .026, .025], cyan, [0, -.02, .53]));
  head.add(box([.66, .06, .08], ceramicDark, [0, .36, .03]));

  function makeArm(side) {
    const shoulder = new THREE.Group();
    shoulder.position.set(side * 1.03, 1.54, .01);
    robot.add(shoulder);
    shoulder.add(mesh(joint, graphite, [0, 0, 0], [.235, .235, .235]));
    shoulder.add(orb(ceramic, [side * .065, .01, .02], [.37, .18, .265]));
    const upper = new THREE.Group();
    upper.position.set(0, -.17, .01);
    shoulder.add(upper);
    upper.add(tube(ceramic, [0, -.42, 0], [.19, .43, .18]));
    upper.add(mesh(joint, graphite, [0, -.87, 0], [.16, .16, .16]));
    const forearm = new THREE.Group();
    forearm.position.set(0, -.89, 0);
    upper.add(forearm);
    forearm.add(tube(ceramicDark, [0, -.39, .01], [.17, .4, .16]));
    forearm.add(orb(ceramic, [0, -.8, .03], [.16, .23, .14]));
    return { shoulder, forearm };
  }
  const leftArm = makeArm(-1);
  const rightArm = makeArm(1);

  function makeLeg(side) {
    const hip = new THREE.Group();
    hip.position.set(side * .39, .06, 0);
    robot.add(hip);
    hip.add(mesh(joint, graphite, [0, 0, 0], [.21, .2, .2]));
    const thigh = new THREE.Group();
    thigh.position.set(0, -.16, 0);
    hip.add(thigh);
    thigh.add(tube(ceramic, [0, -.42, 0], [.27, .39, .23]));
    thigh.add(mesh(joint, graphite, [0, -.83, 0], [.2, .17, .2]));
    const shin = new THREE.Group();
    shin.position.set(0, -.86, 0);
    thigh.add(shin);
    shin.add(tube(ceramicDark, [0, -.42, .02], [.25, .43, .22]));
    shin.add(orb(ceramic, [0, -.91, .21], [.31, .16, .5]));
    return { hip, shin };
  }
  const leftLeg = makeLeg(-1);
  const rightLeg = makeLeg(1);

  const labels = ["SYSTEM READY", "ENVIRONMENT SCAN", "FRIENDLY WAVE", "ACKNOWLEDGED", "MOBILITY CHECK", "READY STANCE"];
  const state = { headYaw: 0, headPitch: 0, leftArm: 0, rightArm: 0, leftElbow: 0, rightElbow: 0, leftLeg: 0, rightLeg: 0, body: 0 };
  const target = { ...state };
  const clock = new THREE.Clock();
  let pose = 0;
  let started = 0;
  const active = () => document.body.classList.contains("is-landing") && !document.body.classList.contains("humanoid-motion-paused") && !document.hidden && !reducedMotion;
  const setPose = (now) => {
    const seconds = (now - started) / 1000;
    const rhythm = Math.sin(seconds * 3.4);
    Object.assign(target, { headYaw: 0, headPitch: 0, leftArm: -.06, rightArm: .06, leftElbow: 0, rightElbow: 0, leftLeg: 0, rightLeg: 0, body: 0 });
    if (pose === 1) target.headYaw = rhythm * .38;
    if (pose === 2) { target.rightArm = 1.2 + rhythm * .16; target.rightElbow = -.55; }
    if (pose === 3) target.headPitch = Math.sin(seconds * 4.2) * .15;
    if (pose === 4) { target.leftLeg = rhythm * .28; target.rightLeg = -rhythm * .28; target.leftArm = -rhythm * .18; target.rightArm = rhythm * .18; target.body = rhythm * .035; }
    if (pose === 5) { target.leftArm = -.16; target.rightArm = .16; target.body = .02; }
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
      robot.rotation.y = -.31 + Math.sin(now / 5400) * .035;
    }
    renderer.render(scene, camera);
  }
  requestAnimationFrame(render);
}
