import os, sqlite3, stat, atexit
from collections import OrderedDict
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
            self.connection.executescript("""
CREATE TABLE IF NOT EXISTS icon(
    name TEXT NOT NULL,
    theme TEXT NOT NULL,
    size INTEGER NOT NULL,
    path TEXT UNIQUE NOT NULL,
    symlink TEXT UNIQUE
);
CREATE UNIQUE INDEX IF NOT EXISTS name_theme_size_idx
    ON icon(name, theme, size);

CREATE TABLE IF NOT EXISTS mimetype(
    type TEXT UNIQUE NOT NULL
);
CREATE INDEX IF NOT EXISTS mime_type_idx
    ON mimetype(type);

CREATE TABLE IF NOT EXISTS icon_mime(
    icon_id INTEGER REFERENCES icon(rowid),
    mimetype_id INTEGER REFERENCES mimetype(rowid)
);
CREATE INDEX IF NOT EXISTS icon_mime_idx
    ON icon_mime(icon_id,mimetype_id);

CREATE TABLE IF NOT EXISTS i18n(
    key TEXT UNIQUE NOT NULL,
    translation TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS i18n_key_idx ON i18n(key);
"""
            )
            self.connection.row_factory = sqlite3.Row
            self.cursor = self.connection.cursor()
        return self

    def query(self, query, params):
        self.cursor.execute(query, params)
        return self

    def find_one_by_name(self, name, theme, size):
        q = """
SELECT i.rowid AS icon_id, i.name, i.theme, i.size, i.path, i.symlink
FROM icon i
WHERE i.name = ? AND i.theme = ? AND i.size = ?
"""
        return self.cursor.execute(
            q, (name, theme, size)
        ).fetchone()

    def find_one_by_mime_type(self, mimetype, theme, size):
        q = """
SELECT
    i.rowid AS icon_id, i.name, i.path, i.symlink,
    im.icon_id AS im_icn_id, im.mimetype_id AS im_mt_id,
    m.rowid AS mimetype_id, m.type AS mimetype
FROM mimetype m
JOIN icon_mime im
    ON m.rowid = im.mimetype_id
JOIN icon i
    ON i.rowid = im.icon_id
WHERE m.type = ? AND i.theme = ? AND i.size = ?
"""
        row = self.cursor.execute(q, (mimetype, theme, size)).fetchone()
        if not row:
            return
        return {k:row[k] for k in row.keys() if k not in ('im_mt_id','im_icn_id')}

    def find_one_by_name_with_mimetypes(self, name, theme, size):
        q = """
SELECT
    i.rowid AS icon_id, i.name, i.theme, i.size, i.path, i.symlink,
    im.icon_id AS im_icn_id, im.mimetype_id AS im_mt_id,
    m.rowid AS mimetype_id, m.type AS mimetype
FROM icon i
JOIN icon_mime im
    ON im.icon_id = i.rowid
JOIN mimetype m
    ON im.mimetype_id = m.rowid
WHERE name = ? AND theme = ? AND size = ?
"""
        rows = self.cursor.execute(q, (name, theme, size)).fetchall()
        icons = OrderedDict()
        for row in rows:
            icn_id = row['icon_id']
            if icn_id not in icons:
                icons[icn_id] = {
                    k:row[i] for i,k in enumerate(row.keys()) if k not in (
                        'im_icn_id', 'im_mt_id', 'mimetype_id', 'mimetype')
                    }
                icons[icn_id]['mimetypes'] = []
            if row['mimetype']:
                icon = icons[icn_id]
                icon['mimetypes'].append({
                    'id': row['mimetype_id'],
                    'name': row['mimetype']
                })
        return icons

    def find_by_mime_type(self, mimetype, theme, size):
        q = """
SELECT
    i.rowid AS icon_id, i.name, i.theme, i.size, i.path, i.symlink,
    im.icon_id AS im_icn_id, im.mimetype_id AS im_mt_id,
    m.rowid AS mimetype_id, m.type AS mimetype
FROM mimetype m
JOIN icon_mime im
    ON m.rowid = im.mimetype_id
JOIN icon i
    ON i.rowid = im.icon_id
WHERE m.type = ? AND i.theme = ? AND i.size = ?
"""
        rows = self.cursor.execute(q, (mimetype, theme, size)).fetchall()
        if not rows:
            return
        mimetypes = OrderedDict()
        for row in rows:
            mime_id = row['mimetype_id']
            if mime_id not in mimetypes:
                mimetypes[mime_id] = {
                    'id': mime_id, 'mimetype': row['mimetype'],
                    'icons': []
                }
            if row['icon_id']:
                mimetype = mimetypes[mime_id]
                mimetype['icons'].append({
                    'id': row['icon_id'],
                    'name': row['name'],
                    'path': row['path'],
                    'symlink': row['symlink']
                })
        return mimetypes

    def save_icon(self, name, theme, size, path, symlink=None, mimetype=None):
        q = "INSERT INTO icon(name,theme,size,path,symlink) VALUES(?,?,?,?,?)"
        self.cursor.execute(q, (name,theme,size,path,symlink))
        icon_id = self.cursor.lastrowid
        if not mimetype:
            return
        m = self.cursor.execute(
            "SELECT * FROM mimetype m WHERE m.type = ?",
            (mimetype,)
        ).fetchone()
        if m is None:
            self.cursor.execute("INSERT INTO mimetype(type) VALUES(?)",
                    (mimetype,))
            mt_id = self.cursor.lastrowid
        else:
            mt_id = m['rowid']
        self.cursor.execute("""
            INSERT INTO icon_mime(icon_id,mimetype_id) VALUES(?,?)""",
            (icon_id, mt_id)
        )

    def update_icon(self, obj, **kwargs):
        mimetype = kwargs.pop('mimetype', None)
        # first update the icon
        if len(kwargs) > 0:
            columns, values = kwargs.keys(), kwargs.values()
            query = "UPDATE icon SET %s" % ','.join(["%s = ?" % col for col in columns])
            query += " WHERE icon.rowid = ?"
            values.append(obj['icon_id'])
            self.cursor.execute(query, values)
        # then mimetype
        if not mimetype:
            return
        if 'mimetype' in obj and obj['mimetype'] == mimetype:
            return
        m = self.cursor.execute(
            "SELECT * FROM mimetype m WHERE m.type = ?",
            (mimetype,)
        ).fetchone()
        if m is None:
            self.cursor.execute("INSERT INTO mimetype(type) VALUES(?)",
                    (mimetype,))
            mt_id = self.cursor.lastrowid
        else:
            mt_id = m['rowid']
        self.cursor.execute("""
            INSERT INTO icon_mime(icon_id,mimetype_id) VALUES(?,?)""",
            (obj['icon_id'], mt_id)
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
        return self


__cache = None

def open():
    global __cache
    if __cache is None:
        __cache = Cache().open()
    return __cache

@atexit.register
def close():
    if __cache:
        __cache.close()

def clear():
    if os.path.isfile(config.CACHE_DB):
        os.remove(config.CACHE_DB)
    for root, dirs, files in os.walk(config.ICON_CACHE_PATH, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
