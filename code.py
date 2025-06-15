import time
import random
import displayio
import terminalio
import usb_midi
from adafruit_display_text import label
from adafruit_macropad import MacroPad
from adafruit_midi import MIDI
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff

# --- Initialization ---
macropad = MacroPad()
midi = MIDI(midi_out=usb_midi.ports[1], out_channel=0)

# --- Boot Animation ---
boot_group = displayio.Group()
boot_title = label.Label(terminalio.FONT, text="WOLFPUNK CHORDS", color=0xFFFFFF)
boot_title.y = 20
boot_status_static = label.Label(terminalio.FONT, text="Booting", color=0xFFFFFF)
boot_status_dynamic = label.Label(terminalio.FONT, text="", color=0xFFFFFF)
boot_status_static.y = 40
boot_status_dynamic.y = 40
boot_group.append(boot_title)
boot_group.append(boot_status_static)
boot_group.append(boot_status_dynamic)
macropad.display.root_group = boot_group

boot_title.x = (macropad.display.width - boot_title.bounding_box[2]) // 2
boot_status_static.x = (macropad.display.width - boot_status_static.bounding_box[2]) // 2
boot_status_dynamic.x = boot_status_static.x + boot_status_static.bounding_box[2] + 2

boot_colors = [(255, 0, 0), (255, 128, 0), (255, 255, 0), (0, 255, 0),
               (0, 255, 255), (0, 0, 255), (128, 0, 255), (255, 0, 255),
               (255, 0, 128), (128, 128, 128), (255, 255, 255), (100, 100, 100)]

start_time = time.monotonic()
while time.monotonic() - start_time < 2.0:
    elapsed = time.monotonic() - start_time
    dot_count = int((elapsed * 5) % 6)
    boot_status_dynamic.text = "." * dot_count
    for i in range(12):
        color_index = (i + int(elapsed * 10)) % len(boot_colors)
        macropad.pixels[i] = boot_colors[color_index]
    time.sleep(0.05)

macropad.pixels.fill((0, 0, 0))

# --- Constants ---
MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]
CHORD_TYPES = {
    "Maj": [0, 4, 7],
    "Min": [0, 3, 7],
    "Dim": [0, 3, 6]
}
ARPEGGIATOR_MODES = ["Off", "Up", "Down", "Rnd"]
CHORD_TYPE_COLORS = {
    "Maj": (0, 30, 0),
    "Min": (0, 100, 0),
    "Dim": (0, 255, 0)
}

# --- State Variables ---
base_key = 60
key_offset = 0
inversion = 0
octave_shift = 0
arpeggiator_mode = 0
bpm = 120
arp_step_time = 60 / (bpm * 2)
last_position = macropad.encoder
active_chords = {}
arpeggiators = {}
latch_mode = False
chord_type_names = list(CHORD_TYPES.keys())
chord_type_index = 0
last_pulse_time = 0
pulse_duration = 0.05
pulse_led_index = 9
arp_flash_decay = {}

# --- Display Setup ---
display_group = displayio.Group()
chord_label = label.Label(terminalio.FONT, text="Chord:", color=0xFFFFFF, x=0, y=5)
status_label = label.Label(terminalio.FONT, text="", color=0xFFFFFF, x=0, y=20)
inversion_label = label.Label(terminalio.FONT, text="", color=0xFFFFFF, x=0, y=35)
arp_label = label.Label(terminalio.FONT, text="", color=0xFFFFFF, x=0, y=50)
display_group.append(chord_label)
display_group.append(status_label)
display_group.append(inversion_label)
display_group.append(arp_label)
macropad.display.root_group = display_group

# --- Utility Functions ---
def update_status_label():
    status_label.text = f"Key: +{key_offset} | Oct: {octave_shift}"

def update_chord_label(chord):
    chord_str = " ".join(str(n) for n in chord)
    chord_label.text = f"Chord: {chord_str}"

def update_inversion_label():
    latch = 1 if latch_mode else 0
    chord_type = chord_type_names[chord_type_index]
    inversion_label.text = f"Inv: {inversion} | Lt: {latch} | {chord_type}"

def update_arp_label():
    mode = ARPEGGIATOR_MODES[arpeggiator_mode]
    arp_label.text = f"Arp: {mode} | BPM: {bpm}"

def update_inversion_led():
    brightness = [30, 100, 255][inversion]
    macropad.pixels[7] = (brightness, 0, 0)

def update_octave_led():
    colors = { -1: (0, 0, 50), 0: (0, 0, 150), 1: (0, 0, 255) }
    macropad.pixels[8] = colors[octave_shift]

