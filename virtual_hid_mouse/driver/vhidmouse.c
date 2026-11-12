#include "vhidmouse.h"

static const UCHAR g_HidDescriptor[] = {
    0x05, 0x01,       // USAGE_PAGE (Generic Desktop)
    0x09, 0x02,       // USAGE (Mouse)
    0xA1, 0x01,       // COLLECTION (Application)
    0x09, 0x01,       //   USAGE (Pointer)
    0xA1, 0x00,       //   COLLECTION (Physical)
    0x05, 0x09,       //     USAGE_PAGE (Button)
    0x19, 0x01,       //     USAGE_MINIMUM (Button 1)
    0x29, 0x03,       //     USAGE_MAXIMUM (Button 3)
    0x15, 0x00,       //     LOGICAL_MINIMUM (0)
    0x25, 0x01,       //     LOGICAL_MAXIMUM (1)
    0x95, 0x03,       //     REPORT_COUNT (3)
    0x75, 0x01,       //     REPORT_SIZE (1)
    0x81, 0x02,       //     INPUT (Data,Var,Abs)
    0x95, 0x01,       //     REPORT_COUNT (1)
    0x75, 0x05,       //     REPORT_SIZE (5)
    0x81, 0x03,       //     INPUT (Cnst,Var,Abs)
    0x05, 0x01,       //     USAGE_PAGE (Generic Desktop)
    0x09, 0x30,       //     USAGE (X)
    0x09, 0x31,       //     USAGE (Y)
    0x15, 0x81,       //     LOGICAL_MINIMUM (-127)
    0x25, 0x7F,       //     LOGICAL_MAXIMUM (127)
    0x75, 0x08,       //     REPORT_SIZE (8)
    0x95, 0x02,       //     REPORT_COUNT (2)
    0x81, 0x06,       //     INPUT (Data,Var,Rel)
    0xC0,             //   END_COLLECTION
    0xC0              // END_COLLECTION
};

DRIVER_INITIALIZE DriverEntry;

NTSTATUS
DriverEntry(
    _In_ PDRIVER_OBJECT  DriverObject,
    _In_ PUNICODE_STRING RegistryPath
)
{
    WDF_DRIVER_CONFIG config;
    WDF_DRIVER_CONFIG_INIT(&config, VhidEvtDeviceAdd);
    return WdfDriverCreate(DriverObject, RegistryPath, WDF_NO_OBJECT_ATTRIBUTES, &config, WDF_NO_HANDLE);
}

NTSTATUS
VhidEvtDeviceAdd(
    _In_ WDFDRIVER       Driver,
    _Inout_ PWDFDEVICE_INIT DeviceInit
)
{
    UNREFERENCED_PARAMETER(Driver);
    WDF_PNPPOWER_EVENT_CALLBACKS pnpPowerCallbacks;
    WDF_OBJECT_ATTRIBUTES deviceAttributes;
    WDFDEVICE device;
    NTSTATUS status;

    WdfDeviceInitSetDeviceType(DeviceInit, FILE_DEVICE_UNKNOWN);
    WdfDeviceInitSetExclusive(DeviceInit, FALSE);

    WDF_PNPPOWER_EVENT_CALLBACKS_INIT(&pnpPowerCallbacks);
    WdfDeviceInitSetPnpPowerEventCallbacks(DeviceInit, &pnpPowerCallbacks);

    WDF_OBJECT_ATTRIBUTES_INIT_CONTEXT_TYPE(&deviceAttributes, DEVICE_CONTEXT);
    status = WdfDeviceCreate(&DeviceInit, &deviceAttributes, &device);
    if (!NT_SUCCESS(status)) return status;

    PDEVICE_CONTEXT devCtx = DeviceGetContext(device);
    devCtx->WdfDevice = device;

    // Create default queue for IOCTLs
    WDF_IO_QUEUE_CONFIG queueConfig;
    WDF_IO_QUEUE_CONFIG_INIT_DEFAULT_QUEUE(&queueConfig, WdfIoQueueDispatchSequential);
    queueConfig.EvtIoDeviceControl = VhidEvtIoDeviceControl;
    status = WdfIoQueueCreate(device, &queueConfig, WDF_NO_OBJECT_ATTRIBUTES, &devCtx->IoctlQueue);
    if (!NT_SUCCESS(status)) return status;

    // Initialize VHF
    VHF_CONFIG vhfConfig;
    VHF_CONFIG_INIT(&vhfConfig, (PUCHAR)g_HidDescriptor, sizeof(g_HidDescriptor));
    status = VhfCreate(device, &vhfConfig, &devCtx->VhfHandle);
    if (!NT_SUCCESS(status)) return status;
    VhfStart(devCtx->VhfHandle);
    return STATUS_SUCCESS;
}

_Forceinline VOID SendReport(VHFHANDLE vhf, CHAR dx, CHAR dy, UCHAR btn)
{
    UCHAR report[3] = { btn, (UCHAR)dx, (UCHAR)dy };
    VHF_REPORT_SEND_OPTIONS opts;
    VHF_REPORT_SEND_OPTIONS_INIT(&opts);
    VhfSubmitReport(vhf, report, sizeof(report), &opts);
}

VOID
VhidEvtIoDeviceControl(
    _In_ WDFQUEUE   Queue,
    _In_ WDFREQUEST Request,
    _In_ size_t     OutputBufferLength,
    _In_ size_t     InputBufferLength,
    _In_ ULONG      IoControlCode
)
{
    UNREFERENCED_PARAMETER(OutputBufferLength);
    PDEVICE_CONTEXT devCtx = DeviceGetContext(WdfIoQueueGetDevice(Queue));

    if (IoControlCode == IOCTL_VHIDMOUSE_MOVE) {
        PMOVE_INPUT inBuf;
        size_t len;
        if (NT_SUCCESS(WdfRequestRetrieveInputBuffer(Request, sizeof(MOVE_INPUT), (PVOID*)&inBuf, &len))) {
            CHAR dx = (CHAR)max(-127, min(127, inBuf->Dx));
            CHAR dy = (CHAR)max(-127, min(127, inBuf->Dy));
            SendReport(devCtx->VhfHandle, dx, dy, 0);
        }
        WdfRequestComplete(Request, STATUS_SUCCESS);
        return;
    }
    if (IoControlCode == IOCTL_VHIDMOUSE_CLICK) {
        PCLICK_INPUT inBuf;
        size_t len;
        if (NT_SUCCESS(WdfRequestRetrieveInputBuffer(Request, sizeof(CLICK_INPUT), (PVOID*)&inBuf, &len))) {
            UCHAR btn = 0;
            if (inBuf->ButtonFlags & 1) btn |= 0x01; // L down
            if (inBuf->ButtonFlags & 4) btn |= 0x02; // R down (report bit 2)
            if (inBuf->ButtonFlags & 16) btn |= 0x04; // M down (report bit 3)
            SendReport(devCtx->VhfHandle, 0, 0, btn);
            LARGE_INTEGER interval; interval.QuadPart = -10 * 1000 * (LONGLONG)inBuf->HoldMs; // ms to 100ns
            KeDelayExecutionThread(KernelMode, FALSE, &interval);
            SendReport(devCtx->VhfHandle, 0, 0, 0);
        }
        WdfRequestComplete(Request, STATUS_SUCCESS);
        return;
    }
    WdfRequestComplete(Request, STATUS_INVALID_DEVICE_REQUEST);
}

