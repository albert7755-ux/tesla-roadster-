import base64
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Yield Runner 飛天跑車", layout="wide", page_icon="🏎️")

# ── 讀取 3D 車子模型（roadster.glb 要跟這個 .py 放在同一個資料夾）──
MODEL_PATH = Path(__file__).parent / "roadster.glb"


@st.cache_data
def load_car_model():
    if MODEL_PATH.exists():
        return base64.b64encode(MODEL_PATH.read_bytes()).decode("ascii")
    return ""


car_b64 = load_car_model()

# ── 側邊欄：市場壓力測試設定 ──
with st.sidebar:
    st.header("⚡ 債券市場壓力測試")
    base_rate = st.slider("SOFR 浮動基準利率 (%)", 1.0, 10.0, 5.5, 0.25,
                          help="利率越高，飛行時賺得越快、飛得越高")
    credit_spread = st.slider("非投資級利差 (bps)", 100, 800, 350, 25,
                              help="利差越大，票息越肥，但違約尖錐也越多")
    inversion_level = st.select_slider("曲線倒掛強度",
                                       options=["正常平緩", "微幅倒掛", "極端倒掛風暴"],
                                       value="微幅倒掛",
                                       help="倒掛越嚴重，可以走的車道越少")
    st.markdown("---")
    st.write("**操作說明**")
    st.write("👉 先點一下右邊畫面，再按「開始」")
    st.write("🎮 **A / D 或 ← →**：換車道，閃避紅色違約尖錐")
    st.write("🚀 **按住空白鍵**：飛行，收益加速，但會**消耗流動性**")
    st.write("💎 **綠色票息**（地面）：補流動性＋加報酬")
    st.write("⭐ **金色高收益票息**（空中）：只有飛起來才吃得到")
    st.write("⏱️ 60 秒結算，看誰的投組報酬最高！")
    st.markdown("---")
    st.caption("💡 教學重點：想追高收益就要動用流動性；流動性見底時再撞到違約，就會斷頭。")
    if not car_b64:
        st.warning("找不到 roadster.glb，先用簡易車型代替。請把 roadster.glb 上傳到跟這個 .py 同一個資料夾。")

LANES = {"正常平緩": 5, "微幅倒掛": 4, "極端倒掛風暴": 3}[inversion_level]

