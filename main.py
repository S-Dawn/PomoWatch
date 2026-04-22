import tkinter as tk
from tkinter import ttk
import threading

import numpy as np
import sounddevice as sd
from ttkthemes import ThemedTk


# ── Audio ─────────────────────────────────────────────────────────────────────

def _chime_worker(work_done: bool) -> None:
    sample_rate = 44100
    if work_done:
        # Ascending 4-note chime: C5 → E5 → G5 → C6
        notes = [523.25, 659.25, 783.99, 1046.50]
        durations = [0.22, 0.22, 0.22, 0.50]
    else:
        # Descending 3-note chime: G5 → E5 → C5
        notes = [783.99, 659.25, 523.25]
        durations = [0.22, 0.22, 0.50]

    chunks: list[np.ndarray] = []
    for freq, dur in zip(notes, durations):
        n = int(sample_rate * dur)
        t = np.linspace(0.0, dur, n, endpoint=False)
        # Fundamental + 2nd/3rd harmonics for a bell-like timbre
        wave = (
            np.sin(2 * np.pi * freq * t)
            + 0.30 * np.sin(4 * np.pi * freq * t)
            + 0.10 * np.sin(6 * np.pi * freq * t)
        )
        # Exponential decay envelope (bell-like fade)
        env = np.exp(-3.5 * t / dur).astype(np.float32)
        chunks.append((wave * env * 0.30).astype(np.float32))
        # Brief silence between notes
        chunks.append(np.zeros(int(0.05 * sample_rate), dtype=np.float32))

    try:
        sd.play(np.concatenate(chunks), sample_rate)
        sd.wait()
    except Exception:
        pass  # silently skip if no audio device is available


def play_chime(work_done: bool = True) -> None:
    threading.Thread(target=_chime_worker, args=(work_done,), daemon=True).start()


# ── Theme & color config ──────────────────────────────────────────────────────

# Preferred themes tried in order; falls back to whatever ttkthemes provides
_PREFERRED_THEMES = ["arc", "adapta", "breeze", "equilux", "radiance", "elegance", "clam"]

# Timer digit color per mode (bright enough for both light and dark themes)
_MODE_COLOR: dict[str, str] = {
    "Work": "#e74c3c",
    "Short Break": "#2ecc71",
    "Long Break": "#3498db",
    "Ready": "#95a5a6",
}


# ── App ───────────────────────────────────────────────────────────────────────

