#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include <syslog.h>
#include <unistd.h>
#include <signal.h>
#include <string.h>
#include <regex.h>
#include <sys/stat.h>
#include <inotifytools/inotifytools.h>
#include <inotifytools/inotify.h>
#include <glib.h>
#include <glib/gprintf.h>

#include "uxdgmenud.h"

static int uxm_stop_event = 0;

/**
 * MAIN
 **/
int main(int argc, char **argv)
{
  int next_option;
  /* list of short options */
  const char *short_options = "abrdvf:";
  /* An array listing valid long options */
  static const struct option long_options[] =
  {
    {"watch-applications",  no_argument, NULL, 'a'},
    {"watch-bookmarks",     no_argument, NULL, 'b'},
    {"watch-recent-files",  no_argument, NULL, 'r'},
    {"daemon",              no_argument, NULL, 'd'},
    {"verbose",             no_argument, NULL, 'v'},
    {"formatter",           required_argument, NULL, 'f'},
    {NULL, 0, NULL, 0} /* End of array need by getopt_long do not delete it*/
  };

  /* ---------- OPTIONS ---------- */
  
  int opts_flags = 0;
  char *formatter = NULL;

  /* ---------- VARS ---------- */
  GAsyncQueue *queue = NULL;
  GThread *worker_thread;
  GThread *listener_thread;
  GError *error = NULL;

  UxmSharedData *shared_data;

  /*****************************************
   * Process Command line args
   ****************************************/
  do
  {
    next_option = getopt_long(argc, argv, short_options, long_options, NULL);
    switch(next_option)
    {
      case 'a':
        opts_flags |= UXM_OPTS_WATCH_APPLICATIONS;
        break;
      case 'b':
        opts_flags |= UXM_OPTS_WATCH_BOOKMARKS;
        break;
      case 'r':
        opts_flags |= UXM_OPTS_WATCH_RECENT_FILES;
        break;
      case 'f':
        formatter = optarg;
        break;
      case 'd':
        opts_flags |= UXM_OPTS_DAEMONIZE;
        break;
      case 'v':
        opts_flags |= UXM_OPTS_VERBOSE;
        break;
      case '?':
        break;
      default:
          /*abort();*/
        break;
    }
  }
  while(next_option != -1);

  if(!formatter) {
    g_print("No formatter provided\n");
    exit(EXIT_FAILURE);
  }

  if(opts_flags & UXM_OPTS_DAEMONIZE) {
    daemon(0,0);
  }

  openlog(UXM_DAEMON_NAME, LOG_PID, LOG_USER);
  syslog(LOG_INFO, "Starting in %s", g_getenv("HOME"));

  /* Setup signal handling */
  signal(SIGCHLD, SIG_IGN); /* ignore child */
  signal(SIGTSTP, SIG_IGN); /* ignore tty signals */
  signal(SIGTTOU, SIG_IGN);
  signal(SIGTTIN, SIG_IGN);
  signal(SIGHUP, uxm_signal_handler);
  signal(SIGINT, uxm_signal_handler);
  signal(SIGQUIT, uxm_signal_handler);
  signal(SIGTERM, uxm_signal_handler);
  signal(SIGKILL, uxm_signal_handler);


  /*****************************************
   *  Core Functionnalities
   ****************************************/
  
  if(!g_thread_supported())
    g_thread_init(NULL);
  
  queue = g_async_queue_new();

  shared_data = uxm_shared_data_new(queue, opts_flags, formatter);

  listener_thread = g_thread_create((GThreadFunc)uxm_monitor_listener, shared_data, FALSE, &error);
  if(!listener_thread) {
    syslog(LOG_ERR, "Error: %s\n", error->message );
    exit(EXIT_FAILURE);
  }

  worker_thread = g_thread_create((GThreadFunc)uxm_monitor_worker, shared_data, TRUE, &error);
  if(!worker_thread) {
    syslog(LOG_ERR, "Error: %s\n", error->message );
    exit(EXIT_FAILURE);
  }

  g_thread_join(worker_thread);

  /**
   * Cleanup
   **/
  g_free(shared_data);
  uxm_cleanup();

  return 0;
}

/**
 * Functions
 **/

