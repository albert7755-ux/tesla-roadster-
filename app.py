import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Yield Runner 3D", layout="wide", page_icon="🏎️")

# --- 側邊欄：市場控制面板 ---
with st.sidebar:
    st.header("⚙️ 殖利率與市場環境設定")
    benchmark_rate = st.slider("聯準會基準利率 (SOFR/Fed Funds %)", 2.0, 8.0, 5.25, 0.25)
    spread_spread = st.slider("信用利差 (Credit Spread bps)", 50, 600, 180, 10)
    market_vol = st.select_slider("市場波動度 (MOVE Index)", options=["平靜", "震盪", "極端風暴"], value="震盪")
    
    st.divider()
    st.caption("按 空白鍵 (Space) 發動浮動利率噴射，左右方向鍵 (A/D) 換道。")

# --- 主畫面：嵌入高畫質 Three.js 視窗 ---
html_code = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {{ margin: 0; overflow: hidden; background: #05070f; font-family: sans-serif; }}
        #hud {{
            position: absolute; top: 15px; left: 20px; color: #fff;
            text-shadow: 0 0 10px #00ffcc; z-index: 10;
        }}
        .hud-val {{ font-size: 24px; font-weight: bold; color: #00ffcc; }}
    </style>
    <!-- 引入 Three.js 與 GLTF 載入器 -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/loaders/GLTFLoader.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
</head>
<body>
    <div id="hud">
        <div>FLOATING BOOST RATE: <span class="hud-val">{benchmark_rate}%</span></div>
        <div>SPREAD: <span class="hud-val">{spread_spread} bps</span></div>
    </div>
    
    <script>
        const scene = new THREE.Scene();
        scene.fog = new THREE.FogExp2(0x05070f, 0.015);

        const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.set(0, 3.5, -7);

        const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.2;
        document.body.appendChild(renderer.domElement);

        // --- 賽博龐克光影 ---
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        scene.add(ambientLight);

        const dirLight = new THREE.DirectionalLight(0x00e5ff, 2.5);
        dirLight.position.set(5, 10, -5);
        scene.add(dirLight);

        const pinkLight = new THREE.PointLight(0xff0055, 3, 20);
        pinkLight.position.set(-4, 2, 0);
        scene.add(pinkLight);

        // --- 載入真正 3D Tesla Roadster 模型 ---
        let roadster;
        const loader = new THREE.GLTFLoader();
        
        // 這裡可替換為你放置在 GitHub Raw 或 CDN 上的真實 Roadster .glb 網址
        const modelUrl = 'https://raw.githubusercontent.com/KhronosGroup/glTF-Sample-Models/master/2.0/SheenChair/glTF-Binary/SheenChair.glb'; 
        
        loader.load(modelUrl, (gltf) => {{
            roadster = gltf.scene;
            roadster.scale.set(1.5, 1.5, 1.5);
            scene.add(roadster);
        }});

        // --- 霓虹賽道網格 ---
        const gridHelper = new THREE.GridHelper(300, 60, 0x00ffcc, 0x1a2634);
        gridHelper.position.y = -0.5;
        scene.add(gridHelper);

        // --- 動態渲染迴圈 ---
        function animate() {{
            requestAnimationFrame(animate);

            // 賽道滾動效果
            gridHelper.position.z = (gridHelper.position.z + 0.8) % 5;

            // 鏡頭與車身微動
            if (roadster) {{
                camera.lookAt(roadster.position.x, roadster.position.y + 1, roadster.position.z + 4);
            }}

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

components.html(html_code, height=650)
