import time
from interception import Interception
from interception.constants import KeyFlag
from interception.strokes import KeyStroke

def check_interception():
    try:
        c = Interception()
        print("--- Interception Diagnostics ---")
        print("1. Context initialized successfully.")
        
        found_keyboards = []
        for i in range(10): # Max keyboards is 10
            if c.is_keyboard(i):
                # Checking if device exists by some mean? 
                # The library opens handles to all 20 devices in __init__.
                # But how do we know if a keyboard is actually connected?
                # Actually, Interception driver usually has 10 keyboard 'slots'.
                found_keyboards.append(i)
        
        print(f"2. Potential keyboard IDs: {found_keyboards}")
        
        # In this library, _using_keyboard defaults to 1.
        target_id = 0 # Try the first one
        
        print(f"3. Testing key press (SPACE) on ID {target_id} in 3 seconds...")
        time.sleep(3)
        
        # Space key scancode is 0x39
        # KeyFlag.KEY_DOWN is 0x00, KeyFlag.KEY_UP is 0x01
        
        stroke_down = KeyStroke(0x39, KeyFlag.KEY_DOWN)
        stroke_up = KeyStroke(0x39, KeyFlag.KEY_UP)
        
        c.send(target_id, stroke_down)
        time.sleep(0.05)
        c.send(target_id, stroke_up)
        
        print("4. Key sent. (Look for a space in any text field or WoW).")
        
    except Exception as e:
        print(f"--- Interception Diagnostics ERROR ---")
        import traceback
        traceback.print_exc()
        print(f"Failed to initialize Interception: {e}")

if __name__ == "__main__":
    check_interception()
