import os, sqlite3, stat
import uxm.config as config

class Cache(object):

    def __init__(self):
        self.connection = None
        self.cursor = None
        self.db_file = config.CACHE_DB

    def get_connexion(self):
        return self.connection

    def get_cursor(self):
        return self.cursor

    def save(self):
        if self.connection.total_changes > 0:
            self.connection.commit()

    def close(self):
        self.save()
        self.connection.close()

    def open(self):
        if not os.path.isfile(self.db_file):
            os.mknod(self.db_file, 0755|stat.S_IFREG)
        if not isinstance(self.connection, sqlite3.Connection):
            self.connection = sqlite3.connect(self.db_file)
            self.connection.execute(
                """CREATE TABLE IF NOT EXISTS icons(key TEXT, path TEXT)"""
            )
            self.connection.execute(
                """CREATE TABLE IF NOT EXISTS i18n(key TEXT, translation TEXT)"""
            )
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()

    def get_icon(self, key):
        self.cursor.execute(
            'SELECT icons.key, icons.path FROM icons WHERE icons.key = ?',
            [key]
        )
        return self.cursor.fetchone()

    def add_icon(self, key, path):
        self.cursor.execute(
            'INSERT INTO icons(key, path) VALUES(?,?)',
            [key, path]
        )

    def get_translation(self, key):
        self.cursor.execute("""
    SELECT i18n.key, i18n.translation FROM i18n
    WHERE i18n.key = ?""",
            [key]
        )
        return self.cursor.fetchone()

    def add_translation(self, key, trans):
        self.cursor.execute(
            'INSERT INTO i18n(key, translation) VALUES(?,?)',
            [unicode(key), unicode(trans)]
        )


def clear():
    if os.path.isfile(config.CACHE_DB):
        os.remove(config.CACHE_DB)

