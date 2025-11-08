# -*- coding: utf-8 -*-
"""
    Flaskr
    ~~~~~~

    A microblog example application written as Flask tutorial with
    Flask and sqlite3.

    :copyright: (c) 2015 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import os
from sqlite3 import dbapi2 as sqlite3
from flask import Flask, request, g, redirect, url_for, render_template, flash


# create our little application :)
app = Flask(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


def init_db():
    """Initializes the database."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Creates the database tables."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def show_entries():
    db = get_db()
    category = request.args.get('category')
    if category:
        cur = db.execute('select id,title, text, categories from entries where categories = ?',(category,))
    else:
        cur = db.execute('select id,title, text, categories from entries order by id desc')
    entries = cur.fetchall()

    curr = db.execute('select Distinct categories from entries')
    categories = [row["categories"] for row in curr.fetchall()]
    return render_template('show_entries.html', entries=entries, categories=categories,selected=category)


@app.route('/add', methods=['POST'])
def add_entry():
    db = get_db()
    db.execute('insert into entries (title, text, categories) values (?, ?, ?)',
               [request.form['title'], request.form['text'], request.form['categories']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))

@app.route("/delete/<int:entry_id>", methods=["POST","GET"])
def delete_entry(entry_id):
    db = get_db()
    db.execute('delete from entries where id = ?', (entry_id,))
    db.commit()
    flash('Entry deleted successfully.')
    return redirect(url_for('show_entries'))

@app.route("/edit/<int:entry_id>", methods=["POST","GET"])
def edit_entry(entry_id):
    db = get_db()
    title = request.form["title"]
    text = request.form["text"]
    categories = request.form["category"]
    db.execute('UPDATE entries Set title = ?, text = ?, categories = ?'
               ' where id = ?', (title, text, categories,entry_id))
    db.commit()
    flash("Entry edited succesfully")
    return redirect(url_for("show_entries"))