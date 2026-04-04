# WoW Rotator (Retail)

An advanced World of Warcraft (Retail) combat rotation assistant using pixel-based data extraction and kernel-level input isolation.

## Features
- **Unobtrusive**: Uses standard WoW UI/Addon API (no memory reading).
- **Safe Input**: Specifically designed to work with the **Interception driver** for hardware-isolated, conflict-free keypresses.
- **Dynamic UI**: Auto-adjusts to character class (e.g., Death Knight specific healing logic).
- **Customizable**: Adjustable health thresholds for automated healing (Death Strike).

## Components

### 1. PixelRotator (Addon)
A custom Lua addon that exposes combat data (GCD, spell state, health, class info) via colored pixels at the top-left of the screen.

### 2. PythonRotator (Bot)
A Python application that:
1. Scans the screen for `PixelRotator` data.
2. Processes rotation logic via JustAC recommendations.
3. Sends inputs through the `Interception` driver.

## Prerequisites

### 1. Python (Required)
The core of the logic depends on Python.
- **Download**: [Download Python 3.10+](https://www.python.org/downloads/)
- **Installation**: During install, **MUST** check the box "**Add Python to PATH**".
- **Dependencies**: Open a terminal in the `PythonRotator` folder and run:
  ```bash
  pip install opencv-python numpy Pillow pywin32
  ```

### 2. JustAssistedCombat (JAC) (Required)
The bot uses JAC to get combat recommendations.
- **Download**: Find it on **CurseForge** or GitHub.
- **Configuration**: Ensure the "Show Icons" option is enabled in JAC settings. 
- **Crucial Settings** (under `Standard Queue` -> `Defensive Display`):
  - **Show Defensive Icons**: Enabled
  - **Defensive Visibility**: `When Health Low`
  - **Max Icons**: `1`
  - **Icon Scale**: `0.5`
  - **Highlight Mode**: `All Glows`
  - **Show Health Bars**: Enabled

### 3. Interception Driver (Optional - Highly Recommended)
The bot works by default using software input simulation. However, for seamless, conflict-free automation (allowing you to use your keyboard normally while the bot is active):
- **Download**: [Interception Driver](https://github.com/oblitum/Interception)
- **Installation**: Run `install-interception.exe /install` as administrator and **restart your PC**.
- The bot will automatically detect the driver on launch and enable **Hardware Mode**.

## Installation & Launch

1. **Addon Setup**: Copy the `PixelRotator` folder to your `World of Warcraft/_retail_/Interface/Addons` directory.
2. **Game Settings**: 
   - Set Display Mode to **Windowed Mode (Maximized)**.
   - Type `/reload` in-game to load the addon.
3. **Launch the Bot**:
   - Navigate to `PythonRotator`.
   - Run `python bot.py`.
4. **Usage**:
   - **Draggable Window**: The bot interface can be moved anywhere on your screen (click and drag).
   - **UI Mode (Left Arrow)**: Click the arrow on the left to cycle through 4 display modes:
     - **Status Only**: Shows only whether the rotator is active or paused.
     - **Next Spell**: Displays only the next recommended action.
     - **Full History**: Shows the next recommended action and a history of recent proposals.
     - **Icon Mode**: Graphical representation of the history using official WoW icons (automatically downloaded to the `/icons` folder).
   - **Toggle Assistant**: Press **F8** by default (Can be rebound in settings).
   - **Settings (Gear Icon)**:
     - **Interrupt Control**: Toggle automated spell interrupts.
     - **Defensive Rotation**: Enable/Disable automated defensive ability usage.
     - **Smart Healing (DK Only)**: Set precise health thresholds for automatic **Death Strike** execution.
     - **Hotkeys**: Rebind the global toggle hotkey to any key.

## Disclaimer
Use at your own risk. Automating gameplay may violate Blizzard's Terms of Service. This project is for educational purposes.

---
**Powered by Krytos**
