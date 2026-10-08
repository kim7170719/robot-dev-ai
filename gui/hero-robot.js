import * as THREE from "three";
import { GLTFLoader } from "./vendor/loaders/GLTFLoader.js";

const host = document.querySelector("#hero-robot-3d");
const canvas = document.querySelector("#hero-robot-canvas");
if (host && canvas && window.WebGLRenderingContext) {
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, canvas, powerPreference: "high-performance" });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1.5));
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(30, 1, 0.1, 100);
  camera.position.set(0, 0.7, 2.6);
  const key = new THREE.DirectionalLight(0xe7f2ff, 3.2);
  key.position.set(2.5, 4, 3);
  scene.add(key, new THREE.HemisphereLight(0xb9ddff, 0x05070b, 2.4));
  const rim = new THREE.DirectionalLight(0x6fb5ff, 1.7);
  rim.position.set(-3, 2, -2);
  scene.add(rim);

  let mixer;
  let activeAction;
  let sequenceIndex = 0;
  let nextChange = 0;
  const clock = new THREE.Clock();
  const actionOrder = ["Idle", "Yes", "Wave", "Idle", "ThumbsUp", "Walking", "Idle", "Jump"];

  function isActive() {
    return document.body.classList.contains("is-landing") && !document.body.classList.contains("humanoid-motion-paused") && !document.hidden && !reducedMotion;
  }
  function resize() {
    const { width, height } = host.getBoundingClientRect();
    if (!width || !height) return;
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  }
  const resizeObserver = new ResizeObserver(resize);
  resizeObserver.observe(host);

  new GLTFLoader().load("./assets/robot-expressive.glb", (gltf) => {
    const robot = gltf.scene;
    const rig = new THREE.Group();
    rig.scale.setScalar(0.18);
    rig.position.set(0, 0.15, 0);
    rig.rotation.y = -0.22;
    rig.add(robot);
    robot.traverse((node) => {
      if (!node.isMesh) return;
      node.castShadow = true;
      node.receiveShadow = true;
      const color = node.material?.color;
      const brightness = color ? (color.r + color.g + color.b) / 3 : 1;
      node.material = new THREE.MeshPhysicalMaterial({
        color: brightness < 0.12 ? 0x141b24 : 0xe9eef5,
        metalness: brightness < 0.12 ? 0.48 : 0.3,
        roughness: brightness < 0.12 ? 0.3 : 0.22,
      });
    });
    scene.add(rig);
    mixer = new THREE.AnimationMixer(robot);
    const actions = new Map(gltf.animations.map((clip) => [clip.name, mixer.clipAction(clip)]));
    const fallback = actions.values().next().value;
    function play(name) {
      const next = actions.get(name) || actions.get("Idle") || fallback;
      if (!next || next === activeAction) return;
      next.reset().setEffectiveTimeScale(1).setEffectiveWeight(1).play();
      if (activeAction) activeAction.crossFadeTo(next, 0.58, false);
      activeAction = next;
    }
    play("Idle");
    host.classList.add("is-ready");
    nextChange = performance.now() + 2500;
    function render(now) {
      requestAnimationFrame(render);
      const delta = Math.min(clock.getDelta(), 0.05);
      if (isActive()) {
        mixer.update(delta);
        rig.rotation.y = -0.22 + Math.sin(now / 3200) * 0.09;
        if (now >= nextChange) {
          sequenceIndex = (sequenceIndex + 1) % actionOrder.length;
          play(actionOrder[sequenceIndex]);
          nextChange = now + (actionOrder[sequenceIndex] === "Walking" ? 4200 : 3000);
        }
      }
      renderer.render(scene, camera);
    }
    resize();
    requestAnimationFrame(render);
  }, undefined, () => host.classList.add("has-fallback"));
}
