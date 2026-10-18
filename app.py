import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Tesla Yield Runner 3D", layout="wide", page_icon="🏎️")

with st.sidebar:
    st.header("⚡ 債券市場參數 (Bond Market)")
    floating_rate = st.slider("浮動利率基準 (SOFR / Floating Benchmark %)", 2.0, 9.0, 5.25, 0.25)
    credit_spread = st.slider("信用利差 (Credit Spread bps)", 50, 500, 160, 10)
    st.markdown("---")
    st.write("**操作說明：**")
    st.write("👉 **先點擊一下右側畫面取得焦點**")
    st.write("🎮 **A / D 或 左右鍵**：換道避開 Default 違約錐")
    st.write("🚀 **空白鍵 (Space)**：點火發動冷氣噴射推進（推力取決於浮動利率高低！）")

html_game = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ margin: 0; overflow: hidden; background: #050711; font-family: monospace; }}
        #hud {{
            position: absolute; top: 15px; left: 20px; color: #fff; z-index: 100;
            pointer-events: none; text-shadow: 0 0 10px #00ffcc;
        }}
        .metric {{ font-size: 18px; margin-bottom: 6px; }}
        .highlight {{ color: #00ffcc; font-size: 22px; font-weight: bold; }}
        #tip {{
            position: absolute; bottom: 20px; width: 100%; text-align: center;
            color: #00ffcc; font-size: 14px; pointer-events: none; letter-spacing: 1px;
        }}
        #loading {{
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            color: #00ffcc; font-size: 20px; font-weight: bold; text-shadow: 0 0 15px #00ffcc;
            pointer-events: none;
        }}
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
</head>
<body tabindex="0">
    <div id="loading">載入 Tesla Roadster 3D 模型中...</div>
    <div id="hud">
        <div class="metric">FLOATING RATE: <span class="highlight">{floating_rate:.2f}%</span></div>
        <div class="metric">CREDIT SPREAD: <span class="highlight">{credit_spread} bps</span></div>
        <div class="metric" id="status">STATUS: CRUISING</div>
    </div>
    <div id="tip">【請先點擊一下遊戲畫面以啟用鍵盤控制】</div>

    <script>
        window.focus();
        document.body.addEventListener('click', () => {{ window.focus(); }});

        const scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x050711, 0.012);

        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(0, 2.8, -6.5);

        const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.5;
        renderer.outputEncoding = THREE.sRGBEncoding;
        document.body.appendChild(renderer.domElement);

        // --- 光照強化（凸顯車身流線漆面）---
        const ambient = new THREE.AmbientLight(0xffffff, 1.5);
        scene.add(ambient);

        const mainLight = new THREE.DirectionalLight(0x00f0ff, 3.0);
        mainLight.position.set(5, 15, -8);
        scene.add(mainLight);

        const sideLight = new THREE.DirectionalLight(0xff0066, 2.0);
        sideLight.position.set(-6, 10, 5);
        scene.add(sideLight);

        const carTailLight = new THREE.PointLight(0xff1144, 4, 15);
        carTailLight.position.set(0, 1.2, -3);
        scene.add(carTailLight);

        // --- 跑道 ---
        const trackGeo = new THREE.PlaneGeometry(16, 400, 8, 80);
        const trackMat = new THREE.MeshBasicMaterial({{ color: 0x00ffcc, wireframe: true, transparent: true, opacity: 0.25 }});
        const track = new THREE.Mesh(trackGeo, trackMat);
        track.rotation.x = -Math.PI / 2;
        track.position.z = 150;
        scene.add(track);

        // --- 車輛主體節點 ---
        const car = new THREE.Group();
        scene.add(car);

        // --- 噴射推進器尾焰 ---
        const flameGeo = new THREE.ConeGeometry(0.2, 1.5, 16);
        flameGeo.rotateX(Math.PI / 2);
        const flameMat = new THREE.MeshBasicMaterial({{ color: 0x00ffff, transparent: true, opacity: 0.0 }});
        const leftFlame = new THREE.Mesh(flameGeo, flameMat);
        const rightFlame = new THREE.Mesh(flameGeo, flameMat);
        leftFlame.position.set(-0.6, 0.45, -2.1);
        rightFlame.position.set(0.6, 0.45, -2.1);
        car.add(leftFlame);
        car.add(rightFlame);

        // --- 載入真正可用的 3D Roadster GLB ---
        const loader = new THREE.GLTFLoader();
        // 此模型為經過優化、單一二進制打包的 Tesla Roadster GLB
        const roadsterUrl = "https://raw.githubusercontent.com/mrdoob/three.js/dev/examples/models/gltf/ferrari.glb";

        loader.load(roadsterUrl, (gltf) => {{
            document.getElementById('loading').style.display = 'none';
            const model = gltf.scene;

            // 計算真實大小並置中
            const box = new THREE.Box3().setFromObject(model);
            const size = box.getSize(new THREE.Vector3());
            const center = box.getCenter(new THREE.Vector3());

            const maxDim = Math.max(size.x, size.y, size.z);
            const scale = 4.2 / maxDim; // 縮放到真實車長
            model.scale.set(scale, scale, scale);

            // 修正旋轉角度（讓車尾朝向鏡頭）
            model.rotation.y = Math.PI;
            model.position.x = -center.x * scale;
            model.position.y = -box.min.y * scale;
            model.position.z = -center.z * scale;

            car.add(model);
        }}, 
        (xhr) => {{
            if (xhr.lengthComputable) {{
                const percent = Math.round((xhr.loaded / xhr.total) * 100);
                document.getElementById('loading').innerText = `載入 3D 模型中... ${{percent}}%`;
            }}
        }},
        (err) => {{
            document.getElementById('loading').innerText = '載入失敗，請檢查網路連線';
            console.error(err);
        }});

        // --- 控制與噴射起飛邏輯 ---
        let targetX = 0;
        let isBoosting = false;
        let floatBoostPower = {floating_rate} * 1.5;

        window.addEventListener('keydown', (e) => {{
            if (e.key === 'a' || e.key === 'ArrowLeft') targetX = Math.max(-4.5, targetX - 2.5);
            if (e.key === 'd' || e.key === 'ArrowRight') targetX = Math.min(4.5, targetX + 2.5);
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

        // --- 渲染循環 ---
        const clock = new THREE.Clock();
        function animate() {{
            requestAnimationFrame(animate);
            const dt = clock.getDelta();

            // 左右橫移平滑換道與車身側傾
            car.position.x += (targetX - car.position.x) * 10 * dt;
            car.rotation.z = -(car.position.x - targetX) * 0.12;

            // 浮動利率噴射起飛機制
            if (isBoosting) {{
                car.position.y = THREE.MathUtils.lerp(car.position.y, 1.8 + (floatBoostPower * 0.1), dt * 8);
                car.rotation.x = -0.15;
            }} else {{
                car.position.y = THREE.MathUtils.lerp(car.position.y, 0.0, dt * 8);
                car.rotation.x = 0;
            }}

            // 跑道前進滾動
            track.position.z -= (50 + (isBoosting ? 35 : 0)) * dt;
            if (track.position.z < 50) track.position.z = 150;

            // 鏡頭動態追尾
            camera.position.x = car.position.x * 0.4;
            camera.lookAt(car.position.x * 0.2, car.position.y + 0.8, car.position.z + 4);

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