gpointer uxm_monitor_worker(UxmSharedData *data)
{
  /* message queued */
  struct UxmMessage *msg;
  /*void *msg_data;*/

  /* log message */
  char message_buf[256];

  /* the notified event */
  struct inotify_event *event;
  /* HOME watch descriptor */
  int home_wd = -1;

  /* Setup paths */
  const char *home = g_getenv("HOME");
  GSList *monitored = NULL;
  GSList *iter = NULL;

  /* Flags */
  int verbose = data->flags & UXM_OPTS_VERBOSE;
  int watch_applications = data->flags & UXM_OPTS_WATCH_APPLICATIONS;
  int watch_bookmarks = data->flags & UXM_OPTS_WATCH_BOOKMARKS;
  int watch_recent_files = data->flags & UXM_OPTS_WATCH_RECENT_FILES;
  int watch_home = watch_recent_files || watch_bookmarks;
  
  if(!home) {
    home = g_get_home_dir();
  }

  g_async_queue_ref(data->queue);

  /**
   * initialize and watch the entire directory tree from the current working
   * directory downwards for all events
   **/
  if(!inotifytools_initialize()) {
    syslog( LOG_ERR, "%s", strerror(inotifytools_error()) );
    exit(EXIT_FAILURE);
  }

  /* set time format to 24 hour time, HH:MM:SS */
  inotifytools_set_printf_timefmt( "%T" );

  if(!inotifytools_ignore_events_by_regex(UXM_EXCLUDE_PATTERN, REG_EXTENDED)) {
    syslog(LOG_ERR, "Invalid exclude pattern: %s", UXM_EXCLUDE_PATTERN);
  } else if (verbose) {
    syslog(LOG_INFO, "Ignoring pattern: %s", UXM_EXCLUDE_PATTERN);
  }

  /**
   * Loop on the monitored directories
   **/
  if(watch_applications) {
    monitored = uxm_get_monitored_directories();
    for(iter = monitored; iter; iter = iter->next) {
      if(!inotifytools_watch_recursively(iter->data, UXM_APPS_EVENTS)) {
        syslog(LOG_ERR, "Cannot watch %s: %s", (char*)iter->data, strerror(inotifytools_error()) );
      } else if (verbose) {
        syslog(LOG_INFO, "Watching %s", (char*)iter->data);
      }
    }
    uxm_gslist_free_full(monitored);
  }

  /**
   * Add a watch on $HOME
   **/
  if(watch_home) {
    if(!inotifytools_watch_file(home, UXM_BOOKMARKS_EVENTS)) {
      syslog( LOG_ERR, "%s: %s", home, strerror(inotifytools_error()) );
    } else {
      home_wd = inotifytools_wd_from_filename(home);
      if (verbose) {
        syslog(LOG_INFO, "Watching %s", home);
      }
    }
  }

  if(!inotifytools_get_num_watches()) {
    syslog(LOG_ERR, "Nothing to watch, aborting...");
    exit(EXIT_FAILURE);
  }

  /**
   * Main event loop
   * Output events as "<timestamp> <events> <path>"
   **/
  event = inotifytools_next_event(-1);
  while (event) {
    if (watch_home && event->wd == home_wd) {
      if (strcmp(event->name, UXM_RECENT_FILES_FILE) == 0) {
        msg = uxm_msg_new(UXM_MSG_TYPE_RECENT_FILE);
        if (verbose) {
          inotifytools_snprintf(message_buf, 256, event, "%T %e %w%f\n");
          msg->data = g_strdup(message_buf);
        }
        g_async_queue_push(data->queue, msg);
      } else if (strcmp(event->name, UXM_BOOKMARKS_FILE) == 0) {
        msg = uxm_msg_new(UXM_MSG_TYPE_BOOKMARK);
        if (verbose) {
          inotifytools_snprintf(message_buf, 256, event, "%T %e %w%f\n");
          msg->data = g_strdup(message_buf);
        }
        g_async_queue_push(data->queue, msg);
      }
    } else if (
        event->wd != home_wd
        && (
          g_str_has_suffix(event->name, UXM_DESKTOP_FILE_EXT)
          || g_str_has_suffix(event->name, UXM_DIRECTORY_FILE_EXT)
          || g_str_has_suffix(event->name, UXM_MENU_FILE_EXT)
        )
    ){
      msg = uxm_msg_new(UXM_MSG_TYPE_APPLICATION);
      if (verbose) {
        inotifytools_snprintf(message_buf, 256, event, "%T %e %w%f\n");
        msg->data = g_strdup(message_buf);
      }
      g_async_queue_push(data->queue, msg);
    }

    if (uxm_stop_event) break;
    event = inotifytools_next_event(-1);
  }
  
  g_async_queue_unref(data->queue);
  return 0;
}

