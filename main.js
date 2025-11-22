// 天体系统模拟器 - 主要JavaScript逻辑

// 全局变量
let scene, camera, renderer, controls;
let celestialBodies = [];
let selectedBody = null;
let isSimulationRunning = true;
let timeSpeed = 1.0;
let simulationTime = 0;
let showOrbits = true;
let showLabels = true;
let showGravityField = false;
let clock = new THREE.Clock();

// 物理常数
const G = 6.67430e-11; // 引力常数
const AU = 149597870.7; // 天文单位 (km)
const DAY = 86400; // 一天的秒数

// 天体类
class CelestialBody {
    constructor(name, type, mass, radius, position, velocity, color = 0xFFFFFF) {
        this.name = name;
        this.type = type;
        this.mass = mass;
        this.radius = radius;
        this.position = new THREE.Vector3(...position);
        this.velocity = new THREE.Vector3(...velocity);
        this.color = color;
        this.mesh = null;
        this.orbitPoints = [];
        this.orbitLine = null;
        this.label = null;
        this.trail = [];
        
        this.createMesh();
        this.createOrbitLine();
        this.createLabel();
    }
    
    createMesh() {
        const geometry = new THREE.SphereGeometry(this.radius / 10000, 32, 32);
        let material;
        
        switch(this.type) {
            case 'star':
                material = new THREE.MeshBasicMaterial({ 
                    color: this.color,
                    emissive: this.color,
                    emissiveIntensity: 0.3
                });
                break;
            case 'planet':
                material = new THREE.MeshPhongMaterial({ 
                    color: this.color,
                    shininess: 30
                });
                break;
            case 'moon':
                material = new THREE.MeshLambertMaterial({ 
                    color: this.color
                });
                break;
            case 'asteroid':
                material = new THREE.MeshLambertMaterial({ 
                    color: 0x8B7355
                });
                break;
            default:
                material = new THREE.MeshPhongMaterial({ color: this.color });
        }
        
        this.mesh = new THREE.Mesh(geometry, material);
        this.mesh.position.copy(this.position);
        this.mesh.userData = { body: this };
        scene.add(this.mesh);
        
        // 为恒星添加光晕效果
        if (this.type === 'star') {
            const glowGeometry = new THREE.SphereGeometry(this.radius / 8000, 32, 32);
            const glowMaterial = new THREE.MeshBasicMaterial({
                color: this.color,
                transparent: true,
                opacity: 0.3
            });
            const glowMesh = new THREE.Mesh(glowGeometry, glowMaterial);
            this.mesh.add(glowMesh);
            
            // 添加点光源
            const light = new THREE.PointLight(this.color, 2, 1000);
            this.mesh.add(light);
        }
    }
    
    createOrbitLine() {
        const geometry = new THREE.BufferGeometry();
        const material = new THREE.LineBasicMaterial({ 
            color: this.color, 
            opacity: 0.6, 
            transparent: true 
        });
        this.orbitLine = new THREE.Line(geometry, material);
        scene.add(this.orbitLine);
    }
    
    createLabel() {
        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');
        canvas.width = 256;
        canvas.height = 64;
        
        context.fillStyle = 'rgba(0, 0, 0, 0.7)';
        context.fillRect(0, 0, canvas.width, canvas.height);
        
        context.fillStyle = '#FFD700';
        context.font = 'bold 16px Arial';
        context.textAlign = 'center';
        context.fillText(this.name, canvas.width / 2, 30);
        
        context.fillStyle = '#00FFFF';
        context.font = '12px Arial';
        context.fillText(this.type, canvas.width / 2, 50);
        
        const texture = new THREE.CanvasTexture(canvas);
        const material = new THREE.SpriteMaterial({ map: texture });
        this.label = new THREE.Sprite(material);
        this.label.scale.set(20, 5, 1);
        this.label.position.copy(this.position);
        this.label.position.y += this.radius / 5000 + 10;
        scene.add(this.label);
    }
    
