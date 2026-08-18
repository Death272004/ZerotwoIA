import math
import queue
import random
import sys
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import ttk
from time import perf_counter

from agents.code_agent import handle as code_handle
from agents.system_agent import execute_command
from agents.web_agent import handle as web_handle
from core.core_brain import enviar_mensaje_streaming
from core.intent import detect_intent
from voice.tts import is_playing, speak_and_play, stop_playback


APP_BG = "#0d1018"
PANEL_BG = "#151a25"
CHAT_BG = "#101522"
TEXT = "#f2f5fb"
MUTED = "#94a3b8"
ACCENT = "#ff4f87"
ACCENT_2 = "#5eead4"
USER_BG = "#243045"
BOT_BG = "#1d2230"
ERROR_BG = "#3b1d2b"


def resource_path(relative_path):
    """Devuelve una ruta valida tanto en desarrollo como dentro de PyInstaller."""
    base_path = getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)
    return Path(base_path) / relative_path


class ZeroTwoApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ZeroTwoIA")
        self.geometry("980x680")
        self.minsize(820, 560)
        self.configure(bg=APP_BG)
        self._set_window_icon()

        self.events = queue.Queue()
        self.busy = False
        self.mode = "idle"
        self.bot_stream_widget = None
        self.bot_stream_text = ""
        self.audio_level = 0.0
        self.spectrum_rays = []
        self.spectrum_rings = []
        self.spectrum_dots = []
        self.spectrum_orbit_lines = []
        self.intro_spoken = False

        self._build_style()
        self._build_layout()
        self._animate_spectrum()
        self._drain_events()
        self.after(650, self._present_on_startup)

    def _set_window_icon(self):
        icon_path = resource_path("assets/zerotwo_icon.ico")
        if not icon_path.exists():
            return
        try:
            self.iconbitmap(str(icon_path))
        except tk.TclError:
            pass

    def _build_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "ZeroTwo.TButton",
            background=ACCENT,
            foreground="white",
            borderwidth=0,
            padding=(14, 10),
            font=("Segoe UI", 10, "bold"),
        )
        style.map("ZeroTwo.TButton", background=[("active", "#ff6a9b"), ("disabled", "#374151")])
        style.configure(
            "Ghost.TButton",
            background="#252c3a",
            foreground=TEXT,
            borderwidth=0,
            padding=(12, 10),
            font=("Segoe UI", 10),
        )
        style.map("Ghost.TButton", background=[("active", "#30394b"), ("disabled", "#1f2937")])

    def _build_layout(self):
        root = tk.Frame(self, bg=APP_BG)
        root.pack(fill="both", expand=True)

        header = tk.Frame(root, bg=APP_BG, height=76)
        header.pack(fill="x", padx=24, pady=(18, 8))
        header.pack_propagate(False)

        title_box = tk.Frame(header, bg=APP_BG)
        title_box.pack(side="left", fill="y")
        tk.Label(title_box, text="ZeroTwoIA", bg=APP_BG, fg=TEXT, font=("Segoe UI", 24, "bold")).pack(anchor="w")
        self.status_label = tk.Label(
            title_box,
            text="Lista para escucharte, Darling.",
            bg=APP_BG,
            fg=MUTED,
            font=("Segoe UI", 10),
        )
        self.status_label.pack(anchor="w", pady=(2, 0))

        self.timer_label = tk.Label(
            header,
            text="respuesta: --",
            bg="#1f2937",
            fg=ACCENT_2,
            font=("Consolas", 11, "bold"),
            padx=14,
            pady=8,
        )
        self.timer_label.pack(side="right", padx=(12, 0), pady=14)

        main = tk.Frame(root, bg=APP_BG)
        main.pack(fill="both", expand=True, padx=24, pady=(0, 20))

        left = tk.Frame(main, bg=CHAT_BG, highlightthickness=1, highlightbackground="#242b39")
        left.pack(side="left", fill="both", expand=True)

        self.chat_canvas = tk.Canvas(left, bg=CHAT_BG, highlightthickness=0)
        self.chat_canvas.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(left, orient="vertical", command=self.chat_canvas.yview)
        scrollbar.pack(side="right", fill="y")
        self.chat_canvas.configure(yscrollcommand=scrollbar.set)

        self.chat_frame = tk.Frame(self.chat_canvas, bg=CHAT_BG)
        self.chat_window = self.chat_canvas.create_window((0, 0), window=self.chat_frame, anchor="nw")
        self.chat_frame.bind("<Configure>", self._on_chat_configure)
        self.chat_canvas.bind("<Configure>", self._on_canvas_configure)

        right = tk.Frame(main, bg=PANEL_BG, width=250, highlightthickness=1, highlightbackground="#242b39")
        right.pack(side="right", fill="y", padx=(18, 0))
        right.pack_propagate(False)

        tk.Label(right, text="Audio", bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 16, "bold")).pack(
            anchor="w", padx=18, pady=(18, 4)
        )
        tk.Label(right, text="Entrada, respuesta y voz", bg=PANEL_BG, fg=MUTED, font=("Segoe UI", 9)).pack(
            anchor="w", padx=18
        )

        self.spectrum = tk.Canvas(right, bg="#0f1420", height=210, highlightthickness=0)
        self.spectrum.pack(fill="x", padx=18, pady=18)
        for _ in range(5):
            self.spectrum_rings.append(self.spectrum.create_oval(0, 0, 0, 0, outline="#1f2937", width=1))
        for _ in range(6):
            self.spectrum_orbit_lines.append(
                self.spectrum.create_arc(0, 0, 0, 0, start=0, extent=360, style="arc", outline="#3b1a5f", width=1)
            )
        for _ in range(145):
            self.spectrum_dots.append(self.spectrum.create_oval(0, 0, 0, 0, fill="#6129ff", outline=""))
        for _ in range(96):
            self.spectrum_rays.append(
                self.spectrum.create_line(0, 0, 0, 0, fill=ACCENT, width=2, capstyle="round")
            )

        self.mic_button = ttk.Button(right, text="Microfono", style="ZeroTwo.TButton", command=self.start_voice)
        self.mic_button.pack(fill="x", padx=18, pady=(2, 10))

        self.stop_button = ttk.Button(right, text="Detener voz", style="Ghost.TButton", command=self.stop_voice)
        self.stop_button.pack(fill="x", padx=18, pady=(0, 10))

        tk.Label(right, text="Tiempo", bg=PANEL_BG, fg=TEXT, font=("Segoe UI", 11, "bold")).pack(
            anchor="w", padx=18, pady=(14, 4)
        )
        self.detail_label = tk.Label(
            right,
            text="intencion --\nprimer texto --\ntotal --",
            justify="left",
            bg=PANEL_BG,
            fg=MUTED,
            font=("Consolas", 10),
        )
        self.detail_label.pack(anchor="w", padx=18)

        bottom = tk.Frame(root, bg=APP_BG)
        bottom.pack(fill="x", padx=24, pady=(0, 20))
        self.input_var = tk.StringVar()
        self.entry = tk.Entry(
            bottom,
            textvariable=self.input_var,
            bg="#151a25",
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=("Segoe UI", 12),
        )
        self.entry.pack(side="left", fill="x", expand=True, ipady=13)
        self.entry.bind("<Return>", lambda _event: self.send_text())
        self.entry.focus_set()

        self.send_button = ttk.Button(bottom, text="Enviar", style="ZeroTwo.TButton", command=self.send_text)
        self.send_button.pack(side="left", padx=(12, 0))

        self._add_message("ZeroTwo", "Estoy aqui. Escribeme o abre el microfono cuando quieras.", "bot")

    def _present_on_startup(self):
        if self.intro_spoken:
            return
        self.intro_spoken = True
        intro = "Zero Two en linea. Hm... ya desperte, Darling. Dime que haremos primero."
        self._set_mode("speaking", "Presentandome con voz...")
        self._speak_async(intro)

    def _on_chat_configure(self, _event=None):
        self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        self.chat_canvas.yview_moveto(1.0)

    def _on_canvas_configure(self, event):
        self.chat_canvas.itemconfig(self.chat_window, width=event.width)

    def _add_message(self, who, text, kind):
        row = tk.Frame(self.chat_frame, bg=CHAT_BG)
        row.pack(fill="x", padx=16, pady=8)

        align = "e" if kind == "user" else "w"
        bubble_bg = USER_BG if kind == "user" else BOT_BG
        if kind == "error":
            bubble_bg = ERROR_BG

        bubble = tk.Frame(row, bg=bubble_bg)
        bubble.pack(anchor=align, padx=(90, 0) if kind == "user" else (0, 90))
        tk.Label(
            bubble,
            text=who,
            bg=bubble_bg,
            fg=ACCENT_2 if kind == "user" else ACCENT,
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w", padx=12, pady=(9, 0))
        label = tk.Label(
            bubble,
            text=text,
            wraplength=560,
            justify="left",
            bg=bubble_bg,
            fg=TEXT,
            font=("Segoe UI", 11),
        )
        label.pack(anchor="w", padx=12, pady=(2, 10))
        self._on_chat_configure()
        return label

    def _set_busy(self, busy):
        self.busy = busy
        state = "disabled" if busy else "normal"
        self.send_button.configure(state=state)
        self.mic_button.configure(state=state)

    def _set_mode(self, mode, status):
        self.mode = mode
        self.status_label.configure(text=status)

    def send_text(self):
        text = self.input_var.get().strip()
        if not text or self.busy:
            return
        self.input_var.set("")
        self._add_message("Tu", text, "user")
        self._start_response(text)

    def start_voice(self):
        if self.busy:
            return
        if is_playing():
            stop_playback()
        self._set_busy(True)
        self._set_mode("recording", "Grabando una toma de voz...")
        threading.Thread(target=self._voice_worker, daemon=True).start()

    def stop_voice(self):
        stop_playback()
        if not self.busy:
            self._set_mode("idle", "Voz detenida.")

    def _voice_worker(self):
        try:
            from voice.stt import grabar_audio, transcribir

            path = grabar_audio(
                path="data/input_voice.wav",
                duracion=5,
                level_callback=lambda level: self.events.put(("audio_level", level)),
            )
            self.events.put(("status", "Transcribiendo voz..."))
            text = transcribir(path).strip()
            if not text:
                self.events.put(("voice_empty", None))
                return
            self.events.put(("voice_text", text))
        except Exception as exc:
            self.events.put(("error", f"No pude usar el microfono: {exc}"))

    def _start_response(self, text):
        self._set_busy(True)
        self._set_mode("thinking", "Pensando rapido...")
        self.bot_stream_widget = None
        self.bot_stream_text = ""
        threading.Thread(target=self._response_worker, args=(text,), daemon=True).start()

    def _response_worker(self, user_input):
        started_at = perf_counter()
        first_chunk_at = None

        try:
            intent = detect_intent(user_input)
            intent_done_at = perf_counter()

            intent_type = intent.get("type")
            if intent_type == "system":
                text = execute_command(intent)
                done_at = perf_counter()
                self.events.put(("tool_result", text, intent_done_at - started_at, done_at - started_at))
                return
            if intent_type == "web":
                text = web_handle(intent)
                done_at = perf_counter()
                self.events.put(("tool_result", text, intent_done_at - started_at, done_at - started_at))
                return
            if intent_type == "code":
                text = code_handle(intent)
                done_at = perf_counter()
                self.events.put(("tool_result", text, intent_done_at - started_at, done_at - started_at))
                return

            self.events.put(("stream_start", None))

            def on_chunk(chunk):
                nonlocal first_chunk_at
                if first_chunk_at is None:
                    first_chunk_at = perf_counter()
                self.events.put(("stream_chunk", chunk))

            text, action = enviar_mensaje_streaming(user_input, callback=on_chunk)
            done_at = perf_counter()
            timings = {
                "intent": intent_done_at - started_at,
                "first": (first_chunk_at or done_at) - started_at,
                "total": done_at - started_at,
            }
            self.events.put(("stream_done", text, action, timings))
        except Exception as exc:
            self.events.put(("error", f"Algo fallo: {exc}"))

    def _speak_async(self, text):
        def worker():
            self.events.put(("speaking", None))
            try:
                speak_and_play(text)
            finally:
                self.events.put(("speaking_done", None))

        threading.Thread(target=worker, daemon=True).start()

    def _drain_events(self):
        try:
            while True:
                event = self.events.get_nowait()
                self._handle_event(event)
        except queue.Empty:
            pass
        self.after(40, self._drain_events)

    def _handle_event(self, event):
        name = event[0]
        if name == "status":
            self._set_mode("thinking", event[1])
        elif name == "audio_level":
            self.audio_level = max(self.audio_level, float(event[1]))
        elif name == "voice_empty":
            self._add_message("ZeroTwo", "No te escuche claro, Darling. Prueba otra vez.", "bot")
            self._set_busy(False)
            self._set_mode("idle", "Lista para escucharte.")
        elif name == "voice_text":
            text = event[1]
            self._add_message("Tu", text, "user")
            self._start_response(text)
        elif name == "stream_start":
            self.bot_stream_widget = self._add_message("ZeroTwo", "", "bot")
            self.bot_stream_text = ""
            self._set_mode("thinking", "Recibiendo respuesta...")
        elif name == "stream_chunk":
            self.bot_stream_text += event[1]
            if self.bot_stream_widget:
                self.bot_stream_widget.configure(text=self.bot_stream_text)
        elif name == "stream_done":
            text, action, timings = event[1], event[2], event[3]
            if self.bot_stream_widget:
                self.bot_stream_widget.configure(text=text)
            self._show_timings(timings["intent"], timings["first"], timings["total"])
            self._set_busy(False)
            self._set_mode("speaking", "Respondiendo con voz...")
            if action:
                threading.Thread(target=self._execute_action_safe, args=(action,), daemon=True).start()
            self._speak_async(text)
        elif name == "tool_result":
            text, intent_time, total_time = event[1], event[2], event[3]
            self._add_message("ZeroTwo", text, "bot")
            self._show_timings(intent_time, total_time, total_time)
            self._set_busy(False)
            self._set_mode("speaking", "Accion ejecutada. Hablando...")
            self._speak_async(text)
        elif name == "action_feedback":
            self._add_message("Sistema", event[1], "bot")
        elif name == "speaking":
            self._set_mode("speaking", "Voz de ZeroTwo activa.")
        elif name == "speaking_done":
            if not self.busy:
                self._set_mode("idle", "Lista para escucharte, Darling.")
        elif name == "error":
            self._add_message("ZeroTwo", event[1], "error")
            self._set_busy(False)
            self._set_mode("idle", "Hubo un error. Lista para intentar de nuevo.")

    def _execute_action_safe(self, action):
        try:
            action_type = action.get("type")
            if action_type == "open_app":
                result = execute_command(action)
                self.events.put(("action_feedback", result))
            elif action_type == "web_search":
                query = action.get("query", "")
                web_handle({"type": "web", "query": query, "raw": query})
            elif action_type == "open_url":
                target = action.get("target", "")
                web_handle({"type": "web", "query": target, "raw": target})
            elif action_type == "youtube":
                query = action.get("query", "")
                web_handle({"type": "web", "query": "youtube " + query, "raw": query})
        except Exception:
            pass

    def _show_timings(self, intent_time, first_time, total_time):
        self.timer_label.configure(text=f"respuesta: {total_time:.2f}s")
        self.detail_label.configure(
            text=(
                f"intencion {intent_time:.2f}s\n"
                f"primer texto {first_time:.2f}s\n"
                f"total {total_time:.2f}s"
            )
        )

    def _animate_spectrum(self):
        width = max(self.spectrum.winfo_width(), 220)
        height = max(self.spectrum.winfo_height(), 190)
        cx = width / 2
        cy = height / 2
        size = min(width, height)
        radius = size * 0.31
        max_ray = size * 0.16

        if self.mode == "recording":
            color = ACCENT_2
            base = max(0.18, self.audio_level)
        elif self.mode == "speaking" or is_playing():
            color = ACCENT
            base = 0.75
        elif self.mode == "thinking":
            color = "#a78bfa"
            base = 0.35
        else:
            color = "#7c3aed"
            base = 0.18

        now = time.time()
        pulse = 1 + math.sin(now * 3.2) * 0.035 + base * 0.03
        glow_colors = ["#1f1140", "#34156f", "#7116c9", "#ff2e9f", "#ff6aa7"]

        for i, ring in enumerate(self.spectrum_rings):
            ring_radius = radius * pulse + i * 3.8
            outline = glow_colors[min(i, len(glow_colors) - 1)]
            self.spectrum.coords(
                ring,
                cx - ring_radius,
                cy - ring_radius,
                cx + ring_radius,
                cy + ring_radius,
            )
            self.spectrum.itemconfig(ring, outline=outline, width=1 + (i // 2))

        for i, arc in enumerate(self.spectrum_orbit_lines):
            tilt = 0.18 + i * 0.11
            wobble = math.sin(now * 1.5 + i) * 0.08
            rx = radius * (0.72 + i * 0.045)
            ry = radius * max(0.12, tilt + wobble)
            angle_start = (now * 34 + i * 54) % 360
            self.spectrum.coords(arc, cx - rx, cy - ry, cx + rx, cy + ry)
            self.spectrum.itemconfig(
                arc,
                start=angle_start,
                extent=250,
                outline="#7c1dff" if i % 2 else "#ff2e9f",
                width=1,
            )

        dot_count = len(self.spectrum_dots)
        columns = 17
        rows = 17
        used = 0
        spin = now * 0.85
        for row in range(rows):
            y_norm = -1 + (2 * row / (rows - 1))
            row_width = math.sqrt(max(0.0, 1 - y_norm * y_norm))
            for col in range(columns):
                if used >= dot_count:
                    break
                x_norm = -1 + (2 * col / (columns - 1))
                if abs(x_norm) > row_width:
                    self.spectrum.coords(self.spectrum_dots[used], 0, 0, 0, 0)
                    used += 1
                    continue

                z = math.sqrt(max(0.0, 1 - x_norm * x_norm - y_norm * y_norm))
                sphere_x = x_norm * math.cos(spin) + z * math.sin(spin)
                depth = 0.55 + 0.45 * (z * math.cos(spin) - x_norm * math.sin(spin))
                wave = math.sin(now * 4.8 + row * 0.8 + col * 0.33) * 0.5 + 0.5
                dot_r = 1.2 + depth * 1.4 + base * wave * 1.2
                px = cx + sphere_x * radius * 0.82
                py = cy + y_norm * radius * 0.82
                dot_color = "#ff2e9f" if depth > 0.78 else "#7c1dff"
                if self.mode == "recording":
                    dot_color = "#5eead4" if depth > 0.78 else "#2563eb"
                self.spectrum.coords(
                    self.spectrum_dots[used],
                    px - dot_r,
                    py - dot_r,
                    px + dot_r,
                    py + dot_r,
                )
                self.spectrum.itemconfig(self.spectrum_dots[used], fill=dot_color)
                used += 1

        while used < dot_count:
            self.spectrum.coords(self.spectrum_dots[used], 0, 0, 0, 0)
            used += 1

        ray_count = len(self.spectrum_rays)
        for i, item in enumerate(self.spectrum_rays):
            angle = (math.tau / ray_count) * i - math.pi / 2
            wave = abs(math.sin(now * 4.3 + i * 0.42))
            secondary = abs(math.sin(now * 2.1 - i * 0.18))
            jitter = random.random() * 0.16
            level = min(1.0, base * (0.22 + wave * 0.58 + secondary * 0.2) + jitter)
            if self.mode == "idle":
                level *= 0.55

            inner = radius * 1.02
            outer = inner + max(5, level * max_ray)
            x1 = cx + math.cos(angle) * inner
            y1 = cy + math.sin(angle) * inner
            x2 = cx + math.cos(angle) * outer
            y2 = cy + math.sin(angle) * outer
            width_px = 1 if self.mode == "idle" else 2
            ray_color = "#ff2e9f" if i < ray_count * 0.46 or i > ray_count * 0.82 else "#5427ff"
            if self.mode == "recording":
                ray_color = "#5eead4" if i % 3 else "#3b82f6"
            self.spectrum.coords(item, x1, y1, x2, y2)
            self.spectrum.itemconfig(item, fill=ray_color if self.mode != "thinking" else color, width=width_px)

        self.audio_level *= 0.82
        self.after(55, self._animate_spectrum)


if __name__ == "__main__":
    app = ZeroTwoApp()
    app.mainloop()
