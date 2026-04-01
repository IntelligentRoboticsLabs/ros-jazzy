# EasyNav (Jazzy) — local buildfarm + user workspace

This page explains:

- How to build EasyNav packages for ROS 2 **jazzy** using this repo (Pixi + Vinca + rattler-build).
- How to consume the resulting packages in a separate colcon workspace (Pixi template).

## What it is

- **Producers** (package creators): build `.conda` artifacts into a local file-channel at `ros-jazzy/output/`.
- **Consumers** (users): create a normal ROS 2 workspace and install dependencies from that local channel.

## For package creators (buildfarm)

From the `ros-jazzy/` folder:

1) Install the build environment:

- `pixi install`

2) Build the EasyNav subset (generate recipes → build → index):

- `pixi run easynav-all`

Artifacts should land under:

- `ros-jazzy/output/linux-64/`

Index files should exist under:

- `ros-jazzy/output/linux-64/repodata.json`

### Troubleshooting

- If a downstream Pixi solve says “No candidates found…”, clear repodata cache:
  - `pixi clean cache --repodata -y`
- The **channel root** is `.../ros-jazzy/output` (not `.../output/linux-64`).

## For users (consumer workspace)

A ready-to-edit Pixi template is in:

- `ros-jazzy/irl-docs/easynav/pixi.toml`
- `ros-jazzy/irl-docs/easynav/activate.sh`

### Quick start

1) Create a workspace and copy the template files:

- `mkdir -p ~/ws/easynav_ws && cd ~/ws/easynav_ws`
- Copy `pixi.toml` and `activate.sh` from `ros-jazzy/irl-docs/easynav/`

2) Enter the environment:

- `pixi shell`

3) Clone sources (example; adjust to your needs):

- `mkdir -p src && cd src`
- `vcs import < easynav.repos`

4) Build:

- `pixi run build`

### Runtime notes

- This template defaults to Zenoh:
  - `export RMW_IMPLEMENTATION=rmw_zenoh_cpp`
- Run the Zenoh daemon in a separate terminal:
  - `ros2 run rmw_zenoh_cpp rmw_zenohd`

### Eigen / PCL note

- The consumer env pins `eigen < 5` to reduce the chance of CMake falling back to system Eigen (`/usr/include/eigen3`) when building PCL-dependent packages.
