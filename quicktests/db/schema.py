import os
import stat
import sqlite3
from collections import OrderedDict

__DIR__ = os.path.dirname(os.path.abspath(__file__))
DB_FILE = __DIR__+'/schema_test.db'

if os.path.isfile(DB_FILE):
    os.remove(DB_FILE)
    os.mknod(DB_FILE, 0755 | stat.S_IFREG)

con = sqlite3.connect(DB_FILE)
con.row_factory = sqlite3.Row
cur = con.cursor()
con.executescript("""
CREATE TABLE icon(
    name TEXT,
    theme TEXT,
    size INTEGER,
    path TEXT UNIQUE,
    symlink TEXT UNIQUE
);
CREATE UNIQUE INDEX icon_name_theme_size_idx ON icon(name, theme, size);
CREATE TABLE mimetype(
    type TEXT UNIQUE
);
CREATE UNIQUE INDEX mimetype_type_idx ON mimetype(type);
CREATE TABLE icon_mime(
    icon_id INTEGER REFERENCES icon(rowid),
    mimetype_id INTEGER REFERENCES mimetype(rowid)
);
CREATE INDEX icon_mime_idx ON icon_mime(icon_id,mimetype_id);
""")


class QueryBuilder(object):
    """Super minimal SQL query builder"""
    def __init__(self, con):
        self.connection = con
        self.cursor = con.cursor()
        self.query = ""
        self.selects = []
        self.froms = []
        self.wheres = []
        self.joins = []
        self.params = []
    
    def get_query(self):
        if not self.query:
            self.query = self.build()
        return self.query

    def execute(self):
        self.cursor.execute(self.get_query(), self.params)
        return self
    def fetchone(self):
        return self.cursor.fetchone()
    def fetchall(self):
        return self.cursor.fetchall()

    def add_select(self, sel):
        self.selects.append(sel)
        return self
    def add_from(self, frm):
        self.froms.append(frm)
        return self
    def add_where(self, wr, params=[]):
        self.wheres.append(wr)
        if not hasattr(params, '__iter__'):
            params = [params]
        self.params.extend(params)
        return self
    def add_join(self, jn, cond, params=[]):
        self.joins.append("JOIN %s ON %s" % (jn, cond))
        if not hasattr(params, '__iter__'):
            params = [params]
        self.params.extend(params)
        return self
    def insert(self, into, params=[]):
        if not hasattr(params, '__iter__'):
            params = [params]
        self.query = "INSERT INTO %s VALUES(%s)" % (into,
                ','.join(['?']*len(params)))
        self.params = params
        return self
    def update(self, table, cols, params):
        if not hasattr(params, '__iter__'):
            params = [params]
        query = "UPDATE %s SET %s" % (table,
                ','.join(["%s = ?" % col for col in cols]))
        self.params.extend(params)

    def build(self):
        query = ""
        if self.selects:
            query = "SELECT "
            query += ','.join(self.selects)
            if self.froms:
                query += "\nFROM "
                query += ','.join(self.froms)
            if self.joins:
                query += "\n"
                query += " ".join(self.joins)
        elif self.updates:
            pass
        elif self.inserts:
            query = "INSERT INTO %s VALUES(%s)"
        if self.wheres:
            query += "\nWHERE "
            query += self.wheres.pop(0)
            query += ''.join([" AND %s" % w for w in self.wheres])
        return query

def find_by_name(name, **kwargs):
    q = QueryBuilder(con)
    q.add_select('i.*, i.rowid AS icon_id').add_from('icon i').add_where('i.name = ?', name)
    q.add_select('im.icon_id AS im_icn_id, im.mimetype_id AS im_mt_id')
    q.add_join('icon_mime im', 'im.icon_id = i.rowid')
    q.add_select('m.type, m.rowid AS mt_id').add_join('mimetype m', 'im.mimetype_id = m.rowid')
    for k, v in kwargs.iteritems():
        q.add_where('i.%s = ?' % k, v)
    rows = q.execute().fetchall()
    icons = OrderedDict()
    for row in rows:
        icn_id = row['icon_id']
        if icn_id not in icons:
            icons[icn_id] = {
                k:row[i] for i,k in enumerate(row.keys()) if k not in (
                    'type', 'rowid', 'im_icn_id', 'im_mt_id', 'mt_id'
                )
            }
            icons[icn_id]['mimetypes'] = []
        if row['type']:
            icon = icons[icn_id]
            icon['mimetypes'].append(row['type'])
    return icons

