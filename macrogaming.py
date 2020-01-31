import keyboard
import time
import pdb

until_key = 'esc'
record_key = 'r'
rec = {}

def recordNew(rec):
    global until_key
    print('wait')
    keyboard.wait(record_key, True, trigger_on_release=True)
    # Record keymap
    print('record keymap')
    keymap = keyboard.read_key()
    print('{}'.format(keymap))

    # Record the keystrokes
    print('record macro')
    rec[keymap] = keyboard.record(until=until_key)[1:-1]
    print(rec[keymap])

    # Add hotkey
    keyboard.add_hotkey('{}'.format(keymap), lambda: keyboard.play(rec[keymap]))

while True:
    print('recrod')
    recordNew(rec)
