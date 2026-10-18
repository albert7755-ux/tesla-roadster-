import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Tesla Yield Runner: Cyber WallSt", layout="wide", page_icon="🏎️")

# 側邊欄：市場壓力測試設定
with st.sidebar:
    st.header("⚡ 債券市場壓力測試")
    base_rate = st.slider("SOFR 浮動基準利率 (%)", 1.0, 10.0, 5.5, 0.25)
    credit_spread = st.slider("非投資級利差 (Credit Spread bps)", 100, 800, 350, 25)
    inversion_level = st.select_slider("曲線倒掛強度 (Inversion Depth)", options=["正常平緩", "微幅倒掛", "極端倒掛風暴"], value="極端倒掛風暴")
    st.markdown("---")
    st.write("**挑戰操作說明：**")
    st.write("👉 **請先點擊一下右側畫面取得焦點**")
    st.write("🎮 **A / D 或 左右方向鍵**：左右變換車道（躲避違約尖錐）")
    st.write("🚀 **按住 空白鍵 (Space)**：點火冷氣噴射推進（推力隨 SOFR 利率飆升！）")
    st.write("💎 **吃綠色 Coupon 鑽石**：補充流動性儲備與投組報酬")

# 乾淨的 HTML 模板，完全避免 f-string 語法錯誤
raw_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body { margin: 0; overflow: hidden; background: #03050c; font-family: 'Segoe UI', monospace; user-select: none; }
        #hud {
            position: absolute; top: 15px; left: 20px; color: #fff; z-index: 100;
            pointer-events: none; text-shadow: 0 0 10px #00ffcc;
        }
        .metric { font-size: 16px; margin-bottom: 4px; }
        .highlight { color: #00ffcc; font-size: 22px; font-weight: bold; }
        #speed-gauge {
            position: absolute; bottom: 25px; right: 25px; color: #00ffcc;
            font-size: 32px; font-weight: bold; text-align: right; pointer-events: none;
            text-shadow: 0 0 15px rgba(0,255,204,0.6);
        }
        #gameover {
            display: none; position: absolute; top: 50%; left: 50%;
            transform: translate(-50%, -50%); color: #ff0055; text-align: center;
            font-size: 34px; font-weight: bold; text-shadow: 0 0 20px #ff0055; z-index: 200;
        }
        #restart-btn {
            margin-top: 20px; padding: 10px 25px; font-size: 18px; color: #fff;
            background: #ff0055; border: none; cursor: pointer; border-radius: 4px; font-weight: bold;
        }
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body tabindex="0">
    <div id="hud">
        <div class="metric">YIELD SPREAD: <span class="highlight">__CREDIT_SPREAD__ bps</span></div>
        <div class="metric">SOFR BOOST RATE: <span class="highlight">__BASE_RATE__%</span></div>
        <div class="metric">LIQUIDITY BUFFER: <span id="liquidity" class="highlight" style="color: #00ff88;">100%</span></div>
        <div class="metric">PORTFOLIO RETURN: <span id="return-val" class="highlight" style="color: #ffaa00;">+0.00%</span></div>
    </div>

    <div id="speed-gauge"><span id="speed-val">120</span> <span style="font-size: 16px;">MPH</span></div>

    <div id="gameover">
        <div>LIQUIDITY DEFAULT! (違約斷頭)</div>
        <button id="restart-btn" onclick="resetGame()">重新發動 ROADSTER</button>
    </div>

    <script>
        window.focus();
        document.body.addEventListener('click', () => { window.focus(); });

        const BASE_RATE = __BASE_RATE__;
        const CREDIT_SPREAD = __CREDIT_SPREAD__;

        const scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x04060f, 0.012);

        const camera = new THREE.PerspectiveCamera(65, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(0, 3.2, -7.5);

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.3;
        document.body.appendChild(renderer.domElement);

        // 都市光效
        const ambient = new THREE.AmbientLight(0xffffff, 0.8);
        scene.add(ambient);

        const neonCyan = new THREE.DirectionalLight(0x00f0ff, 2.5);
        neonCyan.position.set(15, 20, -10);
        scene.add(neonCyan);

        const neonMagenta = new THREE.DirectionalLight(0xff0055, 2.0);
        neonMagenta.position.set(-15, 10, 10);
        scene.add(neonMagenta);

        // 賽博龐克高架都市路面
        const roadGroup = new THREE.Group();
        scene.add(roadGroup);

        const roadMat = new THREE.MeshStandardMaterial({ color: 0x0a0f1d, roughness: 0.3, metalness: 0.8 });
        const roadGeo = new THREE.PlaneGeometry(16, 600);
        const road = new THREE.Mesh(roadGeo, roadMat);
        road.rotation.x = -Math.PI / 2;
        road.position.z = 250;
        roadGroup.add(road);

        const barrierMat = new THREE.MeshBasicMaterial({ color: 0x00ffcc });
        const leftBarrier = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.8, 600), barrierMat);
        const rightBarrier = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.8, 600), barrierMat);
        leftBarrier.position.set(-8, 0.4, 250);
        rightBarrier.position.set(8, 0.4, 250);
        roadGroup.add(leftBarrier, rightBarrier);

        // 兩側摩天金融大樓群
        const buildings = [];
        const buildingMat1 = new THREE.MeshStandardMaterial({ color: 0x060914, roughness: 0.2, metalness: 0.9 });
        const windowMat = new THREE.MeshBasicMaterial({ color: 0x00e5ff, wireframe: true });

        for (let i = 0; i < 40; i++) {
            const h = 25 + Math.random() * 50;
            const w = 12 + Math.random() * 10;
            const side = i % 2 === 0 ? 1 : -1;
            const bMesh = new THREE.Mesh(new THREE.BoxGeometry(w, h, 20), buildingMat1);
            const bWire = new THREE.Mesh(new THREE.BoxGeometry(w + 0.1, h + 0.1, 20.1), windowMat);
            bMesh.add(bWire);

            bMesh.position.set(side * (18 + w / 2), h / 2 - 2, (i * 25));
            scene.add(bMesh);
            buildings.push(bMesh);
        }

        // 特斯拉 Roadster 車體
        const car = new THREE.Group();
        scene.add(car);

        const paintMat = new THREE.MeshStandardMaterial({ color: 0xd90429, metalness: 0.9, roughness: 0.15 });
        const glassMat = new THREE.MeshStandardMaterial({ color: 0x05070d, metalness: 0.95, roughness: 0.05, transparent: true, opacity: 0.85 });
        const trimMat = new THREE.MeshStandardMaterial({ color: 0x111111, metalness: 0.8, roughness: 0.5 });

        const body = new THREE.Mesh(new THREE.BoxGeometry(2.0, 0.5, 4.4), paintMat);
        body.position.y = 0.45;
        car.add(body);

        const hood = new THREE.Mesh(new THREE.CylinderGeometry(0.9, 1.0, 4.0, 16), paintMat);
        hood.rotation.x = Math.PI / 2;
        hood.scale.set(1.0, 1.0, 0.4);
        hood.position.set(0, 0.65, 0);
        car.add(hood);

        const canopy = new THREE.Mesh(new THREE.SphereGeometry(0.85, 16, 16), glassMat);
        canopy.scale.set(0.95, 0.65, 2.0);
        canopy.position.set(0, 0.85, -0.2);
        car.add(canopy);

        const tailLight = new THREE.Mesh(new THREE.BoxGeometry(1.8, 0.08, 0.1), new THREE.MeshBasicMaterial({ color: 0xff0044 }));
        tailLight.position.set(0, 0.65, -2.2);
        car.add(tailLight);

        const wheelGeo = new THREE.CylinderGeometry(0.42, 0.42, 0.3, 16);
        wheelGeo.rotateZ(Math.PI / 2);
        const wheelMat = new THREE.MeshStandardMaterial({ color: 0x1f242d, roughness: 0.6 });
        const wFL = new THREE.Mesh(wheelGeo, wheelMat);
        const wFR = new THREE.Mesh(wheelGeo, wheelMat);
        const wBL = new THREE.Mesh(wheelGeo, wheelMat);
        const wBR = new THREE.Mesh(wheelGeo, wheelMat);
        wFL.position.set(-1.05, 0.42, 1.4);
        wFR.position.set(1.05, 0.42, 1.4);
        wBL.position.set(-1.05, 0.42, -1.3);
        wBR.position.set(1.05, 0.42, -1.3);
        car.add(wFL, wFR, wBL, wBR);

        // 噴射尾焰
        const flameGeo = new THREE.ConeGeometry(0.22, 1.8, 16);
        flameGeo.rotateX(Math.PI / 2);
        const flameMat = new THREE.MeshBasicMaterial({ color: 0x00ffff, transparent: true, opacity: 0 });
        const flameL = new THREE.Mesh(flameGeo, flameMat);
        const flameR = new THREE.Mesh(flameGeo, flameMat);
        flameL.position.set(-0.6, 0.45, -2.4);
        flameR.position.set(0.6, 0.45, -2.4);
        car.add(flameL, flameR);

        // 障礙錐與票息
        const traps = [];
        const coupons = [];

        const trapGeo = new THREE.ConeGeometry(0.7, 1.5, 8);
        const trapMat = new THREE.MeshStandardMaterial({ color: 0xff0044, emissive: 0xaa0033 });
        const couponGeo = new THREE.OctahedronGeometry(0.7);
        const couponMat = new THREE.MeshStandardMaterial({ color: 0x00ff88, emissive: 0x00aa44 });

        for (let i = 0; i < 5; i++) {
            const t = new THREE.Mesh(trapGeo, trapMat);
            t.position.set((Math.random() - 0.5) * 12, 0.75, 80 + i * 70);
            scene.add(t);
            traps.push(t);

            const c = new THREE.Mesh(couponGeo, couponMat);
            c.position.set((Math.random() - 0.5) * 12, 1.2, 50 + i * 65);
            scene.add(c);
            coupons.push(c);
        }

        let currentSpeed = 120;
        let liquidity = 100;
        let totalReturn = 0;
        let targetX = 0;
        let isBoosting = false;
        let isDead = false;
        const boostPower = BASE_RATE * 1.8;

        window.addEventListener('keydown', (e) => {
            if (isDead) return;
            if (e.key === 'a' || e.key === 'ArrowLeft') targetX = Math.max(-6.0, targetX - 3.0);
            if (e.key === 'd' || e.key === 'ArrowRight') targetX = Math.min(6.0, targetX + 3.0);
            if (e.code === 'Space') {
                isBoosting = true;
                flameMat.opacity = 0.95;
            }
        });

        window.addEventListener('keyup', (e) => {
            if (e.code === 'Space') {
                isBoosting = false;
                flameMat.opacity = 0.0;
            }
        });

        function resetGame() {
            liquidity = 100;
            totalReturn = 0;
            currentSpeed = 120;
            car.position.set(0, 0, 0);
            targetX = 0;
            isDead = false;
            document.getElementById('gameover').style.display = 'none';
        }

        const clock = new THREE.Clock();
        function animate() {
            requestAnimationFrame(animate);
            const dt = clock.getDelta();

            if (isDead) return;

            const speedMultiplier = isBoosting ? 2.2 : 1.0;
            const driveSpeed = (currentSpeed * speedMultiplier) * dt * 0.4;
            document.getElementById('speed-val').innerText = Math.round(currentSpeed * speedMultiplier);

            if (isBoosting) {
                car.position.y = THREE.MathUtils.lerp(car.position.y, 2.4 + (boostPower * 0.12), dt * 7);
                car.rotation.x = -0.18;
                totalReturn += BASE_RATE * 0.02 * dt;
            } else {
                car.position.y = THREE.MathUtils.lerp(car.position.y, 0, dt * 8);
                car.rotation.x = 0;
                totalReturn += 0.005 * dt;
            }

            document.getElementById('return-val').innerText = (totalReturn >= 0 ? '+' : '') + totalReturn.toFixed(2) + '%';

            car.position.x += (targetX - car.position.x) * 12 * dt;
            car.rotation.z = -(car.position.x - targetX) * 0.15;

            // 大樓向後滾動
            buildings.forEach(b => {
                b.position.z -= driveSpeed * 4;
                if (b.position.z < -40) b.position.z = 500;
            });

            // 障礙物碰撞
            traps.forEach(t => {
                t.position.z -= driveSpeed * 4;
                if (t.position.z < -10) {
                    t.position.z = 350 + Math.random() * 50;
                    t.position.x = (Math.random() - 0.5) * 12;
                }

                const dist = car.position.distanceTo(t.position);
                if (dist < 1.6 && car.position.y < 1.2) {
                    liquidity = Math.max(0, liquidity - 35);
                    t.position.z = 350;
                    document.getElementById('liquidity').innerText = liquidity + '%';
                    if (liquidity <= 0) {
                        isDead = true;
                        document.getElementById('gameover').style.display = 'block';
                    }
                }
            });

            // 票息拾取
            coupons.forEach(c => {
                c.rotation.y += 2 * dt;
                c.position.z -= driveSpeed * 4;
                if (c.position.z < -10) {
                    c.position.z = 320 + Math.random() * 40;
                    c.position.x = (Math.random() - 0.5) * 12;
                }

                if (car.position.distanceTo(c.position) < 1.8) {
                    liquidity = Math.min(100, liquidity + 15);
                    totalReturn += 0.5;
                    c.position.z = 350;
                    document.getElementById('liquidity').innerText = liquidity + '%';
                }
            });

            camera.position.x = car.position.x * 0.45;
            camera.position.y = 3.2 + (isBoosting ? 0.8 : 0);
            camera.lookAt(car.position.x * 0.2, car.position.y + 1.0, car.position.z + 5);

            renderer.render(scene, camera);
        }
        animate();

        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });
    </script>
</body>
</html>
"""

# 安全替換變數，完全不會被 f-string 報錯
final_html = raw_html.replace("__BASE_RATE__", f"{base_rate:.2f}").replace("__CREDIT_SPREAD__", str(credit_spread))
components.html(final_html, height=720)
