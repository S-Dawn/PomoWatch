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

## Ubuntu `apt install` release path

If you want users to install with:

```bash
sudo apt install pomowatch
```

you need to publish a Debian package to an APT repository. The most practical route for personal/open-source apps is a Launchpad PPA.

### 1. Build and test the Debian package locally

Debian packaging metadata is included in `debian/`.

Install packaging tools:

```bash
sudo apt update
sudo apt install -y build-essential devscripts debhelper dh-python dpkg-dev
```

Build:

```bash
dpkg-buildpackage -us -uc
```

Install generated package for local test:

```bash
sudo apt install ../pomowatch_0.1.0-1_all.deb
```

### 2. Publish through Launchpad PPA

1. Create a PPA on Launchpad.
2. Update `debian/changelog` for each release.
3. Generate source package:

```bash
debuild -S -sa
```

4. Upload with `dput` to your PPA.
5. After Launchpad builds successfully, users can install via:

```bash
sudo add-apt-repository ppa:<your-launchpad-id>/<ppa-name>
sudo apt update
sudo apt install pomowatch
```

### Note about Ubuntu official repositories

Publishing directly in Ubuntu official repositories requires Debian sponsorship and Ubuntu archive processes; this is longer-term. A PPA is the fastest path to `apt install`.

## Project structure

```text
.
├── .dockerignore
├── Dockerfile
├── debian/
├── packaging/
├── main.py
├── pyproject.toml
└── README.md
```
