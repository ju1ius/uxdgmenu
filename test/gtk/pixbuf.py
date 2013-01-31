import os
import gtk

"""gtk.gdk.Pixbuf.composite
def composite(dest, dest_x, dest_y, dest_width, dest_height, offset_x, offset_y, scale_x, scale_y, interp_type, overall_alpha)

dest          : the output gtk.gdk.Pixbuf
dest_x        : the X coordinate for the rectangle
dest_y        : the top coordinate for the rectangle
dest_width    : the width of the rectangle
dest_height   : the height of the rectangle
offset_x      : the offset in the X direction (currently rounded to an integer)
offset_y      : the offset in the Y direction (currently rounded to an integer)
scale_x       : the scale factor in the X direction
scale_y       : the scale factor in the Y direction
interp_type   : the interpolation type for the transformation.
overall_alpha : overall alpha for source image (0..255)
"""

__DIR__ = os.path.dirname(os.path.abspath(__file__))
ICON_DIR = "/usr/share/icons/elementary-statler"

ICON_FILE = ICON_DIR + "/places/48/folder.svg"
LINK_FILE = ICON_DIR + "/emblems/48/emblem-symbolic-link.svg"

icon = gtk.gdk.pixbuf_new_from_file_at_size(ICON_FILE, 48, 48)
link = gtk.gdk.pixbuf_new_from_file_at_size(LINK_FILE, 64, 64)

def get_scale_factor(icon, link):
    result = icon.props.width / 2.0
    scale = result / link.props.width
    return float(scale)

link_w = link.props.width
link_h = link.props.height
icon_w = icon.props.width
icon_h = icon.props.height

scale = get_scale_factor(icon, link)
# the source
link.composite(
    icon, # the dest
    0, 0,
    icon_w, icon_h,
    icon_w/2, icon_h/2,
    scale, scale, # scale the source
    gtk.gdk.INTERP_HYPER,
    255 # alpha of the source
)

icon.save(__DIR__+'/composite.png', 'png')
