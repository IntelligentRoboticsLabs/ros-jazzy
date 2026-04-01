# PlanSys2 (Jazzy) — local buildfarm + user workspace

This page explains:

- How to build PlanSys2 packages for ROS 2 **jazzy** using this repo (Pixi + Vinca + rattler-build).
- How to consume the resulting packages in a separate colcon workspace (Pixi template).

## What it is

- **Producers** (package creators): build `.conda` artifacts into a local file-channel at `ros-jazzy/output/`.
- **Consumers** (users): create a normal ROS 2 workspace and install dependencies from that local channel.

## For package creators (buildfarm)

From the `ros-jazzy/` folder:

1) Install the build environment:

- `pixi install`

2) Build the PlanSys2 subset (generate recipes → build → index):

- `pixi run plansys2-all`

### Why `popf` is built first

`plansys2-clean` wipes `output/`. If you build PlanSys2 after a clean, `ros-jazzy-popf` must exist in the local channel before anything depending on it can resolve.

The task `plansys2-all` includes a `plansys2-build-popf` step that:

- builds `./recipes/ros-jazzy-popf/recipe.yaml`
- runs `rattler-index` on `./output`

### Troubleshooting

- If a downstream Pixi solve says “No candidates found…”, clear repodata cache:
  - `pixi clean cache --repodata -y`
- The **channel root** is `.../ros-jazzy/output` (not `.../output/linux-64`).

## For users (consumer workspace)

A ready-to-edit Pixi template is in:

- `ros-jazzy/irl-docs/plansys2/pixi.toml`
- `ros-jazzy/irl-docs/plansys2/activate.sh`

### Quick start

1) Create a workspace and copy the template files:

- `mkdir -p ~/ws/plansys2_ws && cd ~/ws/plansys2_ws`
- Copy `pixi.toml` and `activate.sh` from `ros-jazzy/irl-docs/plansys2/`

2) Enter the environment:

- `pixi shell`

3) Clone sources (example):

- `mkdir -p src && cd src`
- `git clone https://github.com/PlanSys2/ros2_planning_system.git -b jazzy`

4) Build:

- `pixi run build`

### Runtime notes

- This template defaults to Zenoh:
  - `export RMW_IMPLEMENTATION=rmw_zenoh_cpp`
- Run the Zenoh daemon in a separate terminal:
  - `ros2 run rmw_zenoh_cpp rmw_zenohd`
