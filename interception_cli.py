import ctypes
import ctypes.wintypes as wt
import sys
import os

# Load interception.dll from Interception/library/x64
DLL_PATH = os.path.join(os.path.dirname(__file__), 'Interception', 'library', 'x64', 'interception.dll')
if not os.path.exists(DLL_PATH):
    print('interception.dll not found at', DLL_PATH)
    sys.exit(1)

interception = ctypes.WinDLL(DLL_PATH)

# Types and constants from interception.h (simplified)
InterceptionContext = wt.HANDLE
InterceptionDevice = ctypes.c_int
InterceptionStroke = ctypes.c_ubyte * 24  # enough to hold mouse stroke

INTERCEPTION_MAX_KEYBOARD = 10
INTERCEPTION_MAX_MOUSE = 10
INTERCEPTION_FILTER_MOUSE_ALL = 0xFFFF

# Mouse flags (partial)
INTERCEPTION_MOUSE_LEFT_BUTTON_DOWN  = 0x001
INTERCEPTION_MOUSE_LEFT_BUTTON_UP    = 0x002
INTERCEPTION_MOUSE_RIGHT_BUTTON_DOWN = 0x004
INTERCEPTION_MOUSE_RIGHT_BUTTON_UP   = 0x008
INTERCEPTION_MOUSE_MIDDLE_BUTTON_DOWN= 0x010
INTERCEPTION_MOUSE_MIDDLE_BUTTON_UP  = 0x020
INTERCEPTION_MOUSE_MOVE_RELATIVE     = 0x100

class InterceptionMouseStroke(ctypes.Structure):
    _fields_ = [
        ("state", wt.USHORT),
        ("flags", wt.USHORT),
        ("rolling", wt.SHORT),
        ("x", wt.SHORT),
        ("y", wt.SHORT),
        ("information", wt.USHORT),
    ]

interception.interception_create_context.restype = InterceptionContext
interception.interception_send = interception.interception_send
interception.interception_send.argtypes = [InterceptionContext, InterceptionDevice, ctypes.POINTER(InterceptionMouseStroke), ctypes.c_uint]

def open_context():
    ctx = interception.interception_create_context()
    if not ctx:
        raise OSError('Failed to create Interception context')
    return ctx

def send_move(dx, dy):
    ctx = open_context()
    try:
        stroke = InterceptionMouseStroke()
        stroke.state = 0
        stroke.flags = INTERCEPTION_MOUSE_MOVE_RELATIVE
        stroke.x = int(dx)
        stroke.y = int(dy)
        # Try all mouse device ids (11..20), stop on first success
        for dev in range(11, 21):
            interception.interception_send(ctx, dev, ctypes.byref(stroke), 1)
    finally:
        ctypes.windll.kernel32.CloseHandle(ctx)

def send_click(btn, ms):
    ctx = open_context()
    try:
        if btn == 'L':
            down, up = INTERCEPTION_MOUSE_LEFT_BUTTON_DOWN, INTERCEPTION_MOUSE_LEFT_BUTTON_UP
        elif btn == 'R':
            down, up = INTERCEPTION_MOUSE_RIGHT_BUTTON_DOWN, INTERCEPTION_MOUSE_RIGHT_BUTTON_UP
        else:
            down, up = INTERCEPTION_MOUSE_MIDDLE_BUTTON_DOWN, INTERCEPTION_MOUSE_MIDDLE_BUTTON_UP
        # Send to all mouse devices
        stroke = InterceptionMouseStroke()
        stroke.flags = 0
        stroke.state = down
        for dev in range(11, 21):
            interception.interception_send(ctx, dev, ctypes.byref(stroke), 1)
        if ms > 0:
            import time
            time.sleep(ms / 1000.0)
        stroke.state = up
        for dev in range(11, 21):
            interception.interception_send(ctx, dev, ctypes.byref(stroke), 1)
    finally:
        ctypes.windll.kernel32.CloseHandle(ctx)

def main():
    if len(sys.argv) < 2:
        print('Usage: interception_cli.py move <dx> <dy> | click <L|R|M> <ms>')
        sys.exit(1)
    cmd = sys.argv[1].lower()
    if cmd == 'move' and len(sys.argv) == 4:
        send_move(int(sys.argv[2]), int(sys.argv[3]))
    elif cmd == 'click' and len(sys.argv) == 4:
        send_click(sys.argv[2].upper(), int(sys.argv[3]))
    else:
        print('Usage: interception_cli.py move <dx> <dy> | click <L|R|M> <ms>')
        sys.exit(1)

if __name__ == '__main__':
    main()

