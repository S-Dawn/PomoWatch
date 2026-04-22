import tkinter as tk
from tkinter import ttk


class PomodoroApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("PomoWatch")
        self.root.geometry("360x360")
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

        self._build_ui()
        self._set_time_display(self.work_minutes.get() * 60)

    def _build_ui(self) -> None:
        frame = ttk.Frame(self.root, padding=16)
        frame.pack(fill="both", expand=True)

        title = ttk.Label(frame, text="PomoWatch", font=("TkDefaultFont", 20, "bold"))
        title.pack(pady=(0, 12))

        self.mode_label = ttk.Label(frame, text="Mode: Ready", font=("TkDefaultFont", 12))
        self.mode_label.pack(pady=(0, 8))

        self.timer_label = ttk.Label(frame, text="25:00", font=("TkDefaultFont", 44, "bold"))
        self.timer_label.pack(pady=(0, 12))

        controls = ttk.Frame(frame)
        controls.pack(pady=(0, 16))

        self.start_button = ttk.Button(controls, text="Start", command=self.start)
        self.start_button.grid(row=0, column=0, padx=4)

        self.pause_button = ttk.Button(controls, text="Pause", command=self.pause, state="disabled")
        self.pause_button.grid(row=0, column=1, padx=4)

        self.reset_button = ttk.Button(controls, text="Reset", command=self.reset)
        self.reset_button.grid(row=0, column=2, padx=4)

        settings = ttk.LabelFrame(frame, text="Settings (minutes)", padding=10)
        settings.pack(fill="x")

        self._add_setting_row(settings, "Work", self.work_minutes, 0)
        self._add_setting_row(settings, "Short Break", self.short_break_minutes, 1)
        self._add_setting_row(settings, "Long Break", self.long_break_minutes, 2)
        self._add_setting_row(settings, "Cycles", self.cycles_before_long_break, 3)

        self.session_label = ttk.Label(frame, text="Completed sessions: 0")
        self.session_label.pack(pady=(10, 0))

    def _add_setting_row(self, parent: ttk.Widget, label: str, variable: tk.IntVar, row: int) -> None:
        ttk.Label(parent, text=label).grid(row=row, column=0, sticky="w", pady=3)
        spinbox = ttk.Spinbox(
            parent,
            from_=1,
            to=120,
            textvariable=variable,
            width=8,
            command=self._on_setting_change,
        )
        spinbox.grid(row=row, column=1, sticky="e", pady=3)
        spinbox.bind("<FocusOut>", lambda _event: self._on_setting_change())
        spinbox.bind("<Return>", lambda _event: self._on_setting_change())

    def _on_setting_change(self) -> None:
        if not self.is_running:
            self._set_time_display(self.work_minutes.get() * 60)

    def _set_time_display(self, total_seconds: int) -> None:
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        self.timer_label.config(text=f"{minutes:02}:{seconds:02}")

    def _update_mode(self, mode: str) -> None:
        self.current_mode = mode
        self.mode_label.config(text=f"Mode: {mode}")

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
            self.root.bell()
            self._start_break_session()
        else:
            self.root.bell()
            self._start_work_session()

        self.timer_id = self.root.after(1000, self._tick)


def main() -> None:
    root = tk.Tk()
    app = PomodoroApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
