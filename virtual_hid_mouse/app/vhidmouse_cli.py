import ctypes
import ctypes.wintypes as wt
import sys

GENERIC_READ  = 0x80000000
GENERIC_WRITE = 0x40000000
OPEN_EXISTING = 3
FILE_SHARE_READ  = 1
FILE_SHARE_WRITE = 2

# Must match the driver's IOCTLs
FILE_DEVICE_VHIDMOUSE = 0x8000
def CTL_CODE(DeviceType, Function, Method, Access):
    return (DeviceType << 16) | (Access << 14) | (Function << 2) | Method

IOCTL_VHIDMOUSE_MOVE  = CTL_CODE(FILE_DEVICE_VHIDMOUSE, 0x801, 0, 0)
IOCTL_VHIDMOUSE_CLICK = CTL_CODE(FILE_DEVICE_VHIDMOUSE, 0x802, 0, 0)

class MOVE_INPUT(ctypes.Structure):
    _fields_ = [("Dx", wt.LONG), ("Dy", wt.LONG)]

class CLICK_INPUT(ctypes.Structure):
    _fields_ = [("ButtonFlags", wt.ULONG), ("HoldMs", wt.ULONG)]

CreateFile = ctypes.windll.kernel32.CreateFileW
DeviceIoControl = ctypes.windll.kernel32.DeviceIoControl
CloseHandle = ctypes.windll.kernel32.CloseHandle

def open_device():
    # Symbolic link created by the driver (adjust if you create a different link)
    path = r"\\.\VHIDMOUSE"
    h = CreateFile(path, GENERIC_READ | GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_WRITE, None, OPEN_EXISTING, 0, None)
    if h == wt.HANDLE(-1).value:
        raise OSError("Cannot open device: %s" % path)
    return h

def io_move(dx, dy):
    h = open_device()
    try:
        buf = MOVE_INPUT(dx, dy)
        out = wt.DWORD()
        ok = DeviceIoControl(h, IOCTL_VHIDMOUSE_MOVE, ctypes.byref(buf), ctypes.sizeof(buf), None, 0, ctypes.byref(out), None)
        if not ok:
            raise OSError("MOVE failed")
    finally:
        CloseHandle(h)

def io_click(btn, ms):
    h = open_device()
    try:
        flags = 0
        if btn == 'L':
            flags = 1 | 2  # Down+Up handled inside driver with hold
        elif btn == 'R':
            flags = 4 | 8
        elif btn == 'M':
            flags = 16 | 32
        buf = CLICK_INPUT(flags, max(0, int(ms)))
        out = wt.DWORD()
        ok = DeviceIoControl(h, IOCTL_VHIDMOUSE_CLICK, ctypes.byref(buf), ctypes.sizeof(buf), None, 0, ctypes.byref(out), None)
        if not ok:
            raise OSError("CLICK failed")
    finally:
        CloseHandle(h)

def main():
    if len(sys.argv) < 2:
        print("Usage: vhidmouse_cli.py move <dx> <dy> | click <L|R|M> <ms>")
        sys.exit(1)
    cmd = sys.argv[1].lower()
    if cmd == 'move' and len(sys.argv) == 4:
        io_move(int(sys.argv[2]), int(sys.argv[3]))
    elif cmd == 'click' and len(sys.argv) == 4:
        io_click(sys.argv[2].upper(), int(sys.argv[3]))
    else:
        print("Usage: vhidmouse_cli.py move <dx> <dy> | click <L|R|M> <ms>")
        sys.exit(1)

if __name__ == '__main__':
    main()

