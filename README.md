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

## Setup Instructions

### Prerequisites
1. **Interception Driver**: Required for hardware-level input. [Download and install the Interception driver](https://github.com/oblitum/Interception).
2. **Python 3.10+**: Ensure Python is in your PATH.
3. **Required Addons**: `JustAssistedCombat` (JAC) for rotation suggestions.

### Installation
1. Copy the `PixelRotator` folder to your `World of Warcraft/_retail_/Interface/Addons` directory.
2. Launch WoW and enable the addon (`/reload`).
3. Set your Game Resolution to Windowed Mode (Maximized).

### Running the Bot
1. Open a terminal in the `PythonRotator` directory.
2. Run `pip install -r requirements.txt` (if applicable) or ensure you have `opencv-python`, `numpy`, `PIL`, and `pywin32`.
3. Launch the bot: `python bot.py`.
4. **F8**: Toggle the rotation assistant ON/OFF.
5. **Gear Icon**: Access advanced settings (Healing thresholds, interrupts).

## Disclaimer
Use at your own risk. Automating gameplay may violate Blizzard's Terms of Service. This project is for educational purposes.

---
**Powered by Krytos**