    updateLabel() {
        if (this.label) {
            this.label.position.copy(this.mesh.position);
            this.label.position.y += this.radius / 5000 + 10;
        }
    }
    
    updateOrbitLine() {
        if (!showOrbits || this.type === 'star') return;
        
        this.trail.push(this.position.clone());
        if (this.trail.length > 1000) {
            this.trail.shift();
        }
        
        const positions = new Float32Array(this.trail.length * 3);
        for (let i = 0; i < this.trail.length; i++) {
            positions[i * 3] = this.trail[i].x;
            positions[i * 3 + 1] = this.trail[i].y;
            positions[i * 3 + 2] = this.trail[i].z;
        }
        
        this.orbitLine.geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        this.orbitLine.geometry.setDrawRange(0, this.trail.length);
    }
    
    updateVisibility() {
        if (this.orbitLine) {
            this.orbitLine.visible = showOrbits;
        }
        if (this.label) {
            this.label.visible = showLabels;
        }
    }
}

// 引力计算引擎
class GravityEngine {
    static calculateForces(bodies) {
        const forces = new Array(bodies.length).fill(null).map(() => new THREE.Vector3());
        
        for (let i = 0; i < bodies.length; i++) {
            for (let j = i + 1; j < bodies.length; j++) {
                const bodyA = bodies[i];
                const bodyB = bodies[j];
                
                const distance = bodyA.position.distanceTo(bodyB.position);
                
                if (distance > 0) {
                    const forceMagnitude = G * bodyA.mass * bodyB.mass / (distance * distance);
                    const forceDirection = new THREE.Vector3().subVectors(bodyB.position, bodyA.position).normalize();
                    
                    const force = forceDirection.multiplyScalar(forceMagnitude);
                    forces[i].add(force);
                    forces[j].sub(force);
                }
            }
        }
        
        return forces;
    }
    
    static updatePositions(bodies, deltaTime) {
        const forces = this.calculateForces(bodies);
        
        for (let i = 0; i < bodies.length; i++) {
            const body = bodies[i];
            const force = forces[i];
            
            // 计算加速度 F = ma -> a = F/m
            const acceleration = force.divideScalar(body.mass);
            
            // 更新速度 v = v + a*t
            body.velocity.add(acceleration.multiplyScalar(deltaTime));
            
            // 更新位置 p = p + v*t
            body.position.add(body.velocity.clone().multiplyScalar(deltaTime));
            
            // 更新网格位置
            body.mesh.position.copy(body.position);
            
            // 更新轨道线
            body.updateOrbitLine();
            
            // 更新标签位置
            body.updateLabel();
            
            // 更新可见性
            body.updateVisibility();
        }
    }
}

// 初始化3D场景
function initScene() {
    // 创建场景
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x000000);
    
    // 创建相机
    const canvas = document.getElementById('simulator-canvas');
    const aspect = canvas.clientWidth / canvas.clientHeight;
    camera = new THREE.PerspectiveCamera(75, aspect, 0.1, 1000000);
    camera.position.set(0, 0, 500);
    
    // 创建渲染器
    renderer = new THREE.WebGLRenderer({ 
        canvas: canvas, 
        antialias: true,
        alpha: true 
    });
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    
    // 添加环境光
    const ambientLight = new THREE.AmbientLight(0x404040, 0.3);
    scene.add(ambientLight);
    
    // 添加星空背景
    createStarField();
    
    // 设置相机控制
    setupCameraControls();
    
    // 添加事件监听器
    setupEventListeners();
    
    // 开始渲染循环
    animate();
}

// 创建星空背景
function createStarField() {
    const starGeometry = new THREE.BufferGeometry();
    const starCount = 10000;
    const positions = new Float32Array(starCount * 3);
    
    for (let i = 0; i < starCount * 3; i += 3) {
        positions[i] = (Math.random() - 0.5) * 10000;
        positions[i + 1] = (Math.random() - 0.5) * 10000;
        positions[i + 2] = (Math.random() - 0.5) * 10000;
    }
    
    starGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    
    const starMaterial = new THREE.PointsMaterial({
        color: 0xFFFFFF,
        size: 2,
        sizeAttenuation: false
    });
    
    const stars = new THREE.Points(starGeometry, starMaterial);
    scene.add(stars);
}

