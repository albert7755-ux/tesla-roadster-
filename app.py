import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Tesla Yield Runner 3D", layout="wide", page_icon="🏎️")

with st.sidebar:
    st.header("⚡ 債券市場參數 (Bond Market)")
    floating_rate = st.slider("浮動利率基準 (SOFR / Floating Benchmark %)", 2.0, 9.0, 5.25, 0.25)
    credit_spread = st.slider("信用利差 (Credit Spread bps)", 50, 500, 160, 10)
    st.markdown("---")
    st.write("**操作說明：**")
    st.write("🎮 **A / D 或 左右鍵**：換道避開 Default 違約錐")
    st.write("🚀 **空白鍵 (Space)**：點火發動冷氣噴射推進（推力取決於浮動利率高低！）")

# Three.js 3D 遊戲核心視窗
html_game = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ margin: 0; overflow: hidden; background: #050711; font-family: 'Segoe UI', sans-serif; }}
        #hud {{
            position: absolute; top: 15px; left: 20px; color: #fff; z-index: 100;
            pointer-events: none; font-family: monospace;
        }}
        .metric {{ font-size: 18px; margin-bottom: 5px; text-shadow: 0 0 10px #00ffcc; }}
        .highlight {{ color: #00ffcc; font-size: 24px; font-weight: bold; }}
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
</head>
<body>
    <div id="hud">
        <div class="metric">FLOATING RATE: <span class="highlight">{floating_rate:.2f}%</span></div>
        <div class="metric">CREDIT SPREAD: <span class="highlight">{credit_spread} bps</span></div>
        <div class="metric" id="status">STATUS: CRUISING</div>
    </div>

    <script>
        const scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x050711, 0.02);

        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(0, 2.2, -5.5);

        const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.4;
        document.body.appendChild(renderer.domElement);

        // --- 賽博龐克光照 ---
        const ambient = new THREE.AmbientLight(0xffffff, 0.8);
        scene.add(ambient);

        const sun = new THREE.DirectionalLight(0x00e5ff, 2.0);
        sun.position.set(5, 12, -10);
        scene.add(sun);

        const redGlow = new THREE.PointLight(0xff1144, 4, 15);
        redGlow.position.set(0, 1.5, -2);
        scene.add(redGlow);

        // --- 跑道網格 ---
        const trackGeo = new THREE.PlaneGeometry(16, 400, 8, 100);
        const trackMat = new THREE.MeshBasicMaterial({{ color: 0x0a1428, wireframe: true }});
        const track = new THREE.Mesh(trackGeo, trackMat);
        track.rotation.x = -Math.PI / 2;
        track.position.z = 150;
        scene.add(track);

        // --- 載入 Tesla Roadster 模型 ---
        let car = new THREE.Group();
        scene.add(car);

        const loader = new THREE.GLTFLoader();
        // 如果把模型放在 GitHub static 或 raw 連結，把 URL 填在這：
        // 預設先用優雅的跑車外框代理，一旦載入成功即套用真車
        loader.load('./static/scene.gltf', (gltf) => {{
            const model = gltf.scene;
            // 修正 Sketchfab FBX 轉 glTF 的座標軸與比例
            model.scale.set(1.0, 1.0, 1.0);
            model.rotation.y = Math.PI; 
            car.add(model);
        }}, undefined, (err) => {{
            // 若本機未放檔案，建立臨時 Cyber-Car 確保立即可玩
            const body = new THREE.Mesh(
                new THREE.BoxGeometry(1.6, 0.6, 3.8),
                new THREE.MeshStandardMaterial({{ color: 0xcc0022, metalness: 0.9, roughness: 0.1 }})
            );
            body.position.y = 0.4;
            car.add(body);
        }});

        // --- 噴射推進尾焰粒子 ---
        const flameGeo = new THREE.ConeGeometry(0.18, 1.2, 16);
        flameGeo.rotateX(Math.PI / 2);
        const flameMat = new THREE.MeshBasicMaterial({{ color: 0x00ffff, transparent: true, opacity: 0.0 }});
        const leftFlame = new THREE.Mesh(flameGeo, flameMat);
        const rightFlame = new THREE.Mesh(flameGeo, flameMat);
        leftFlame.position.set(-0.6, 0.35, -2.1);
        rightFlame.position.set(0.6, 0.35, -2.1);
        car.add(leftFlame);
        car.add(rightFlame);

        // --- 遊戲邏輯與控制 ---
        let targetX = 0;
        let isBoosting = false;
        let floatBoostPower = {floating_rate} * 1.5; // 浮動利率決定噴射推力！

        window.addEventListener('keydown', (e) => {{
            if (e.key === 'a' || e.key === 'ArrowLeft') targetX = Math.max(-4.5, targetX - 2.5);
            if (e.key === 'd' || e.key === 'ArrowRight') targetX = Math.min(4.5, targetX + 2.5);
            if (e.code === 'Space') {{
                isBoosting = true;
                flameMat.opacity = 0.9;
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

        // 渲染迴圈
        let clock = new THREE.Clock();
        function animate() {{
            requestAnimationFrame(animate);
            let dt = clock.getDelta();

            // 車身左右插值換道
            car.position.x += (targetX - car.position.x) * 10 * dt;
            car.rotation.z = -(car.position.x - targetX) * 0.15; // 轉向側傾

            // 浮動噴射起飛機制
            if (isBoosting) {{
                car.position.y = THREE.MathUtils.lerp(car.position.y, 1.8 + (floatBoostPower * 0.1), dt * 8);
                car.rotation.x = -0.15; // 車頭微仰
            }} else {{
                car.position.y = THREE.MathUtils.lerp(car.position.y, 0.0, dt * 8);
                car.rotation.x = 0;
            }}

            // 跑道滾動
            track.position.z = (track.position.z - 45 * dt);
            if (track.position.z < 0) track.position.z = 100;

            // 攝影機動態跟隨
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
