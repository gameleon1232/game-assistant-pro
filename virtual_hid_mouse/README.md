Virtual HID Mouse (Windows)

Overview
- Creates a real virtual HID mouse that appears in Windows Device Manager.
- Provides a tiny user-mode CLI to send relative moves and clicks to the virtual mouse.
- Built with Windows 10/11 WDK using the Virtual HID Framework (VHF).

What you get
- Kernel driver (KMDF) that enumerates a HID Mouse (usage page 0x01, usage 0x02).
- Simple IOCTL interface to submit MOVE and CLICK from user-mode.

Prerequisites
- Windows 10 or later (VHF available).
- Visual Studio 2022 + Windows 10/11 WDK.
- Test-signing enabled (unless you sign the driver):
  - Run as Administrator:
    - bcdedit /set testsigning on
    - reboot

Build
1) Open the driver solution in Visual Studio (create one and add the sources from driver/).
2) Set configuration to x64, Release.
3) Build.

Install (test mode)
1) Open an elevated Developer Command Prompt for VS.
2) Use DevCon or pnputil to install INF:
   - pnputil /add-driver vhidmouse.inf /install
3) After install, you should see a new HID-compliant mouse in Device Manager.

User-mode control
- Use app/vhidmouse_cli.py to send MOVE and CLICK via IOCTLs to the kernel driver.
- Examples (PowerShell):
  - py app/vhidmouse_cli.py move 10 0
  - py app/vhidmouse_cli.py click L 50

Wire into your app
- Replace pyautogui calls with invoking the CLI (or use the same IOCTLs directly from Python via pywin32/ctypes).

Security & Signing
- For production, obtain an EV code signing cert and sign the driver.
- In test environments, leave testsigning on.

Notes
- This project uses the same approach as the official Windows Driver Samples (Virtual HID Miniport/VHF).
- If you prefer UMDF, porting the logic to UMDF Virtual HID Miniport sample is also possible.

