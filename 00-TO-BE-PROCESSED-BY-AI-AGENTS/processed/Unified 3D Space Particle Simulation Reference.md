# Unified 3D Space Particle Simulation Reference

## Core Physics Equations

### Gravitational N-Body
```
F_i = G∑_{j≠i} m_i m_j(r_j-r_i)/|r_j-r_i|³
H = ∑_i |p_i|²/(2m_i) - G∑_{i<j} m_i m_j/|r_i-r_j|  # Hamiltonian
```

### Electromagnetic Forces
```
F = q(E + v×B)  # Lorentz force
∇²V = 0  # Laplace potential
V(r) = ∑_{ℓ=0}^∞ ∑_{m=-ℓ}^ℓ (A_ℓᵐ/r^{ℓ+1}) Y_ℓᵐ(θ,φ)  # Spherical harmonics
γ = 1/√(1-v²/c²)  # Relativistic corrections
```

### MHD Plasma Equations
```
∂ρ/∂t + ∇·(ρv) = 0  # Continuity
∂(ρv)/∂t + ∇·(ρvv + pI + BB/4π) = ρg  # Momentum
∂B/∂t + ∇×(v×B) = 0  # Induction
∇·B = 0  # Divergence constraint
```

### Phase Transitions & Boundaries
```
dp/dT = L/(T·ΔV)  # Clausius-Clapeyron
n₊n₋/n₀ = (2πm_e kT/h²)^{3/2} exp(-E_i/kT)  # Saha ionization
u(∂u/∂x) + v(∂u/∂y) = -(1/ρ)(∂p/∂x) + ν(∂²u/∂y²)  # Prandtl boundary layer
```

## Numerical Integration Methods

### Symplectic Integrators
```javascript
// Velocity-Verlet (energy-conserving)
function verletStep(pos,vel,masses,dt) {
  let acc = computeAccelerations(pos,masses);
  vel += 0.5*dt*acc;
  pos += dt*vel;
  acc = computeAccelerations(pos,masses);
  vel += 0.5*dt*acc;
  return {pos,vel};
}

// Boris integrator (magnetic fields)
function borisUpdate(v,E,B,q,m,dt) {
  const α = q*dt/(2*m);
  v += α*E;
  const t = α*B;
  const s = 2*t/(1 + dot(t,t));
  v_minus = v + α*E;
  v_prime = v_minus + cross(v_minus,t);
  v_plus = v_minus + cross(v_prime,s);
  return v_plus + α*E;
}
```

### RK4 Implementation
```javascript
function rk4Step(pos,vel,masses,dt) {
  const k1v = computeAccelerations(pos,masses);
  const k1r = vel;
  const k2v = computeAccelerations(pos+0.5*dt*k1r,masses);
  const k2r = vel+0.5*dt*k1v;
  const k3v = computeAccelerations(pos+0.5*dt*k2r,masses);
  const k3r = vel+0.5*dt*k2v;
  const k4v = computeAccelerations(pos+dt*k3r,masses);
  const k4r = vel+dt*k3v;
  vel += (dt/6)*(k1v+2*k2v+2*k3v+k4v);
  pos += (dt/6)*(k1r+2*k2r+2*k3r+k4r);
  return {pos,vel};
}
```

## Spatial Acceleration Structures

### Barnes-Hut O(N log N)
```javascript
class OctreeNode {
  insert(body) {
    if(!this.body) {
      this.body = body;
      this.centerOfMass = body.position;
      this.totalMass = body.mass;
    } else {
      this.centerOfMass = (this.centerOfMass*this.totalMass + 
                          body.position*body.mass)/(this.totalMass+body.mass);
      this.totalMass += body.mass;
      this.subdivide();
    }
  }
  
  computeForce(pos,theta=0.5) {
    const r_vec = this.centerOfMass - pos;
    const dist = length(r_vec);
    if(this.isLeaf || this.size/dist < theta) {
      return this.totalMass * r_vec / dist³;
    }
    return sum(child.computeForce(pos,theta) for child in children);
  }
}
```

