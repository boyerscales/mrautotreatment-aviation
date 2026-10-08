// AnointedSuds walkaround.
// A business jet built from code (no model file), drawn in gold lines first, like the
// line-drawing jet on the first draft he liked, then turned solid nose to tail. Scrolling
// flies the camera around it, one stop per .tcard in index.html, in the same order.
// Not modeled on any one real aircraft. Loaded on demand by index.html.
//
// Motion rules (from how the best scroll-driven 3D sites do it): nothing jumps. Scroll
// progress, camera, look-at target and mouse all run through frame-rate independent
// damping, the camera never stops dead between stops (it only slows near them), and
// there's always something alive on screen: nav lights, strobes, drifting dust.
import * as THREE from 'three';
import { RoomEnvironment } from 'three/addons/environments/RoomEnvironment.js';
import { RoundedBoxGeometry } from 'three/addons/geometries/RoundedBoxGeometry.js';

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
const easeOut = t => 1 - Math.pow(1 - t, 3);
const backOut = t => { const c = 1.7; return 1 + (c + 1) * Math.pow(t - 1, 3) + c * Math.pow(t - 1, 2); };
const damp = (a, b, k, dt) => a + (b - a) * (1 - Math.exp(-k * dt));
const V = (x, y, z) => new THREE.Vector3(x, y, z);
const REDUCED_SNAP = { on:false };
const rnd = (a, b) => a + Math.random() * (b - a);

// How much scroll each leg of the tour gets. Leg 4 (leaving the square foot) is longer
// because the cleaning plays out on it. Shared with index.html so the stop list jumps right.
const LEG = [2.8, 1.5, 1.5, 1.2, 1.8, 1.2, 1.2, 1.3];   // leg 0 is long: the build plays out on it; nose → windscreen → wing get extra room
const CUM = [0]; { const sum = LEG.reduce((a, b) => a + b, 0); LEG.forEach(w => CUM.push(CUM[CUM.length - 1] + w / sum)); }
// The overview stop sits where the build finishes, so jumping to it shows the finished jet.
const BUILD_END = .66;
window.__tourStopP = CUM.map((c, i) => i === 0 ? CUM[0] + (CUM[1] - CUM[0]) * BUILD_END : c);

if (!root.classList.contains('static')) start().catch(e => { console.error(e); root.classList.add('static'); });