// 设置相机控制
function setupCameraControls() {
    let isMouseDown = false;
    let mouseButton = 0;
    let mouseX = 0;
    let mouseY = 0;
    let targetRotationX = 0;
    let targetRotationY = 0;
    let currentRotationX = 0;
    let currentRotationY = 0;
    let cameraDistance = 500;
    
    const canvas = document.getElementById('simulator-canvas');
    
    canvas.addEventListener('mousedown', (event) => {
        isMouseDown = true;
        mouseButton = event.button;
        mouseX = event.clientX;
        mouseY = event.clientY;
        event.preventDefault();
    });
    
    canvas.addEventListener('mousemove', (event) => {
        if (!isMouseDown) return;
        
        const deltaX = event.clientX - mouseX;
        const deltaY = event.clientY - mouseY;
        
        if (mouseButton === 0) { // 左键 - 旋转
            targetRotationY += deltaX * 0.01;
            targetRotationX += deltaY * 0.01;
            targetRotationX = Math.max(-Math.PI/2, Math.min(Math.PI/2, targetRotationX));
        } else if (mouseButton === 2) { // 右键 - 平移
            const panSpeed = cameraDistance * 0.001;
            camera.position.x -= deltaX * panSpeed;
            camera.position.y += deltaY * panSpeed;
        }
        
        mouseX = event.clientX;
        mouseY = event.clientY;
    });
    
    canvas.addEventListener('mouseup', () => {
        isMouseDown = false;
    });
    
    canvas.addEventListener('wheel', (event) => {
        cameraDistance += event.deltaY * 0.1;
        cameraDistance = Math.max(10, Math.min(10000, cameraDistance));
        event.preventDefault();
    });
    
    canvas.addEventListener('contextmenu', (event) => {
        event.preventDefault();
    });
    
    // 更新相机位置
    function updateCamera() {
        currentRotationX += (targetRotationX - currentRotationX) * 0.1;
        currentRotationY += (targetRotationY - currentRotationY) * 0.1;
        
        camera.position.x = Math.sin(currentRotationY) * Math.cos(currentRotationX) * cameraDistance;
        camera.position.y = Math.sin(currentRotationX) * cameraDistance;
        camera.position.z = Math.cos(currentRotationY) * Math.cos(currentRotationX) * cameraDistance;
        
        camera.lookAt(0, 0, 0);
        
        requestAnimationFrame(updateCamera);
    }
    updateCamera();
    
    // 键盘控制
    document.addEventListener('keydown', (event) => {
        switch(event.code) {
            case 'Space':
                event.preventDefault();
                toggleSimulation();
                break;
            case 'KeyR':
                resetCamera();
                break;
        }
    });
    
    function resetCamera() {
        targetRotationX = 0;
        targetRotationY = 0;
        cameraDistance = 500;
        camera.position.set(0, 0, 500);
        camera.lookAt(0, 0, 0);
    }
}

// 设置事件监听器
function setupEventListeners() {
    // 时间速度控制
    const timeSpeedSlider = document.getElementById('time-speed');
    const currentSpeedDisplay = document.getElementById('current-speed');
    
    timeSpeedSlider.addEventListener('input', (event) => {
        timeSpeed = parseFloat(event.target.value);
        currentSpeedDisplay.textContent = timeSpeed.toFixed(1) + 'x';
    });
    
    // 播放/暂停按钮
    const playPauseBtn = document.getElementById('play-pause-btn');
    playPauseBtn.addEventListener('click', toggleSimulation);
    
    // 显示选项按钮
    document.getElementById('show-orbits').addEventListener('click', toggleOrbits);
    document.getElementById('show-labels').addEventListener('click', toggleLabels);
    document.getElementById('show-gravity').addEventListener('click', toggleGravityField);
    
    // 窗口大小调整
    window.addEventListener('resize', onWindowResize);
}