raw_html = r"""
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body { margin:0; overflow:hidden; background:#03050c; font-family:'Segoe UI','Microsoft JhengHei',sans-serif; user-select:none; }
  #hud { position:absolute; top:14px; left:18px; color:#fff; z-index:100; pointer-events:none; text-shadow:0 0 10px #00ffcc; }
  .metric { font-size:15px; margin-bottom:4px; }
  .hl { color:#00ffcc; font-size:21px; font-weight:bold; }
  #bar-wrap { width:190px; height:10px; border:1px solid #00ff88; border-radius:5px; margin-top:2px; overflow:hidden; }
  #bar { height:100%; width:100%; background:#00ff88; transition:width .1s; }
  #timer { position:absolute; top:14px; left:50%; transform:translateX(-50%); color:#fff; font-size:40px; font-weight:bold;
           text-shadow:0 0 14px #ff00aa; pointer-events:none; z-index:100; }
  #speed { position:absolute; bottom:24px; right:24px; color:#00ffcc; font-size:30px; font-weight:bold; text-align:right;
           pointer-events:none; text-shadow:0 0 15px rgba(0,255,204,.6); }
  #toast { position:absolute; top:80px; left:50%; transform:translateX(-50%); color:#ffdd00; font-size:22px; font-weight:bold;
           text-shadow:0 0 12px #000; pointer-events:none; opacity:0; transition:opacity .3s; z-index:150; }
  #credit { position:absolute; bottom:6px; left:10px; color:rgba(255,255,255,.45); font-size:11px; pointer-events:none; }
  .panel { position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); text-align:center; z-index:200;
           background:rgba(3,5,12,.88); border:2px solid #00ffcc; border-radius:12px; padding:26px 40px; color:#fff; min-width:340px; }
  .panel h1 { margin:0 0 10px; font-size:30px; color:#00ffcc; text-shadow:0 0 14px #00ffcc; }
  .panel p { margin:6px 0; font-size:16px; }
  .big { font-size:34px; font-weight:bold; color:#ffaa00; }
  button { margin-top:16px; padding:10px 28px; font-size:18px; color:#03050c; background:#00ffcc; border:none; cursor:pointer;
           border-radius:6px; font-weight:bold; }
  #over { display:none; }
  #over.fail h1 { color:#ff0055; text-shadow:0 0 14px #ff0055; }
  #over.fail { border-color:#ff0055; }
</style>
<script type="importmap">
{ "imports": {
    "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
    "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
} }
</script>
</head>
<body tabindex="0">
  <div id="hud">
    <div class="metric">利差 SPREAD：<span class="hl">__SPREAD__ bps</span></div>
    <div class="metric">SOFR：<span class="hl">__RATE__%</span>　車道：<span class="hl">__LANES__</span></div>
    <div class="metric">流動性 LIQUIDITY：<span id="liq" class="hl" style="color:#00ff88">100%</span>
      <div id="bar-wrap"><div id="bar"></div></div></div>
    <div class="metric">投組報酬 RETURN：<span id="ret" class="hl" style="color:#ffaa00">+0.00%</span></div>
  </div>
  <div id="timer">60</div>
  <div id="toast"></div>
  <div id="speed"><span id="spd">120</span> <span style="font-size:15px">MPH</span></div>
  <div id="credit">3D model "Tesla Roadster 2020" by metarex.4d (Sketchfab), CC-BY-4.0</div>

  <div id="start" class="panel">
    <h1>YIELD RUNNER 飛天跑車</h1>
    <p>60 秒內，衝出最高投組報酬！</p>
    <p style="color:#aaa;font-size:14px">← → 換車道　|　按住空白鍵飛行</p>
    <p id="load-msg" style="color:#ffdd00;font-size:14px">車子模型載入中…</p>
    <button id="start-btn">開始</button>
  </div>

  <div id="over" class="panel">
    <h1 id="over-title">結算</h1>
    <p>投組報酬</p>
    <div class="big" id="final-ret">+0.00%</div>
    <p id="grade" style="font-size:22px;margin-top:10px"></p>
    <p id="stats" style="color:#aaa;font-size:14px"></p>
    <p id="lesson" style="color:#00ffcc;font-size:14px"></p>
    <button id="restart-btn">再跑一次</button>
  </div>

<script type="module">
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { MeshoptDecoder } from 'three/addons/libs/meshopt_decoder.module.js';

const RATE = __RATE__;
const SPREAD = __SPREAD__;
const LANES = __LANES__;
const CAR_B64 = "__CAR_B64__";
const LANE_GAP = 3.0;
const GAME_TIME = 60;

window.focus();
document.body.addEventListener('click', () => window.focus());

// ── 場景 ──
const scene = new THREE.Scene();
scene.fog = new THREE.FogExp2(0x04060f, 0.011);
const camera = new THREE.PerspectiveCamera(62, innerWidth / innerHeight, 0.1, 1000);
camera.position.set(0, 3.2, -8);
const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setSize(innerWidth, innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.2;
renderer.outputColorSpace = THREE.SRGBColorSpace;
document.body.appendChild(renderer.domElement);

// 簡易環境反射，讓車漆有光澤
const pmrem = new THREE.PMREMGenerator(renderer);
const envScene = new THREE.Scene();
envScene.background = new THREE.Color(0x101830);
const l1 = new THREE.Mesh(new THREE.PlaneGeometry(20, 4), new THREE.MeshBasicMaterial({ color: 0x00f0ff }));
l1.position.set(0, 8, 0); l1.rotation.x = Math.PI / 2; envScene.add(l1);
const l2 = new THREE.Mesh(new THREE.PlaneGeometry(8, 8), new THREE.MeshBasicMaterial({ color: 0xff2080 }));
l2.position.set(-10, 2, 0); l2.rotation.y = Math.PI / 2; envScene.add(l2);
scene.environment = pmrem.fromScene(envScene, 0.04).texture;

scene.add(new THREE.AmbientLight(0xffffff, 0.6));
const dl1 = new THREE.DirectionalLight(0x00f0ff, 2.2); dl1.position.set(15, 20, -10); scene.add(dl1);
const dl2 = new THREE.DirectionalLight(0xff0055, 1.6); dl2.position.set(-15, 10, 10); scene.add(dl2);
const dl3 = new THREE.DirectionalLight(0xffffff, 1.2); dl3.position.set(0, 10, -15); scene.add(dl3);

// ── 道路（寬度隨倒掛強度變窄）──
const halfRoad = (LANES * LANE_GAP) / 2 + 0.5;
const road = new THREE.Mesh(new THREE.PlaneGeometry(halfRoad * 2, 700),
  new THREE.MeshStandardMaterial({ color: 0x0a0f1d, roughness: 0.3, metalness: 0.8 }));
road.rotation.x = -Math.PI / 2; road.position.z = 300; scene.add(road);
const barrierMat = new THREE.MeshBasicMaterial({ color: 0x00ffcc });
[-1, 1].forEach(s => {
  const b = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.8, 700), barrierMat);
  b.position.set(s * halfRoad, 0.4, 300); scene.add(b);
});
// 車道虛線
const dashes = [];
const dashMat = new THREE.MeshBasicMaterial({ color: 0x1d4a66 });
for (let k = 1; k < LANES; k++) {
  const x = -halfRoad + 0.5 + k * LANE_GAP;
  for (let i = 0; i < 40; i++) {
    const d = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.02, 3), dashMat);
    d.position.set(x, 0.02, i * 12); scene.add(d); dashes.push(d);
  }
}
const laneX = i => -halfRoad + 0.5 + LANE_GAP / 2 + i * LANE_GAP;

// ── 兩側金融大樓 ──
const buildings = [];
const bMat = new THREE.MeshStandardMaterial({ color: 0x060914, roughness: 0.2, metalness: 0.9 });
const wMat = new THREE.MeshBasicMaterial({ color: 0x00e5ff, wireframe: true });
for (let i = 0; i < 40; i++) {
  const h = 25 + Math.random() * 50, w = 12 + Math.random() * 10, side = i % 2 ? -1 : 1;
  const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, 20), bMat);
  m.add(new THREE.Mesh(new THREE.BoxGeometry(w + 0.1, h + 0.1, 20.1), wMat));
  m.position.set(side * (halfRoad + 10 + w / 2), h / 2 - 2, i * 25);
  scene.add(m); buildings.push(m);
}

// ── 車子 ──
const car = new THREE.Group();
scene.add(car);
const flameMat = new THREE.MeshBasicMaterial({ color: 0x00ffff, transparent: true, opacity: 0 });
const flameGeo = new THREE.ConeGeometry(0.22, 1.8, 16); flameGeo.rotateX(-Math.PI / 2);
const flames = [-0.55, 0.55].map(x => { const f = new THREE.Mesh(flameGeo, flameMat); f.position.set(x, 0.5, -2.9); car.add(f); return f; });

function buildFallbackCar() {
  const paint = new THREE.MeshStandardMaterial({ color: 0xd90429, metalness: 0.9, roughness: 0.15 });
  const body = new THREE.Mesh(new THREE.BoxGeometry(2.0, 0.5, 4.4), paint); body.position.y = 0.45; car.add(body);
  const glass = new THREE.Mesh(new THREE.SphereGeometry(0.85, 16, 16),
    new THREE.MeshStandardMaterial({ color: 0x05070d, metalness: 0.95, roughness: 0.05 }));
  glass.scale.set(0.95, 0.65, 2.0); glass.position.set(0, 0.85, -0.2); car.add(glass);
  const wg = new THREE.CylinderGeometry(0.42, 0.42, 0.3, 16); wg.rotateZ(Math.PI / 2);
  const wm = new THREE.MeshStandardMaterial({ color: 0x1f242d });
  [[-1.05, 1.4], [1.05, 1.4], [-1.05, -1.3], [1.05, -1.3]].forEach(([x, z]) => {
    const w = new THREE.Mesh(wg, wm); w.position.set(x, 0.42, z); car.add(w);
  });
}

const loadMsg = document.getElementById('load-msg');
if (CAR_B64.length > 10) {
  const bin = Uint8Array.from(atob(CAR_B64), c => c.charCodeAt(0));
  const loader = new GLTFLoader();
  loader.setMeshoptDecoder(MeshoptDecoder);
  loader.parse(bin.buffer, '', gltf => {
    const model = gltf.scene;
    // 車漆改成賽博紅（想換顏色就改 0xd90429 這個色碼）
    model.traverse(o => {
      if (o.isMesh && o.material && /paint/i.test(o.material.name)) {
        o.material.color.set(0xd90429); o.material.metalness = 0.6; o.material.roughness = 0.25;
      }
    });
    // 自動縮放成約 4.6 公尺長、車頭朝前方
    const box = new THREE.Box3().setFromObject(model);
    const size = box.getSize(new THREE.Vector3());
    const s = 4.6 / Math.max(size.x, size.z);
    model.scale.setScalar(s);
    model.rotation.y = __MODEL_YAW__;
    const box2 = new THREE.Box3().setFromObject(model);
    const c = box2.getCenter(new THREE.Vector3());
    model.position.set(-c.x, -box2.min.y, -c.z);
    car.add(model);
    loadMsg.textContent = '✅ 車子準備好了';
    loadMsg.style.color = '#00ff88';
  }, err => {
    console.error(err);
    buildFallbackCar();
    loadMsg.textContent = '模型載入失敗，改用簡易車型';
  });
} else {
  buildFallbackCar();
  loadMsg.textContent = '（未放入 roadster.glb，使用簡易車型）';
}

// ── 違約尖錐與票息 ──
const trapCount = Math.round(3 + (SPREAD - 100) / 100);          // 利差 100bps→3 個，800bps→10 個
const groundCouponGain = 0.3 + SPREAD / 1000;                     // 地面票息報酬（%）
const skyCouponGain = 0.8 + SPREAD / 400;                         // 空中高收益票息報酬（%）
const randLane = () => laneX(Math.floor(Math.random() * LANES));

const trapGeo = new THREE.ConeGeometry(0.7, 1.5, 8);
const trapMat = new THREE.MeshStandardMaterial({ color: 0xff0044, emissive: 0xaa0033 });
const traps = [];
for (let i = 0; i < trapCount; i++) {
  const t = new THREE.Mesh(trapGeo, trapMat); t.position.y = 0.75; scene.add(t); traps.push(t);
}
const gMat = new THREE.MeshStandardMaterial({ color: 0x00ff88, emissive: 0x00aa44 });
const sMat = new THREE.MeshStandardMaterial({ color: 0xffcc00, emissive: 0xaa7700 });
const coupons = [];
for (let i = 0; i < 4; i++) {
  const c = new THREE.Mesh(new THREE.OctahedronGeometry(0.7), gMat); c.userData.sky = false; c.position.y = 1.0;
  scene.add(c); coupons.push(c);
}
for (let i = 0; i < 3; i++) {
  const c = new THREE.Mesh(new THREE.OctahedronGeometry(0.8), sMat); c.userData.sky = true; c.position.y = 3.2;
  scene.add(c); coupons.push(c);
}
function placeAll() {
  traps.forEach((t, i) => { t.position.x = randLane(); t.position.z = 60 + i * (360 / trapCount) + Math.random() * 20; });
  coupons.forEach((c, i) => { c.position.x = randLane(); c.position.z = 40 + i * 55 + Math.random() * 20; });
}

// ── 遊戲狀態 ──
let state = 'ready';   // ready / play / over
let lane = Math.floor(LANES / 2), liquidity = 100, ret = 0, timeLeft = GAME_TIME;
let boosting = false, spaceHeld = false, lockout = false, crashes = 0, grabbed = 0, flash = 0;
const baseSpeed = 120;

const $ = id => document.getElementById(id);
function toast(msg, color) {
  const t = $('toast'); t.textContent = msg; t.style.color = color || '#ffdd00'; t.style.opacity = 1;
  clearTimeout(t._h); t._h = setTimeout(() => t.style.opacity = 0, 1100);
}
function updateHud() {
  $('liq').textContent = Math.round(liquidity) + '%';
  const col = liquidity > 50 ? '#00ff88' : liquidity > 25 ? '#ffcc00' : '#ff0055';
  $('liq').style.color = col; $('bar').style.background = col; $('bar').style.width = liquidity + '%';
  $('ret').textContent = (ret >= 0 ? '+' : '') + ret.toFixed(2) + '%';
  $('timer').textContent = Math.ceil(timeLeft);
}
function startGame() {
  lane = Math.floor(LANES / 2); liquidity = 100; ret = 0; timeLeft = GAME_TIME;
  crashes = 0; grabbed = 0; lockout = false; boosting = false;
  car.position.set(laneX(lane), 0, 0);
  placeAll(); updateHud();
  $('start').style.display = 'none'; $('over').style.display = 'none';
  state = 'play'; window.focus();
}
function endGame(defaulted) {
  state = 'over'; boosting = false; flameMat.opacity = 0;
  const o = $('over'); o.className = 'panel' + (defaulted ? ' fail' : ''); o.style.display = 'block';
  $('over-title').textContent = defaulted ? '流動性違約！斷頭出場' : '60 秒結算';
  $('final-ret').textContent = (ret >= 0 ? '+' : '') + ret.toFixed(2) + '%';
  const g = defaulted ? 'D 級：違約' : ret >= 25 ? 'S 級：投資機長' : ret >= 15 ? 'A 級：穩健操盤' : ret >= 8 ? 'B 級：還有進步空間' : 'C 級：再接再厲';
  $('grade').textContent = '評等 ' + g;
  $('stats').textContent = `吃到票息 ${grabbed} 顆　撞到違約 ${crashes} 次`;
  $('lesson').textContent = defaulted
    ? '提醒：飛太久把流動性用光，一碰到違約就扛不住。'
    : (crashes === 0 ? '零違約！好的信用篩選就是最好的報酬。' : '利差越高、票息越肥，但違約尖錐也越多。');
}
$('start-btn').onclick = startGame;
$('restart-btn').onclick = startGame;

addEventListener('keydown', e => {
  if (e.code === 'Space') { e.preventDefault(); spaceHeld = true; }
  if (state !== 'play') { if (e.code === 'Enter' || e.code === 'Space') { if (state === 'ready') startGame(); } return; }
  if (e.key === 'a' || e.key === 'A' || e.key === 'ArrowLeft') lane = Math.max(0, lane - 1);
  if (e.key === 'd' || e.key === 'D' || e.key === 'ArrowRight') lane = Math.min(LANES - 1, lane + 1);
});
addEventListener('keyup', e => { if (e.code === 'Space') spaceHeld = false; });

// ── 主迴圈 ──
const clock = new THREE.Clock();
function animate() {
  requestAnimationFrame(animate);
  const dt = Math.min(clock.getDelta(), 0.05);
  const t = clock.elapsedTime;

  if (state === 'play') {
    timeLeft -= dt;
    if (timeLeft <= 0) { timeLeft = 0; updateHud(); endGame(false); }

    // 飛行：消耗流動性；流動性用光就強制降落，回到 25% 才能再飛
    if (lockout && liquidity >= 25) lockout = false;
    boosting = spaceHeld && !lockout;
    if (boosting) {
      liquidity -= 16 * dt;
      ret += RATE * 0.05 * dt;
      if (liquidity <= 0) { liquidity = 0; lockout = true; toast('流動性枯竭！強制降落', '#ff0055'); }
    } else {
      liquidity = Math.min(100, liquidity + 4 * dt);
      ret += RATE * 0.008 * dt;
    }
    flameMat.opacity = boosting ? 0.6 + Math.random() * 0.35 : 0;

    const speed = baseSpeed * (boosting ? 2.0 : 1.0) * (1 + (GAME_TIME - timeLeft) / 120);
    const move = speed * dt * 1.6;
    $('spd').textContent = Math.round(speed);

    const targetY = boosting ? 2.4 + RATE * 0.12 : 0;
    car.position.y = THREE.MathUtils.lerp(car.position.y, targetY, dt * 6);
    car.rotation.x = boosting ? -0.12 : 0;
    const tx = laneX(lane);
    car.position.x += (tx - car.position.x) * Math.min(1, 12 * dt);
    car.rotation.z = (car.position.x - tx) * 0.12;

    buildings.forEach(b => { b.position.z -= move; if (b.position.z < -40) b.position.z += 1000; });
    dashes.forEach(d => { d.position.z -= move; if (d.position.z < -10) d.position.z += 480; });

    traps.forEach(tr => {
      tr.position.z -= move;
      if (tr.position.z < -10) { tr.position.z += 380 + Math.random() * 40; tr.position.x = randLane(); }
      const hit = Math.abs(tr.position.z - car.position.z) < 2.0 && Math.abs(tr.position.x - car.position.x) < 1.4;
      // 只有車子夠高才飛得過去（尖錐高 1.5）
      if (hit && car.position.y < 1.3) {
        crashes++; liquidity -= 30; ret -= 1.0; flash = 0.3;
        tr.position.z += 380;
        toast('撞到違約！流動性 -30%', '#ff0055');
        if (liquidity <= 0) { liquidity = 0; updateHud(); endGame(true); }
      }
    });

    coupons.forEach(c => {
      c.rotation.y += 2 * dt;
      c.position.z -= move;
      if (c.position.z < -10) { c.position.z += 360 + Math.random() * 40; c.position.x = randLane(); }
      const near = Math.abs(c.position.z - car.position.z) < 2.0 && Math.abs(c.position.x - car.position.x) < 1.6;
      const heightOk = c.userData.sky ? car.position.y > 1.8 : car.position.y < 1.5;
      if (near && heightOk) {
        grabbed++;
        if (c.userData.sky) { ret += skyCouponGain; toast('高收益票息 +' + skyCouponGain.toFixed(2) + '%', '#ffcc00'); }
        else { ret += groundCouponGain; liquidity = Math.min(100, liquidity + 12); toast('票息入袋 +' + groundCouponGain.toFixed(2) + '%　流動性 +12%', '#00ff88'); }
        c.position.z += 360;
      }
    });
    if (state === 'play') updateHud();
  } else {
    // 待機畫面：車子輕輕浮動
    car.position.y = 0.05 + Math.sin(t * 2) * 0.05;
    coupons.forEach(c => c.rotation.y += 2 * dt);
  }

  if (flash > 0) { flash -= dt; renderer.setClearColor(0x330011); } else renderer.setClearColor(0x03050c);
  camera.position.x = car.position.x * 0.5;
  camera.position.y = 3.2 + car.position.y * 0.6;
  camera.lookAt(car.position.x * 0.3, car.position.y + 0.8, 6);
  renderer.render(scene, camera);
}
placeAll();
animate();

addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});
</script>
</body>
</html>
"""

final_html = (raw_html
              .replace("__RATE__", f"{base_rate:.2f}")
              .replace("__SPREAD__", str(credit_spread))
              .replace("__LANES__", str(LANES))
              .replace("__MODEL_YAW__", "0")
              .replace("__CAR_B64__", car_b64))
components.html(final_html, height=720)