gpointer uxm_monitor_listener(UxmSharedData *data)
{
  UxmMessage *msg;
  gint l;
  int types = 0;
  int verbose = data->flags & UXM_OPTS_VERBOSE;
  char command_buf[UXM_UPDATE_CMD_BUF_SIZE];

  g_async_queue_ref(data->queue);

  while(!uxm_stop_event) {
    l = g_async_queue_length(data->queue);
    /* There are messages in the queue ! */
    if(l > 0) {
      msg = (UxmMessage*) g_async_queue_try_pop(data->queue);
      /* Loop on every msg in the queue */
      while(msg) {
        types |= msg->type;
        if(verbose) {
          syslog(LOG_INFO, "%s", msg->data);
          /*g_printf("%s\n", msg->data);*/
          g_free(msg->data);
        }
        g_free(msg);
        msg = (UxmMessage*) g_async_queue_try_pop(data->queue);
      }

      g_snprintf(
        command_buf, UXM_UPDATE_CMD_BUF_SIZE,
        "%s -f %s", UXM_UPDATE_CMD_PREFIX, data->formatter
      );
      if(types & UXM_MSG_TYPE_APPLICATION) {
        strcat(command_buf, " -a");
      }    
      if(types & UXM_MSG_TYPE_BOOKMARK) {
        strcat(command_buf, " -b");
      }
      if(types & UXM_MSG_TYPE_RECENT_FILE) {
        strcat(command_buf, " -r");
      }
      g_printf("%s\n",command_buf);
      system(command_buf);

    } else {
      /**
       * Go to sleep only if we had no messages,
       * because updating takes some time,
       * and we want new messages processed immediately
       **/
      sleep(1);
    }
  }

  g_async_queue_unref(data->queue);
  return 0; 
}

UxmSharedData * uxm_shared_data_new(GAsyncQueue *queue, int flags, char *formatter)
{
  UxmSharedData *data = (UxmSharedData*) g_malloc(sizeof(UxmSharedData));
  if(!data) {
    g_printf("Could not allocate %d bytes for UxmSharedData\n", (int)sizeof(UxmSharedData));
    return NULL;
  }
  data->queue = queue;
  data->flags = flags;
  data->formatter = formatter;
  return data;
}

UxmMessage * uxm_msg_new(UxmMessageType type)
{
  UxmMessage *msg = (UxmMessage*) g_malloc(sizeof(UxmMessage));
  if(!msg) {
    g_printf("Could not allocate %d bytes for UxmMessage\n", (int)sizeof(UxmMessage));
    return NULL;
  }
  msg->type = type;
  return msg;
}

void uxm_cleanup(void)
{
  inotifytools_cleanup();
  syslog(LOG_INFO, "Exiting...");
  closelog();
}

void uxm_signal_handler(int signum)
{
  (void) signum;
  uxm_stop_event = 1;
  uxm_cleanup();
  exit(0);
}

GSList * uxm_get_monitored_directories(void)
{
  const gchar* const *data_dirs = g_get_system_data_dirs();
  const gchar* const *config_dirs = g_get_system_config_dirs();
  const gchar* user_data_dir = g_get_user_data_dir(); 
  const gchar* user_config_dir = g_get_user_config_dir();
  GSList *monitored = NULL;
  gchar *path;
  int i;

  for(i = 0; data_dirs[i]; i++) {
    path = g_build_path("/", data_dirs[i], "applications", NULL);
    if(uxm_path_is_dir(path)) {
      monitored = g_slist_prepend(monitored, path);
    }
    path = g_build_path("/", data_dirs[i], "desktop-directories", NULL);
    if(uxm_path_is_dir(path)) {
      monitored = g_slist_prepend(monitored, path);
    }
  }
  for(i = 0; config_dirs[i]; i++) {
    path = g_build_path("/", config_dirs[i], "menus", NULL);
    if(uxm_path_is_dir(path)) {
      monitored = g_slist_prepend(monitored, path);
    }
  }
  path = g_build_path("/", user_data_dir, "applications", NULL);
  if(uxm_path_is_dir(path)) monitored = g_slist_prepend(monitored, path);
  path = g_build_path("/", user_data_dir, "desktop-directories", NULL);
  if(uxm_path_is_dir(path)) monitored = g_slist_prepend(monitored, path);
  path = g_build_path("/", user_config_dir, "menus", NULL);
  if(uxm_path_is_dir(path)) monitored = g_slist_prepend(monitored, path);

  return monitored;
}

void uxm_gslist_free_full(GSList *list)
{
  if(!GLIB_CHECK_VERSION(2,28,0)) {
    GSList *iter;
    for(iter = list; iter; iter = iter->next) {
      g_free(iter->data);
    }
    g_slist_free(list);
  } else {
    g_slist_free_full(list, g_free);
  }
}

gboolean uxm_path_is_dir(const gchar *path)
{
  struct stat stat_buf;

  if(path == NULL || stat(path, &stat_buf) == -1) {
    return FALSE;
  }
  if(stat_buf.st_mode & S_IFDIR) {
    return TRUE;
  }
  return FALSE;
}
