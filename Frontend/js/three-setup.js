/**
 * Three.js Setup
 * Creates 3D animated background
 */

let scene, camera, renderer, particles;

function initThreeJS() {
    const container = document.getElementById('canvas-container');
    
    if (!container) {
        Logger.warn('Canvas container not found');
        return;
    }
    
    try {
        // Scene
        scene = new THREE.Scene();
        scene.background = null;
        
        // Camera
        camera = new THREE.PerspectiveCamera(
            75,
            window.innerWidth / window.innerHeight,
            0.1,
            1000
        );
        camera.position.z = 50;
        
        // Renderer
        renderer = new THREE.WebGLRenderer({
            antialias: true,
            alpha: true,
            powerPreference: 'high-performance'
        });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        container.appendChild(renderer.domElement);
        
        // Create particles
        createParticles();
        
        // Lights
        const ambientLight = new THREE.AmbientLight(0x06b6d4, 0.6);
        scene.add(ambientLight);
        
        const pointLight1 = new THREE.PointLight(0x06b6d4, 0.8);
        pointLight1.position.set(50, 50, 50);
        scene.add(pointLight1);
        
        const pointLight2 = new THREE.PointLight(0xa78bfa, 0.6);
        pointLight2.position.set(-50, -50, 50);
        scene.add(pointLight2);
        
        // Handle resize
        window.addEventListener('resize', onWindowResize);
        
        // Start animation
        animate();
        
        Logger.log('Three.js initialized');
        
    } catch (error) {
        Logger.error('Three.js initialization error', error);
    }
}

function createParticles() {
    const geometry = new THREE.BufferGeometry();
    const particleCount = 1000;
    
    const positions = new Float32Array(particleCount * 3);
    const velocities = new Float32Array(particleCount * 3);
    
    for (let i = 0; i < particleCount * 3; i += 3) {
        positions[i] = (Math.random() - 0.5) * 200;
        positions[i + 1] = (Math.random() - 0.5) * 200;
        positions[i + 2] = (Math.random() - 0.5) * 200;
        
        velocities[i] = (Math.random() - 0.5) * 0.5;
        velocities[i + 1] = (Math.random() - 0.5) * 0.5;
        velocities[i + 2] = (Math.random() - 0.5) * 0.5;
    }
    
    geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    
    const material = new THREE.PointsMaterial({
        color: 0x06b6d4,
        size: 0.5,
        sizeAttenuation: true,
        transparent: true,
        opacity: 0.6
    });
    
    particles = new THREE.Points(geometry, material);
    particles.userData.velocities = velocities;
    scene.add(particles);
}

function animate() {
    requestAnimationFrame(animate);
    
    if (particles) {
        const positions = particles.geometry.attributes.position.array;
        const velocities = particles.userData.velocities;
        
        for (let i = 0; i < positions.length; i += 3) {
            positions[i] += velocities[i];
            positions[i + 1] += velocities[i + 1];
            positions[i + 2] += velocities[i + 2];
            
            if (Math.abs(positions[i]) > 100) velocities[i] *= -1;
            if (Math.abs(positions[i + 1]) > 100) velocities[i + 1] *= -1;
            if (Math.abs(positions[i + 2]) > 100) velocities[i + 2] *= -1;
        }
        
        particles.geometry.attributes.position.needsUpdate = true;
        particles.rotation.x += 0.0001;
        particles.rotation.y += 0.0002;
    }
    
    scene.rotation.x += 0.00005;
    scene.rotation.y += 0.0001;
    
    if (renderer) {
        renderer.render(scene, camera);
    }
}

function onWindowResize() {
    const width = window.innerWidth;
    const height = window.innerHeight;
    
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
}

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initThreeJS);
} else {
    initThreeJS();
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (renderer) {
        renderer.dispose();
    }
});