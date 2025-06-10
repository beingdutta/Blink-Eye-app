import time
import sys, os
import threading
import tkinter as tk
from tkinter import Toplevel
from PIL import Image, ImageTk, ImageSequence


# Constants
REMINDER_INTERVAL = 20 * 60  # 20 minutes
DISPLAY_DURATION = 20        # 50 seconds for debug

# Color Palette
BG_COLOR = "#1C1C21"
POPUP_COLOR = "#2F3037"
TITLE_COLOR = "#EAEAEA"
TEXT_COLOR = "#CCCCCC"

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

GIF_PATH = resource_path("tenor.gif")
ICON_PATH = resource_path("icon.ico")

class BlinkNotifier:
    def __init__(self, root):
        self.root = root

        # Keep root in taskbar, but invisible
        self.root.geometry("0x0+0+0")
        self.root.overrideredirect(True)
        try:
            self.root.iconbitmap(ICON_PATH)
        except Exception as e:
            print(f"[WARN] Could not set root icon: {e}")

        self.running = True
        print("[INFO] Application started.")
        print("[INFO] Scheduling first immediate notification...")

        self.root.after(0, self.show_notification)
        threading.Thread(target=self.scheduler_loop, daemon=True).start()

    def scheduler_loop(self):
        while self.running:
            print(f"[INFO] Sleeping for {REMINDER_INTERVAL} seconds (20 minutes)...")
            time.sleep(REMINDER_INTERVAL)

            if self.running:
                print("[INFO] Time to show a new notification.")
                self.root.after(0, self.show_notification)

    def show_notification(self):
        print("[INFO] Creating reminder popup window...")

        popup = Toplevel(self.root)
        popup.title("Time to Blink!")
        popup_width = 280
        popup_height = 440

        # Calculate position for bottom-right
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()
        x = screen_width - popup_width - 10
        y = (screen_height // 2) - (popup_height // 2)

        popup.geometry(f"{popup_width}x{popup_height}+{x}+{y}")
        popup.configure(bg=POPUP_COLOR)

        popup.resizable(False, False)
        popup.attributes('-topmost', True)
        popup.overrideredirect(True)

        try:
            popup.iconbitmap(ICON_PATH)
        except Exception as e:
            print(f"[WARN] Could not set popup icon: {e}")

        # --- Custom Title Bar ---
        title_bar = tk.Frame(popup, bg=BG_COLOR)
        title_bar.pack(fill="x")

        title_label = tk.Label(title_bar, text="Time to Blink!", bg=BG_COLOR, fg=TITLE_COLOR, font=("Segoe UI Semibold", 12))
        title_label.pack(side="left", padx=10, pady=5)

        close_button = tk.Button(
            title_bar,
            text="✕",
            command=lambda: self.close_popup(popup),
            bg=BG_COLOR,
            fg="white",
            bd=0,
            padx=10,
            font=("Segoe UI", 10, "bold"),
            activebackground="red",
            activeforeground="white"
        )
        close_button.pack(side="right")

        # Make window draggable
        def start_move(event):
            popup.x = event.x
            popup.y = event.y

        def do_move(event):
            x = event.x_root - popup.x
            y = event.y_root - popup.y
            popup.geometry(f"+{x}+{y}")

        title_bar.bind("<Button-1>", start_move)
        title_bar.bind("<B1-Motion>", do_move)

        # --- GIF display ---
        gif_label = tk.Label(popup, bg=POPUP_COLOR)
        gif_label.pack(pady=10)

        try:
            gif = Image.open(GIF_PATH)
            frames = [ImageTk.PhotoImage(frame.copy().resize((250, 250), Image.Resampling.LANCZOS)) for frame in ImageSequence.Iterator(gif)]
            print(f"[INFO] Loaded {len(frames)} frames from GIF.")

            def animate(counter):
                frame = frames[counter]
                gif_label.configure(image=frame)
                gif_label.image = frame
                popup.after(100, lambda: animate((counter + 1) % len(frames)))

            animate(0)
        except Exception as e:
            print(f"[ERROR] Failed to load GIF: {e}")
            tk.Label(popup, text="[GIF failed to load]", bg=POPUP_COLOR, fg="red").pack()

        # --- Reminder Text ---
        tk.Label(
            popup,
            text="Hi Cutie 🤗 !!\nGive your eyes a break.\nBlink slowly a few times.\n\nAnd Look 20 Feet away....",
            font=("Segoe UI Emoji", 12, "bold"),
            bg=POPUP_COLOR,
            fg=TEXT_COLOR,
            justify="center"
        ).pack(pady=10)

        # --- Auto-close ---
        popup.after(DISPLAY_DURATION * 1000, lambda: self.close_popup(popup))

    def close_popup(self, popup):
        if popup.winfo_exists():
            print(f"[INFO] Closing popup window after {DISPLAY_DURATION} seconds.")
            popup.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = BlinkNotifier(root)
    root.mainloop()

"""
To build the exe file:
pyinstaller --noconfirm --onefile --windowed --icon=icon.ico --add-data "tenor.gif;." eye-blinker.py

"""