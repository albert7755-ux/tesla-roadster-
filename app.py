import base64
import os
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Tesla Yield Runner 3D", layout="wide", page_icon="🏎️")

with st.sidebar:
    st.header("⚡ 債券市場參數 (Bond Market)")
    floating_rate = st.slider("浮動利率基準 (SOFR / Floating Benchmark %)", 2.0, 9.0, 5.25, 0.25)
    credit_spread = st.slider("信用利差 (Credit Spread bps)", 50, 500, 160, 10)
    st.markdown("---")
    st.write("**操作說明：**")
    st.write("🎮 **點擊右側遊戲畫面取得焦點**")
    st.write("🎮 **A / D 或 左右鍵**：換道避開 Default 違約錐")
    st.write("🚀 **空白鍵 (Space)**：點火發動冷氣噴射推進（推力取決於浮動利率高低！）")

# --- 讀取本地 glb 模型並轉為 Base64 ---
model_base64 = ""
glb_path = "tesla_roadster.glb"  # 確認你的 .glb 檔名與路徑

if os.path.exists(glb_path):
    with open(glb_path, "rb") as f:
        model_base64 = base64.b64encode(f.read()).decode("utf-8")
    model_uri = f"data:application/octet-stream;base64,{model_base64}"
else:
    # 備用線上有車子的公開 GLB 網址
    model_uri = "https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/Buggy/glTF-Binary/Buggy.glb"

# Three.js 3D 遊戲核心視窗
html_game = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ margin: 0; overflow: hidden; background: #050711; font-family: 'Segoe UI', monospace; }}
        #hud {{
            position: absolute; top: 15px; left: 20px; color: #fff; z-index: 100;
            pointer-events: none; text-shadow: 0 0 10px #00ffcc;
        }}
        .metric {{ font-size: 18px; margin-bottom: 5px; }}
        .highlight {{ color: #00ffcc; font-size: 22px; font-weight: bold; }}
        #tip {{
            position: absolute; bottom: 20px; width: 100%; text-align: center;
            color: #00ffcc; font-size: 14px; pointer-events: none; letter-spacing: 1px;
        }}
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
</head>
<body tabindex="0">
    <div id="hud">
        <div class="metric">FLOATING RATE: <span class="highlight">{floating_rate:.2f}%</span></div>
        <div class="metric">CREDIT SPREAD: <span class="highlight">{credit_spread} bps</span></div>
        <div class="metric" id="status">STATUS: CRUISING</div>
    </div>
    <div id="tip">【請先點擊一下遊戲畫面以啟用鍵盤控制】</div>

    <script>
        // 點擊畫面自動聚焦，確保鍵盤事件能被收到
        window.focus();
        document.body.addEventListener('click', () => {{ window.focus(); }});

        const scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x050711, 0.015);

        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(0, 2.5, -6.5);

        const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.3;
        document.body.appendChild(renderer.domElement);

        // --- 光照系統 ---
        const ambient = new THREE.AmbientLight(0xffffff, 1.2);
        scene.add(ambient);

        const dirLight = new THREE.DirectionalLight(0x00e5ff, 2.5);
        dirLight.position.set(5, 12, -8);
        scene.add(dirLight);

        const rearGlow = new THREE.PointLight(0xff0044, 3, 20);
        rearGlow.position.set(0, 1.5, -3);
        scene.add(rearGlow);

        // --- 霓虹跑道 ---
        const trackGeo = new THREE.PlaneGeometry(18, 400, 10, 80);
        const trackMat = new THREE.MeshBasicMaterial({{ color: 0x00ffcc, wireframe: true, transparent: true, opacity: 0.3 }});
        const track = new THREE.Mesh(trackGeo, trackMat);
        track.rotation.x = -Math.PI / 2;
        track.position.z = 150;
        scene.add(track);

        // --- 載入模型 (Base64 / 遠端) ---
        let car = new THREE.Group();
        scene.add(car);

        const modelUrl = "{model_uri}";
        const loader = new THREE.GLTFLoader();

        loader.load(modelUrl, (gltf) => {{
            const model = gltf.scene;

            // 自動計算模型的包圍盒並將其置中、調整到合適大小
            const box = new THREE.Box3().setFromObject(model);
            const size = box.getSize(new THREE.Vector3());
            const center = box.getCenter(new THREE.Vector3());

            // 調整車長至約 4.2 米
            const maxAxis = Math.max(size.x, size.y, size.z);
            const scale = 4.2 / maxAxis;
            model.scale.set(scale, scale, scale);

            // 重新置中
            model.position.x = -center.x * scale;
            model.position.y = -box.min.y * scale;
            model.position.z = -center.z * scale;

            car.add(model);
        }}, undefined, (err) => {{
            console.error("模型載入失敗", err);
        }});

        // --- 噴射尾焰 ---
        const flameGeo = new THREE.ConeGeometry(0.18, 1.4, 16);
        flameGeo.rotateX(Math.PI / 2);
        const flameMat = new THREE.MeshBasicMaterial({{ color: 0x00ffff, transparent: true, opacity: 0.0 }});
        const leftFlame = new THREE.Mesh(flameGeo, flameMat);
        const rightFlame = new THREE.Mesh(flameGeo, flameMat);
        leftFlame.position.set(-0.6, 0.4, -2.2);
        rightFlame.position.set(0.6, 0.4, -2.2);
        car.add(leftFlame);
        car.add(rightFlame);

        // --- 控制與物理 ---
        let targetX = 0;
        let isBoosting = false;
        let floatBoostPower = {floating_rate} * 1.6;

        window.addEventListener('keydown', (e) => {{
            if (e.key === 'a' || e.key === 'ArrowLeft') targetX = Math.max(-5.0, targetX - 2.5);
            if (e.key === 'd' || e.key === 'ArrowRight') targetX = Math.min(5.0, targetX + 2.5);
            if (e.code === 'Space') {{
                isBoosting = true;
                flameMat.opacity = 0.95;
                document.getElementById('status').innerText = 'STATUS: FLOATING BOOST ACTIVE!';
                document.getElementById('status').style.color = '#ff0055';
            }}
        }});

        window.addEventListener('keyup', (e) => {{
            if (e.code === 'Space') {{
                isBoosting = false;
                flameMat.opacity = 0.0;
                document.getElementById('status').innerText = 'STATUS: CRUISING';
                document.getElementById('status').style.color = '#fff';
            }}
        }});

        // 動畫循環
        let clock = new THREE.Clock();
        function animate() {{
            requestAnimationFrame(animate);
            let dt = clock.getDelta();

            // 左右轉向平滑跟隨
            car.position.x += (targetX - car.position.x) * 10 * dt;
            car.rotation.z = -(car.position.x - targetX) * 0.12;

            // 浮動利率噴射起飛
            if (isBoosting) {{
                car.position.y = THREE.MathUtils.lerp(car.position.y, 1.8 + (floatBoostPower * 0.1), dt * 8);
                car.rotation.x = -0.15;
            }} else {{
                car.position.y = THREE.MathUtils.lerp(car.position.y, 0.0, dt * 8);
                car.rotation.x = 0;
            }}

            // 賽道前進滾動
            track.position.z -= (50 + (isBoosting ? 30 : 0)) * dt;
            if (track.position.z < 50) track.position.z = 150;

            // 追尾攝影機跟隨
            camera.position.x = car.position.x * 0.45;
            camera.lookAt(car.position.x * 0.2, car.position.y + 0.9, car.position.z + 4);

            renderer.render(scene, camera);
        }}
        animate();

        window.addEventListener('resize', () => {{
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        }});
    </script>
</body>
</html>
"""

components.html(html_game, height=680)