### Spatial Hashing O(1)
```javascript
function hashPosition(pos,cellSize) {
  const ix = floor(pos.x/cellSize);
  const iy = floor(pos.y/cellSize);
  const iz = floor(pos.z/cellSize);
  return (ix*73856093) ^ (iy*19349663) ^ (iz*83492791);
}
```

## GPU Compute Shaders

### WebGPU Force Calculation
```wgsl
@compute @workgroup_size(64)
fn particleForces(@builtin(global_invocation_id) id: vec3<u32>) {
  let i = id.x;
  var force = vec3<f32>(0.0);
  
  // Tile-based calculation with shared memory
  for (var tile = 0u; tile < numTiles; tile++) {
    // Load tile to shared memory
    workgroupBarrier();
    
    // Compute forces from tile
    for (var j = 0u; j < TILE_SIZE; j++) {
      if (i != j) {
        let r = positions[j] - positions[i];
        let r3 = pow(length(r) + softening, 3.0);
        force += G * masses[j] * r / r3;
      }
    }
  }
  
  velocities[i] += force * deltaTime / masses[i];
}
```

### WebGL Transform Feedback
```glsl
// Vertex shader for GPU physics
attribute vec3 a_position;
attribute vec3 a_velocity;
uniform sampler2D u_forceTexture;
varying vec3 v_newPosition;
varying vec3 v_newVelocity;

void main() {
  vec3 force = texture2D(u_forceTexture, getTexCoord(gl_VertexID)).xyz;
  v_newVelocity = a_velocity + force * u_deltaTime;
  v_newPosition = a_position + v_newVelocity * u_deltaTime;
  gl_Position = vec4(0.0); // Not rendering
}
```

## Collision Detection

### SPH Kernels
```javascript
// Poly6 (density)
W_poly6 = (315/(64*π*h⁹))*(h²-r²)³
// Spiky gradient (pressure)
∇W_spiky = -(45/(π*h⁶))*(h-r)²*r̂
// Viscosity Laplacian
∇²W_visc = (45/(π*h⁶))*(h-r)
```

### Continuous Collision Detection
```javascript
// Solve: |p₁(t) - p₂(t)|² = (r₁+r₂)²
function timeOfImpact(p1,v1,r1,p2,v2,r2) {
  const dv = v1-v2, dp = p1-p2;
  const a = dot(dv,dv);
  const b = 2*dot(dp,dv);
  const c = dot(dp,dp) - (r1+r2)²;
  const disc = b²-4*a*c;
  if(disc < 0) return Infinity;
  return (-b - sqrt(disc))/(2*a);
}
```

### Ray-Triangle Intersection (Möller-Trumbore)
```glsl
bool intersectTriangle(vec3 orig, vec3 dir, vec3 v0, vec3 v1, vec3 v2) {
  vec3 e1 = v1-v0, e2 = v2-v0;
  vec3 pvec = cross(dir,e2);
  float det = dot(e1,pvec);
  if(abs(det) < EPSILON) return false;
  float invDet = 1.0/det;
  vec3 tvec = orig-v0;
  float u = dot(tvec,pvec)*invDet;
  if(u < 0.0 || u > 1.0) return false;
  vec3 qvec = cross(tvec,e1);
  float v = dot(dir,qvec)*invDet;
  if(v < 0.0 || u+v > 1.0) return false;
  float t = dot(e2,qvec)*invDet;
  return t > 0.0;
}
```

## Galactic-Scale Formulations

### Dark Matter Profiles
```
ρ_NFW(r) = ρ₀/[(r/Rs)(1+r/Rs)²]
ρ_Einasto(r) = ρs exp(-2/α[(r/rs)^α-1]), α≈0.91
```

### Galaxy Formation
```
dn/dM = (ρ₀/M²)(δc/σ(M))(1/√(2π))exp(-δc²/2σ²(M))|dln σ/dln M|
Σ_SFR = A × Σ_gas^N, N≈1.4-1.5  # Schmidt-Kennicutt
```