// 窗口大小调整
function onWindowResize() {
    const canvas = document.getElementById('simulator-canvas');
    const width = canvas.clientWidth;
    const height = canvas.clientHeight;
    
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    
    renderer.setSize(width, height);
}

// 动画循环
function animate() {
    requestAnimationFrame(animate);
    
    const deltaTime = clock.getDelta() * timeSpeed * DAY; // 转换为秒
    
    if (isSimulationRunning && celestialBodies.length > 0) {
        simulationTime += deltaTime;
        GravityEngine.updatePositions(celestialBodies, deltaTime);
        updateRealTimeData();
    }
    
    updateFPS();
    renderer.render(scene, camera);
}

// 更新实时数据
function updateRealTimeData() {
    document.getElementById('sim-time').textContent = (simulationTime / DAY).toFixed(2) + ' 天';
    document.getElementById('body-count').textContent = celestialBodies.length;
    
    let totalKineticEnergy = 0;
    let totalPotentialEnergy = 0;
    
    // 计算动能
    celestialBodies.forEach(body => {
        const speed = body.velocity.length();
        totalKineticEnergy += 0.5 * body.mass * speed * speed;
    });
    
    // 计算势能
    for (let i = 0; i < celestialBodies.length; i++) {
        for (let j = i + 1; j < celestialBodies.length; j++) {
            const distance = celestialBodies[i].position.distanceTo(celestialBodies[j].position);
            if (distance > 0) {
                totalPotentialEnergy -= G * celestialBodies[i].mass * celestialBodies[j].mass / distance;
            }
        }
    }
    
    const totalEnergy = totalKineticEnergy + totalPotentialEnergy;
    
    document.getElementById('total-energy').textContent = totalEnergy.toExponential(2) + ' J';
    document.getElementById('kinetic-energy').textContent = totalKineticEnergy.toExponential(2) + ' J';
    document.getElementById('potential-energy').textContent = totalPotentialEnergy.toExponential(2) + ' J';
}

// 更新FPS计数器
let frameCount = 0;
let lastTime = performance.now();

function updateFPS() {
    frameCount++;
    const currentTime = performance.now();
    
    if (currentTime - lastTime >= 1000) {
        const fps = Math.round((frameCount * 1000) / (currentTime - lastTime));
        document.getElementById('fps-counter').textContent = fps;
        
        const performanceBar = document.getElementById('performance-bar');
        const performancePercent = Math.min(100, (fps / 60) * 100);
        performanceBar.style.width = performancePercent + '%';
        
        frameCount = 0;
        lastTime = currentTime;
    }
}

// 创建天体
function createCelestialBody() {
    const type = document.getElementById('body-type').value;
    const name = document.getElementById('body-name').value || `${type}_${celestialBodies.length + 1}`;
    const mass = parseFloat(document.getElementById('body-mass').value);
    const radius = parseFloat(document.getElementById('body-radius').value);
    const velocity = document.getElementById('body-velocity').value.split(',').map(v => parseFloat(v.trim()));
    const position = document.getElementById('body-position').value.split(',').map(p => parseFloat(p.trim()));
    
    if (!name || !mass || !radius) {
        alert('请填写完整的天体信息');
        return;
    }
    
    // 根据类型设置颜色
    let color;
    switch(type) {
        case 'star':
            color = 0xFFD700;
            break;
        case 'planet':
            color = 0x4169E1;
            break;
        case 'moon':
            color = 0xC0C0C0;
            break;
        case 'asteroid':
            color = 0x8B7355;
            break;
        default:
            color = 0xFFFFFF;
    }
    
    const body = new CelestialBody(name, type, mass, radius, position, velocity, color);
    celestialBodies.push(body);
    
    updateBodiesList();
    updateRealTimeData();
    
    // 清空输入框
    document.getElementById('body-name').value = '';
    
    console.log(`创建了天体: ${name} (${type})`);
}

