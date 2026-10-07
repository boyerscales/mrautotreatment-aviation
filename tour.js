// AnointedSuds walkaround.
// A business jet built from code (no model file), drawn in gold lines first, like the
// line-drawing jet on the first draft he liked, then turned solid nose to tail. Scrolling
// flies the camera around it, one stop per .tcard in index.html, in the same order.
// Not modeled on any one real aircraft.
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';

const root = document.getElementById('tour');
const canvas = document.getElementById('gl');
const cards = [...root.querySelectorAll('.tcard')];
const navBtns = [...root.querySelectorAll('.tnav button')];
const hot = document.getElementById('hot'), hotLb = hot.querySelector('.lb');
const countEl = document.getElementById('tCount'), barEl = document.getElementById('tBar');
const phaseEls = [...document.querySelectorAll('#phase span')];
const N = cards.length;
const REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;
const FINE = matchMedia('(hover: hover) and (pointer: fine)').matches;
const clamp = (v, a, b) => Math.min(b, Math.max(a, v));
const smooth = t => t * t * (3 - 2 * t);
const easeIO = t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
const backOut = t => { const c = 1.7; return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2); };
const V = (x, y, z) => new THREE.Vector3(x, y, z);

if (!root.classList.contains('static')) start();

function start(){
  let renderer;
  try { renderer = new THREE.WebGLRenderer({ canvas, antialias:true, alpha:true, powerPreference:'high-performance' }); }
  catch (_) { root.classList.add('static'); return; }
  window.__tourReady = true;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.02;
  renderer.localClippingEnabled = true;
  renderer.setClearColor(0x000000, 0);

  const scene = new THREE.Scene();
  scene.fog = new THREE.Fog(0x000000, 30, 72);
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), .04).texture;
  const camera = new THREE.PerspectiveCamera(36, 1, .01, 200);

  const key = new THREE.DirectionalLight(0xffe2b4, 2.1); key.position.set(8, 12, 7); scene.add(key);
  const rim = new THREE.DirectionalLight(0xc6d6ff, 1.0); rim.position.set(-12, 5, -9); scene.add(rim);
  scene.add(new THREE.HemisphereLight(0xffffff, 0x1d160c, .35));

  /* ---------------- materials ----------------
     Every solid shares one clipping plane. Sliding it from nose to tail is how the
     line drawing "turns real". Solids sit a hair behind their own outlines
     (polygonOffset) so the gold lines never flicker against them. */
  const clipPlane = new THREE.Plane(V(1, 0, 0), -30);
  const C = [clipPlane];
  const off = { polygonOffset:true, polygonOffsetFactor:1, polygonOffsetUnits:1 };
  const M = o => new THREE.MeshPhysicalMaterial({ clippingPlanes:C, ...o });
  const paint  = M({ color:0xf2f1ec, roughness:.24, metalness:.05, clearcoat:1, clearcoatRoughness:.08, ...off });
  const hullM  = M({ color:0xf2f1ec, roughness:.24, metalness:.05, clearcoat:1, clearcoatRoughness:.08, transparent:true, side:THREE.DoubleSide, ...off });
  const glass  = M({ color:0x07090c, roughness:.05, metalness:.4, clearcoat:1, transparent:true, ...off });
  const gold   = M({ color:0xd8a845, metalness:1, roughness:.28 });
  const chrome = M({ color:0xe2e5ea, metalness:1, roughness:.14 });
  const nacM   = M({ color:0xe6e6e2, metalness:.5, roughness:.26, side:THREE.DoubleSide, ...off });
  const dark   = M({ color:0x141518, metalness:.6, roughness:.45, side:THREE.DoubleSide });
  const tire   = M({ color:0x0d0d0d, roughness:.9 });
  const seatM  = M({ color:0xe4d8c3, roughness:.7 });
  const carpetM= M({ color:0x3b342c, roughness:1 });
  const woodM  = M({ color:0x5b3d22, roughness:.35, clearcoat:.6 });

  const jet = new THREE.Group(); scene.add(jet);
  const edgeMeshes = [];
  const add = (geo, mat, parent = jet, outline = false) => { const m = new THREE.Mesh(geo, mat); parent.add(m); if (outline) edgeMeshes.push(m); return m; };

  /* ---------------- fuselage: nose at +x, 20 units long ---------------- */
  const rad = s => {                                // radius at s units back from the nose
    if (s <= 0) return 0;
    if (s < 4){ const u = (4 - s) / 4; return 1.1 * Math.sqrt(1 - u * u); }
    if (s <= 13.5) return 1.1;
    return Math.max(.28, 1.1 - .82 * Math.pow((s - 13.5) / 6.5, 1.4));
  };
  const prof = [new THREE.Vector2(.0001, -10.06)];
  for (let i = 120; i >= 0; i--){ const s = i / 120 * 20; prof.push(new THREE.Vector2(Math.max(rad(s), .0001), 10 - s)); }
  const hullGeo = new THREE.LatheGeometry(prof, 72); hullGeo.rotateZ(-Math.PI / 2);
  const hull = add(hullGeo, hullM);

  // windscreen: a band over the top of the nose
  const ws = [];
  for (let i = 16; i >= 0; i--){ const s = 2.05 + i / 16 * 1.55; ws.push(new THREE.Vector2(rad(s) + .014, 10 - s)); }
  const wsGeo = new THREE.LatheGeometry(ws, 24, 1.5 * Math.PI - .78, 1.56); wsGeo.rotateZ(-Math.PI / 2);
  add(wsGeo, glass, jet, true);

  // cabin windows
  const winGeo = new THREE.CircleGeometry(.16, 28); winGeo.scale(1, 1.3, 1);
  const windows = [];
  for (const side of [1, -1]) for (let x = 4.8; x > -2.4; x -= 1.05){
    const y = .22, z = side * Math.sqrt(1.1 * 1.1 - y * y) + side * .008;
    const w = add(winGeo, glass, jet, true);
    w.position.set(x, y, z); w.lookAt(V(x, y * 2, z * 2)); windows.push(w);
  }
  // gold cheatline down both sides
  for (const side of [1, -1]){
    const pts = [];
    for (let s = 3; s <= 16.2; s += .4){ const r = rad(s) + .006, y = -.32 * r / 1.1; pts.push(V(10 - s, y, side * Math.sqrt(r * r - y * y))); }
    add(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 80, .028, 6), gold);
  }

  /* ---------------- wings, winglets, tail ---------------- */
  const extrude = (pts, depth, bevel = .04) => new THREE.ExtrudeGeometry(
    new THREE.Shape(pts.map(p => new THREE.Vector2(p[0], p[1]))),
    { depth, bevelEnabled:true, bevelThickness:bevel, bevelSize:bevel * .8, bevelSegments:2, curveSegments:1, steps:1 });
  const wingGeo = extrude([[2.0,.6],[-2.6,8.2],[-3.55,8.25],[-2.7,3.2],[-2.6,.6]], .16, .05); wingGeo.rotateX(Math.PI / 2);
  const wingletGeo = extrude([[-2.55,0],[-3.55,0],[-3.95,1.2],[-3.35,1.2]], .07, .02);
  const leGeo = new THREE.TubeGeometry(new THREE.LineCurve3(V(2.0, -.07, .62), V(-2.57, -.07, 8.18)), 1, .055, 10);
  const wings = {};
  for (const side of [1, -1]){
    const g = new THREE.Group(); jet.add(g);
    g.position.set(0, -.62, 0); g.rotation.x = -.05 * side; if (side < 0) g.scale.z = -1;
    add(wingGeo, paint, g, true);
    const wl = add(wingletGeo, paint, g, true); wl.position.z = 8.17;
    add(leGeo, chrome, g);
    wings[side] = g;
  }
  const fin = add(extrude([[-6.4,.5],[-9.15,4.35],[-10.8,4.35],[-9.75,.5]], .16, .04), paint, jet, true);
  fin.geometry.translate(0, 0, -.08);
  const stabGeo = extrude([[-9.1,0],[-10.3,3.3],[-11.0,3.3],[-10.85,0]], .1, .03); stabGeo.rotateX(Math.PI / 2);
  for (const side of [1, -1]){ const s = add(stabGeo, paint, jet, true); s.position.y = 4.42; if (side < 0) s.scale.z = -1; }

  /* ---------------- engines (aft-mounted) ---------------- */
  const nacPts = [[.40,-1.55],[.47,-1.2],[.56,-.4],[.58,.4],[.55,1.2],[.5,1.52],[.45,1.5]];
  const nacR = y => { for (let i = 0; i < nacPts.length - 1; i++){ const [r0, y0] = nacPts[i], [r1, y1] = nacPts[i + 1]; if (y >= y0 && y <= y1) return r0 + (r1 - r0) * (y - y0) / (y1 - y0); } return .5; };
  const engines = [];
  for (const side of [1, -1]){
    const g = new THREE.Group(); jet.add(g);
    add(new THREE.LatheGeometry(nacPts.map(p => new THREE.Vector2(p[0], p[1])), 44), nacM, g);
    const intake = add(new THREE.CircleGeometry(.45, 40), dark, g); intake.rotation.x = -Math.PI / 2; intake.position.y = 1.4;
    const bladeGeo = new THREE.BoxGeometry(.4, .015, .07);
    for (let k = 0; k < 18; k++){ const a = k / 18 * Math.PI * 2, b = add(bladeGeo, dark, g); b.position.set(Math.cos(a) * .22, 1.38, Math.sin(a) * .22); b.rotation.set(0, -a, .5); }
    const spin = add(new THREE.ConeGeometry(.13, .3, 24), chrome, g); spin.position.y = 1.47;
    const lip = add(new THREE.TorusGeometry(.5, .03, 10, 48), gold, g); lip.rotation.x = Math.PI / 2; lip.position.y = 1.52;
    const ex = add(new THREE.CircleGeometry(.38, 32), dark, g); ex.rotation.x = Math.PI / 2; ex.position.y = -1.5;
    const cone = add(new THREE.ConeGeometry(.22, .5, 24), dark, g); cone.rotation.x = Math.PI; cone.position.y = -1.75;
    g.rotation.z = -Math.PI / 2; g.position.set(-5.65, .7, side * 1.98);
    engines.push(g);
    const py = add(new THREE.BoxGeometry(1.5, .12, .7), paint, jet, true); py.position.set(-5.7, .64, side * 1.2);
  }

  /* ---------------- landing gear ---------------- */
  const strutGeo = h => new THREE.CylinderGeometry(.06, .06, h, 12);
  const wheelGeo = new THREE.CylinderGeometry(.26, .26, .15, 28), hubGeo = new THREE.CylinderGeometry(.12, .12, .16, 20);
  const mwheelGeo = new THREE.CylinderGeometry(.33, .33, .18, 28), mhubGeo = new THREE.CylinderGeometry(.15, .15, .19, 20);
  add(strutGeo(1.3), chrome, jet, true).position.set(7.0, -1.68, 0);
  for (const z of [.12, -.12]){
    const w = add(wheelGeo, tire, jet, true); w.rotation.x = Math.PI / 2; w.position.set(7.0, -2.36, z);
    const h = add(hubGeo, chrome); h.rotation.x = Math.PI / 2; h.position.set(7.0, -2.36, z);
  }
  for (const side of [1, -1]){
    add(strutGeo(1.6), chrome, jet, true).position.set(-1.25, -1.5, side * 2.2);
    for (const dz of [.15, -.15]){
      const w = add(mwheelGeo, tire, jet, true); w.rotation.x = Math.PI / 2; w.position.set(-1.25, -2.29, side * 2.2 + dz);
      const h = add(mhubGeo, chrome); h.rotation.x = Math.PI / 2; h.position.set(-1.25, -2.29, side * 2.2 + dz);
    }
  }

  /* ---------------- cabin (seen when the hull goes x-ray) ---------------- */
  const carpet = add(new THREE.PlaneGeometry(8.4, 1.5), carpetM); carpet.rotation.x = -Math.PI / 2; carpet.position.set(1.0, -.79, 0);
  const seat = (x, z, dir) => {
    add(new THREE.BoxGeometry(.62, .3, .56), seatM).position.set(x, -.6, z);
    add(new THREE.BoxGeometry(.14, .75, .56), seatM).position.set(x - dir * .26, -.25, z);
  };
  for (const z of [.4, -.4]){ seat(4.4, z, -1); seat(3.0, z, 1); seat(1.6, z, -1); seat(.2, z, 1); }
  for (const x of [3.7, .9]) add(new THREE.BoxGeometry(.5, .04, 1.1), woodM).position.set(x, -.33, 0);
  add(new THREE.BoxGeometry(1.8, .3, .5), seatM).position.set(-1.9, -.6, -.45);
  add(new THREE.BoxGeometry(1.8, .62, .12), seatM).position.set(-1.9, -.25, -.68);
  add(new THREE.BoxGeometry(.6, 1.2, .45), M({ color:0xd9d4ca, roughness:.5 })).position.set(5.55, -.2, -.5);

  /* ---------------- one square foot, on top of the right wing ---------------- */
  const patch = new THREE.Group(); patch.position.set(-1.2, .0505, 3.6); wings[1].add(patch);
  const plateMat = M({ color:0xcfcabe, roughness:.6, metalness:.05, clearcoat:0, clearcoatRoughness:.04 });
  add(new THREE.BoxGeometry(.305, .003, .305), plateMat, patch).position.y = .0015;
  {
    const h = .1525, l = .045, y = .0045, p = [];
    for (const sx of [1, -1]) for (const sz of [1, -1]){ p.push(sx*h, y, sz*h, sx*(h-l), y, sz*h, sx*h, y, sz*h, sx*h, y, sz*(h-l)); }
    const bg = new THREE.BufferGeometry(); bg.setAttribute('position', new THREE.Float32BufferAttribute(p, 3));
    patch.add(new THREE.LineSegments(bg, new THREE.LineBasicMaterial({ color:0xe0b45c })));
  }
  const rnd = (a, b) => a + Math.random() * (b - a);
  const dirt = Array.from({ length:520 }, () => ({ x:rnd(-.145, .145), z:rnd(-.145, .145), r:rnd(.0011, .0042) }));
  const dirtIM = new THREE.InstancedMesh(new THREE.IcosahedronGeometry(1, 0), M({ color:0x45392c, roughness:1 }), dirt.length);
  patch.add(dirtIM);
  const beads = Array.from({ length:64 }, () => ({ x:rnd(-.135, .135), z:rnd(-.135, .135), r:rnd(.004, .012), t0:rnd(0, .75) }));
  const beadIM = new THREE.InstancedMesh(new THREE.SphereGeometry(1, 18, 12), M({ color:0xffffff, roughness:.02, metalness:0, clearcoat:1, transparent:true, opacity:.55 }), beads.length);
  patch.add(beadIM);
  const wiper = add(new THREE.BoxGeometry(.012, .007, .31), new THREE.MeshBasicMaterial({ color:0xe0b45c, transparent:true, opacity:0 }), patch);
  const sheen = add(new THREE.PlaneGeometry(.026, .3), new THREE.MeshBasicMaterial({ color:0xffe1a0, transparent:true, opacity:0, blending:THREE.AdditiveBlending, depthWrite:false }), patch);
  sheen.rotation.x = -Math.PI / 2; sheen.position.y = .0045;
  const dummy = new THREE.Object3D();
  const plateDull = new THREE.Color(0xcfcabe), plateClean = new THREE.Color(0xf6f5f1);
  let lastSub = -1;
  function macro(sub){
    if (Math.abs(sub - lastSub) < .0005) return;
    lastSub = sub;
    const lift = clamp(sub / .34, 0, 1), polish = clamp((sub - .34) / .32, 0, 1), protect = clamp((sub - .66) / .34, 0, 1);
    const wx = -.17 + lift * .36;
    dirt.forEach((d, i) => {
      const L = clamp((wx - d.x) / .05, 0, 1), s = 1 - L;
      dummy.position.set(d.x, .003 + d.r * .5 + L * .03, d.z); dummy.rotation.set(d.x * 40, d.z * 40, 0);
      dummy.scale.set(d.r * s + 1e-5, d.r * .6 * s + 1e-5, d.r * s + 1e-5); dummy.updateMatrix(); dirtIM.setMatrixAt(i, dummy.matrix);
    });
    dirtIM.instanceMatrix.needsUpdate = true;
    wiper.position.set(wx, .006, 0); wiper.material.opacity = lift > 0 && lift < 1 ? .9 : 0;
    plateMat.color.lerpColors(plateDull, plateClean, lift);
    plateMat.roughness = .6 - .54 * polish; plateMat.clearcoat = protect;
    sheen.position.x = -.15 + polish * .3; sheen.material.opacity = Math.sin(polish * Math.PI) * .85;
    beads.forEach((b, i) => {
      const k = clamp((protect - b.t0) / .25, 0, 1), e = k ? backOut(k) : 0;
      dummy.position.set(b.x, .003 + b.r * .25 * e, b.z); dummy.rotation.set(0, 0, 0);
      dummy.scale.set(b.r * e + 1e-5, b.r * .48 * e + 1e-5, b.r * e + 1e-5); dummy.updateMatrix(); beadIM.setMatrixAt(i, dummy.matrix);
    });
    beadIM.instanceMatrix.needsUpdate = true;
    [lift, polish, protect].forEach((k, i) => { if (!phaseEls[i]) return; phaseEls[i].style.setProperty('--k', k.toFixed(3)); phaseEls[i].classList.toggle('done', k >= 1); });
  }
  macro(0);

  /* ---------------- floor: soft glow, rings, contact shadow ---------------- */
  const tex = draw => { const c = document.createElement('canvas'); c.width = c.height = 512; draw(c.getContext('2d')); const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; return t; };
  const floorTex = tex(g => {
    const r = g.createRadialGradient(256, 256, 0, 256, 256, 256);
    r.addColorStop(0, 'rgba(224,180,92,.16)'); r.addColorStop(.55, 'rgba(224,180,92,.04)'); r.addColorStop(1, 'rgba(224,180,92,0)');
    g.fillStyle = r; g.fillRect(0, 0, 512, 512);
    g.strokeStyle = 'rgba(224,180,92,.22)'; g.lineWidth = 1.2;
    for (const rr of [120, 175, 230]){ g.beginPath(); g.arc(256, 256, rr, 0, 7); g.stroke(); }
  });
  const floor = new THREE.Mesh(new THREE.CircleGeometry(16, 72), new THREE.MeshBasicMaterial({ map:floorTex, transparent:true, depthWrite:false }));
  floor.rotation.x = -Math.PI / 2; floor.position.y = -2.64; scene.add(floor);
  const shadowTex = tex(g => { const r = g.createRadialGradient(256, 256, 0, 256, 256, 256); r.addColorStop(0, 'rgba(0,0,0,.85)'); r.addColorStop(1, 'rgba(0,0,0,0)'); g.fillStyle = r; g.fillRect(0, 0, 512, 512); });
  const shadow = new THREE.Mesh(new THREE.PlaneGeometry(26, 12), new THREE.MeshBasicMaterial({ map:shadowTex, transparent:true, depthWrite:false, opacity:0 }));
  shadow.rotation.x = -Math.PI / 2; shadow.position.set(-.5, -2.63, 0); scene.add(shadow);

  /* ---------------- the gold line drawing ---------------- */
  jet.updateMatrixWorld(true);
  const segs = [];
  const seg = (a, b) => segs.push(a.x, a.y, a.z, b.x, b.y, b.z);
  const poly = (pts, closed) => { for (let i = 0; i < pts.length - 1; i++) seg(pts[i], pts[i + 1]); if (closed) seg(pts[pts.length - 1], pts[0]); };
  for (const s of [.35,.9,1.6,2.4,3.3,4.4,5.6,6.8,8,9.2,10.4,11.6,12.8,14,15.2,16.4,17.6,18.6,19.4]){
    const r = rad(s) * 1.004, pts = [];
    for (let k = 0; k < 64; k++){ const a = k / 64 * Math.PI * 2; pts.push(V(10 - s, Math.cos(a) * r, Math.sin(a) * r)); }
    poly(pts, true);
  }
  for (let k = 0; k < 12; k++){
    const a = k / 12 * Math.PI * 2, pts = [];
    for (let s = .02; s <= 20; s += .25){ const r = rad(s) * 1.004; pts.push(V(10 - s, Math.cos(a) * r, Math.sin(a) * r)); }
    poly(pts);
  }
  for (const g of engines){
    const m = g.matrixWorld;
    for (const y of [-1.5, -1.1, -.5, .2, .9, 1.48]){
      const r = nacR(y) * 1.006, pts = [];
      for (let k = 0; k < 40; k++){ const a = k / 40 * Math.PI * 2; pts.push(V(Math.cos(a) * r, y, Math.sin(a) * r).applyMatrix4(m)); }
      poly(pts, true);
    }
    for (let k = 0; k < 10; k++){
      const a = k / 10 * Math.PI * 2, pts = [];
      for (let y = -1.55; y <= 1.52; y += .1){ const r = nacR(y) * 1.006; pts.push(V(Math.cos(a) * r, y, Math.sin(a) * r).applyMatrix4(m)); }
      poly(pts);
    }
  }
  for (const mesh of edgeMeshes){
    const eg = new THREE.EdgesGeometry(mesh.geometry, 25); eg.applyMatrix4(mesh.matrixWorld);
    const p = eg.attributes.position.array; for (let i = 0; i < p.length; i++) segs.push(p[i]);
    eg.dispose();
  }
  // Draw order: nose to tail, so it sketches itself front to back.
  const nSeg = segs.length / 6;
  const order = Array.from({ length:nSeg }, (_, i) => i).sort((i, j) => (segs[j*6] + segs[j*6+3]) - (segs[i*6] + segs[i*6+3]));
  const arr = new Float32Array(segs.length);
  order.forEach((s, k) => { for (let q = 0; q < 6; q++) arr[k*6+q] = segs[s*6+q]; });
  const lineGeo = new THREE.BufferGeometry(); lineGeo.setAttribute('position', new THREE.BufferAttribute(arr, 3));
  const lineMat = new THREE.LineBasicMaterial({ color:0xe0b45c, transparent:true, opacity:.9, depthWrite:false });
  const lines = new THREE.LineSegments(lineGeo, lineMat); scene.add(lines);
  lineGeo.setDrawRange(0, 0);
  const totalVerts = arr.length / 3;

  // the light ring that sweeps down the fuselage as it turns solid
  const scan = new THREE.Mesh(new THREE.RingGeometry(1.16, 1.3, 72), new THREE.MeshBasicMaterial({ color:0xffd98a, transparent:true, opacity:0, blending:THREE.AdditiveBlending, depthWrite:false, side:THREE.DoubleSide }));
  scan.rotation.y = Math.PI / 2; scene.add(scan);

  /* ---------------- camera stops (same order as the cards) ---------------- */
  const P = new THREE.Vector3(); patch.getWorldPosition(P);
  const LE = wings[1].localToWorld(V(-.42, -.07, 4.6));
  const KF = [
    { p:V(19.5, 6.8, 22.5),  t:V(-.5, .3, 0) },                    // overview
    { p:V(14.2, .9, 5.6),    t:V(9.0, -.2, 0) },                   // nose
    { p:V(10.6, 3.5, 3.8),   t:V(7.0, .6, 0) },                    // windscreen
    { p:V(4.4, 1.2, 11.8),   t:V(-.8, -.6, 5.2) },                 // leading edge
    { p:P.clone().add(V(.24, .32, .36)), t:P.clone() },            // one square foot
    { p:V(-1.4, 2.4, 7.0),   t:V(-5.3, .6, 1.9) },                 // engine
    { p:V(3.4, -1.8, 6.4),   t:V(-1.1, -1.9, 1.9) },               // gear
    { p:V(5.6, 5.2, 6.0),    t:V(.4, -.4, 0) },                    // cabin, x-ray
    { p:V(-19, 5.4, 17.5),   t:V(-.5, .4, 0) },                    // done
  ];
  const HOT = [null,
    { p:V(10.02, 0, 0), l:'Nose & radome' }, { p:V(7.1, 1.05, 0), l:'Windscreen' }, { p:LE, l:'Leading edge' },
    { p:P.clone(), l:'1 sq ft' }, { p:V(-4.13, .7, 1.98), l:'Engine inlet' }, { p:V(-1.25, -1.9, 2.2), l:'Main gear' },
    { p:V(1.5, -.3, 0), l:'Cabin' }, null];
  const posC = new THREE.CatmullRomCurve3(KF.map(k => k.p), false, 'centripetal');
  const tgtC = new THREE.CatmullRomCurve3(KF.map(k => k.t), false, 'centripetal');

  /* ---------------- sizing, pointer, visibility ---------------- */
  let W = 1, H = 1, portrait = false;
  function resize(){
    W = canvas.clientWidth || innerWidth; H = canvas.clientHeight || innerHeight;
    portrait = W / H < .85;
    renderer.setPixelRatio(Math.min(devicePixelRatio || 1, portrait ? 1.5 : 1.75));
    renderer.setSize(W, H, false);
    camera.aspect = W / H; camera.fov = portrait ? 52 : 36; camera.updateProjectionMatrix();
  }
  resize(); addEventListener('resize', resize);
  let mx = 0, my = 0, tmx = 0, tmy = 0;
  if (FINE) root.addEventListener('pointermove', e => { tmx = e.clientX / innerWidth * 2 - 1; tmy = e.clientY / innerHeight * 2 - 1; });

  let inView = false, raf = 0, introAt = -1, readyShown = false;
  new IntersectionObserver(es => {
    inView = es[0].isIntersecting;
    if (inView && introAt < 0) introAt = performance.now();
    if (inView && !raf) raf = requestAnimationFrame(frame);
  }, { rootMargin:'0px 0px -15% 0px' }).observe(root);
  document.addEventListener('visibilitychange', () => { if (!document.hidden && inView && !raf) raf = requestAnimationFrame(frame); });

  const tmpP = new THREE.Vector3(), tmpT = new THREE.Vector3(), fwd = new THREE.Vector3(), right = new THREE.Vector3(), upv = new THREE.Vector3(), UP = V(0, 1, 0), proj = new THREE.Vector3();
  let active = -1;

  function frame(now){
    raf = 0;
    const t = now / 1000;

    // intro: draw the lines, then sweep the solids in nose to tail
    const T = introAt < 0 ? 0 : (now - introAt) / 1000;
    const drawK = REDUCED ? 1 : clamp(T / 2.6, 0, 1);
    const reveal = REDUCED ? 1 : smooth(clamp((T - 2.1) / 1.9, 0, 1));
    lineGeo.setDrawRange(0, Math.floor(drawK * totalVerts / 2) * 2);
    const cx = 11.2 - reveal * 23.6;
    clipPlane.constant = -cx;
    scan.position.x = cx; scan.scale.setScalar((rad(10 - cx) || .3) / 1.1 + .06);
    scan.material.opacity = reveal > 0 && reveal < 1 ? Math.sin(reveal * Math.PI) * .9 : 0;
    shadow.material.opacity = reveal * .9;

    // scroll -> where the camera is on its path
    const r = root.getBoundingClientRect(), span = Math.max(1, r.height - innerHeight);
    const p = clamp(-r.top / span, 0, 1), s = p * (N - 1);
    const i = Math.min(Math.floor(s), N - 2), f = s - i;
    const dwell = i === 4 ? .64 : .34;
    const mv = clamp((f - dwell) / (1 - dwell), 0, 1);
    const cu = i + easeIO(mv), u = cu / (N - 1);
    macro(i === 4 ? clamp(f / dwell, 0, 1) : i > 4 ? 1 : 0);
    patch.visible = cu > 2.6 && cu < 5.4;

    // x-ray the hull at the cabin stop
    const xr = clamp(1 - Math.abs(cu - 7) / .7, 0, 1);
    hullM.opacity = 1 - .87 * xr; hullM.depthWrite = xr < .02;
    glass.opacity = 1 - .8 * xr;
    lineMat.opacity = (.9 - .76 * reveal) + xr * .45;
    // the close-up is a white wing filling the screen; bring the exposure down so it reads
    renderer.toneMappingExposure = 1.02 - .34 * clamp(1 - Math.abs(cu - 4) / .6, 0, 1);

    // camera
    posC.getPoint(u, tmpP); tgtC.getPoint(u, tmpT);
    const d = tmpP.distanceTo(tmpT), isMacro = Math.abs(cu - 4) < .5;
    if (portrait) tmpP.sub(tmpT).multiplyScalar(isMacro ? 1.2 : 1.38).add(tmpT);
    fwd.subVectors(tmpT, tmpP).normalize(); right.crossVectors(fwd, UP).normalize(); upv.crossVectors(right, fwd);
    const dd = tmpP.distanceTo(tmpT);
    if (portrait) tmpT.addScaledVector(upv, -dd * .11);         // subject sits above the card
    else tmpT.addScaledVector(right, -dd * .11);                  // subject sits right of the card
    mx += (tmx - mx) * .05; my += (tmy - my) * .05;
    if (!REDUCED){
      tmpP.addScaledVector(right, mx * d * .035).addScaledVector(upv, -my * d * .025);
      tmpP.y += Math.sin(t * .5) * d * .005;
    }
    camera.position.copy(tmpP); camera.lookAt(tmpT);

    renderer.render(scene, camera);
    if (!readyShown){ readyShown = true; root.classList.add('ready'); }

    // UI: active card, counter, nav, progress, hotspot
    const a = f < dwell + (1 - dwell) * .5 ? i : i + 1;
    if (a !== active){
      active = a;
      cards.forEach((c, k) => c.classList.toggle('on', k === a));
      navBtns.forEach((b, k) => b.classList.toggle('on', k === a));
      countEl.innerHTML = `<b>${String(a + 1).padStart(2, '0')}</b> / ${String(N).padStart(2, '0')}`;
    }
    barEl.style.setProperty('--p', p.toFixed(4));
    const h = HOT[Math.round(cu)], near = Math.abs(cu - Math.round(cu)) < .06 && reveal >= 1;
    if (h && near){
      proj.copy(h.p).project(camera);
      if (proj.z < 1){
        hot.style.transform = `translate(${((proj.x * .5 + .5) * W).toFixed(1)}px,${((-proj.y * .5 + .5) * H).toFixed(1)}px)`;
        if (hotLb.textContent !== h.l) hotLb.textContent = h.l;
        hot.classList.add('on');
      } else hot.classList.remove('on');
    } else hot.classList.remove('on');

    if (inView && !document.hidden) raf = requestAnimationFrame(frame);
  }
  raf = requestAnimationFrame(frame);
}