### Turbulence Spectra
```
E(k) = C_K ε^{2/3} k^{-5/3}  # Kolmogorov
E(k) ∝ k^{-2}  # Compressible
σ²(ln ρ) = ln(1 + b²M²)  # Mach dependence
```

## Coordinate Transformations

### Spherical ↔ Cartesian
```javascript
// To Cartesian
x = r*sin(θ)*cos(φ);
y = r*sin(θ)*sin(φ);
z = r*cos(θ);

// To Spherical
r = sqrt(x²+y²+z²);
θ = atan2(sqrt(x²+y²),z);
φ = atan2(y,x);
```

### Logarithmic Depth (Universe Scale)
```glsl
float logDepthBufFC = 2.0/log2(farPlane+1.0);
gl_Position.z = log2(max(1e-6,1.0+gl_Position.w))*logDepthBufFC-1.0;
gl_Position.z *= gl_Position.w;
```

### Galactic Coordinates (J2000.0)
```javascript
const α_p = 192.859°, δ_p = 27.128°;  // Galactic pole
// Quaternion rotation for stability
q * v * q_conjugate
```

## Volumetric Rendering

```glsl
vec4 volumetricRayMarch(vec3 origin, vec3 dir) {
  vec4 color = vec4(0);
  float transmittance = 1.0;
  vec3 pos = origin;
  
  for(int i = 0; i < MAX_STEPS; i++) {
    float density = sampleVolume(pos);
    float absorption = exp(-density * σ_t * stepSize);
    
    // Scattering calculation
    vec3 lightContrib = computeScattering(pos, lightDir);
    color.rgb += lightContrib * transmittance * (1.0-absorption);
    transmittance *= absorption;
    
    pos += dir * stepSize;
    if(transmittance < 0.01) break;
  }
  
  color.a = 1.0 - transmittance;
  return color;
}
```

### Atmospheric Scattering
```
β_Rayleigh ∝ λ⁻⁴
β_Mie = β_Mie₀ × (λ/λ₀)^{-α}, α≈1.3
```

## Memory Layout Optimization

```javascript
// Structure of Arrays (SoA) for SIMD
class ParticleSystemSoA {
  constructor(n) {
    // Separate arrays for vectorization
    this.posX = new Float32Array(n);
    this.posY = new Float32Array(n);
    this.posZ = new Float32Array(n);
    this.velX = new Float32Array(n);
    this.velY = new Float32Array(n);
    this.velZ = new Float32Array(n);
    this.mass = new Float32Array(n);
  }
}

// Morton ordering for cache efficiency
function mortonEncode3D(x,y,z) {
  return spreadBits3(x) | (spreadBits3(y)<<1) | (spreadBits3(z)<<2);
}
```

## Single HTML Deployment

```javascript
// WASM embedding
const wasmB64 = "AGFzbQEAAAA...";
const wasmBytes = Uint8Array.from(atob(wasmB64), c=>c.charCodeAt(0));
const module = await WebAssembly.instantiate(wasmBytes);

// Asset compression via PNG encoding
function encodeAssetAsPNG(data) {
  const width = Math.ceil(Math.sqrt(data.length/4));
  // Pack binary data into RGBA pixels
}

// Inline shaders
const shaderCode = `#version 310 es
  // Entire shader as template literal
`;
```

## Performance Benchmarks

- **WebGPU**: 1M+ particles @ 60 FPS
- **WebGL2+Transform Feedback**: 100K @ 60 FPS
- **Barnes-Hut**: O(N log N) vs O(N²)
- **SIMD speedup**: 2-4x
- **Memory bandwidth**: 95% with SoA
- **GPU scaling**: 288K cores, 2B particles

## Key Missing Implementations

1. **Plasma-material interactions** with Debye shielding
2. **Rankine-Hugoniot shock relations** for atmospheric entry
3. **Fay-Riddell stagnation heating** for ablation
4. **Self-interacting dark matter** σ/m ~ 0.1 cm²/g
5. **Implicit integration** for stiff systems
6. **WebGPU radix sort** for spatial queries
7. **BVH with SAH** construction
8. **Neural ODE surrogates** for 1000x speedup