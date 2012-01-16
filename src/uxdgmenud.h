
#ifndef __UXDGMENUD_H__
#define __UXDGMENUD_H__

#include <glib.h>
#include <inotifytools/inotify.h>

#define UXM_DAEMON_NAME           "uxdgmenud"
#define UXM_UPDATE_CMD_PREFIX     "uxm-daemon update"
#define UXM_UPDATE_CMD_BUF_SIZE   256

#define UXM_DESKTOP_FILE_EXT      ".desktop"
#define UXM_DIRECTORY_FILE_EXT    ".directory"
#define UXM_MENU_FILE_EXT         ".menu"
#define UXM_BOOKMARKS_FILE        ".gtk-bookmarks"
#define UXM_RECENT_FILES_FILE     ".recently-used.xbel"

#define UXM_UDISKS_OBJECT_NAME    "org.freedesktop.UDisks"
#define UXM_UDISKS_OBJECT_PATH    "/org/freedesktop/UDisks"
#define UXM_UDISKS_OBJECT_IFACE   "org.freedesktop.UDisks"

#define UXM_APPS_EVENTS           IN_CLOSE_WRITE|IN_DELETE|IN_MOVE
#define UXM_BOOKMARKS_EVENTS      IN_CLOSE_WRITE
#define UXM_EXCLUDE_PATTERN				"/.local/share/applications/menu-xdg/"

#define UXM_OPTS_VERBOSE						0x01
#define UXM_OPTS_DAEMONIZE          0x02
#define UXM_OPTS_WATCH_APPLICATIONS	0x04
#define UXM_OPTS_WATCH_BOOKMARKS    0x08
#define UXM_OPTS_WATCH_RECENT_FILES 0x10
#define UXM_OPTS_WATCH_DEVICES      0x20

/**
 * Shared data between threads
 **/
typedef struct UxmSharedData {
	GAsyncQueue *queue;
	char *formatter;
	int flags;
} UxmSharedData;

/**
 * Constructs a UxmSharedData object
 **/
static UxmSharedData *
uxm_shared_data_new(GAsyncQueue *queue,
                    int flags,
                    char *formatter);

/**
 * Types of messages emitted by the monitor worker
 **/
enum UxmMessageType {
  UXM_MSG_TYPE_APPLICATION	= 0x01,
  UXM_MSG_TYPE_BOOKMARK			= 0x02,
  UXM_MSG_TYPE_RECENT_FILE	= 0x04,
  UXM_MSG_TYPE_DEVICE       = 0x08
};
typedef enum UxmMessageType UxmMessageType;

/**
 * The message object emitted by the monitor worker
 **/
typedef struct UxmMessage {
  char *data;
  UxmMessageType type;
} UxmMessage;

/**
 * Constructs message objects
 **/
static UxmMessage *
uxm_msg_new(UxmMessageType type);

static void
uxm_msg_dispatch(GAsyncQueue *queue,
                  struct inotify_event *event,
                  UxmMessageType type,
                  char *msg_buf,
                  int verbose);
/**
 * Monitors directories
 **/
static int
uxm_inotify_worker(UxmSharedData *data);

static int
uxm_udisks_worker(UxmSharedData *data);

static void
uxm_udisks_signal_handler(GDBusProxy *proxy,
                          gchar      *sender_name,
                          gchar      *signal_name,
                          GVariant   *parameters,
                          gpointer    user_data);

/**
 * Listens to messages emitted by uxm_inotify_worker
 * and call update commands accordingly
 **/
static int
uxm_monitor_listener(UxmSharedData *data);

/**
 * Handles termination signals
 **/
static void
uxm_signal_handler(int signum);

/**
 * Cleans up memory before shutdown
 **/
static void
uxm_cleanup(void);

/**
 * Retrieve the list of directories to monitor
 **/
static GSList *
uxm_get_monitored_directories(void);

static gchar *
uxm_get_recent_files_path(void);

/**
 * Compatibility with glib < 2.28
 **/
static void
uxm_gslist_free_full(GSList *list);

/**
 * Checks is given path is a directory
 **/
static gboolean
uxm_path_is_dir(const gchar *path);

static gchar *
uxm_path_ensure_trailing_slash(const gchar *path);

#endif /* __UXDGMENUD_H__ */

