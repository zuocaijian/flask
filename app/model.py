# -*- coding:utf-8 -*-

"""
author:zcj
create:2017.11.23
fun:
"""

import sqlite3

from app import app


def connect():
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    with app.app_context():
        with app.open_resource('schema.sql', 'r') as f:
            db = connect()
            db.cursor().executescript(f.read())
            db.commit()


if __name__ == '__main__':
    init_db()