def find_by_mimetype(mimetype, **kwargs):
    q = QueryBuilder(con)
    q.add_select('i.*, i.rowid AS icon_id').add_from('icon i').add_where('m.type = ?', mimetype)
    q.add_select('im.icon_id AS im_icn_id, im.mimetype_id AS im_mt_id')
    q.add_join('icon_mime im', 'im.icon_id = i.rowid')
    q.add_select('m.type, m.rowid AS mt_id').add_join('mimetype m', 'im.mimetype_id = m.rowid')
    for k, v in kwargs.iteritems():
        q.add_where('i.%s = ?' % k, tuple(v))
    rows = q.execute().fetchall()
    icons = OrderedDict()
    for row in rows:
        icn_id = row['icon_id']
        if icn_id not in icons:
            icons[icn_id] = {
                k:row[i] for i,k in enumerate(row.keys()) if k not in (
                    'type', 'rowid', 'im_icn_id', 'im_mt_id', 'mt_id'
                }
            icons[icn_id]['mimetypes'] = []
        if row['type']:
            icon = icons[icn_id]
            icon['mimetypes'].append(row['type'])
    return icons



def add_icon(**kwargs):
    q = QueryBuilder(con)
    mimetypes = False
    if 'mimetypes' in kwargs:
        mimetypes = kwargs.pop('mimetypes')
    q.insert('icon(%s)' % ','.join(kwargs.keys()), kwargs.values())
    print q.get_query(), q.params
    q.execute()
    lastrowid = cur.lastrowid
    print lastrowid
    if not mimetypes: return lastrowid
    for t in mimetypes:
        q = QueryBuilder(con)
        #q.add_select('i.rowid').add_from('icon i').add_where('rowid = ?', lastrowid)
        #icon = q.execute().fetchone()
        #q = QueryBuilder(con)
        q.insert('mimetype(type,icon_id)', (t, lastrowid))
        q.execute()
    return lastrowid


data = [
    {
        'name': 'text-plain',
        'theme': 'gnome-colors-statler', 'size': 32,
        'path': '/home/ju1ius/.cache/uxdgmenu/icons/text-plain.png',
        'mimetypes': ['text/plain','text/x-python','text/x-php']
    },
    {
        'name': 'image-png',
        'theme': 'gnome-colors-statler', 'size': 32,
        'path': '/home/ju1ius/.cache/uxdgmenu/icons/image-png.png',
        'mimetypes': ['image/png']
    },
    {
        'name': 'text-plain',
        'theme': 'gnome-colors', 'size': 24,
        'path': '/home/ju1ius/.cache/uxdgmenu/icons/text-plain_24x24.png',
        'mimetypes': ['text/plain']
    },
]
for d in data:
    icn = find_by_name(d['name'], theme=d['theme'], size=d['size'])
    if not icn:
        print d
        add_icon(**d)
#for d in data:
    #cur.execute("SELECT * FROM icon WHERE name = ?", (d['name'],))
    #icon = cur.fetchone()
    #if not icon:
        #cur.execute("INSERT INTO icon(name,theme,size,path) VALUES(?,?,?,?)",
                #(d['name'],d['theme'],d['size'],d['path']))
        #cur.execute("SELECT id FROM icon WHERE name = ?", (d['name'],))
        #icon = cur.fetchone()
    #cur.execute("INSERT INTO mimetype(type,icon_id) VALUES(?,?)",
                #(d['type'], icon['id']))

con.commit()



query = QueryBuilder(con).add_select('i.*,mt.*').add_select(
    'i.id AS i_id, mt.id AS mt_id'
).add_from('icon i').add_join(
    'mimetype mt', 'mt.icon_id = i.id'
)
print query.get_query()
query.execute()
rows = query.fetchall()

#cur.execute("""
#SELECT i.*, mt.*, i.id AS i_id, mt.id AS mt_id
#FROM icon i
#INNER JOIN mimetype mt ON mt.icon_id = i.id
#""")
icons = {}
for row in rows:
    icon_id = row['i_id']
    if icon_id not in icons:
        icons[icon_id] = {
            'name': row['name'],
            'theme': row['theme'], 'size': row['size'],
            'path': row['path'], 'symlink': row['symlink'],
            'types': []
        }
    icon = icons[icon_id]
    icon['types'].append(row['type'])

for icon in icons.itervalues():
    print icon