async function start(){
  let renderer;
  try { renderer = new THREE.WebGLRenderer({ canvas, antialias:true, powerPreference:'high-performance' }); }
  catch (_) { root.classList.add('static'); return; }
  window.__tourReady = true;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.02;
  const maxAniso = renderer.capabilities.getMaxAnisotropy();
  let portrait = innerWidth / innerHeight < .85;
  const LITE = portrait || !FINE;                       // phones and tablets: no mirror floor, fewer particles

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x000000);
  scene.fog = new THREE.Fog(0x000000, 30, 76);
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), .04).texture;
  scene.environmentIntensity = .75;
  const camera = new THREE.PerspectiveCamera(36, 1, .01, 260);

  const key = new THREE.DirectionalLight(0xffe2b4, 1.8); key.position.set(8, 12, 7); scene.add(key);
  const rim = new THREE.DirectionalLight(0xc6d6ff, 1.1); rim.position.set(-12, 5, -9); scene.add(rim);
  scene.add(new THREE.HemisphereLight(0xffffff, 0x1d160c, .3));

  await document.fonts.ready.catch(() => {});

  /* ---------------- canvas textures ---------------- */
  const canvasTex = (w, h, draw, srgb = true) => {
    const c = document.createElement('canvas'); c.width = w; c.height = h; draw(c.getContext('2d'), w, h);
    const t = new THREE.CanvasTexture(c); if (srgb) t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = maxAniso; return t;
  };
  const halo = canvasTex(128, 128, (g) => {
    const r = g.createRadialGradient(64, 64, 0, 64, 64, 64);
    r.addColorStop(0, 'rgba(255,255,255,1)'); r.addColorStop(.25, 'rgba(255,255,255,.45)'); r.addColorStop(1, 'rgba(255,255,255,0)');
    g.fillStyle = r; g.fillRect(0, 0, 128, 128);
  });

  // Livery, painted onto the fuselage's own UVs: u runs around it (0 right side, .25 belly,
  // .5 left side, .75 crown), v runs nose (top of the canvas) to tail.
  const LW = 2048, LH = 1024, Y = s => s / 20.17 * LH, X = u => u * LW;
  const drawPanels = (g, ink) => {
    g.fillStyle = ink;
    for (const s of [3.95, 6.6, 9.6, 12.7, 15.6, 17.9]) g.fillRect(0, Y(s), LW, 2);
    g.fillRect(X(.75) - 1, Y(4), 2, LH);
    g.strokeStyle = ink; g.lineWidth = 4;
    const dr = (x0, x1, s0, s1) => { g.beginPath(); g.roundRect(X(x0), Y(s0), X(x1) - X(x0), Y(s1) - Y(s0), 18); g.stroke(); };
    dr(.418, .618, 2.95, 3.78);                                       // main door, left side
    dr(.875, .975, 9.55, 10.15);                                      // over-wing exit, right side
  };
  const livery = canvasTex(LW, LH, (g) => {
    g.fillStyle = '#f3f2ee'; g.fillRect(0, 0, LW, LH);
    const b0 = X(.047), b1 = X(.453);
    g.fillStyle = '#121214';
    g.beginPath(); g.moveTo(b0, Y(3.6)); g.bezierCurveTo(b0, Y(2.5), b1, Y(2.5), b1, Y(3.6)); g.lineTo(b1, LH); g.lineTo(b0, LH); g.closePath(); g.fill();
    g.fillStyle = '#d9a845';
    g.fillRect(b0 - 30, Y(3.9), 5, LH); g.fillRect(b1 + 25, Y(3.9), 5, LH);
    drawPanels(g, 'rgba(0,0,0,.14)');
  });
  const bump = canvasTex(LW, LH, (g) => { g.fillStyle = '#808080'; g.fillRect(0, 0, LW, LH); drawPanels(g, '#3a3a3a'); }, false);
  const textTex = (text, w, h, color) => canvasTex(w, h, (g) => {
    g.font = `800 ${Math.round(h * .66)}px Manrope, system-ui, sans-serif`; g.fillStyle = color;
    g.textAlign = 'center'; g.textBaseline = 'middle'; g.fillText(text, w / 2, h / 2 + h * .04);
  });
  const markTex = canvasTex(512, 512, () => {});
  {
    const svg = document.getElementById('mark');
    if (svg){
      const src = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${svg.getAttribute('viewBox')}">${svg.innerHTML}</svg>`;
      const img = new Image();
      img.onload = () => { const g = markTex.image.getContext('2d'); g.clearRect(0, 0, 512, 512); g.drawImage(img, 0, 0, 512, 512); markTex.needsUpdate = true; };
      img.src = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(src);
    }
  }
  const woodTex = canvasTex(512, 512, (g, w, h) => {
    g.fillStyle = '#4a2c16'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 140; i++){
      const y = Math.random() * h, a = rnd(.04, .16);
      g.strokeStyle = Math.random() < .5 ? `rgba(20,8,0,${a})` : `rgba(140,90,50,${a})`; g.lineWidth = rnd(1, 3);
      g.beginPath(); g.moveTo(0, y); for (let x = 0; x <= w; x += 32) g.lineTo(x, y + Math.sin(x / 70 + i) * 4); g.stroke();
    }
  });
  const carpetTex = canvasTex(256, 256, (g, w, h) => {
    g.fillStyle = '#3b332b'; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 4000; i++){ g.fillStyle = `rgba(${Math.random() < .5 ? '0,0,0' : '255,235,200'},${rnd(.03, .09)})`; g.fillRect(Math.random() * w, Math.random() * h, 1.5, 1.5); }
    g.strokeStyle = 'rgba(224,180,92,.12)'; g.lineWidth = 2;
    for (let x = -h; x < w; x += 64){ g.beginPath(); g.moveTo(x, 0); g.lineTo(x + h, h); g.moveTo(x + h, 0); g.lineTo(x, h); g.stroke(); }
  });
  carpetTex.wrapS = carpetTex.wrapT = THREE.RepeatWrapping; carpetTex.repeat.set(10, 2);

  /* ---------------- materials ----------------
     Every solid shares one reveal cut. Sliding it from nose to tail is how the
     line drawing "turns real". Solids sit a hair behind their own outlines
     (polygonOffset) so the gold lines never flicker against them. */
  // The reveal is written into the jet's own shaders: any fragment with world x below
  // cut.value is discarded. (three's clipping planes leaked between materials here.)
  const cut = { value:40 };
  const reveal = mat => {
    mat.onBeforeCompile = sh => {
      sh.uniforms.uCut = cut;
      sh.vertexShader = sh.vertexShader.replace('#include <common>', '#include <common>\nvarying float vWX;')
        .replace('#include <project_vertex>', `#include <project_vertex>
          vec4 wxp = vec4(transformed, 1.0);
          #ifdef USE_INSTANCING
            wxp = instanceMatrix * wxp;
          #endif
          vWX = (modelMatrix * wxp).x;`);
      sh.fragmentShader = sh.fragmentShader.replace('#include <common>', '#include <common>\nvarying float vWX;\nuniform float uCut;')
        .replace('#include <clipping_planes_fragment>', '#include <clipping_planes_fragment>\nif (vWX < uCut) discard;');
    };
    mat.customProgramCacheKey = () => 'reveal';
    return mat;
  };
  const off = { polygonOffset:true, polygonOffsetFactor:1, polygonOffsetUnits:1 };
  const M = o => reveal(new THREE.MeshPhysicalMaterial(o));
  const paint  = M({ color:0xf2f1ec, roughness:.22, metalness:.05, clearcoat:1, clearcoatRoughness:.06, ...off });
  const hullM  = M({ map:livery, bumpMap:bump, bumpScale:.5, roughness:.22, metalness:.05, clearcoat:1, clearcoatRoughness:.06, transparent:true, side:THREE.DoubleSide, ...off });
  const finM   = M({ color:0x121315, roughness:.25, metalness:.2, clearcoat:1, clearcoatRoughness:.05, ...off });
  const glass  = M({ color:0x07090c, roughness:.04, metalness:.4, clearcoat:1, transparent:true, ...off });
  const winM   = M({ color:0x0c0a08, emissive:0xffa64a, emissiveIntensity:.5, roughness:.05, metalness:.2, clearcoat:1, transparent:true, ...off });
  const gold   = M({ color:0xd8a845, metalness:1, roughness:.25 });
  const chrome = M({ color:0xe6e9ee, metalness:1, roughness:.1 });
  const nacM   = M({ color:0xeceae6, metalness:.45, roughness:.22, clearcoat:.8, side:THREE.DoubleSide, ...off });
  const dark   = M({ color:0x141518, metalness:.7, roughness:.4, side:THREE.DoubleSide });
  const tire   = M({ color:0x0b0b0b, roughness:.85 });
  const leather= M({ color:0xe9dcc5, roughness:.48, sheen:.5, sheenColor:0xffffff, sheenRoughness:.6 });
  const fabric = M({ color:0xc59c4f, roughness:.8, sheen:.6, sheenColor:0xffe2a0 });
  const woodM  = M({ map:woodTex, roughness:.3, clearcoat:1, clearcoatRoughness:.08 });
  const carpetM= M({ map:carpetTex, roughness:1 });
  const stone  = M({ color:0xf2efe9, roughness:.12, clearcoat:1 });
  // Decals: their empty parts must not write depth, or they punch a see-through box in the
  // (transparent, later-drawn) hull. alphaTest drops the empty pixels; they draw after the hull.
  const decal  = (map) => M({ map, transparent:true, alphaTest:.35, depthWrite:false, roughness:.25, clearcoat:1, polygonOffset:true, polygonOffsetFactor:-2, polygonOffsetUnits:-2 });

  const jet = new THREE.Group(); scene.add(jet);
  const edgeMeshes = [];
  const add = (geo, mat, parent = jet, outline = false) => { const m = new THREE.Mesh(geo, mat); parent.add(m); if (outline) edgeMeshes.push(m); return m; };

  /* ---------------- fuselage: nose at +x, 20 units long ---------------- */
  const rad = s => {
    if (s <= 0) return 0;
    if (s < 4){ const u = (4 - s) / 4; return 1.1 * Math.sqrt(1 - u * u); }
    if (s <= 13.5) return 1.1;
    return Math.max(.28, 1.1 - .82 * Math.pow((s - 13.5) / 6.5, 1.4));
  };
  const prof = [new THREE.Vector2(.0001, -10.06)];
  for (let i = 120; i >= 0; i--){ const s = i / 120 * 20; prof.push(new THREE.Vector2(Math.max(rad(s), .0001), 10 - s)); }
  const hullGeo = new THREE.LatheGeometry(prof, 96); hullGeo.rotateZ(-Math.PI / 2);
  add(hullGeo, hullM);

  // windscreen with a center post
  const ws = [];
  for (let i = 16; i >= 0; i--){ const s = 2.05 + i / 16 * 1.55; ws.push(new THREE.Vector2(rad(s) + .014, 10 - s)); }
  const wsGeo = new THREE.LatheGeometry(ws, 32, 1.5 * Math.PI - .78, 1.56); wsGeo.rotateZ(-Math.PI / 2);
  add(wsGeo, glass, jet, true);
  {
    const pts = []; for (let s = 2.05; s <= 3.6; s += .1) pts.push(V(10 - s, rad(s) + .02, 0));
    add(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 20, .03, 6), dark);
  }
  // cabin windows: warm glass in chrome frames, so the cabin looks lit
  const winGeo = new THREE.CircleGeometry(.16, 28); winGeo.scale(1, 1.3, 1);
  const frameGeo = new THREE.TorusGeometry(.165, .014, 6, 32); frameGeo.scale(1, 1.3, 1);
  for (const side of [1, -1]) for (let x = 4.8; x > -2.4; x -= 1.05){
    const y = .22, z = side * (Math.sqrt(1.1 * 1.1 - y * y) + .008);
    const w = add(winGeo, winM, jet, true); w.position.set(x, y, z); w.lookAt(V(x, y * 2, z * 2));
    add(frameGeo, chrome, w);
  }
  // gold cheatline along the edge of the dark belly
  for (const side of [1, -1]){
    const pts = [];
    for (let s = 3.9; s <= 16.4; s += .4){ const r = rad(s) + .006, y = -.32 * r / 1.1; pts.push(V(10 - s, y, side * Math.sqrt(r * r - y * y))); }
    add(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts), 90, .024, 6), gold);
  }
  // registration, both sides: N633AS (Matthew 6:33, AnointedSuds)
  const regTex = textTex('N633AS', 1024, 180, '#141414');
  for (const side of [1, -1]){
    const y = .34, z = side * (Math.sqrt(1.1 * 1.1 - y * y) + .014);
    const r = add(new THREE.PlaneGeometry(1.7, .3), decal(regTex)); r.position.set(-2.9, y, z); r.lookAt(V(-2.9, y * 2, z * 2)); r.renderOrder = 2;
  }

  /* ---------------- wings, winglets, tail ---------------- */
  const extrude = (pts, depth, bevel = .04) => new THREE.ExtrudeGeometry(
    new THREE.Shape(pts.map(p => new THREE.Vector2(p[0], p[1]))),
    { depth, bevelEnabled:true, bevelThickness:bevel, bevelSize:bevel * .8, bevelSegments:3, curveSegments:1, steps:1 });
  const wingGeo = extrude([[2.0,.6],[-2.6,8.2],[-3.55,8.25],[-2.7,3.2],[-2.6,.6]], .16, .05); wingGeo.rotateX(Math.PI / 2);
  const wingletGeo = extrude([[-2.55,0],[-3.55,0],[-3.95,1.2],[-3.35,1.2]], .07, .02);
  const leGeo = new THREE.TubeGeometry(new THREE.LineCurve3(V(2.0, -.07, .62), V(-2.57, -.07, 8.18)), 1, .055, 12);
  const flapGeo = new THREE.BoxGeometry(.012, .004, 1);
  const wings = {};
  for (const side of [1, -1]){
    const g = new THREE.Group(); jet.add(g);
    g.position.set(0, -.62, 0); g.rotation.x = -.05 * side; if (side < 0) g.scale.z = -1;
    add(wingGeo, paint, g, true);
    const wl = add(wingletGeo, finM, g, true); wl.position.z = 8.17;
    add(leGeo, chrome, g);
    // flap and aileron hinge lines on the top skin
    const lineM = reveal(new THREE.MeshBasicMaterial({ color:0x9a9890 }));
    for (const [x0, z0, x1, z1] of [[-2.0,.9,-2.42,3.6],[-2.42,3.6,-2.95,6.3],[-2.95,6.3,-3.25,7.9]]){
      const m = add(flapGeo, lineM, g); m.position.set((x0 + x1) / 2, .052, (z0 + z1) / 2);
      m.scale.z = Math.hypot(x1 - x0, z1 - z0); m.rotation.y = Math.atan2(x1 - x0, z1 - z0) - Math.PI;
    }
    wings[side] = g;
  }
  const fin = add(extrude([[-6.4,.5],[-9.15,4.35],[-10.8,4.35],[-9.75,.5]], .16, .04), finM, jet, true);
  fin.geometry.translate(0, 0, -.08);
  for (const side of [1, -1]){
    const d = add(new THREE.PlaneGeometry(1.5, 1.5), decal(markTex)); d.position.set(-9.15, 2.45, side * .126); d.renderOrder = 2;
    if (side < 0) d.rotation.y = Math.PI;
  }
  const stabGeo = extrude([[-9.1,0],[-10.3,3.3],[-11.0,3.3],[-10.85,0]], .1, .03); stabGeo.rotateX(Math.PI / 2);
  for (const side of [1, -1]){ const s = add(stabGeo, paint, jet, true); s.position.y = 4.42; if (side < 0) s.scale.z = -1; }

  /* ---------------- engines (aft-mounted) ---------------- */
  const nacPts = [[.40,-1.55],[.47,-1.2],[.56,-.4],[.58,.4],[.55,1.2],[.5,1.52],[.45,1.5]];
  const nacR = y => { for (let i = 0; i < nacPts.length - 1; i++){ const [r0, y0] = nacPts[i], [r1, y1] = nacPts[i + 1]; if (y >= y0 && y <= y1) return r0 + (r1 - r0) * (y - y0) / (y1 - y0); } return .5; };
  const engines = [], fans = [];
  for (const side of [1, -1]){
    const g = new THREE.Group(); jet.add(g);
    add(new THREE.LatheGeometry(nacPts.map(p => new THREE.Vector2(p[0], p[1])), 48), nacM, g);
    const intake = add(new THREE.CircleGeometry(.45, 40), dark, g); intake.rotation.x = -Math.PI / 2; intake.position.y = 1.36;
    const fan = new THREE.Group(); fan.position.y = 1.4; g.add(fan); fans.push(fan);
    const bladeGeo = new THREE.BoxGeometry(.4, .012, .075);
    for (let k = 0; k < 22; k++){ const a = k / 22 * Math.PI * 2, b = add(bladeGeo, chrome, fan); b.position.set(Math.cos(a) * .22, 0, Math.sin(a) * .22); b.rotation.set(0, -a, .55); }
    const spin = add(new THREE.ConeGeometry(.13, .32, 28), chrome, fan); spin.position.y = .08;
    const lip = add(new THREE.TorusGeometry(.5, .032, 12, 56), gold, g); lip.rotation.x = Math.PI / 2; lip.position.y = 1.52;
    const ex = add(new THREE.CircleGeometry(.38, 32), dark, g); ex.rotation.x = Math.PI / 2; ex.position.y = -1.5;
    const exRing = add(new THREE.TorusGeometry(.39, .02, 8, 40), chrome, g); exRing.rotation.x = Math.PI / 2; exRing.position.y = -1.55;
    const cone = add(new THREE.ConeGeometry(.22, .5, 24), dark, g); cone.rotation.x = Math.PI; cone.position.y = -1.75;
    g.rotation.z = -Math.PI / 2; g.position.set(-5.65, .7, side * 1.98);
    engines.push(g);
    const py = add(new RoundedBoxGeometry(1.5, .12, .7, 2, .04), paint, jet, true); py.position.set(-5.7, .64, side * 1.2);
  }

  /* ---------------- landing gear ---------------- */
  const cyl = (r, h, s = 16) => new THREE.CylinderGeometry(r, r, h, s);
  const wheel = (x, y, z, r, w) => {
    const t = add(new THREE.TorusGeometry(r * .78, r * .25, 12, 32), tire, jet, true); t.position.set(x, y, z); t.scale.z = w / (r * .5);
    const hub = add(cyl(r * .56, w * .9, 24), chrome); hub.rotation.x = Math.PI / 2; hub.position.set(x, y, z);
    const cap = add(cyl(r * .2, w * .96, 16), gold); cap.rotation.x = Math.PI / 2; cap.position.set(x, y, z);
  };
  const strut = (x, z, top, bottom) => {
    const h = top - bottom;
    add(cyl(.075, h * .55), dark, jet, true).position.set(x, top - h * .275, z);
    add(cyl(.05, h * .5), chrome).position.set(x, bottom + h * .25, z);
  };
  strut(7.0, 0, -1.0, -2.3);
  for (const z of [.13, -.13]) wheel(7.0, -2.36, z, .27, .15);
  for (const side of [1, -1]){
    strut(-1.25, side * 2.2, -.7, -2.25);
    for (const dz of [.16, -.16]) wheel(-1.25, -2.28, side * 2.2 + dz, .34, .18);
  }

  /* ---------------- cabin (seen when the hull goes x-ray) ---------------- */
  const cabin = new THREE.Group(); jet.add(cabin);
  const RB = (w, h, d, r = .05) => new RoundedBoxGeometry(w, h, d, 3, r);
  const cp = add(new THREE.PlaneGeometry(8.6, 1.55), carpetM, cabin); cp.rotation.x = -Math.PI / 2; cp.position.set(1.0, -.79, 0);
  const seat = (x, z, dir) => {
    add(RB(.62, .24, .58), leather, cabin).position.set(x, -.64, z);
    add(RB(.54, .1, .5, .04), leather, cabin).position.set(x + dir * .03, -.48, z);
    const back = add(RB(.16, .74, .58, .06), leather, cabin); back.position.set(x - dir * .27, -.2, z); back.rotation.z = dir * .1;
    for (const az of [.27, -.27]) add(RB(.56, .13, .07, .03), leather, cabin).position.set(x, -.43, z + az);
  };
  for (const z of [.41, -.41]){ seat(4.4, z, -1); seat(3.0, z, 1); seat(1.6, z, -1); seat(.2, z, 1); }
  for (const x of [3.7, .9]){
    add(RB(.62, .04, 1.02, .015), woodM, cabin).position.set(x, -.34, 0);
    add(cyl(.03, .42), gold, cabin).position.set(x, -.56, 0);
  }
  for (const z of [.87, -.87]){
    add(RB(5.9, .22, .16, .03), woodM, cabin).position.set(1.0, -.4, z);
    add(new THREE.BoxGeometry(5.9, .012, .17), gold, cabin).position.set(1.0, -.285, z);
  }
  const glowBar = reveal(new THREE.MeshBasicMaterial({ color:new THREE.Color(5, 3.3, 1.5), toneMapped:false }));
  for (const z of [.46, -.46]) add(new THREE.BoxGeometry(7.4, .02, .05), glowBar, cabin).position.set(1.0, .76, z);
  add(RB(1.9, .3, .56), leather, cabin).position.set(-1.9, -.62, -.47);
  add(RB(1.9, .62, .13), leather, cabin).position.set(-1.9, -.26, -.72);
  for (const x of [-2.5, -1.9, -1.3]){ const p = add(RB(.34, .3, .1, .04), fabric, cabin); p.position.set(x, -.34, -.6); p.rotation.x = -.2; }
  add(RB(.62, 1.15, .5), woodM, cabin).position.set(5.5, -.22, -.55);
  add(new THREE.BoxGeometry(.66, .035, .54), stone, cabin).position.set(5.5, .37, -.55);
  add(RB(.08, 1.55, 1.9, .03), M({ color:0xe9e4da, roughness:.4 }), cabin).position.set(-3.3, -.08, 0);

  /* ---------------- lights: nav, strobes, beacons, landing light ---------------- */
  const lights = [];
  const light = (parent, pos, rgb, size = .8) => {
    const g = new THREE.Group(); g.position.copy(pos); parent.add(g);
    const core = new THREE.Mesh(new THREE.SphereGeometry(.045, 12, 8), new THREE.MeshBasicMaterial({ color:new THREE.Color(...rgb).multiplyScalar(9), toneMapped:false }));
    const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map:halo, color:new THREE.Color(...rgb), blending:THREE.AdditiveBlending, transparent:true, depthWrite:false, toneMapped:false }));
    sp.scale.setScalar(size); g.add(core, sp);
    const L = { g, sp, size }; lights.push(L); return L;
  };
  const navG = light(wings[1], V(-3.1, -.02, 8.32), [.2, 1, .45], .5);
  const navR = light(wings[-1], V(-3.1, -.02, 8.32), [1, .15, .12], .5);
  const strobes = [light(wings[1], V(-3.5, -.02, 8.26), [1, 1, 1], .55), light(wings[-1], V(-3.5, -.02, 8.26), [1, 1, 1], .55), light(jet, V(-10.12, 0, 0), [1, 1, 1], .45)];
  const beacons = [light(jet, V(0, 1.14, 0), [1, .1, .08], .6), light(jet, V(0, -1.14, 0), [1, .1, .08], .6)];
  light(jet, V(7.12, -1.95, 0), [1, .95, .85], .55);
  const beamMat = new THREE.ShaderMaterial({
    uniforms:{ uOp:{ value:0 } }, transparent:true, depthWrite:false, blending:THREE.AdditiveBlending, side:THREE.DoubleSide,
    // The cone's tip has zero-length normals; normalizing those gives NaN, and bloom smears a
    // NaN pixel into a black block. So normals are normalized only when they have length.
    vertexShader:`varying vec2 vUv; varying vec3 vN; varying vec3 vV;
      void main(){ vUv = uv; vec4 mvPosition = modelViewMatrix * vec4(position, 1.); vN = normalMatrix * normal; vV = -mvPosition.xyz; gl_Position = projectionMatrix * mvPosition;
      }`,
    fragmentShader:`uniform float uOp; varying vec2 vUv; varying vec3 vN; varying vec3 vV;
      void main(){
        float ln = dot(vN, vN), lv = dot(vV, vV);
        float facing = (ln > 1e-8 && lv > 1e-8) ? abs(dot(vN * inversesqrt(ln), vV * inversesqrt(lv))) : 0.;
        float a = pow(clamp(vUv.y, 0., 1.), 2.4) * .2 * pow(clamp(facing, 0., 1.), 1.5) * uOp;
        gl_FragColor = vec4(vec3(1., .93, .8) * max(a, 0.), 1.); }`
  });
  const beamGeo = new THREE.ConeGeometry(2.3, 8, 48, 1, true); beamGeo.translate(0, -4, 0);
  const beam = new THREE.Mesh(beamGeo, beamMat); beam.position.set(7.12, -1.95, 0);
  beam.quaternion.setFromUnitVectors(V(0, -1, 0), V(1, -.2, 0).normalize()); scene.add(beam);

  /* ---------------- one square foot, on the black tail fin (dark paint shows it best) ---------------- */
  // Low and forward on the fin, well clear of the emblem decal (centered at -9.15, 2.45), so the logo never fills the close-up.
  const patch = new THREE.Group(); patch.position.set(-7.6, 1.15, .1215); patch.rotation.x = Math.PI / 2; jet.add(patch);
  const plateMat = M({ color:0x3a3733, roughness:.7, metalness:.1, clearcoat:0, clearcoatRoughness:.03 });
  add(new THREE.BoxGeometry(.305, .003, .305), plateMat, patch).position.y = .0015;
  {
    const h = .1525, l = .045, y = .0045, p = [];
    for (const sx of [1, -1]) for (const sz of [1, -1]) p.push(sx*h, y, sz*h, sx*(h-l), y, sz*h, sx*h, y, sz*h, sx*h, y, sz*(h-l));
    const bg = new THREE.BufferGeometry(); bg.setAttribute('position', new THREE.Float32BufferAttribute(p, 3));
    patch.add(new THREE.LineSegments(bg, reveal(new THREE.LineBasicMaterial({ color:0xe0b45c }))));
  }
  const dirt = Array.from({ length:520 }, () => ({ x:rnd(-.145, .145), z:rnd(-.145, .145), r:rnd(.0011, .0042) }));
  const dirtIM = new THREE.InstancedMesh(new THREE.IcosahedronGeometry(1, 0), M({ color:0x9c8a70, roughness:1 }), dirt.length); patch.add(dirtIM);
  const beads = Array.from({ length:70 }, () => ({ x:rnd(-.135, .135), z:rnd(-.135, .135), r:rnd(.003, .009), t0:rnd(0, .75) }));
  const beadIM = new THREE.InstancedMesh(new THREE.SphereGeometry(1, 18, 12), M({ color:0xe8f0f8, roughness:.02, metalness:0, clearcoat:1, transparent:true, opacity:.7 }), beads.length); patch.add(beadIM);
  const wiper = add(new THREE.BoxGeometry(.012, .007, .31), reveal(new THREE.MeshBasicMaterial({ color:0xe0b45c, transparent:true, opacity:0 })), patch);
  const sheen = add(new THREE.PlaneGeometry(.026, .3), reveal(new THREE.MeshBasicMaterial({ color:new THREE.Color(2, 1.6, 1), transparent:true, opacity:0, blending:THREE.AdditiveBlending, depthWrite:false, toneMapped:false })), patch);
  sheen.rotation.x = -Math.PI / 2; sheen.position.y = .0045;
  const dummy = new THREE.Object3D();
  const plateDull = new THREE.Color(0x3a3733), plateClean = new THREE.Color(0x0c0d0f);
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
    plateMat.roughness = .7 - .62 * polish; plateMat.clearcoat = Math.max(polish * .6, protect);
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

  /* ---------------- floor and dust ---------------- */
  const FY = -2.66;
  // ONE floor surface. The rings, warm glow and contact shadow are painted into its texture
  // instead of being separate layers a hair apart: stacked coplanar layers z-fight and
  // flicker when the camera swoops low (between the overview and the nose).
  const FR = 40;
  const floorTex = canvasTex(2048, 2048, (g) => {
    const C2 = 1024, px = C2 / FR;                         // pixels per world unit
    g.fillStyle = '#060606'; g.fillRect(0, 0, 2048, 2048);
    let r = g.createRadialGradient(C2, C2, 0, C2, C2, 17 * px);
    r.addColorStop(0, 'rgba(224,180,92,.16)'); r.addColorStop(.5, 'rgba(224,180,92,.05)'); r.addColorStop(1, 'rgba(224,180,92,0)');
    g.fillStyle = r; g.fillRect(0, 0, 2048, 2048);
    // contact shadow under the jet: a soft ellipse, long along the fuselage
    g.save(); g.translate(C2 - .5 * px, C2); g.scale(13 * px, 6 * px);
    r = g.createRadialGradient(0, 0, 0, 0, 0, 1); r.addColorStop(0, 'rgba(0,0,0,.85)'); r.addColorStop(1, 'rgba(0,0,0,0)');
    g.fillStyle = r; g.beginPath(); g.arc(0, 0, 1, 0, 7); g.fill(); g.restore();
    g.strokeStyle = 'rgba(224,180,92,.34)'; g.lineWidth = 3;
    for (const rr of [8.3, 12, 15.7]){ g.beginPath(); g.arc(C2, C2, rr * px, 0, 7); g.stroke(); }
    g.setLineDash([10, 22]); g.strokeStyle = 'rgba(224,180,92,.22)'; g.lineWidth = 2.5;
    for (let a = 0; a < 12; a++){ const c = Math.cos(a / 12 * Math.PI * 2), sn = Math.sin(a / 12 * Math.PI * 2); g.beginPath(); g.moveTo(C2 + c * 8.3 * px, C2 + sn * 8.3 * px); g.lineTo(C2 + c * 15.7 * px, C2 + sn * 15.7 * px); g.stroke(); }
    // fade the disc's edge into the outer floor color so there's no seam
    r = g.createRadialGradient(C2, C2, .8 * C2, C2, C2, C2); r.addColorStop(0, 'rgba(6,6,6,0)'); r.addColorStop(1, 'rgba(6,6,6,1)');
    g.fillStyle = r; g.fillRect(0, 0, 2048, 2048);
  });
  {
    const inner = new THREE.Mesh(new THREE.CircleGeometry(FR, 96), new THREE.MeshBasicMaterial({ map:floorTex }));
    inner.rotation.x = -Math.PI / 2; inner.position.y = FY; scene.add(inner);
    const outer = new THREE.Mesh(new THREE.RingGeometry(FR, 220, 96), new THREE.MeshBasicMaterial({ color:0x060606 }));
    outer.rotation.x = -Math.PI / 2; outer.position.y = FY; scene.add(outer);
  }
  const DUST = LITE ? 150 : 340;
  const dustPos = new Float32Array(DUST * 3), dustSeed = new Float32Array(DUST);
  for (let i = 0; i < DUST; i++){ dustPos[i*3] = rnd(-16, 16); dustPos[i*3+1] = rnd(FY, 8); dustPos[i*3+2] = rnd(-13, 13); dustSeed[i] = Math.random(); }
  const dustGeo = new THREE.BufferGeometry(); dustGeo.setAttribute('position', new THREE.BufferAttribute(dustPos, 3));
  scene.add(new THREE.Points(dustGeo, new THREE.PointsMaterial({ size:.07, map:halo, color:0xffdf9e, transparent:true, opacity:.5, depthWrite:false, blending:THREE.AdditiveBlending, sizeAttenuation:true })));

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
  const nSeg = segs.length / 6;
  const order = Array.from({ length:nSeg }, (_, i) => i).sort((i, j) => (segs[j*6] + segs[j*6+3]) - (segs[i*6] + segs[i*6+3]));
  const arr = new Float32Array(segs.length);
  order.forEach((s, k) => { for (let q = 0; q < 6; q++) arr[k*6+q] = segs[s*6+q]; });
  const lineGeo = new THREE.BufferGeometry(); lineGeo.setAttribute('position', new THREE.BufferAttribute(arr, 3));
  const lineMat = new THREE.LineBasicMaterial({ color:0xe0b45c, transparent:true, opacity:.9, depthWrite:false });
  scene.add(new THREE.LineSegments(lineGeo, lineMat));
  lineGeo.setDrawRange(0, 0);
  const totalVerts = arr.length / 3;

  const scan = new THREE.Mesh(new THREE.RingGeometry(1.16, 1.3, 72), new THREE.MeshBasicMaterial({ color:new THREE.Color(5, 3.8, 1.9), transparent:true, opacity:0, blending:THREE.AdditiveBlending, depthWrite:false, side:THREE.DoubleSide, toneMapped:false }));
  scan.rotation.y = Math.PI / 2; scene.add(scan);

  /* ---------------- camera stops (same order as the cards) ---------------- */
  const P = new THREE.Vector3(); patch.getWorldPosition(P);
  const LE = wings[1].localToWorld(V(-.42, -.07, 4.6));
  const KF = [
    { p:V(22.5, 8.2, 25.5),  t:V(-1.2, .2, 0) },                   // overview
    { p:V(14.2, .9, 5.6),    t:V(9.0, -.2, 0) },                   // nose
    { p:V(10.6, 3.5, 3.8),   t:V(7.0, .6, 0) },                    // windscreen
    { p:V(4.4, 1.2, 11.8),   t:V(-.8, -.6, 5.2) },                 // leading edge
    { p:P.clone().add(V(.22, .12, .5)), t:P.clone() },             // one square foot, on the fin
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
  let W = 1, H = 1;
  function resize(){
    W = canvas.clientWidth || innerWidth; H = canvas.clientHeight || innerHeight;
    portrait = W / H < .85;
    const pr = Math.min(devicePixelRatio || 1, portrait ? 1.5 : 1.75);
    renderer.setPixelRatio(pr); renderer.setSize(W, H, false);
    camera.aspect = W / H; camera.updateProjectionMatrix();
  }
  resize(); addEventListener('resize', resize);
  let mx = 0, my = 0, tmx = 0, tmy = 0;
  if (FINE) root.addEventListener('pointermove', e => { tmx = e.clientX / innerWidth * 2 - 1; tmy = e.clientY / innerHeight * 2 - 1; });

  let inView = false, raf = 0, introAt = null, readyShown = false, last = performance.now();
  // Run only while the section is on (or near) the screen; check on every scroll too,
  // so the loop never waits on a late visibility callback.
  const near = () => { const b = root.getBoundingClientRect(); return b.top < innerHeight + 200 && b.bottom > -200; };
  const wake = () => { inView = near(); if (inView && !raf && !document.hidden){ last = performance.now(); raf = requestAnimationFrame(frame); } };
  new IntersectionObserver(wake, { rootMargin:'200px 0px 200px 0px' }).observe(root);
  addEventListener('scroll', wake, { passive:true }); addEventListener('resize', wake);
  document.addEventListener('visibilitychange', () => { if (!document.hidden && inView && !raf){ last = performance.now(); raf = requestAnimationFrame(frame); } });

  const P0 = new THREE.Vector3(), T0 = new THREE.Vector3(), camP = new THREE.Vector3(), camT = new THREE.Vector3();
  const off3 = new THREE.Vector3(), fwd = new THREE.Vector3(), right = new THREE.Vector3(), upv = new THREE.Vector3(), UP = V(0, 1, 0), proj = new THREE.Vector3();
  let active = -1, pSm = null, camInit = false;
  const legOf = p => { for (let i = 0; i < LEG.length; i++) if (p <= CUM[i + 1] || i === LEG.length - 1) return [i, clamp((p - CUM[i]) / (CUM[i + 1] - CUM[i]), 0, 1)]; };

  function frame(now){
    raf = 0;
    const dt = Math.min(.05, (now - last) / 1000); last = now;
    const t = now / 1000;
    const r = root.getBoundingClientRect(), span = Math.max(1, r.height - innerHeight);
    if (introAt === null && r.top < innerHeight * .95) introAt = now;

    // damped scroll
    const pRaw = clamp(-r.top / span, 0, 1);
    if (pSm === null || REDUCED || REDUCED_SNAP.on) pSm = pRaw;
    pSm = damp(pSm, pRaw, 4.5, dt);
    const [i, f] = legOf(pSm);

    // The build, driven by scroll. The gold lines start drawing on their own as soon as the
    // section shows up (motion before anyone scrolls); from there the first stretch of scroll
    // sweeps the jet solid, nose to tail, while the camera circles it. The camera doesn't head
    // for the nose until the jet is 100% built, and scrolling back up un-builds it.
    const T = introAt === null ? 0 : (now - introAt) / 1000;
    const build = REDUCED ? 1 : i > 0 ? 1 : clamp(f / BUILD_END, 0, 1);
    const drawK = REDUCED ? 1 : clamp(Math.max(T / 1.8, build / .3), 0, 1);
    const reveal = REDUCED ? 1 : smooth(clamp((build - .25) / .75, 0, 1));
    const swing = REDUCED ? 0 : 1 - easeOut(build);
    lineGeo.setDrawRange(0, Math.floor(drawK * totalVerts / 2) * 2);
    const cx = 11.2 - reveal * 23.6;
    cut.value = cx;
    scan.position.x = cx; scan.scale.setScalar((rad(10 - cx) || .3) / 1.1 + .06);
    scan.material.opacity = reveal > 0 && reveal < 1 ? Math.sin(reveal * Math.PI) : 0;

    // never a dead stop: legs ease through their stops instead of parking on them.
    // The square-foot leg holds the camera on the tail (with a slow orbit) while it cleans.
    let cu, sub = i > 4 ? 1 : 0, hold = 0;
    if (i === 0) cu = easeIO(clamp((f - BUILD_END) / (1 - BUILD_END), 0, 1));
    else if (i === 4){
      if (f < .66){ hold = f / .66; cu = 4; sub = hold; }
      else { cu = 4 + easeIO((f - .66) / .34); sub = 1; hold = 1; }
    } else cu = i + f - .78 * Math.sin(2 * Math.PI * f) / (2 * Math.PI);
    macro(sub);
    cabin.visible = cu > 6.2 && cu < 7.8;
    dirtIM.parent.visible = cu > 2.6 && cu < 5.4;

    const xr = clamp(1 - Math.abs(cu - 7) / .7, 0, 1);
    hullM.opacity = 1 - .87 * xr; hullM.depthWrite = xr < .02;
    glass.opacity = 1 - .8 * xr; winM.opacity = 1 - .8 * xr;
    lineMat.opacity = (.9 - .78 * reveal) + xr * .4;
    const macroK = clamp(1 - Math.abs(cu - 4) / .6, 0, 1);
    renderer.toneMappingExposure = 1.02 + .15 * macroK;

    // camera on the rails, plus orbit, intro swing, mouse and a breath of drift
    const u = cu / (N - 1);
    posC.getPoint(u, P0); tgtC.getPoint(u, T0);
    off3.subVectors(P0, T0);
    let ang = Math.sin(t * .17) * .05 + swing * 1.15;
    if (i === 4 && f < .66) ang -= (hold - .35) * .9;   // swings toward the nose side, looking away from the emblem
    off3.applyAxisAngle(UP, ang);
    off3.multiplyScalar(1 + swing * .3 + (portrait ? (macroK > .5 ? .2 : .22) : 0));
    off3.y += swing * 2.2;
    P0.copy(T0).add(off3);
    const d = off3.length();
    fwd.subVectors(T0, P0).normalize(); right.crossVectors(fwd, UP).normalize(); upv.crossVectors(right, fwd);
    if (portrait) T0.addScaledVector(upv, -d * .1); else T0.addScaledVector(right, -d * .11);
    mx = damp(mx, tmx, 3, dt); my = damp(my, tmy, 3, dt);
    if (!REDUCED){ P0.addScaledVector(right, mx * d * .035).addScaledVector(upv, -my * d * .025); P0.y += Math.sin(t * .5) * d * .005; }
    if (!camInit || REDUCED_SNAP.on){ camP.copy(P0); camT.copy(T0); camInit = true; }
    camP.x = damp(camP.x, P0.x, 7, dt); camP.y = damp(camP.y, P0.y, 7, dt); camP.z = damp(camP.z, P0.z, 7, dt);
    camT.x = damp(camT.x, T0.x, 7, dt); camT.y = damp(camT.y, T0.y, 7, dt); camT.z = damp(camT.z, T0.z, 7, dt);
    camera.position.copy(camP); camera.lookAt(camT);
    const nearWanted = clamp(camP.distanceTo(camT) * .02, .01, .4);
    if (Math.abs(camera.near - nearWanted) > .002){ camera.near = nearWanted; camera.updateProjectionMatrix(); }
    const fov = portrait ? 52 : 36;
    if (Math.abs(camera.fov - fov) > .01){ camera.fov = fov; camera.updateProjectionMatrix(); }

    // life: lights blink, fans turn, dust drifts
    const on = reveal >= 1;
    for (const L of lights) L.g.visible = on;
    navG.sp.material.opacity = navR.sp.material.opacity = .9;
    const st = t % 1.3, strobe = st < .05 || (st > .13 && st < .18) ? 1 : 0;
    strobes.forEach(L => { L.sp.material.opacity = strobe; L.sp.scale.setScalar(L.size * (strobe ? 1.4 : .01)); });
    const bk = Math.exp(-((t + .4) % 1.1) * 9);
    beacons.forEach(L => { L.sp.material.opacity = bk; L.sp.scale.setScalar(L.size * (.4 + bk)); });
    beamMat.uniforms.uOp.value = on ? .9 : 0;
    fans.forEach(fan => fan.rotation.y += dt * 2.2);
    const dp = dustGeo.attributes.position.array;
    for (let k = 0; k < DUST; k++){
      dp[k*3+1] += dt * (.06 + dustSeed[k] * .1); dp[k*3] += Math.sin(t * .3 + dustSeed[k] * 20) * dt * .05;
      if (dp[k*3+1] > 8) dp[k*3+1] = FY;
    }
    dustGeo.attributes.position.needsUpdate = true;

    renderer.render(scene, camera);
    if (!readyShown){ readyShown = true; root.classList.add('ready'); }

    // UI
    const a = clamp(Math.round(cu), 0, N - 1);
    if (a !== active){
      active = a;
      cards.forEach((c, k) => c.classList.toggle('on', k === a));
      navBtns.forEach((b, k) => b.classList.toggle('on', k === a));
      countEl.innerHTML = `<b>${String(a + 1).padStart(2, '0')}</b> / ${String(N).padStart(2, '0')}`;
    }
    barEl.style.setProperty('--p', pSm.toFixed(4));
    const h = HOT[Math.round(cu)], atStop = Math.abs(cu - Math.round(cu)) < .12 && on;
    if (h && atStop){
      proj.copy(h.p).project(camera);
      if (proj.z < 1){
        hot.style.transform = `translate(${((proj.x * .5 + .5) * W).toFixed(1)}px,${((-proj.y * .5 + .5) * H).toFixed(1)}px)`;
        if (hotLb.textContent !== h.l) hotLb.textContent = h.l;
        hot.classList.add('on');
      } else hot.classList.remove('on');
    } else hot.classList.remove('on');

    inView = near();
    if (inView && !document.hidden) raf = requestAnimationFrame(frame);
  }
  // Test hook (only with ?debug3d): render one frame as if `sec` seconds into the intro, with
  // no damping, and hand back the image. Used to check stops where animation frames don't run.
  // Compile every shader before the first frame, so nothing pops in half-ready.
  cut.value = -40;
  camera.position.copy(KF[0].p); camera.lookAt(KF[0].t); camera.updateMatrixWorld();
  try { await renderer.compileAsync(scene, camera); } catch (_) { renderer.compile(scene, camera); }
  cut.value = 40;
  if (/debug3d/.test(location.search)) window.__tourDebug = { scene, camera, jet, lineGeo, cut, renderer, get introAt(){ return introAt; }, get pSm(){ return pSm; } };
  if (/debug3d/.test(location.search)) window.__tourSnap = (sec = 10) => {
    introAt = performance.now() - sec * 1000; pSm = null; camInit = false;
    const saved = REDUCED_SNAP.on; REDUCED_SNAP.on = true; frame(performance.now()); frame(performance.now()); REDUCED_SNAP.on = saved;
    if (raf){ cancelAnimationFrame(raf); raf = 0; }
    // read back through an offscreen target (the hidden test browser never presents the canvas)
    const w = Math.round(W * 1.5), h = Math.round(H * 1.5);
    const rt = new THREE.WebGLRenderTarget(w, h, { colorSpace:THREE.SRGBColorSpace, samples:4 });
    renderer.setRenderTarget(rt); renderer.render(scene, camera); renderer.setRenderTarget(null);
    const px = new Uint8Array(w * h * 4); renderer.readRenderTargetPixels(rt, 0, 0, w, h, px); rt.dispose();
    const c2 = document.createElement('canvas'); c2.width = w; c2.height = h; const g2 = c2.getContext('2d');
    const img = g2.createImageData(w, h);
    for (let y = 0; y < h; y++) img.data.set(px.subarray((h - 1 - y) * w * 4, (h - y) * w * 4), y * w * 4);
    g2.putImageData(img, 0, 0);
    return c2.toDataURL('image/jpeg', .85);
  };
  wake();
}
