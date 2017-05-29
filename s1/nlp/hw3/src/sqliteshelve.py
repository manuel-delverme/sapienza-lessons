# sqliteshelve module
import pickle, sqlite3, os


class Shelf(object):
    """ Hackified Shelf class with sqlite3 """

    def __init__(self, dbpath):
        """ Opens or creates an existing sqlite3_shelf"""

        self.db = sqlite3.connect(dbpath)
        # create shelf table if it doesn't already exist
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM sqlite_master WHERE type = 'table' AND tbl_name = 'shelf'")
        rows = cursor.fetchall()
        if len(rows) == 0:
            cursor.execute(
                "CREATE TABLE shelf (id INTEGER PRIMARY KEY AUTOINCREMENT, key_str TEXT, value_str TEXT, UNIQUE(key_str))")
        cursor.close()

    def __setitem__(self, key, value):
        """ Sets an entry for key to value using pickling """
        pdata = pickle.dumps(value, pickle.HIGHEST_PROTOCOL)
        curr = self.db.cursor()
        curr.execute("INSERT OR REPLACE INTO shelf (key_str,value_str) VALUES (:key,:value)",
                     {'key': key, 'value': sqlite3.Binary(pdata)})
        curr.close()

    def get(self, key, default_value):
        """ Returns an entry for key """
        curr = self.db.cursor()
        curr.execute("SELECT value_str FROM shelf WHERE key_str = :key", {'key': key})
        result = curr.fetchone()
        curr.close()
        if result:
            return pickle.loads(result[0])
        else:
            return default_value

    def __getitem__(self, key):
        """ Returns an entry for key """
        curr = self.db.cursor()
        curr.execute("SELECT value_str FROM shelf WHERE key_str = :key", {'key': key})
        result = curr.fetchone()
        curr.close()
        if result:
            return pickle.loads(result[0])
        else:
            raise KeyError("Key: %s does not exist." % key)

    def keys(self):
        """ Returns list of keys """
        curr = self.db.cursor()
        curr.execute('SELECT key_str FROM shelf')
        keylist = [row[0] for row in curr]
        curr.close()
        return keylist

    def __contains__(self, key):
        """
          implements in operator
          if <key> in db
       """
        return key in list(self.keys())

    def __iter__(self):
        return iter(list(self.keys()))

    def __len__(self):
        """ Returns number of entries in shelf """
        return len(list(self.keys()))

    def __delitem__(self, key):
        """ Deletes an existing item. """
        curr = self.db.cursor()
        curr.execute("delete from shelf where key_str = '%s'" % key)
        curr.close()

    def close(self):
        """
        Closes database and commits changes
      """
        self.db.commit()


def open(dbpath):
    """ Creates and returns a Shelf object """
    return Shelf(dbpath)


def close(db):
    """
      commits changes to the database
    """
    db.close()
