#pragma once
#include <ntddk.h>
#include <wdf.h>
#include <vhf.h>

// IOCTL interface to accept user-mode commands
#define FILE_DEVICE_VHIDMOUSE 0x8000
#define IOCTL_VHIDMOUSE_MOVE CTL_CODE(FILE_DEVICE_VHIDMOUSE, 0x801, METHOD_BUFFERED, FILE_ANY_ACCESS)
#define IOCTL_VHIDMOUSE_CLICK CTL_CODE(FILE_DEVICE_VHIDMOUSE, 0x802, METHOD_BUFFERED, FILE_ANY_ACCESS)

typedef struct _MOVE_INPUT {
    LONG Dx;
    LONG Dy;
} MOVE_INPUT, *PMOVE_INPUT;

typedef struct _CLICK_INPUT {
    ULONG ButtonFlags; // 1:LeftDown, 2:LeftUp, 4:RightDown, 8:RightUp, 16:MiddleDown, 32:MiddleUp
    ULONG HoldMs;      // optional delay between down & up in ms
} CLICK_INPUT, *PCLICK_INPUT;

typedef struct _DEVICE_CONTEXT {
    WDFDEVICE WdfDevice;
    VHFHANDLE VhfHandle;
    WDFQUEUE IoctlQueue;
} DEVICE_CONTEXT, *PDEVICE_CONTEXT;

WDF_DECLARE_CONTEXT_TYPE_WITH_NAME(DEVICE_CONTEXT, DeviceGetContext)

DRIVER_INITIALIZE DriverEntry;
EVT_WDF_DRIVER_DEVICE_ADD VhidEvtDeviceAdd;
EVT_WDF_IO_QUEUE_IO_DEVICE_CONTROL VhidEvtIoDeviceControl;