// 更新天体列表显示
function updateBodiesList() {
    const listContainer = document.getElementById('bodies-list');
    listContainer.innerHTML = '';
    
    celestialBodies.forEach((body, index) => {
        const item = document.createElement('div');
        item.className = 'body-item';
        item.innerHTML = `
            <div class="body-name">${body.name}</div>
            <div class="body-type">${body.type} | 质量: ${body.mass.toExponential(2)} kg</div>
        `;
        
        item.addEventListener('click', () => selectBody(body, item));
        
        listContainer.appendChild(item);
    });
}

// 选择天体
function selectBody(body, element) {
    // 移除之前的选中状态
    document.querySelectorAll('.body-item').forEach(item => {
        item.classList.remove('selected');
    });
    
    // 添加选中状态
    element.classList.add('selected');
    
    selectedBody = body;
    document.getElementById('selected-body').textContent = body.name;
    
    console.log(`选中了天体: ${body.name}`);
}

// 控制函数
function toggleSimulation() {
    isSimulationRunning = !isSimulationRunning;
    const btn = document.getElementById('play-pause-btn');
    const status = document.getElementById('simulation-status');
    
    if (isSimulationRunning) {
        btn.textContent = '暂停';
        status.textContent = '运行中';
    } else {
        btn.textContent = '继续';
        status.textContent = '已暂停';
    }
}

function toggleOrbits() {
    showOrbits = !showOrbits;
    const btn = document.getElementById('show-orbits');
    
    if (showOrbits) {
        btn.classList.add('active');
    } else {
        btn.classList.remove('active');
    }
    
    celestialBodies.forEach(body => body.updateVisibility());
}

function toggleLabels() {
    showLabels = !showLabels;
    const btn = document.getElementById('show-labels');
    
    if (showLabels) {
        btn.classList.add('active');
    } else {
        btn.classList.remove('active');
    }
    
    celestialBodies.forEach(body => body.updateVisibility());
}

function toggleGravityField() {
    showGravityField = !showGravityField;
    const btn = document.getElementById('show-gravity');
    
    if (showGravityField) {
        btn.classList.add('active');
        // 这里可以添加引力场可视化代码
    } else {
        btn.classList.remove('active');
    }
}

function resetSimulation() {
    simulationTime = 0;
    celestialBodies.forEach(body => {
        body.trail = [];
        if (body.orbitLine) {
            body.orbitLine.geometry.setDrawRange(0, 0);
        }
    });
    console.log('模拟已重置');
}

function clearAllBodies() {
    celestialBodies.forEach(body => {
        scene.remove(body.mesh);
        scene.remove(body.orbitLine);
        scene.remove(body.label);
    });
    
    celestialBodies = [];
    selectedBody = null;
    updateBodiesList();
    updateRealTimeData();
    
    document.getElementById('selected-body').textContent = '无';
    console.log('所有天体已清空');
}

// 预设场景
function loadSolarSystem() {
    clearAllBodies();
    
    // 太阳
    const sun = new CelestialBody('太阳', 'star', 1.989e30, 696340, [0, 0, 0], [0, 0, 0], 0xFFD700);
    celestialBodies.push(sun);
    
    // 水星
    const mercury = new CelestialBody('水星', 'planet', 3.301e23, 2439.7, [0.387 * AU, 0, 0], [0, 47.87, 0], 0x8C7853);
    celestialBodies.push(mercury);
    
    // 金星
    const venus = new CelestialBody('金星', 'planet', 4.867e24, 6051.8, [0.723 * AU, 0, 0], [0, 35.02, 0], 0xFFC649);
    celestialBodies.push(venus);
    
    // 地球
    const earth = new CelestialBody('地球', 'planet', 5.972e24, 6371, [1.0 * AU, 0, 0], [0, 29.78, 0], 0x4169E1);
    celestialBodies.push(earth);
    
    // 火星
    const mars = new CelestialBody('火星', 'planet', 6.417e23, 3389.5, [1.524 * AU, 0, 0], [0, 24.13, 0], 0xCD5C5C);
    celestialBodies.push(mars);
    
    // 木星
    const jupiter = new CelestialBody('木星', 'planet', 1.898e27, 69911, [5.203 * AU, 0, 0], [0, 13.07, 0], 0xDAA520);
    celestialBodies.push(jupiter);
    
    // 土星
    const saturn = new CelestialBody('土星', 'planet', 5.683e26, 58232, [9.537 * AU, 0, 0], [0, 9.69, 0], 0xF4A460);
    celestialBodies.push(saturn);
    
    updateBodiesList();
    updateRealTimeData();
    
    console.log('太阳系模型已加载');
}

