import keyboard
import time
import pdb

until_key = 'p'
record_key = 'r'
rec = {}

def recordNew(rec):
    global until_key
    # Record keymap
    print('record keymap')
    #keymap = keyboard.record(until=until_key)[0].name
    keymap = keyboard.read_hotkey()
    print('{}'.format(keymap))

    # Record the keystrokes
    print('record macro')
    #rec[keymap] = keyboard.record(until=until_key)
    #rec[keymap] = keyboard.record(until=until_key,trigger_on_release=True)
    rec[keymap] = keyboard.record(trigger_on_release=True)
    print(rec[keymap])

    # Add hotkey
    keyboard.add_hotkey('{}'.format(keymap), lambda: keyboard.play(rec[keymap]))

def handleEvent(e):
    global rec
    recordNew(rec)

#recordNew(rec)
#keyboard.add_hotkey(record_key, lambda: recordNew(rec) )
while True:
    #keyboard.wait(record_key, trigger_on_release=True)
    print('wait')
    keyboard.wait(record_key, True, trigger_on_release=True)
    print('recrod')
    recordNew(rec)
#keyboard.on_release_key(record_key, handleEvent)
keyboard.wait()
