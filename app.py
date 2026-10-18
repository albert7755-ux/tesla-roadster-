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
    st.write("🎮 **A / D 或 左右鍵**：高速變換車道（躲避違約尖刺與建築）")
    st.write("🚀 **按住 空白鍵 (Space)**：點火冷氣噴射推進（推力取決於 SOFR 利率！）")
    st.write("💎 **吃綠色 Coupon 鑽石**：補充流動性與防禦護盾")

# 完整 3D 街景與挑戰機制核心
html_game = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ margin: 0; overflow: hidden; background: #03050c; font-family: 'Segoe UI', monospace; user-select: none; }}
        #hud {{
            position: absolute; top: 15px; left: 20px; color: #fff; z-index: 100;
            pointer-events: none; text-shadow: 0 0 10px #00ffcc;
        }}
        .metric {{ font-size: 16px; margin-bottom: 4px; }}
        .highlight {{ color: #00ffcc; font-size: 22px; font-weight: bold; }}
        #speed-gauge {{
            position: absolute; bottom: 25px; right: 25px; color: #00ffcc;
            font-size: 32px; font-weight: bold; text-align: right; pointer-events: none;
            text-shadow: 0 0 15px rgba(0,255,204,0.6);
        }}
        #gameover {{
            display: none; position: absolute; top: 50%; left: 50%;
            transform: translate(-50%, -50%); color: #ff0055; text-align: center;
            font-size: 36px; font-weight: bold; text-shadow: 0 0 20px #ff0055; z-index: 200;
        }}
        #restart-btn {{
            margin-top: 20px; padding: 10px 25px; font-size: 18px; color: #fff;
            background: #ff0055; border: none; cursor: pointer; border-radius: 4px;
        }}
    </style>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body tabindex="0">
    <div id="hud">
        <div class="metric">YIELD SPREAD: <span class="highlight">{credit_spread} bps</span></div>
        <div class="metric">SOFR BOOST RATE: <span class="highlight">{base_rate:.2f}%</span></div>
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
        document.body.addEventListener('click', () => {{ window.focus(); }});

        // --- 場景初始化 ---
        const scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x04060f, 0.012);

        const camera = new THREE.PerspectiveCamera(65, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(0, 3.2, -7.5);

        const renderer = new THREE.WebGLRenderer({{ antialias: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.3;
        document.body.appendChild(renderer.domElement);

        // --- 華爾街都市光效 ---
        const ambient = new THREE.AmbientLight(0xffffff, 0.8);
        scene.add(ambient);

        const neonCyan = new THREE.DirectionalLight(0x00f0ff, 2.5);
        neonCyan.position.set(15, 20, -10);
        scene.add(neonCyan);

        const neonMagenta = new THREE.DirectionalLight(0xff0055, 2.0);
        neonMagenta.position.set(-15, 10, 10);
        scene.add(neonMagenta);

        // --- 賽博龐克高架都市路面 ---
        const roadGroup = new THREE.Group();
        scene.add(roadGroup);

        const roadMat = new THREE.MeshStandardMaterial({{ color: 0x0a0f1d, roughness: 0.3, metalness: 0.8 }});
        const roadGeo = new THREE.PlaneGeometry(16, 600);
        const road = new THREE.Mesh(roadGeo, roadMat);
        road.rotation.x = -Math.PI / 2;
        road.position.z = 250;
        roadGroup.add(road);

        // 發光護欄與分道線
        const barrierMat = new THREE.MeshBasicMaterial({{ color: 0x00ffcc }});
        const leftBarrier = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.8, 600), barrierMat);
        const rightBarrier = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.8, 600), barrierMat);
        leftBarrier.position.set(-8, 0.4, 250);
        rightBarrier.position.set(8, 0.4, 250);
        roadGroup.add(leftBarrier, rightBarrier);

        // --- 兩側摩天金融大樓群 (動態生成) ---
        const buildings = [];
        const buildingMat1 = new THREE.MeshStandardMaterial({{ color: 0x060914, roughness: 0.2, metalness: 0.9 }});
        const windowMat = new THREE.MeshBasicMaterial({{ color: 0x00e5ff, wireframe: true }});

        for (let i = 0; i < 40; i++) {{
            const h = 25 + Math.random() * 50;
            const w = 12 + Math.random()