class PomodoroApp:
    def __init__(self, root: ThemedTk) -> None:
        self.root = root
        self.root.title("PomoWatch")
        self.root.resizable(False, False)

        self.work_minutes = tk.IntVar(value=25)
        self.short_break_minutes = tk.IntVar(value=5)
        self.long_break_minutes = tk.IntVar(value=15)
        self.cycles_before_long_break = tk.IntVar(value=4)

        self.session_count = 0
        self.is_running = False
        self.remaining_seconds = 0
        self.timer_id: str | None = None
        self.current_mode = "Ready"

        available = set(root.get_themes())
        self._themes = [t for t in _PREFERRED_THEMES if t in available] or sorted(available)
        self.current_theme = tk.StringVar(value=self._themes[0])

        self._style = ttk.Style()
        self._build_ui()
        self._set_time_display(self.work_minutes.get() * 60)
        self._fit_window()

    def _build_ui(self) -> None:
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="PomoWatch", font=("TkDefaultFont", 22, "bold")).pack(pady=(0, 6))

        self.mode_label = ttk.Label(frame, text="Mode: Ready", font=("TkDefaultFont", 12))
        self.mode_label.pack(pady=(0, 4))

        self._style.configure(
            "Timer.TLabel",
            font=("TkDefaultFont", 48, "bold"),
            foreground=_MODE_COLOR["Ready"],
        )
        self.timer_label = ttk.Label(frame, text="25:00", style="Timer.TLabel")
        self.timer_label.pack(pady=(0, 14))

        controls = ttk.Frame(frame)
        controls.pack(pady=(0, 16))

        self.start_button = ttk.Button(controls, text="Start", command=self.start, width=8)
        self.start_button.grid(row=0, column=0, padx=5)

        self.pause_button = ttk.Button(controls, text="Pause", command=self.pause, state="disabled", width=8)
        self.pause_button.grid(row=0, column=1, padx=5)

        self.reset_button = ttk.Button(controls, text="Reset", command=self.reset, width=8)
        self.reset_button.grid(row=0, column=2, padx=5)

        settings = ttk.LabelFrame(frame, text="Settings", padding=10)
        settings.pack(fill="x", pady=(0, 8))
        settings.columnconfigure(1, weight=1)

        self._add_setting_row(settings, "Work (min)", self.work_minutes, 0)
        self._add_setting_row(settings, "Short Break (min)", self.short_break_minutes, 1)
        self._add_setting_row(settings, "Long Break (min)", self.long_break_minutes, 2)
        self._add_setting_row(settings, "Cycles", self.cycles_before_long_break, 3)

        ttk.Label(settings, text="Theme").grid(row=4, column=0, sticky="w", pady=3)
        theme_cb = ttk.Combobox(
            settings,
            textvariable=self.current_theme,
            values=self._themes,
            state="readonly",
            width=14,
        )
        theme_cb.grid(row=4, column=1, sticky="e", pady=3)
        theme_cb.bind("<<ComboboxSelected>>", self._apply_theme)

        self.session_label = ttk.Label(frame, text="Completed sessions: 0")
        self.session_label.pack(pady=(4, 0))

    def _add_setting_row(self, parent: ttk.Widget, label: str, variable: tk.IntVar, row: int) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=3)
        spinbox = ttk.Spinbox(
            parent,
            from_=1,
            to=120,
            textvariable=variable,
            width=10,
            command=self._on_setting_change,
        )
        spinbox.grid(row=row, column=1, sticky="e", pady=3)
        spinbox.bind("<FocusOut>", lambda _e: self._on_setting_change())
        spinbox.bind("<Return>", lambda _e: self._on_setting_change())

    def _on_setting_change(self) -> None:
        if not self.is_running:
            self._set_time_display(self.work_minutes.get() * 60)

    def _fit_window(self) -> None:
        """Resize the window to exactly fit its content for the current theme."""
        self.root.update_idletasks()
        w = self.root.winfo_reqwidth()
        h = self.root.winfo_reqheight()
        self.root.geometry(f"{w}x{h}")
        self.root.minsize(w, h)

    def _apply_theme(self, *_) -> None:
        self.root.set_theme(self.current_theme.get())
        # Re-apply custom timer style after the theme resets all styles
        self._style.configure(
            "Timer.TLabel",
            font=("TkDefaultFont", 48, "bold"),
            foreground=_MODE_COLOR.get(self.current_mode, "#95a5a6"),
        )
        self._fit_window()

    def _set_time_display(self, total_seconds: int) -> None:
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        self.timer_label.config(text=f"{minutes:02}:{seconds:02}")

    def _update_mode(self, mode: str) -> None:
        self.current_mode = mode
        self.mode_label.config(text=f"Mode: {mode}")
        self._style.configure("Timer.TLabel", foreground=_MODE_COLOR.get(mode, "#95a5a6"))

    def start(self) -> None:
        if self.is_running:
            return

        if self.remaining_seconds <= 0:
            if self.current_mode in ("Ready", "Long Break", "Short Break"):
                self._start_work_session()
            else:
                self._start_break_session()

        self.is_running = True
        self.start_button.config(state="disabled")
        self.pause_button.config(state="normal")
        self._tick()

    def pause(self) -> None:
        self.is_running = False
        self.start_button.config(state="normal")
        self.pause_button.config(state="disabled")
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

    def reset(self) -> None:
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

        self.is_running = False
        self.remaining_seconds = self.work_minutes.get() * 60
        self._update_mode("Ready")
        self._set_time_display(self.remaining_seconds)

        self.start_button.config(state="normal")
        self.pause_button.config(state="disabled")

    def _start_work_session(self) -> None:
        self.remaining_seconds = self.work_minutes.get() * 60
        self._update_mode("Work")
        self._set_time_display(self.remaining_seconds)

    def _start_break_session(self) -> None:
        if self.session_count > 0 and self.session_count % self.cycles_before_long_break.get() == 0:
            break_minutes = self.long_break_minutes.get()
            self._update_mode("Long Break")
        else:
            break_minutes = self.short_break_minutes.get()
            self._update_mode("Short Break")

        self.remaining_seconds = break_minutes * 60
        self._set_time_display(self.remaining_seconds)

    def _tick(self) -> None:
        if not self.is_running:
            return

        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self._set_time_display(self.remaining_seconds)
            self.timer_id = self.root.after(1000, self._tick)
            return

        if self.current_mode == "Work":
            self.session_count += 1
            self.session_label.config(text=f"Completed sessions: {self.session_count}")
            play_chime(work_done=True)
            self._start_break_session()
        else:
            play_chime(work_done=False)
            self._start_work_session()

        self.timer_id = self.root.after(1000, self._tick)


def main() -> None:
    root = ThemedTk(theme="arc")
    app = PomodoroApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
