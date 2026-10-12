import * as THREE from "three";
import { GLTFLoader } from "./vendor/addons/loaders/GLTFLoader.js";
import { MeshoptDecoder } from "./vendor/addons/libs/meshopt_decoder.module.js";

const host = document.querySelector("#hero-robot-3d");
const canvas = document.querySelector("#hero-robot-canvas");
const status = document.querySelector(".humanoid-pose");
const loading = document.querySelector(".hero-robot-loading");

if (host && canvas && window.WebGLRenderingContext) {
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, canvas, powerPreference: "high-performance" });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.25));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.12;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  renderer.domElement.setAttribute("role", "img");
  renderer.domElement.setAttribute("aria-label", "三維人形機器人展示，可用滑鼠或觸控移動視角。載入失敗時使用本機原創備援模型。");

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

  const pearl = new THREE.MeshPhysicalMaterial({ color: 0xf2f1ee, metalness: .16, roughness: .18, clearcoat: .85, clearcoatRoughness: .08 });
  const silver = new THREE.MeshPhysicalMaterial({ color: 0xbfc2c4, metalness: .62, roughness: .21, clearcoat: .42 });
  const graphite = new THREE.MeshPhysicalMaterial({ color: 0x0a0b0e, metalness: .62, roughness: .3, clearcoat: .35, clearcoatRoughness: .13 });
  const visor = new THREE.MeshPhysicalMaterial({ color: 0x01050a, metalness: .84, roughness: .06, clearcoat: 1, clearcoatRoughness: .03 });
  const signal = new THREE.MeshStandardMaterial({ color: 0xb7f4ff, emissive: 0x128cff, emissiveIntensity: 2.6, roughness: .24 });
  const robot = new THREE.Group();
  robot.rotation.y = -.3;
  scene.add(robot);
  let referenceRig = null;
  const pointer = { x: 0, y: 0, targetX: 0, targetY: 0 };

  const setShadow = (node) => { node.castShadow = true; node.receiveShadow = true; return node; };
  const mesh = (geometry, material, position = [0, 0, 0], scale = [1, 1, 1]) => {
    const node = setShadow(new THREE.Mesh(geometry, material));
    node.position.set(...position);
    node.scale.set(...scale);
    return node;
  };
  const sphere = (material, position, scale) => mesh(new THREE.SphereGeometry(1, 28, 20), material, position, scale);
  const capsule = (radius, length, material, position) => mesh(new THREE.CapsuleGeometry(radius, length, 8, 20), material, position);
  const cylinder = (top, bottom, height, material, position, rotation = [0, 0, 0]) => {
    const node = mesh(new THREE.CylinderGeometry(top, bottom, height, 28, 2), material, position);
    node.rotation.set(...rotation);
    return node;
  };
  const torus = (radius, tube, material, position, rotation = [0, 0, 0]) => {
    const node = mesh(new THREE.TorusGeometry(radius, tube, 10, 36), material, position);
    node.rotation.set(...rotation);
    return node;
  };
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

  // Reference-derived original silhouette: ceramic shell, exposed flexible joints, cyan visor seam.
  const pelvis = new THREE.Group();
  pelvis.position.set(0, .12, 0);
  robot.add(pelvis);
  pelvis.add(shell(1.04, .38, .62, .16, graphite, [0, 0, 0]));
  pelvis.add(shell(.77, .18, .09, .07, pearl, [0, .01, .32]));
  pelvis.add(shell(.42, .27, .67, .09, pearl, [0, -.02, .02]));
  robot.add(cylinder(.24, .27, .42, graphite, [0, .55, 0]));
  [-.13, 0, .13].forEach((y) => robot.add(torus(.245, .034, silver, [0, .55 + y, 0], [Math.PI / 2, 0, 0])));
  robot.add(sphere(pearl, [0, 1.28, -.015], [.77, .68, .34]));
  robot.add(shell(1.3, .5, .22, .18, pearl, [0, 1.42, .18]));
  robot.add(shell(.73, .52, .07, .12, pearl, [0, 1.04, .35]));
  robot.add(shell(.42, .035, .02, .01, signal, [0, 1.34, .405]));
  robot.add(shell(.54, .11, .4, .05, graphite, [0, 1.9, 0]));

  const head = new THREE.Group();
  head.position.set(0, 2.34, .02);
  robot.add(head);
  head.add(sphere(pearl, [0, .04, -.01], [.56, .47, .42]));
  head.add(shell(.9, .35, .12, .11, pearl, [0, -.11, .31]));
  head.add(shell(.74, .22, .04, .055, visor, [0, -.07, .43]));
  head.add(shell(.67, .023, .016, .01, signal, [0, -.065, .462]));
  head.add(shell(.55, .18, .12, .055, pearl, [0, -.31, .31]));
  [-1, 1].forEach((side) => {
    head.add(cylinder(.16, .16, .105, graphite, [side * .55, .01, .01], [0, 0, Math.PI / 2]));
    head.add(cylinder(.105, .105, .116, silver, [side * .605, .01, .01], [0, 0, Math.PI / 2]));
  });

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
    const hand = new THREE.Group();
    hand.position.set(0, -.96, .02);
    forearm.add(hand);
    hand.add(sphere(graphite, [0, -.08, 0], [.14, .19, .105]));
    [-.075, -.025, .025, .075].forEach((offset) => {
      const finger = capsule(.022, .16, silver, [offset, -.22, .015]);
      finger.rotation.z = side * -.08;
      hand.add(finger);
    });
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
    thigh.add(shell(.21, .48, .055, .07, pearl, [0, -.39, .2]));
    thigh.add(sphere(graphite, [0, -.8, 0], [.17, .145, .17]));
    const shin = new THREE.Group();
    shin.position.set(0, -.84, 0);
    thigh.add(shin);
    shin.add(shell(.29, .67, .32, .1, silver, [0, -.38, .01]));
    shin.add(shell(.33, .72, .11, .1, pearl, [0, -.39, .18]));
    shin.add(sphere(graphite, [0, -.79, .02], [.15, .14, .15]));
    shin.add(shell(.39, .19, .72, .08, pearl, [0, -.91, .2]));
    return { hip, shin };
  }
  const leftLeg = makeLeg(-1);
  const rightLeg = makeLeg(1);

  const labels = ["SYSTEM READY", "ENVIRONMENT SCAN", "ACKNOWLEDGED", "MOBILITY CHECK", "READY STANCE"];
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
    if (pose === 2) target.headPitch = Math.sin(seconds * 4.2) * .13;
    if (pose === 3) { target.leftLeg = rhythm * .24; target.rightLeg = -rhythm * .24; target.leftArm = -rhythm * .13; target.rightArm = rhythm * .13; target.body = rhythm * .028; }
    if (pose === 4) { target.leftArm = -.13; target.rightArm = .13; target.body = .018; }
  };
  const resize = () => {
    const { width, height } = host.getBoundingClientRect();
    if (!width || !height) return;
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  };
  new ResizeObserver(resize).observe(host);
  host.addEventListener("pointermove", (event) => {
    const bounds = host.getBoundingClientRect();
    pointer.targetX = THREE.MathUtils.clamp(((event.clientX - bounds.left) / bounds.width - .5) * 2, -1, 1);
    pointer.targetY = THREE.MathUtils.clamp(((event.clientY - bounds.top) / bounds.height - .5) * 2, -1, 1);
  });
  host.addEventListener("pointerleave", () => {
    pointer.targetX = 0;
    pointer.targetY = 0;
  });
  resize();
  host.classList.add("is-ready");

  const activateReferenceModel = (gltf) => {
    const model = gltf.scene;
    const bounds = new THREE.Box3().setFromObject(model);
    const size = bounds.getSize(new THREE.Vector3());
    const center = bounds.getCenter(new THREE.Vector3());
    const targetHeight = 4.15;
    const scale = targetHeight / size.y;

    referenceRig = new THREE.Group();
    model.position.set(-center.x, -bounds.min.y, -center.z);
    referenceRig.add(model);
    referenceRig.scale.setScalar(scale);
    referenceRig.position.set(0, floor.position.y + .02, 0);
    referenceRig.rotation.y = -.35;
    model.traverse((node) => {
      if (node.isMesh) {
        node.castShadow = true;
        node.receiveShadow = true;
      }
    });
    scene.add(referenceRig);
    robot.visible = false;
    if (status) status.textContent = "REFERENCE MODEL READY";
    if (loading) loading.textContent = "REFERENCE MODEL READY";
  };

  const loader = new GLTFLoader();
  loader.setMeshoptDecoder(MeshoptDecoder);
  loader.load(
    "./assets/humanoid-reference.glb",
    activateReferenceModel,
    (event) => {
      if (loading && event.total) loading.textContent = `LOADING REFERENCE ${Math.round((event.loaded / event.total) * 100)}%`;
    },
    (error) => {
      console.warn("Reference GLB did not load; keeping the local procedural fallback.", error);
      if (status) status.textContent = "LOCAL MODEL READY";
      if (loading) loading.textContent = "LOCAL MODEL READY";
    },
  );

  function render(now) {
    requestAnimationFrame(render);
    const delta = Math.min(clock.getDelta(), .05);
    if (active()) {
      pointer.x = THREE.MathUtils.damp(pointer.x, pointer.targetX, 4.5, delta);
      pointer.y = THREE.MathUtils.damp(pointer.y, pointer.targetY, 4.5, delta);
      if (referenceRig) {
        referenceRig.rotation.y = -.35 + Math.sin(now / 7200) * .055 + pointer.x * .16;
        referenceRig.rotation.x = pointer.y * -.035;
        referenceRig.position.y = floor.position.y + .02 + Math.sin(now / 2100) * .018;
      } else {
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
    }
    renderer.render(scene, camera);
  }
  requestAnimationFrame(render);
}
