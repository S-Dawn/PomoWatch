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

## Project structure

```text
.
├── main.py
├── pyproject.toml
└── README.md
```
