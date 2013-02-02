import uxm.config as config
import uxm.parser as parser
import uxm.udisks as udisks
import uxm.utils as utils

_ = config.translate

class Parser(parser.BaseParser):
    
    def __init__(self, formatter="pckl"):
        super(Parser, self).__init__()
        self.formatter = formatter
        self.file_manager = self.preferences.get('General', 'filemanager')
        if self.show_icons:
            for name in ['folder','internal_drive','optical_drive',
                        'removable_drive', 'mount','unmount']:
                icn_cfg = self.preferences.get('Icons', name)
                icn = self.icon_finder.find_by_name(icn_cfg)
                setattr(self, "%s_icn" % name, icn)

    def parse_devices(self):
        devices_list = []
        for device in udisks.enumerate_devices():
            if device.is_filesystem:
                devices_list.append(self.parse_device(device))
        return {
            "type": "menu",
            "label": _("Devices"),
            "id": "uxm-devices",
            "icon": "%s" % self.internal_drive_icn if self.show_icons else "",
            "items": sorted(devices_list, key=lambda d: d['label'])
        }

    def parse_device(self, device):
        device_file = device.device_file.encode('utf-8')
        device_name = device_file
        if device.label:
            device_name = device.label.encode('utf-8')
        elif device.is_mounted:
            device_name = "%s on %s" % (
                device_file, device.mount_paths[0].encode('utf-8')
            )
        label = "%s (%s - %s)" % (
            device_name,
            utils.fmt.filesize(int(device.size)),
            device.id_type
        )
        if device.is_mounted:
            open_cmd = '%s "%s"' % (
                self.file_manager,
                device.mount_paths[0]
            )
            action = {
                "type": "application",
                "label": _("Unmount the selected volume"),
                "icon": "%s" % self.unmount_icn if self.show_icons else "",
                "command": 'uxm-daemon device:unmount "%s"' % (
                    device_file    
                )
            }
        else:
            open_cmd = 'uxm-daemon device:open "%s"' % device_file
            action = {
                "type": "application",
                "label": _("Mount the selected volume"),
                "icon": "%s" % self.mount_icn if self.show_icons else "",
                "command": 'uxm-daemon device:mount "%s"' % device_file
            }
        icn = self.find_icon_for_device(device)
        return {
            "type": "menu",
            "id": device_file,
            "label": label,
            "icon": "%s" % icn if self.show_icons else "",
            "items": [
                {
                    "type": "application",
                    "label": _("Open"),
                    "icon": "%s" % self.folder_icn if self.show_icons else "",
                    "command": open_cmd
                },
                action
            ]
        }

    def find_icon_for_device(self, device):
        if device.is_optical:
            return self.optical_drive_icn
        if device.is_system_internal:
            return self.internal_drive_icn
        return self.removable_drive_icn
