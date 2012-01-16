import os

#import uxm.udisks as udisks
from . import UDISKS_OBJECT, UDISKS_DEVICE_INTERFACE, DBUS_PROPS_INTERFACE

class Device:

    def __init__(self, bus, device_path):
        self.bus = bus
        self.device_path = device_path
        self.device = self.bus.get_object(UDISKS_OBJECT, device_path)

    def __str__(self):
        return self.device_path

    def _get_property(self, prop):
        return self.device.Get(UDISKS_DEVICE_INTERFACE, prop,
                               dbus_interface=DBUS_PROPS_INTERFACE)

    @property
    def partition_slave(self):
        return self._get_property('PartitionSlave')

    @property
    def is_partition_table(self):
        return self._get_property('DeviceIsPartitionTable')

    @property
    def is_system_internal(self):
        return self._get_property('DeviceIsSystemInternal')

    @property
    def label(self):
        return self._get_property('IdLabel')

    @property
    def size(self):
        return self._get_property('DeviceSize')
    
    @property
    def is_mounted(self):
        return bool(self._get_property('DeviceIsMounted'))

    @property
    def mount_paths(self):
        raw_paths = self._get_property('DeviceMountPaths')
        return [os.path.normpath(path) for path in raw_paths]

    @property
    def device_file(self):
        return os.path.normpath(self._get_property('DeviceFile'))

    @property
    def is_filesystem(self):
        return bool(self._get_property('IdUsage') == 'filesystem')

    @property
    def is_optical(self):
        return bool(self._get_property('DeviceIsOpticalDisc'))

    @property
    def has_media(self):
        return bool(self._get_property('DeviceIsMediaAvailable'))

    @property
    def id_type(self):
        return self._get_property('IdType')

    @property
    def id_version(self):
        return self._get_property('IdVersion')

    @property
    def connection_interface(self):
        return self._get_property('DriveConnectionInterface')

    def mount(self, options=[]):
        self.device.FilesystemMount(
            self.id_type,
            options,
            dbus_interface=UDISKS_DEVICE_INTERFACE
        )

    def unmount(self, options=[]):
        self.device.FilesystemUnmount(
            options,
            dbus_interface=UDISKS_DEVICE_INTERFACE
        )

