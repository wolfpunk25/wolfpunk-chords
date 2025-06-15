# WOLFPUNK Chord Machine

A CircuitPython-based MIDI chord machine built for the Adafruit MacroPad RP2040. Inspired by devices like the Pocket Audio HiChord, this custom firmware transforms the MacroPad into a powerful chord and arpeggiator performance tool with rich LED feedback and a dynamic OLED interface.

---

## 🔧 Required Libraries
Ensure your `lib/` directory on the CIRCUITPY drive contains the following CircuitPython libraries:

- `adafruit_display_text`
- `adafruit_macropad`
- `adafruit_midi`
- `adafruit_pixelbuf`

You can download these from the [Adafruit CircuitPython Bundle](https://circuitpython.org/libraries).

---

## 🚀 Setup Instructions
1. Copy `code.py` to the root of your CIRCUITPY drive.
2. Install the required libraries in a `lib` folder on CIRCUITPY.
3. Reboot the MacroPad or press Ctrl+D in the serial console.

Upon boot, you'll see:
- A **boot animation** with animated pixels and a "WOLFPUNK CHORDS" title.

---

## 🎹 How to Use
### 🔢 Keys 1–7 (Lit yellow):
- Trigger chord notes. Each key corresponds to a scale degree in the key.

### 🔘 Key Functions
- **Key 8**: Cycle through chord inversions (0, 1, 2)
- **Key 9**: Shift octave (-1, 0, +1)
- **Key 10**: Change arpeggiator mode (Off → Up → Down → Random)
- **Key 11**: Toggle Latch mode (Hold chords after release)
- **Key 12**: Toggle chord type (Major / Minor / Diminished)

### 🎛 Encoder
- Turn: Adjust key offset
- Press + Turn: Adjust BPM

### 💡 LED Feedback
- Keys 1–7: Yellow when idle, green when pressed or arpeggiated.
- Key 8: Red (brightness indicates inversion)
- Key 9: Blue (brightness indicates octave)
- Key 10: Orange (tempo pulse when arp active, dim when off)
- Key 11: Purple (bright = latch on, dim = off)
- Key 12: Green (brightness varies by chord type)

### 🖥 OLED Display
```
Chord: 60 64 67
Key: +1 | Oct: 0
Inv: 1 | Lt: 1 | Maj
Arp: Up | BPM: 120
```
- **Chord**: MIDI notes of the current chord  
- **Key**: Offset in semitones  
- **Oct**: Octave shift  
- **Inv**: Chord inversion  
- **Lt**: Latch (0 = Off, 1 = On)  
- **Maj**: Chord type  
- **Arp**: Arpeggiator mode  
- **BPM**: Tempo  

---

## 📦 License
GNU General Public License v3.0 (GPL-3.0). Created for creative MIDI exploration with the Adafruit MacroPad RP2040.

---

## 🐺 About
Developed by WOLFPUNK for expressive chord and performance interaction, ideal for live electronic music and generative composition.
