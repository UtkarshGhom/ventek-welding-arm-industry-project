# VENTEK Autonomous Welding Docker Environment

This directory provides a multi-architecture Docker configuration supporting **Apple Silicon (MacBook M2, M3, M4 — ARM64)** and standard x86_64 PCs (AMD64).

It packages:
- **Ubuntu 22.04 LTS**
- **ROS 2 Humble**
- **Gazebo Sim 8 (Harmonic)**
- **Robot State Publisher, RViz2, Xacro, and Controllers**
- **Browser-based noVNC Desktop** (zero client configuration required on macOS)

---

## 1. Quick Start on MacBook M2+ (via Browser Desktop)

On macOS, running 3D graphics (Gazebo / RViz) via standard XQuartz often fails due to indirect OpenGL limitations. This Docker image includes a built-in **Web Desktop (noVNC)** that streams directly into your Safari or Chrome browser.

### Step 1: Start the Desktop Container
From the `ventek_project/docker/` directory:
```bash
docker compose up desktop
```
*(On first run, this builds the ARM64 image natively on your M2 chip.)*

### Step 2: Open the Desktop in Your Browser
Open Safari or Chrome on your Mac and navigate to:
```
http://localhost:6080/vnc.html?autoconnect=true
```
You will see a lightweight Linux desktop with full display and keyboard control.

### Step 3: Launch Simulation Inside the Browser Desktop
Open a terminal in the browser desktop (or attach from your Mac terminal using `docker exec -it ventek_desktop bash`):
```bash
# 1. Build workspace packages
cd /home/ventek/ventek_ws
colcon build --paths ventek_project ventek_project/ventek_cell_description --symlink-install
source install/setup.bash

# 2. Launch Continuous Arc Welding Cell (KUKA KR 6)
ros2 launch ventek_autonomous_welding simulation.launch.py

# OR Launch Spot Welding Cell (FANUC R-2000iA)
ros2 launch ventek_cell_description gazebo_cell.launch.py
```

---

## 2. Interactive Development Shell (CLI Mode)

To attach an interactive bash shell to edit, build, and test:
```bash
docker compose run --rm dev
```
Inside the container:
```bash
# Verify environment and coordinate frames
python3 scripts/verify_cell_setup.py

# Run all 46 pytest tests
PYTHONPATH=. pytest tests/ integration/tests/

# Run end-to-end baseline pipeline
PYTHONPATH=. python3 scripts/run_integration_pipeline.py
```
> All code changes made on your host machine in `ventek_project/` are live-synced through the mounted volume.

---

## 3. Automated Headless Testing (CI / Pre-commit)

To execute all tests non-interactively and exit with status code:
```bash
docker compose run --rm test
```

---

## 4. Alternative: Native macOS XQuartz Forwarding

If you prefer native window pop-ups instead of the web browser:
1. Install and open XQuartz on macOS:
   ```bash
   brew install --cask xquartz
   open -a XQuartz
   ```
2. In XQuartz Preferences → Security, check **"Allow connections from network clients"**.
3. In macOS Terminal, allow local connections:
   ```bash
   xhost +localhost
   ```
4. Run the container with host display forwarding:
   ```bash
   docker run -it --rm \
     -e DISPLAY=host.docker.internal:0 \
     -e LIBGL_ALWAYS_SOFTWARE=1 \
     -v $(pwd)/..:/home/ventek/ventek_ws/ventek_project \
     ventek-autonomous-welding:latest bash
   ```

---

## 5. Performance Tips for Apple Silicon Mac

- **Recommended Docker Engine**: [OrbStack](https://orbstack.dev/) provides significantly lower CPU/memory overhead and faster volume performance on Apple Silicon than Docker Desktop.
- **Resource Allocation**: In Docker Desktop Settings → Resources, allocate at least **4 CPU cores** and **6 GB RAM** for smooth Gazebo physics and sensor rendering.
