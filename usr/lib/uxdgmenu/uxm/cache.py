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
        return self

    def close(self):
        self.save()
        self.connection.close()

    def open(self):
        if not os.path.isfile(self.db_file):
            os.mknod(self.db_file, 0755|stat.S_IFREG)
        if not isinstance(self.connection, sqlite3.Connection):
            self.connection = sqlite3.connect(self.db_file)
            self.connection.execute("""
CREATE TABLE IF NOT EXISTS icons(
    name TEXT,
    theme TEXT,
    size INTEGER,
    path TEXT
)"""
            )
            self.connection.execute(
                """CREATE TABLE IF NOT EXISTS i18n(key TEXT, translation TEXT)"""
            )
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()
        return self

    def get_icon(self, name, theme=None, size=None):
        query = "SELECT * FROM icons WHERE icons.name = ?"
        params = [name]
        if theme:
            query += " AND icons.theme = ?"
            params.append(theme)
        if size:
            query += " AND icons.size = ?"
            params.append(size)
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def add_icon(self, name, theme, size, path):
        self.cursor.execute(
            'INSERT INTO icons(name, theme, size, path) VALUES(?,?,?,?)',
            [name, theme, size, path]
        )
        return self

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
        return self


def clear():
    if os.path.isfile(config.CACHE_DB):
        os.remove(config.CACHE_DB)
    for root, dirs, files in os.walk(config.ICON_CACHE_PATH, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
