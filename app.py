import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Tesla Yield Runner 3D", layout="wide", page_icon="🏎️")

with st.sidebar:
    st.header("⚡ 債券市場參數 (Bond Market)")
    floating_rate = st.slider("浮動利率基準 (SOFR / Floating Benchmark %)", 2.0, 9.0, 5.25, 0.25)
    credit_spread = st.slider("信用利差 (Credit Spread bps)", 50, 500, 160, 10)
    st.markdown("---")
    st.write("**操作說明：**")
    st.write("👉 **請先點擊一下右側畫面取得鍵盤焦點**")
    st.write("🎮 **A / D 或 左右方向鍵**：左右換道避開 Default 違約紅錐")
    st.write("🚀 **空白鍵 (Space)**：點火冷氣噴射推進（推力隨浮動利率成正比！）")

html_game = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ margin: 0; overflow: hidden; background: #050711; font-family: monospace; user-select: none; }}
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
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body tabindex="0">
    <div id="hud">
        <div class="metric">FLOATING RATE: <span class="highlight">{floating_rate:.2f}%</span></div>
        <div class="metric">CREDIT SPREAD: <span class="highlight">{credit_spread} bps</span></div>
        <div class="metric" id="status">STATUS: CRUISING</div>
    </div>
    <div id="tip">【請先點擊一下畫面以啟用鍵盤控制】</div>

    <script>
        window.focus();
        document.body.addEventListener('click', () => {{ window.focus(); }});

        // --- 場景與攝影機 ---
        const scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x050711, 0.015);

        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(0, 2.6, -6.8);

        const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.4;
        document.body.appendChild(renderer.domElement);

        // --- 光照系統 ---
        const ambient = new THREE.AmbientLight(0xffffff, 1.2);
        scene.add(ambient);

        const keyLight = new THREE.DirectionalLight(0x00f0ff, 2.5);
        keyLight.position.set(6, 15, -10);
        scene.add(keyLight);

        const rimLight = new THREE.DirectionalLight(0xff0055, 2.0);
        rimLight.position.set(-6, 8, 8);
        scene.add(rimLight);

        // --- 霓虹跑道 ---
        const trackGeo = new THREE.PlaneGeometry(16, 400, 8, 80);
        const trackMat = new THREE.MeshBasicMaterial({{ color: 0x00ffcc, wireframe: true, transparent: true, opacity: 0.25 }});
        const track = new THREE.Mesh(trackGeo, trackMat);
        track.rotation.x = -Math.PI / 2;
        track.position.z = 150;
        scene.add(track);

        // --- 精緻程序化 Tesla Roadster 3D 模型 ---
        const car = new THREE.Group();
        scene.add(car);

        // Tesla 招牌金屬多塗層紅 (Red Multi-Coat)
        const paintMat = new THREE.MeshStandardMaterial({{
            color: 0xc8102e,
            metalness: 0.85,
            roughness: 0.18,
            envMapIntensity: 1.5
        }});

        // 全景玻璃車頂材質
        const glassMat = new THREE.MeshStandardMaterial({{
            color: 0x111622,
            metalness: 0.95,
            roughness: 0.05,
            transparent: true,
            opacity: 0.85
        }});

        // 碳纖維與深色部件
        const trimMat = new THREE.MeshStandardMaterial({{
            color: 0x151515,
            metalness: 0.6,
            roughness: 0.4
        }});

        // 貫穿式 LED 尾燈
        const tailLightMat = new THREE.MeshBasicMaterial({{ color: 0xff0033 }});

        // 1. 車身下底盤與擾流
        const chassis = new THREE.Mesh(new THREE.BoxGeometry(1.85, 0.22, 4.3), trimMat);
        chassis.position.y = 0.25;
        car.add(chassis);

        // 2. 主車體流線
        const bodyMain = new THREE.Mesh(new THREE.CylinderGeometry(0.88, 0.95, 4.1, 16), paintMat);
        bodyMain.rotation.x = Math.PI / 2;
        bodyMain.scale.set(1.0, 1.0, 0.38);
        bodyMain.position.set(0, 0.48, 0.1);
        car.add(bodyMain);

        // 3. 駕駛艙與斜背水滴天幕 (Fastback Canopy)
        const cabin = new THREE.Mesh(new THREE.SphereGeometry(0.85, 16, 16), glassMat);
        cabin.scale.set(0.9, 0.55, 2.2);
        cabin.position.set(0, 0.72, -0.2);
        car.add(cabin);

        // 4. 車尾翹起擾流板 (Integrated Ducktail Spoiler)
        const spoiler = new THREE.Mesh(new THREE.BoxGeometry(1.5, 0.08, 0.35), paintMat);
        spoiler.position.set(0, 0.68, -1.9);
        spoiler.rotation.x = -0.12;
        car.add(spoiler);

        // 5. 貫穿式超細一體化 LED 尾燈
        const rearLight = new THREE.Mesh(new THREE.BoxGeometry(1.55, 0.05, 0.08), tailLightMat);
        rearLight.position.set(0, 0.58, -2.06);
        car.add(rearLight);

        // 6. 四個大輪圈與性能跑胎
        const wheelGeo = new THREE.CylinderGeometry(0.38, 0.38, 0.28, 20);
        wheelGeo.rotateZ(Math.PI / 2);
        const wheelMat = new THREE.MeshStandardMaterial({{ color: 0x222222, roughness: 0.7 }});
        
        const wheelFL = new THREE.Mesh(wheelGeo, wheelMat);
        const wheelFR = new THREE.Mesh(wheelGeo, wheelMat);
        const wheelRL = new THREE.Mesh(wheelGeo, wheelMat);
        const wheelRR = new THREE.Mesh(wheelGeo, wheelMat);

        wheelFL.position.set(-0.95, 0.38, 1.4);
        wheelFR.position.set(0.95, 0.38, 1.4);
        wheelRL.position.set(-0.95, 0.38, -1.3);
        wheelRR.position.set(0.95, 0.38, -1.3);

        car.add(wheelFL, wheelFR, wheelRL, wheelRR);

        // --- SpaceX 冷氣噴射推進尾焰 (Thrusters) ---
        const flameGeo = new THREE.ConeGeometry(0.18, 1.4, 16);
        flameGeo.rotateX(Math.PI / 2);
        const flameMat = new THREE.MeshBasicMaterial({{ color: 0x00ffff, transparent: true, opacity: 0.0 }});
        const leftFlame = new THREE.Mesh(flameGeo, flameMat);
        const rightFlame = new THREE.Mesh(flameGeo, flameMat);
        leftFlame.position.set(-0.5, 0.38, -2.2);
        rightFlame.position.set(0.5, 0.38, -2.2);
        car.add(leftFlame, rightFlame);

        // --- 跑道障礙物與票息生成 (Default Traps & Coupons) ---
        const obstacles = [];
        const coneGeo = new THREE.ConeGeometry(0.4, 0.9, 8);
        const coneMat = new THREE.MeshStandardMaterial({{ color: 0xff0044, roughness: 0.2, emissive: 0x880022 }});

        for (let i = 0; i < 6; i++) {{
            const obs = new THREE.Mesh(coneGeo, coneMat);
            obs.position.set((Math.random() - 0.5) * 8, 0.45, 50 + i * 40);
            scene.add(obs);
            obstacles.push(obs);
        }}

        // --- 操作與浮動利率起飛邏輯 ---
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

        // --- 動畫循環 ---
        const clock = new THREE.Clock();
        function animate() {{
            requestAnimationFrame(animate);
            const dt = clock.getDelta();

            // 左右橫移與轉向側傾
            car.position.x += (targetX - car.position.x) * 10 * dt;
            car.rotation.z = -(car.position.x - targetX) * 0.12;

            // 浮動利率噴射升力
            if (isBoosting) {{
                car.position.y = THREE.MathUtils.lerp(car.position.y, 1.8 + (floatBoostPower * 0.1), dt * 8);
                car.rotation.x = -0.15; // 仰角起飛
            }} else {{
                car.position.y = THREE.MathUtils.lerp(car.position.y, 0.0, dt * 8);
                car.rotation.x = 0;
            }}

            // 跑道前進滾動
            const speed = 55 + (isBoosting ? 40 : 0);
            track.position.z -= speed * dt;
            if (track.position.z < 50) track.position.z = 150;

            // 障礙物向後滾動
            obstacles.forEach(obs => {{
                obs.position.z -= speed * dt;
                if (obs.position.z < -10) {{
                    obs.position.z = 200 + Math.random() * 50;
                    obs.position.x = (Math.random() - 0.5) * 8;
                }}
            }});

            // 鏡頭動態追尾跟隨
            camera.position.x = car.position.x * 0.45;
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
