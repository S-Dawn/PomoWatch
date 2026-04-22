# PomoWatch

A simple Pomodoro timer desktop app built with Python and Tkinter.

## Features

- Work, short break, and long break timers
- Configurable session durations
- Configurable number of work cycles before long break
- Start, pause, and reset controls
- Completed session counter

## Requirements

- Python 3.10+
- [uv](https://github.com/astral-sh/uv)

Tkinter is included with most standard Python distributions. However, on some Linux systems it must be installed separately via the system package manager — it cannot be installed through pip, uv, or Poetry.

**Debian/Ubuntu:**
```bash
sudo apt-get install python3-tk
```

**Fedora/RHEL:**
```bash
sudo dnf install python3-tkinter
```

## Run with uv

From the project root:

```bash
uv run main.py
```

## Docker

This app is a desktop GUI, so Docker needs access to your host display (X11) and optional audio device.

Build image:

```bash
docker build -t pomowatch:latest .
```

Explanation:

- `docker build` creates a Docker image from the Dockerfile in the current directory.
- `-t pomowatch:latest` tags the image with the name `pomowatch` and tag `latest`.
- `.` sets the build context to the current folder (project root).

Run image on Linux with X11 and sound:

```bash
xhost +local:docker
docker run --rm \
	-e DISPLAY=$DISPLAY \
	-v /tmp/.X11-unix:/tmp/.X11-unix \
	--device /dev/snd \
	pomowatch:latest
xhost -local:docker
```

Explanation:

- `xhost +local:docker` temporarily allows local Docker containers to access your X server so the Tkinter window can open.
- `docker run --rm` starts the container and removes it automatically when the app exits.
- `-e DISPLAY=$DISPLAY` passes your current X display environment into the container.
- `-v /tmp/.X11-unix:/tmp/.X11-unix` mounts the X11 Unix socket so GUI drawing works.
- `--device /dev/snd` passes the host audio device to the container so chimes can play.
- `pomowatch:latest` is the image tag to run.
- `xhost -local:docker` revokes the X server permission granted earlier.

Optional run without audio:

```bash
xhost +local:docker
docker run --rm \
	-e DISPLAY=$DISPLAY \
	-v /tmp/.X11-unix:/tmp/.X11-unix \
	pomowatch:latest
xhost -local:docker
```

Files used:

- `Dockerfile`
- `.dockerignore`

## Install on Ubuntu

### 1) Download the .deb from GitHub Release

From the release page, download:

`pomowatch_0.1.0-1_all.deb`

or use `wget`:

```bash
wget https://github.com/S-Dawn/PomoWatch/releases/download/v0.1.0-1/pomowatch_0.1.0-1_all.deb
```

### 2) Install the downloaded file with apt

From the folder containing the file:

```bash
sudo apt install ./pomowatch_0.1.0-1_all.deb
```

### 3) Run the app

```bash
pomowatch
```

## For maintainers: build your own .deb

If you want to create a new `.deb` package from source, follow the guide in `BUILD_DEB.md`.

### VS Code tasks for packaging

This project includes ready-made tasks in `.vscode/tasks.json`.

Open Command Palette and run `Tasks: Run Task`, then use:

- `Package: Full .deb workflow` to install build dependencies, build the package, move `.deb` to `dist/`, and clean generated artifacts.
- `Install: local .deb from dist` to install the generated package locally with apt.

You can also run individual steps with:

- `Package: Install build dependencies`
- `Package: Build .deb`
- `Package: Move .deb to dist`
- `Package: Clean generated artifacts`

## Project structure

```text
.
├── .dockerignore
├── BUILD_DEB.md
├── Dockerfile
├── dist/
├── debian/
├── packaging/
├── main.py
├── pyproject.toml
└── README.md
```
