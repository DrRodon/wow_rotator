import time
import random
import pydirectinput
from PIL import ImageGrab
import keyboard
import sys
import threading
import tkinter as tk
from pystray import Icon, Menu, MenuItem
from PIL import Image, ImageDraw, ImageTk
import json
import os
import urllib.request

try:
    from interception import Interception
    from interception.constants import KeyFlag
    from interception.strokes import KeyStroke
    INTERCEPTION_AVAILABLE = True
except ImportError:
    INTERCEPTION_AVAILABLE = False

# Ścieżka do pliku konfiguracyjnego
if getattr(sys, 'frozen', False):
    APPLICATION_PATH = os.path.dirname(sys.executable)
else:
    APPLICATION_PATH = os.path.dirname(os.path.abspath(__file__))

CONFIG_PATH = os.path.join(APPLICATION_PATH, "config.json")

def load_config():
    default = {"x": 40, "y": 40, "defensives_enabled": True, "interrupts_enabled": True, "healing_enabled": True, "healing_threshold": 75, "ui_state": 1, "toggle_key": "f8"}
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as f:
                config = json.load(f)
                for k, v in default.items():
                    if k not in config: config[k] = v
                return config
        except: pass
    return default

def save_config(x, y, def_en, int_en, heal_en, heal_thr, ui_state, toggle_key):
    try:
        with open(CONFIG_PATH, 'w') as f:
            json.dump({
                "x": x, "y": y, 
                "defensives_enabled": def_en, 
                "interrupts_enabled": int_en, 
                "healing_enabled": heal_en,
                "healing_threshold": heal_thr,
                "ui_state": ui_state,
                "toggle_key": toggle_key
            }, f)
    except: pass

SCAN_WIDTH = 1000 # Zwiększono zasięg skanowania (DPI / 4K)
debug_snapshot_done = False

ID_TO_KEY = {
    1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 
    6: '6', 7: '7', 8: '8', 9: '9', 10: '0', 
    11: '-', 12: '=',
    20: 'a', 21: 'b', 22: 'c', 23: 'd', 24: 'e', 25: 'f', 26: 'g', 27: 'h', 28: 'i', 29: 'j', 
    30: 'k', 31: 'l', 32: 'm', 33: 'n', 34: 'o', 35: 'p', 36: 'q', 37: 'r', 38: 's', 39: 't', 
    40: 'u', 41: 'v', 42: 'w', 43: 'x', 44: 'y', 45: 'z',
    50: 'f1', 51: 'f2', 52: 'f3', 53: 'f4', 54: 'f5', 55: 'f6', 
    56: 'f7', 57: 'f8', 58: 'f9', 59: 'f10', 60: 'f11', 61: 'f12',
    70: 'space', 71: 'tab',
    80: 'middle', 81: 'x1', 82: 'x2'
}

