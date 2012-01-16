DBUS_PROPS_INTERFACE = 'org.freedesktop.DBus.Properties'
UDISKS_INTERFACE = 'org.freedesktop.UDisks'
UDISKS_DEVICE_INTERFACE = 'org.freedesktop.UDisks.Device'

UDISKS_OBJECT = 'org.freedesktop.UDisks'
UDISKS_OBJECT_PATH = '/org/freedesktop/UDisks'

UDISKS_ERROR_BUSY = 'org.freedesktop.UDisks.Error.Busy'


import dbus

# delayed imports so that other modules in uxm.udisks can access constants
from uxm.udisks.device import Device


def enumerate_devices():
    """Lists available devices on the System Bus"""
    sysbus = dbus.SystemBus()
    udisks = sysbus.get_object(UDISKS_OBJECT, UDISKS_OBJECT_PATH)
    for path in udisks.EnumerateDevices(dbus_interface=UDISKS_INTERFACE):
        yield Device(sysbus, path)

def mount(path):
    """Mounts a filesystem given its mout point or device file."""
    for device in enumerate_devices():
        if path == device.device_file:
            return mount_device(device)

def mount_device(device):
    """Mounts a uxm.udisks.device.Device"""
    if not device.is_mounted:
        device.mount()
    return device

def unmount(path):
    """Unmounts a filesystem given its mout point or device file."""

    for device in enumerate_devices():
        if path in device.mount_paths or path == device.device_file:
            return unmount_device(device)

def unmount_device(device):
    """Unmount a uxm.udisks.device.Device"""

    if device.is_mounted:
        device.unmount()
    return device
