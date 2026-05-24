import sqlite3
import os
from flask import g, current_app

DATABASE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'staysync.db')

def get_db():
    """Get or create sqlite3 database connection for the current application context."""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        # Enable foreign key support in SQLite (disabled by default)
        db.execute("PRAGMA foreign_keys = ON;")
    return db

def close_db(e=None):
    """Close the database connection if it exists."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    """Initialize the database with the schema defined in database/schema.sql."""
    db = get_db()
    schema_path = os.path.join(current_app.root_path, 'database', 'schema.sql')
    with open(schema_path, mode='r', encoding='utf-8') as f:
        db.executescript(f.read())
    db.commit()

def query_db(query, args=(), one=False):
    """Convenience helper to query the database and fetch results."""
    db = get_db()
    cur = db.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def insert_db(query, args=()):
    """Convenience helper to insert/update database and return the last row ID."""
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    lastrowid = cur.lastrowid
    cur.close()
    return lastrowid

def update_db(query, args=()):
    """Convenience helper to execute an update/delete query and commit changes."""
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    rowcount = cur.rowcount
    cur.close()
    return rowcount