class InputManager:
    def __init__(self):
        self.active = False
        self.device = None
        if INTERCEPTION_AVAILABLE:
            try:
                self.context = Interception()
                for i in range(20):
                    if self.context.is_keyboard(i):
                        self.device = i
                        self.active = True
                        print(f"INFO: Wykryto sterownik Interception (ID: {i}). Hardware Mode ACTIVE.")
                        break
            except Exception as e:
                print(f"INFO: Interception Init Failed (expected if driver not installed): {e}")
        
    def _get_interception_key(self, key_name):
        mapping = {
            '1': 0x02, '2': 0x03, '3': 0x04, '4': 0x05, '5': 0x06,
            '6': 0x07, '7': 0x08, '8': 0x09, '9': 0x0A, '0': 0x0B,
            '-': 0x0C, '=': 0x0D, 'space': 0x39, 'tab': 0x0F,
            'q': 0x10, 'w': 0x11, 'e': 0x12, 'r': 0x13, 't': 0x14,
            'y': 0x15, 'u': 0x16, 'i': 0x17, 'o': 0x18, 'p': 0x19,
            'a': 0x1E, 's': 0x1F, 'd': 0x20, 'f': 0x21, 'g': 0x22,
            'h': 0x23, 'j': 0x24, 'k': 0x25, 'l': 0x26,
            'z': 0x2C, 'x': 0x2D, 'c': 0x2E, 'v': 0x2F, 'b': 0x30,
            'n': 0x31, 'm': 0x32,
            'f1': 0x3B, 'f2': 0x3C, 'f3': 0x3D, 'f4': 0x3E, 'f5': 0x3F,
            'f6': 0x40, 'f7': 0x41, 'f8': 0x42, 'f9': 0x43, 'f10': 0x44,
            'shift': 0x2A, 'ctrl': 0x1D, 'alt': 0x38
        }
        return mapping.get(key_name.lower())

    def press(self, key_name, mods=[]):
        if self.active:
            try:
                clash_keys = ['shift', 'ctrl', 'alt']
                restorable_codes = []
                for k in clash_keys:
                    if keyboard.is_pressed(k) and k not in mods:
                        code = self._get_interception_key(k)
                        if code:
                            self.context.send(self.device, KeyStroke(code, KeyFlag.KEY_UP))
                            restorable_codes.append(code)

                for m in mods:
                    code = self._get_interception_key(m)
                    if code: self.context.send(self.device, KeyStroke(code, KeyFlag.KEY_DOWN))
                
                code = self._get_interception_key(key_name)
                if code:
                    self.context.send(self.device, KeyStroke(code, KeyFlag.KEY_DOWN))
                    time.sleep(random.uniform(0.015, 0.035))
                    self.context.send(self.device, KeyStroke(code, KeyFlag.KEY_UP))
                
                for m in reversed(mods):
                    code = self._get_interception_key(m)
                    if code: self.context.send(self.device, KeyStroke(code, KeyFlag.KEY_UP))

                for code in restorable_codes:
                    self.context.send(self.device, KeyStroke(code, KeyFlag.KEY_DOWN))

                return
            except Exception as e:
                print(f"DEBUG: Interception send failed: {e}")
                pass
        
        physical_mods = []
        for m in ['shift', 'ctrl', 'alt']:
            if keyboard.is_pressed(m): physical_mods.append(m)
        to_release = [m for m in physical_mods if m not in mods]
        for m in to_release: pydirectinput.keyUp(m)
        for m in mods: pydirectinput.keyDown(m)
        
        if key_name in ['middle', 'x1', 'x2']:
            pydirectinput.mouseDown(button=key_name)
            time.sleep(random.uniform(0.045, 0.085))
            pydirectinput.mouseUp(button=key_name)
        else:
            pydirectinput.press(key_name)
            
        for m in reversed(mods): pydirectinput.keyUp(m)
        for m in to_release:
            if keyboard.is_pressed(m): pydirectinput.keyDown(m)

conf = load_config()
input_manager = InputManager()
active = False
defensives_enabled = conf["defensives_enabled"]
interrupts_enabled = conf["interrupts_enabled"]
healing_enabled = conf.get("healing_enabled", True)
healing_threshold = conf.get("healing_threshold", 75)
ui_state = conf["ui_state"]
current_toggle_key = conf.get("toggle_key", "f8")
global_is_dk = False
running = True
tray_icon = None
last_action = "Waiting for data..."
spell_history = []

def create_icon_image(color):
    image = Image.new('RGB', (64, 64), color)
    draw = ImageDraw.Draw(image)
    draw.rectangle((16, 16, 48, 48), fill='white')
    return image