def update_arp_led():
    if ARPEGGIATOR_MODES[arpeggiator_mode] == "Off":
        macropad.pixels[9] = (30, 10, 0)
    else:
        brightness = [10, 50, 150, 255][arpeggiator_mode]
        macropad.pixels[9] = (brightness, brightness // 2, 0)

def update_latch_led():
    macropad.pixels[10] = (100, 0, 100) if not latch_mode else (255, 0, 255)

def update_chord_type_led():
    chord_type = chord_type_names[chord_type_index]
    macropad.pixels[11] = CHORD_TYPE_COLORS[chord_type]

def compute_chord(index, extended=False):
    root = base_key + MAJOR_SCALE[(index + key_offset) % 7] + 12 * ((index + key_offset) // 7)
    intervals = CHORD_TYPES[chord_type_names[chord_type_index]]
    base_chord = [root + interval for interval in intervals]
    for i in range(inversion):
        base_chord[i] += 12
    base_chord = sorted(note + 12 * octave_shift for note in base_chord)
    if extended:
        return (base_chord + [note + 12 for note in base_chord])[:8]
    else:
        return base_chord

def shuffle_in_place(lst):
    for i in range(len(lst) - 1, 0, -1):
        j = int(random.random() * (i + 1))
        lst[i], lst[j] = lst[j], lst[i]

def update_arp_step_time():
    global arp_step_time
    arp_step_time = 60 / (bpm * 2)

def stop_all_notes():
    for chord in active_chords.values():
        for note in chord:
            midi.send(NoteOff(note, 0))
    active_chords.clear()
    for arp in arpeggiators.values():
        if arp["last_note"]:
            midi.send(NoteOff(arp["last_note"], 0))
    arpeggiators.clear()
    for i in range(7):
        macropad.pixels[i] = (255, 255, 0)
    update_chord_label([])

# --- Initial Setup ---
for i in range(7):
    macropad.pixels[i] = (255, 255, 0)
update_chord_label([])
update_status_label()
update_inversion_label()
update_arp_label()
update_inversion_led()
update_octave_led()
update_arp_led()
update_latch_led()
update_chord_type_led()
update_arp_step_time()

# --- Main Loop ---
last_arp_time = time.monotonic()

while True:
    event = macropad.keys.events.get()
    if event:
        key = event.key_number

        if key < 7:
            chord = compute_chord(key)
            arp_chord = compute_chord(key, extended=True)
            if event.pressed:
                if ARPEGGIATOR_MODES[arpeggiator_mode] == "Off":
                    for note in chord:
                        midi.send(NoteOn(note, 120))
                    active_chords[key] = chord
                else:
                    if ARPEGGIATOR_MODES[arpeggiator_mode] == "Up":
                        arp = arp_chord
                    elif ARPEGGIATOR_MODES[arpeggiator_mode] == "Down":
                        arp = list(reversed(arp_chord))
                    else:
                        arp = arp_chord[:]
                        shuffle_in_place(arp)
                    note = arp[0]
                    midi.send(NoteOn(note, 120))
                    arpeggiators[key] = {
                        "notes": arp,
                        "index": 1 % len(arp),
                        "next_time": time.monotonic() + arp_step_time,
                        "last_note": note
                    }
                macropad.pixels[key] = (0, 255, 0)
                update_chord_label(chord)

            elif event.released and not latch_mode:
                if key in active_chords:
                    for note in active_chords[key]:
                        midi.send(NoteOff(note, 0))
                    del active_chords[key]
                if key in arpeggiators:
                    last_note = arpeggiators[key]["last_note"]
                    if last_note:
                        midi.send(NoteOff(last_note, 0))
                    del arpeggiators[key]
                macropad.pixels[key] = (255, 255, 0)
                update_chord_label([])

        elif key == 7 and event.pressed:
            inversion = (inversion + 1) % 3
            update_inversion_label()
            update_inversion_led()

        elif key == 8 and event.pressed:
            octave_shift = {-1: 0, 0: 1, 1: -1}[octave_shift]
            update_status_label()
            update_octave_led()

        elif key == 9 and event.pressed:
            arpeggiator_mode = (arpeggiator_mode + 1) % len(ARPEGGIATOR_MODES)
            update_arp_label()
            update_arp_led()

        elif key == 10 and event.pressed:
            latch_mode = not latch_mode
            update_inversion_label()
            update_arp_label()
            update_latch_led()
            if not latch_mode:
                stop_all_notes()

        elif key == 11 and event.pressed:
            chord_type_index = (chord_type_index + 1) % len(chord_type_names)
            update_inversion_label()
            update_chord_type_led()

    pos = macropad.encoder
    if pos != last_position:
        diff = pos - last_position
        if macropad.encoder_switch:
            bpm = max(30, min(300, bpm + diff))
            update_arp_label()
            update_arp_step_time()
        else:
            key_offset = (key_offset + diff) % 12
            update_status_label()
        last_position = pos

    now = time.monotonic()
    # Tempo pulse flash (only if arp is not off)
    if ARPEGGIATOR_MODES[arpeggiator_mode] != "Off":
        if now - last_pulse_time >= 60 / bpm:
            macropad.pixels[pulse_led_index] = (255, 255, 255)
            last_pulse_time = now
        elif now - last_pulse_time >= pulse_duration:
            update_arp_led()

    # Arp note advance and light animation
    for key, arp in list(arpeggiators.items()):
        if now >= arp["next_time"]:
            if arp["last_note"]:
                midi.send(NoteOff(arp["last_note"], 0))
            note = arp["notes"][arp["index"]]
            midi.send(NoteOn(note, 120))
            arpeggiators[key]["last_note"] = note
            arpeggiators[key]["index"] = (arp["index"] + 1) % len(arp["notes"])
            arpeggiators[key]["next_time"] = now + arp_step_time
            macropad.pixels[key] = (0, 255, 0)
            arp_flash_decay[key] = now + 0.05

    # Arp flash decay
    for key in list(arp_flash_decay):
        if now > arp_flash_decay[key]:
            if key not in active_chords:
                macropad.pixels[key] = (255, 255, 0)
            del arp_flash_decay[key]

    time.sleep(0.01)
