import * as THREE from "three";

const host = document.querySelector("#hero-robot-3d");
const canvas = document.querySelector("#hero-robot-canvas");
const status = document.querySelector(".humanoid-pose");
if (host && canvas && window.WebGLRenderingContext) {
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, canvas, powerPreference: "high-performance" });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5)); renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.shadowMap.enabled = true; renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.domElement.setAttribute("role", "img"); renderer.domElement.setAttribute("aria-label", "原創三維人形機器人，持續執行掃描、招手與跨步動作。");
  const scene = new THREE.Scene(); const camera = new THREE.PerspectiveCamera(27, 1, .1, 40);
  camera.position.set(2.65, .78, 11.2); camera.lookAt(0, .42, 0);
  const key = new THREE.DirectionalLight(0xf4f8ff, 4.6); key.position.set(3.5, 5.5, 4.5); key.castShadow = true; scene.add(key);
  scene.add(new THREE.HemisphereLight(0xa3c9ff, 0x05080d, 2.25)); const rim = new THREE.DirectionalLight(0x5da9ff, 2.6); rim.position.set(-4, 3, -2); scene.add(rim);
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(16, 16), new THREE.ShadowMaterial({ color: 0x000000, opacity: .35 })); floor.rotation.x = -Math.PI / 2; floor.position.y = -1.9; floor.receiveShadow = true; scene.add(floor);
  const porcelain = new THREE.MeshPhysicalMaterial({ color: 0xe8eef5, metalness: .38, roughness: .2, clearcoat: .55, clearcoatRoughness: .14 });
  const graphite = new THREE.MeshPhysicalMaterial({ color: 0x101722, metalness: .62, roughness: .26, clearcoat: .25 });
  const visor = new THREE.MeshPhysicalMaterial({ color: 0x03070d, metalness: .78, roughness: .1, clearcoat: .9, clearcoatRoughness: .08 });
  const cyan = new THREE.MeshStandardMaterial({ color: 0x9be2ff, emissive: 0x169cff, emissiveIntensity: 3.4, roughness: .22 });
  const robot = new THREE.Group(); robot.rotation.y = -.34; scene.add(robot);
  const sphereG = new THREE.SphereGeometry(1, 32, 22), capsuleG = new THREE.CapsuleGeometry(.5, 1, 8, 20), jointG = new THREE.SphereGeometry(1, 20, 16), footG = new THREE.CapsuleGeometry(.5, .55, 6, 16);
  const mesh = (geometry, material, position, scale) => { const node = new THREE.Mesh(geometry, material); node.position.set(...position); node.scale.set(...scale); node.castShadow = true; node.receiveShadow = true; return node; };
  const shell = (position, scale) => mesh(sphereG, porcelain, position, scale), dark = (position, scale) => mesh(jointG, graphite, position, scale), capsule = (position, scale) => mesh(capsuleG, porcelain, position, scale);
  const abdomen = mesh(new THREE.CylinderGeometry(.42, .33, .72, 24, 2), graphite, [0, .82, 0], [1, 1, 1]); robot.add(abdomen);
  const pelvis = shell([0, .3, .02], [.61, .36, .34]); robot.add(pelvis); const chest = shell([0, 1.48, .02], [.74, .7, .42]); robot.add(chest);
  const core = shell([0, 1.04, .4], [.3, .22, .07]); core.material = graphite; robot.add(core); robot.add(dark([0, 2.2, 0], [.22, .18, .2]));
  const head = new THREE.Group(); head.position.set(0, 2.55, .02); robot.add(head); head.add(shell([0, 0, 0], [.66, .47, .5])); head.add(mesh(sphereG, visor, [0, -.02, .47], [.55, .23, .1])); const visorLine = mesh(new THREE.BoxGeometry(1, 1, 1), cyan, [0, -.02, .58], [.66, .026, .025]); head.add(visorLine);
  function makeArm(side) { const shoulder = new THREE.Group(); shoulder.position.set(side * .78, 1.72, 0); robot.add(shoulder); shoulder.add(dark([0, 0, 0], [.24, .24, .24])); shoulder.add(shell([side * .04, .02, 0], [.38, .22, .3])); const upper = new THREE.Group(); upper.position.set(0, -.2, 0); shoulder.add(upper); upper.add(capsule([0, -.32, 0], [.25, .48, .22])); upper.add(dark([0, -.68, 0], [.19, .19, .19])); const lower = new THREE.Group(); lower.position.set(0, -.7, 0); upper.add(lower); lower.add(capsule([0, -.3, .02], [.22, .48, .2])); lower.add(shell([0, -.71, .04], [.18, .22, .16])); return { shoulder, lower }; }
  const leftArm = makeArm(-1), rightArm = makeArm(1);
  function makeLeg(side) { const hip = new THREE.Group(); hip.position.set(side * .35, .28, 0); robot.add(hip); hip.add(dark([0, 0, 0], [.23, .22, .23])); const thigh = new THREE.Group(); thigh.position.set(0, -.18, 0); hip.add(thigh); thigh.add(mesh(new THREE.CylinderGeometry(.27, .22, .78, 24, 2), porcelain, [0, -.4, 0], [1, 1, 1])); thigh.add(dark([0, -.83, 0], [.2, .18, .2])); const shin = new THREE.Group(); shin.position.set(0, -.84, 0); thigh.add(shin); shin.add(mesh(new THREE.CylinderGeometry(.21, .28, .8, 24, 2), porcelain, [0, -.42, .02], [1, 1, 1])); shin.add(mesh(footG, porcelain, [0, -.92, .2], [.27, .18, .5])); return { hip, shin }; }
  const leftLeg = makeLeg(-1), rightLeg = makeLeg(1);
  const labels = ["SYSTEM READY", "ENVIRONMENT SCAN", "FRIENDLY WAVE", "ACKNOWLEDGED", "MOBILITY CHECK", "READY STANCE"];
  const state = { headYaw: 0, headPitch: 0, leftArm: 0, rightArm: 0, leftElbow: 0, rightElbow: 0, leftLeg: 0, rightLeg: 0, body: 0 }, target = { ...state }, clock = new THREE.Clock(); let pose = 0, started = 0;
  const active = () => document.body.classList.contains("is-landing") && !document.body.classList.contains("humanoid-motion-paused") && !document.hidden && !reducedMotion;
  const setPose = (now) => { const t = (now - started) / 1000, wave = Math.sin(t * 3.4); Object.assign(target, { headYaw: 0, headPitch: 0, leftArm: .04, rightArm: -.04, leftElbow: .05, rightElbow: -.05, leftLeg: 0, rightLeg: 0, body: 0 }); if (pose === 1) target.headYaw = wave * .42; if (pose === 2) { target.rightArm = -1.36 + wave * .2; target.rightElbow = .72; } if (pose === 3) target.headPitch = Math.sin(t * 4.4) * .17; if (pose === 4) { target.leftLeg = wave * .33; target.rightLeg = -wave * .33; target.leftArm = -wave * .2; target.rightArm = wave * .2; target.body = wave * .045; } if (pose === 5) { target.leftArm = .22; target.rightArm = -.22; target.body = .025; } };
  function resize() { const { width, height } = host.getBoundingClientRect(); if (!width || !height) return; renderer.setSize(width, height, false); camera.aspect = width / height; camera.updateProjectionMatrix(); }
  new ResizeObserver(resize).observe(host); resize(); host.classList.add("is-ready");
  function render(now) { requestAnimationFrame(render); const delta = Math.min(clock.getDelta(), .05); if (active()) { if (!started) started = now; if ((now - started) > 3600) { pose = (pose + 1) % labels.length; started = now; if (status) status.textContent = labels[pose]; } setPose(now); Object.keys(state).forEach((key) => { state[key] = THREE.MathUtils.damp(state[key], target[key], 5.5, delta); }); head.rotation.set(state.headPitch, state.headYaw, 0); leftArm.shoulder.rotation.z = state.leftArm; rightArm.shoulder.rotation.z = state.rightArm; leftArm.lower.rotation.z = state.leftElbow; rightArm.lower.rotation.z = state.rightElbow; leftLeg.hip.rotation.x = state.leftLeg; rightLeg.hip.rotation.x = state.rightLeg; robot.rotation.z = state.body; robot.rotation.y = -.34 + Math.sin(now / 5400) * .045; visorLine.material.emissiveIntensity = 2.8 + Math.sin(now / 430) * 1.1; } renderer.render(scene, camera); }
  requestAnimationFrame(render);
}