def create_shield_image(color):
    img = Image.new('RGBA', (20, 20), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    points = [(4, 2), (16, 2), (16, 10), (10, 18), (4, 10)]
    draw.polygon(points, fill=color, outline="white")
    return ImageTk.PhotoImage(img)

def create_lightning_image(color):
    img = Image.new('RGBA', (20, 20), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    points = [(11, 2), (15, 8), (11, 8), (13, 18), (7, 10), (11, 10), (9, 2)]
    draw.polygon(points, fill=color, outline="white")
    return ImageTk.PhotoImage(img)

def on_exit(icon, item):
    global running
    running = False
    icon.stop()
    sys.exit()

def start_tray():
    global active, tray_icon
    menu = Menu(MenuItem('Exit', on_exit))
    tray_icon = Icon("WoWRotator", create_icon_image('red'), menu=menu)
    tray_icon.run()

spell_cache = {}
icon_cache = {}
ICONS_DIR = os.path.join(APPLICATION_PATH, "icons")
if not os.path.exists(ICONS_DIR): os.makedirs(ICONS_DIR)

def get_fallback_image(color, size):
    img = Image.new('RGB', (size, size), color)
    draw = ImageDraw.Draw(img)
    return img

fallback_large_img = get_fallback_image('#333333', 48)
fallback_small_img = get_fallback_image('#333333', 24)
fallback_large = None
fallback_small = None

def ensure_icon_loaded(spell_id, icon_name):
    if not icon_name: return
    icon_path = os.path.join(ICONS_DIR, f"{icon_name}.jpg")
    if not os.path.exists(icon_path):
        try:
            url = f"https://wow.zamimg.com/images/wow/icons/large/{icon_name}.jpg"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3) as resp, open(icon_path, 'wb') as f:
                f.write(resp.read())
        except Exception: return
            
    if os.path.exists(icon_path):
        try:
            img = Image.open(icon_path).convert("RGBA")
            img_large = img.resize((48, 48), Image.Resampling.LANCZOS)
            img_small = img.resize((24, 24), Image.Resampling.LANCZOS)
            icon_cache[spell_id] = {
                'large': ImageTk.PhotoImage(img_large),
                'small': ImageTk.PhotoImage(img_small)
            }
        except Exception: pass

def get_spell_data_api(spell_id):
    if spell_id <= 0: return "Unknown", None
    if spell_id in spell_cache:
        return spell_cache[spell_id], icon_cache.get(spell_id)
        
    spell_cache[spell_id] = f"Spell #{spell_id}"
    icon_cache[spell_id] = {'large': fallback_large, 'small': fallback_small}
    
    def fetch():
        try:
            req = urllib.request.Request(f"https://nether.wowhead.com/tooltip/spell/{spell_id}", headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=3) as response:
                data = json.loads(response.read().decode('utf-8'))
                if "name" in data: spell_cache[spell_id] = data["name"]
                if "icon" in data: ensure_icon_loaded(spell_id, data["icon"])
        except Exception: pass

    threading.Thread(target=fetch, daemon=True).start()
    return spell_cache[spell_id], icon_cache.get(spell_id)

def get_action_from_y(img, y):
    # Wyszukiwanie "Anchor" (niebieskiego) i "End" (zielonego)
    start_x = -1
    end_x = -1
    for x in range(SCAN_WIDTH):
        p = img.getpixel((x, y))
        # Sprawdzamy czy niebieski dominuje (odpornosc na wplyw tla)
        if start_x == -1 and p[2] > 100 and p[2] > p[0] + 50 and p[2] > p[1] + 50:
            start_x = x
        # Szukamy zielonego końca za niebieskim start_x
        if start_x != -1 and end_x == -1 and x > start_x + 5:
            if p[1] > 100 and p[1] > p[0] + 50 and p[1] > p[2] + 50:
                end_x = x
                break
            
    if start_x == -1 or end_x == -1: return None
    
    # Core.lua: 1 (Blue) i 43 (Green). Dystans = 42 blokow.
    p_width = (end_x - start_x) / 42.0
    if p_width <= 0: return None
    
    def luma(p): return p[0]*0.299 + p[1]*0.587 + p[2]*0.114
    
    # Zbieranie probek pomiedzy anchorami (41 probek, indexy 2 do 42)
    samples = []
    for i in range(1, 42):
        sample_x = start_x + int((i + 0.5) * p_width)
        if sample_x >= SCAN_WIDTH: break
        samples.append(img.getpixel((sample_x, y)))
        
    if len(samples) < 41: return None
    
    # Dynamiczny prog jasnosci bazujacy na kalibracji: blok Bialy i Czarny
    lum_1 = luma(samples[0])
    lum_0 = luma(samples[1])
    
    # Jesli miedzy bialym a czarnym jest za mala roznica, szum / cos nas zaslania
    if lum_1 - lum_0 < 30: return None
    
    threshold = (lum_1 + lum_0) / 2
    bits = [1 if luma(sp) > threshold else 0 for sp in samples]
    
    def read_int(start, length):
        v = 0
        for i in range(length):
            v |= (bits[start + i] << i)
        return v
        
    act_type = read_int(2, 3)
    
    if act_type == 7:
        # Ten rzad definiuje szerokosc czerwonego Paska Statusu HP (35 blokow od index 6 do 40)
        # Próbujemy odczytać bit klasy (DK) na indexie 5 (hpRow[7])
        is_dk_bit = bits[5]
        
        # Logowanie wyłączone (działa poprawnie)
        # print(f"DEBUG: ROW {y} TYPE 7 | DKBit: {is_dk_bit} | L1:{lum_1:.0f} L0:{lum_0:.0f} Thr:{threshold:.1f}")

        
        red_count = 0
        for i in range(6, 41):
            if i >= len(samples): break
            p = samples[i]
            # Red dominujacy
            if p[0] > 150 and p[1] < 100 and p[2] < 100:
                red_count += 1
        hp_percent = red_count / 35.0
        is_dk = (is_dk_bit == 1)
        
        # if is_dk: print(f"DEBUG: Wykryto DK na rzedzie {y}!")
        
        return {"act_type": 7, "hp": hp_percent, "is_dk": is_dk}
        
    mod_mask = read_int(5, 3)
    key_id   = read_int(8, 8)
    spell_id = read_int(16, 24)
    hb       = read_int(40, 1)
    
    name, _ = get_spell_data_api(spell_id)
    key_name = ID_TO_KEY.get(key_id)
    
    if key_name and act_type > 0:
        return {
            "spell_name": name,
            "key_name": key_name,
            "mod_mask": mod_mask,
            "spell_id": spell_id,
            "act_type": act_type
        }
    return None

def start_gui():
    global active, last_action, defensives_enabled, interrupts_enabled, ui_state, fallback_large, fallback_small
    config = load_config()
    defensives_enabled = config.get("defensives_enabled", True)
    interrupts_enabled = config.get("interrupts_enabled", True)
    ui_state = config.get("ui_state", 1)
    
    root = tk.Tk()
    root.title("WoWRotator")
    
    fallback_large = ImageTk.PhotoImage(fallback_large_img)
    fallback_small = ImageTk.PhotoImage(fallback_small_img)
    
    # State heights/geometries: 0 -> 38, 1 -> 82, 2 -> 190, 3 -> Icon mode
    heights = {0: 38, 1: 82, 2: 190}
    curr_h = heights.get(ui_state, 82)
    current_geom = f"260x86" if ui_state == 3 else f"260x{curr_h}"
    root.geometry(f"{current_geom}+{config['x']}+{config['y']}")
    root.attributes("-topmost", True)
    root.overrideredirect(True)
    root.configure(bg='#121212')
    
    main_frame = tk.Frame(root, bg='#1a1a1a', highlightthickness=1, highlightbackground='#333333')
    main_frame.pack(expand=True, fill="both", padx=2, pady=2)

    # State Button (Left)
    state_btn = tk.Label(main_frame, text="▼", bg="#1a1a1a", fg="#666666", font=("Segoe UI", 10), cursor="hand2")
    state_btn.place(x=5, y=5)

    status_label = tk.Label(main_frame, text="ROTATOR PAUSED", bg="#1a1a1a", fg="#ff5555", font=("Segoe UI", 11, "bold"))
    status_label.pack(pady=(2, 0))
    
    history_frame = tk.Frame(main_frame, bg="#1a1a1a")
    history_frame.pack(fill="both", expand=True, padx=5)
    
    history_labels = []
    for i in range(6):
        lbl = tk.Label(history_frame, text="", bg="#1a1a1a", fg="#00d4ff", font=("Segoe UI", 9, "bold"), anchor="w", justify="left")
        history_labels.append(lbl)
        
    icon_mode_frame = tk.Frame(main_frame, bg="#1a1a1a")
    current_icon_lbl = tk.Label(icon_mode_frame, bg="#1a1a1a")
    current_icon_lbl.place(x=5, y=0, width=48, height=48)
    current_key_lbl = tk.Label(icon_mode_frame, text="", bg="#1a1a1a", fg="yellow", font=("Segoe UI", 8, "bold"))
    current_key_lbl.place(x=5, y=33)
    
    hist_icons_lbls = []
    for i in range(5):
        lbl = tk.Label(icon_mode_frame, bg="#1a1a1a")
        lbl.place(x=68 + i*34, y=12, width=24, height=24)
        hist_icons_lbls.append(lbl)

    settings_open = False
    
    # Gear Button (Right)
    settings_btn = tk.Label(main_frame, text="⚙", bg="#1a1a1a", fg="#666666", font=("Segoe UI", 12), cursor="hand2")
    settings_btn.place(relx=1.0, x=-5, y=4, anchor='ne')

    # Settings Frame (hidden by default)
    settings_frame = tk.Frame(main_frame, bg="#1a1a1a")
    
    # Interrupts Toggle
    int_var = tk.BooleanVar(value=interrupts_enabled)
    def toggle_int_v():
        global interrupts_enabled
        interrupts_enabled = int_var.get()
        save_current_config()
    tk.Checkbutton(settings_frame, text="Interrupts", variable=int_var, command=toggle_int_v, 
                   bg="#1a1a1a", fg="#50fa7b", selectcolor="#282a36", font=("Segoe UI", 9)).pack(anchor="w", padx=10)

    # Defensives Toggle
    def_var = tk.BooleanVar(value=defensives_enabled)
    def toggle_def_v():
        global defensives_enabled
        defensives_enabled = def_var.get()
        save_current_config()
    tk.Checkbutton(settings_frame, text="Defensives", variable=def_var, command=toggle_def_v,
                   bg="#1a1a1a", fg="#50fa7b", selectcolor="#282a36", font=("Segoe UI", 9)).pack(anchor="w", padx=10)

    # --- Healing Section (Grouped for dynamic visibility) ---
    healing_options_frame = tk.Frame(settings_frame, bg="#1a1a1a")
    
    heal_var = tk.BooleanVar(value=healing_enabled)
    def toggle_heal_v():
        global healing_enabled
        healing_enabled = heal_var.get()
        save_current_config()
    tk.Checkbutton(healing_options_frame, text="Healing (DS)", variable=heal_var, command=toggle_heal_v,
                   bg="#1a1a1a", fg="#50fa7b", selectcolor="#282a36", font=("Segoe UI", 9)).pack(anchor="w", padx=10)

    hp_thr_var = tk.IntVar(value=healing_threshold)
    def update_hp_thr(val):
        global healing_threshold
        healing_threshold = int(val)
        save_current_config()
    
    tk.Label(healing_options_frame, text="Healing HP %:", bg="#1a1a1a", fg="#00d4ff", font=("Segoe UI", 8)).pack(anchor="w", padx=10)
    hp_slider = tk.Scale(healing_options_frame, from_=0, to=100, orient="horizontal", variable=hp_thr_var, 
                         command=update_hp_thr, bg="#1a1a1a", fg="white", highlightthickness=0,
                         troughcolor="#333333", activebackground="#50fa7b")
    hp_slider.pack(fill="x", padx=20)
    
    # Pakujemy healing domyslnie (zostanie zarzadzane w update())
    healing_options_frame.pack(fill="x")
    # -------------------------------------------------------

    # Toggle Key Rebind
    tk.Label(settings_frame, text="Toggle Bot Key:", bg="#1a1a1a", fg="#00d4ff", font=("Segoe UI", 8)).pack(anchor="w", padx=10, pady=(10, 0))
    key_btn = tk.Button(settings_frame, text=current_toggle_key.upper(), bg="#282a36", fg="white", 
                        relief="flat", font=("Segoe UI", 9, "bold"))
    key_btn.pack(fill="x", padx=20, pady=5)

    def on_key_press(event):
        global current_toggle_key
        new_key = event.keysym.lower()
        if new_key == "escape":
            key_btn.config(text=current_toggle_key.upper(), bg="#282a36")
        else:
            current_toggle_key = new_key
            key_btn.config(text=current_toggle_key.upper(), bg="#282a36")
            register_toggle_key(current_toggle_key)
            save_current_config()
        root.unbind("<Key>")
        root.config(cursor="")

    def start_rebind():
        key_btn.config(text="PRESS ANY KEY...", bg="#ff5555")
        root.config(cursor="wait")
        root.bind("<Key>", on_key_press)

    key_btn.config(command=start_rebind)

    tk.Label(settings_frame, text="Powered by Krytos", bg="#1a1a1a", fg="#777777", font=("Segoe UI", 7, "italic")).pack(side="bottom", pady=5)

    def save_current_config():
        save_config(root.winfo_x(), root.winfo_y(), defensives_enabled, interrupts_enabled, 
                    healing_enabled, healing_threshold, ui_state, current_toggle_key)

    def adjust_window_size():
        root.update_idletasks()
        req_h = main_frame.winfo_reqheight()
        root.geometry(f"260x{req_h}")

    def toggle_settings(event=None):
        nonlocal settings_open
        settings_open = not settings_open
        if settings_open:
            history_frame.pack_forget()
            icon_mode_frame.pack_forget()
            settings_frame.pack(fill="both", expand=True, pady=5)
            adjust_window_size()
            settings_btn.config(fg="#50fa7b")
        else:
            settings_frame.pack_forget()
            settings_btn.config(fg="#666666")
            apply_ui_state()

    settings_btn.bind("<Button-1>", toggle_settings)

    def apply_ui_state():
        status_label.pack(pady=(2, 0))
        
        if ui_state == 3:
            root.geometry(f"260x86")
            history_frame.pack_forget()
            icon_mode_frame.pack(fill="both", expand=True)
        else:
            icon_mode_frame.pack_forget()
            h = heights.get(ui_state, 82)
            root.geometry(f"260x{h}")
            if ui_state == 0:
                history_frame.pack_forget()
            else:
                history_frame.pack(fill="both", expand=True, padx=5)
                for i, lbl in enumerate(history_labels):
                    if ui_state == 1:
                        if i == 0: lbl.pack(fill="x", pady=2)
                        else: lbl.pack_forget()
                    else: # ui_state == 2
                        lbl.pack(fill="x", pady=1)
        
        save_current_config()

    def next_state(event=None):
        global ui_state
        ui_state = (ui_state + 1) % 4
        apply_ui_state()

    state_btn.bind("<Button-1>", next_state)

    def update():
        if not running: root.destroy(); return
        status_label.config(text="ROTATOR ACTIVE" if active else "ROTATOR PAUSED", fg="#50fa7b" if active else "#ff5555")
        if tray_icon: tray_icon.icon = create_icon_image('green' if active else 'red')
        
        if ui_state > 0 and ui_state < 3:
            for i in range(6):
                if i < len(spell_history):
                    spell = spell_history[i]
                    txt = f"{spell['name']}\n[{spell['key']}]" if ui_state == 1 else f"• {spell['name']} [{spell['key']}]"
                    history_labels[i].config(text=txt)
                else: history_labels[i].config(text="")
        elif ui_state == 3:
            # Tryma 3: Icon View (z automatycznym pobieraniem ikon)
            if spell_history:
                curr = spell_history[0]
                _, icons = get_spell_data_api(curr["id"])
                current_icon_lbl.config(image=icons['large'] if icons else fallback_large)
                current_key_lbl.config(text=curr["key"])
                
                for i in range(1, 6):
                    if i < len(spell_history):
                        h_spell = spell_history[i]
                        _, h_icons = get_spell_data_api(h_spell["id"])
                        hist_icons_lbls[i-1].config(image=h_icons['small'] if h_icons else fallback_small)
                    else:
                        hist_icons_lbls[i-1].config(image='')
        
        # Dynamiczna widocznosc sekcji leczenia
        is_visible = healing_options_frame.winfo_manager() != ""
        if global_is_dk:
            if not is_visible and settings_open:
                # print("DEBUG: Pokazuje panel leczenia (DK)")
                children = settings_frame.winfo_children()
                if len(children) >= 2:
                    healing_options_frame.pack(fill="x", after=children[1])
                else:
                    healing_options_frame.pack(fill="x")
                adjust_window_size()
        else:
            if is_visible:
                # print("DEBUG: Ukrywam panel leczenia (nie-DK)")
                healing_options_frame.pack_forget()
                if settings_open: adjust_window_size()

        root.after(100, update)

    def start_move(event): root.x = event.x; root.y = event.y
    def stop_move(event): root.x = None; root.y = None; save_current_config()
    def on_move(event):
        dx, dy = event.x - root.x, event.y - root.y
        root.geometry(f"+{root.winfo_x() + dx}+{root.winfo_y() + dy}")

    main_frame.bind("<Button-1>", start_move)
    main_frame.bind("<ButtonRelease-1>", stop_move)
    main_frame.bind("<B1-Motion>", on_move)

    apply_ui_state()
    update()
    root.mainloop()

def toggle():
    global active
    active = not active
    if not active:
        for key in ['shift', 'ctrl', 'alt']: pydirectinput.keyUp(key)

def listen_for_toggle():
    global running
    last_pressed = False
    while running:
        # Sprawdzaj co 10ms - ultra responsywnosc
        is_p = keyboard.is_pressed(current_toggle_key)
        if is_p and not last_pressed:
            toggle()
            last_pressed = True
        elif not is_p:
            last_pressed = False
        time.sleep(0.01)

threading.Thread(target=start_gui, daemon=True).start()
threading.Thread(target=start_tray, daemon=True).start()
threading.Thread(target=listen_for_toggle, daemon=True).start()

def execute_action(action, prefix_label):
    global last_action, spell_history
    sn, kn, mm = action["spell_name"], action["key_name"], action["mod_mask"]
    bm = []
    if mm & 1: bm.append('shift')
    if mm & 2: bm.append('ctrl')
    if mm & 4: bm.append('alt')
    ms = '+'.join([m.upper() for m in bm])
    
    key_str = f"{ms + '+' if ms else ''}{kn.upper()}"
    last_action = f"Casting: {sn}\n[{key_str}]"
    
    # Update spell history dedup by explicit spell_id to prevent transient name-fetch dupes
    new_spell = {"name": sn, "key": key_str, "id": action.get("spell_id", 0)}
    if not spell_history or spell_history[0]["id"] != new_spell["id"] or spell_history[0]["key"] != new_spell["key"]:
        spell_history.insert(0, new_spell)
        spell_history = spell_history[:6]
        
    input_manager.press(kn, bm)
    time.sleep(random.uniform(0.01, 0.03))

last_def_name, def_start_time = None, 0

try:
    global_hp = 1.0
    print(f"INFO: Rozpoczeto petle skanowania. Czekam na dane (Klawisz: {current_toggle_key.upper()})")
    
    while running:
        # GŁÓWNA PĘTLA ROBOCZA
        img = ImageGrab.grab(bbox=(0, 0, SCAN_WIDTH, 70))
        
        # Zapisz jeden kadr do debugowania (raz na start)
        if not debug_snapshot_done:
            try:
                img.save("debug_scan.png")
                print("INFO: Zapisano zrzut ekranu do debug_scan.png dla diagnostyki.")
                debug_snapshot_done = True
            except: pass

        found_actions, seen_uids = [], set()
        for y in range(70): 
            res = get_action_from_y(img, y)
            if res:
                if res.get("act_type") == 7:
                    global_hp = res.get("hp", 1.0)
                    if "is_dk" in res:
                        if global_is_dk != res["is_dk"]:
                            print(f"INFO: Wykryto zmiane klasy! DK Mode: {res['is_dk']}")
                        global_is_dk = res["is_dk"]
                
                # Akcje (czary) zbieramy tylko jeśli bot jest aktywny
                elif active and (res.get("spell_id", 0) > 0 or res.get("key_name")):
                    uid = (res["key_name"], res["spell_name"], res["spell_id"])
                    if uid not in seen_uids:
                        found_actions.append(res)
                        seen_uids.add(uid)
        
        if active:
            inta, defa, offa = None, [], None
            for a in found_actions:
                # ====== TWW SecretNumbers Bypass (Death Strike) ======
                if a["act_type"] == 2 and a.get("spell_id") == 49998:
                    if global_is_dk:
                        if not healing_enabled or global_hp > healing_threshold / 100.0:
                            continue # HP powyzej progu lub leczenie wylaczone!
                # ====================================================
            
                if a["act_type"] == 5: inta = a
                elif a["act_type"] == 2: defa.append(a)
                elif a["act_type"] == 1: offa = a

            # Wykonanie akcji tylko gdy aktywny
            if interrupts_enabled and inta: execute_action(inta, "")
            
            if def_actions := (defa if defensives_enabled else []):
                curr_dn = def_actions[0]["spell_name"]
                if curr_dn != last_def_name:
                    last_def_name, def_start_time = curr_dn, time.time()
                if time.time() - def_start_time > 0.8 and offa:
                    execute_action(offa, ""); def_start_time = time.time()
                else:
                    execute_action(def_actions[0], "")
            elif offa:
                last_def_name = None
                execute_action(offa, "")
        else:
            # Oszczędność CPU na pauzie
            time.sleep(0.1)
        
        time.sleep(0.01)
except KeyboardInterrupt: pass
