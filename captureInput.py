from pynput import keyboard

temp=''
def on_press(key):
    try:
        print('alphanumeric key {0} pressed'.format(
            key.char))
    except AttributeError:
        print('special key {0} pressed'.format(
            key))

def on_release(key):
    global temp
    print('{0} released'.format(
        key))        
    try:
        temp = temp + key.char
    except AttributeError:
        if(key==keyboard.Key.enter):
            print(temp)
            temp=""
        if key == keyboard.Key.esc:
            # Stop listener
            return False
        

# Collect events until released
with keyboard.Listener(
        on_press=on_press,
        on_release=on_release) as listener:
    listener.join()

# ...or, in a non-blocking fashion:
listener = keyboard.Listener(
    on_press=on_press,
    on_release=on_release)
listener.start()