function loadBinarySystem() {
    clearAllBodies();
    
    // 主星
    const star1 = new CelestialBody('主星', 'star', 2.0e30, 696340, [-1e8, 0, 0], [0, 10, 0], 0xFFD700);
    celestialBodies.push(star1);
    
    // 伴星
    const star2 = new CelestialBody('伴星', 'star', 1.5e30, 600000, [1e8, 0, 0], [0, -13.33, 0], 0xFFA500);
    celestialBodies.push(star2);
    
    // 行星1
    const planet1 = new CelestialBody('行星A', 'planet', 6e24, 6371, [-2e8, 0, 0], [0, 25, 0], 0x4169E1);
    celestialBodies.push(planet1);
    
    // 行星2
    const planet2 = new CelestialBody('行星B', 'planet', 4e24, 5000, [2.5e8, 0, 0], [0, -15, 0], 0x32CD32);
    celestialBodies.push(planet2);
    
    updateBodiesList();
    updateRealTimeData();
    
    console.log('双星系统模型已加载');
}

function loadRandomSystem() {
    clearAllBodies();
    
    // 中央恒星
    const star = new CelestialBody('恒星', 'star', 1.5e30, 696340, [0, 0, 0], [0, 0, 0], 0xFFD700);
    celestialBodies.push(star);
    
    // 随机生成行星
    const planetCount = Math.floor(Math.random() * 5) + 3;
    const colors = [0x4169E1, 0x32CD32, 0xFF6347, 0x9370DB, 0xFF1493, 0x00CED1, 0xFFD700];
    
    for (let i = 0; i < planetCount; i++) {
        const distance = (Math.random() * 300 + 50) * 1e6;
        const angle = Math.random() * Math.PI * 2;
        const mass = Math.random() * 1e25 + 1e23;
        const radius = Math.random() * 5000 + 2000;
        
        const position = [
            Math.cos(angle) * distance,
            (Math.random() - 0.5) * distance * 0.1,
            Math.sin(angle) * distance
        ];
        
        const orbitalSpeed = Math.sqrt(G * star.mass / distance);
        const velocity = [
            -Math.sin(angle) * orbitalSpeed,
            (Math.random() - 0.5) * 5,
            Math.cos(angle) * orbitalSpeed
        ];
        
        const planet = new CelestialBody(
            `行星${i + 1}`,
            'planet',
            mass,
            radius,
            position,
            velocity,
            colors[i % colors.length]
        );
        celestialBodies.push(planet);
    }
    
    updateBodiesList();
    updateRealTimeData();
    
    console.log('随机系统模型已加载');
}

// 页面加载完成后初始化
window.addEventListener('load', () => {
    setTimeout(() => {
        initScene();
        document.getElementById('loading-overlay').style.display = 'none';
        
        // 默认加载太阳系
        loadSolarSystem();
    }, 2000);
});

// 导出函数供HTML调用
window.createCelestialBody = createCelestialBody;
window.toggleSimulation = toggleSimulation;
window.resetSimulation = resetSimulation;
window.clearAllBodies = clearAllBodies;
window.loadSolarSystem = loadSolarSystem;
window.loadBinarySystem = loadBinarySystem;
window.loadRandomSystem = loadRandomSystem;