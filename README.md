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

Tkinter is included with most standard Python distributions.

## Run with uv

From the project root:

```bash
uv run main.py
```

Or run via the project script entry point:

```bash
uv run pomowatch
```

## Project structure

```text
.
├── main.py
├── pyproject.toml
└── README.md
```
