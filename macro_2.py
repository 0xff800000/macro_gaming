from pynput import mouse, keyboard
import time
import json
import pdb

mouse_ctrl = None
keyboard_ctrl = None
mouse_listener = None
recorded_events = []
unreleased_keys = []

# recorded = [
#         {
#             "periph": "mouse",
#             "type" : "on_move",
#             "time" : 0,
#             "params" : {x,y},
#         }, ...
#      ]

stopping_key = keyboard.Key.esc

start_time = 0

def get_time():
    global start_time
    return  time.time() - start_time

dbg_mode = True
def print_dbg(string):
    if dbg_mode:
        print(string)

#################
# Mouse callbacks
#################

def on_move(x, y):
    record_event(
            {
                "periph": "mouse",
                "type": "on_move",
                "time": get_time(),
                "params": {"x":x,"y":y}
                })
    print_dbg('Pointer moved to {0}'.format(
        (x, y)))

def on_click(x, y, button, pressed):
    record_event(
            {
                "periph": "mouse",
                "type": "on_click",
                "time": get_time(),
                "params": {"x":x,"y":y,"button":str(button),"pressed":pressed}
                })
    print_dbg('{0} at {1}'.format(
        'Pressed' if pressed else 'Released',
        (x, y)))
    #if not pressed:
    #    # Stop listener
    #    return False

def on_scroll(x, y, dx, dy):
    record_event(
            {
                "periph": "mouse",
                "type": "on_scroll",
                "time": get_time(),
                "params": {"x":x,"y":y,"dx":dx,"dy":dy}
                })
    print_dbg('Scrolled {0} at {1}'.format(
        'down' if dy < 0 else 'up',
        (x, y)))

####################
# Keyboard callbacks
####################

def on_press(key):
    global unreleased_keys
    if key in unreleased_keys:
        return
    else:
        unreleased_keys.append(key)

    record_event(
            {
                "periph": "keyboard",
                "type": "on_press",
                "time": get_time(),
                "params": {"key":str(key)}
                })
    try:
        print_dbg('alphanumeric key {0} pressed'.format(
            key.char))
    except AttributeError:
        print_dbg('special key {0} pressed'.format(
            key))

def on_release(key):
    global unreleased_keys
    try:
        unreleased_keys.remove(key)
    except ValueError:
        print('ERROR: {} not in unreleased_keys'.format(key))
    record_event(
            {
                "periph": "keyboard",
                "type": "on_release",
                "time": get_time(),
                "params": {"key":str(key)}
                })
    print_dbg('{0} released'.format(
        key))
    if key == stopping_key:
        # Stop listener
        global mouse_listener
        mouse_listener.stop()
        return False

def record_event(event):
    recorded_events.append(event)

def record_action():

    # Start all listener

    #with mouse.Listener(
    #        on_move=on_move,
    #        on_click=on_click,
    #        on_scroll=on_scroll) as listener:
    #    listener.join()
    global mouse_listener
    mouse_listener = mouse.Listener(
            #on_move=on_move,
            on_click=on_click,
            on_scroll=on_scroll)
    mouse_listener.start()

    with keyboard.Listener(
            on_press=on_press, 
            on_release=on_release) as listener:
        global start_time
        start_time = time.time()
        listener.join()

##########
# Handlers
##########

def on_move_handler(event):
    global mouse_ctrl
    ev = event["params"]
    x,y = (ev["x"],ev["y"])
    mouse_ctrl.position = (x,y)

def on_click_handler(event):
    global mouse_ctrl
    ev = event["params"]
    x,y,button,pressed = (ev["x"],ev["y"],ev["button"],ev["pressed"])

    mouse_ctrl.position = (x,y)
    if button == "Button.left":
        button = mouse.Button.left
    elif button == "Button.right":
        button = mouse.Button.right
    elif button == "Button.middle":
        button = mouse.Button.middle
    
    if pressed:
        mouse_ctrl.press(button)
    else:
        mouse_ctrl.release(button)

def on_scroll_handler(event):
    global mouse_ctrl
    ev = event["params"]
    x,y,dx,dy = (ev["x"],ev["y"],ev["dx"],ev["dy"])

    mouse_ctrl.position = (x,y)
    mouse_ctrl.scroll(dx,dy)

def convertKey(button):
    PYNPUT_SPECIAL_CASE_MAP = {
        'esc': keyboard.Key.esc,
        'space': keyboard.Key.space,
        'alt_l': keyboard.Key.alt_l,
        'alt_r': keyboard.Key.alt_r,
        'alt_gr': keyboard.Key.alt_gr,
        'caps_lock': keyboard.Key.caps_lock,
        'ctrl_l': keyboard.Key.ctrl_l,
        'ctrl_r': keyboard.Key.ctrl_r,
        'page_down': keyboard.Key.page_down,
        'page_up': keyboard.Key.page_up,
        'shift_l': keyboard.Key.shift_l,
        'shift_r': keyboard.Key.shift_r,
        'num_lock': keyboard.Key.num_lock,
        'print_screen': keyboard.Key.print_screen,
        'scroll_lock': keyboard.Key.scroll_lock,
        'tab': keyboard.Key.tab,
        'up': keyboard.Key.up,
        'down': keyboard.Key.down,
        'left': keyboard.Key.left,
        'right': keyboard.Key.right,
    }
    # example: 'Key.F9' should return 'F9', 'w' should return as 'w'
    cleaned_key = button.replace('Key.', '')
    cleaned_key = cleaned_key.replace("\'", '')

    if cleaned_key in PYNPUT_SPECIAL_CASE_MAP:
        return PYNPUT_SPECIAL_CASE_MAP[cleaned_key]

    return cleaned_key

def on_press_handler(event):
    global keyboard_ctrl
    ev = event["params"]
    key = ev["key"]
    key = convertKey(key)

    keyboard_ctrl.press(key)

def on_release_handler(event):
    global keyboard_ctrl
    ev = event["params"]
    key = ev["key"]
    key = convertKey(key)

    keyboard_ctrl.release(key)

def replay_actions(filename):
    global keyboard_ctrl
    global mouse_ctrl
    data = json.load(open(filename,"r"))

    mouse_ctrl = mouse.Controller()
    keyboard_ctrl = keyboard.Controller()

    for i,event in enumerate(data):
        start_action_time = time.time()
        if event["type"] == "on_move":
            on_move_handler(event)
        elif event["type"] == "on_click":
            on_click_handler(event)
        elif event["type"] == "on_scroll":
            on_scroll_handler(event)
        elif event["type"] == "on_press":
            on_press_handler(event)
        elif event["type"] == "on_release":
            on_release_handler(event)

        diff_time = 0
        if i != len(data) - 1:
            diff_time = data[i+1]["time"] - event["time"]
        time_to_wait = diff_time - (time.time() - start_action_time)
        if time_to_wait < 0:
            time_to_wait = 0

        time.sleep(time_to_wait)

#record_action()
#json.dump(recorded_events, open("recording.json","w"), indent=4)
pdb.set_trace()
time.sleep(4)
replay_actions("recording.json")

while True:
    time.sleep(10)
