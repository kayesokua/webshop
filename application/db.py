import sqlite3

import click
from flask import current_app
from flask import g

from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash


import os
import urllib.parse as up
import psycopg2

up.uses_netloc.append("postgres")
url = up.urlparse(os.environ["DATABASE_URL"])
conn = psycopg2.connect(database=url.path[1:],
user=url.username,
password=url.password,
host=url.hostname,
port=url.port
)

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"], detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
       
        db.executescript(f.read().decode('utf8'))

def create_admin():
    db = get_db()

    username = input("username?")
    password = input("password?")
    password2 = input("confirm password?")
    is_active = True
    is_admin = True
    error = None

    if password != password2:
        error = "Passwords do not match"

    if error is None:
        try:
            db.execute("INSERT INTO user (username, password, is_active, is_admin) VALUES (?, ?, ?, ?)",(username, generate_password_hash(password), is_active, is_admin),)
            db.commit()
        except db.IntegrityError:
            error = print("Username has already been used")
        else:
            return print("Admin has successfully created")

@click.command("test-db")
def test_db_command():
    result = get_db()
    click.echo(result)

@click.command("init-db")
def init_db_command():
    init_db()
    
    click.echo("Initialized the database.")

@click.command("create-admin")
def create_admin_command():
    create_admin()
    
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(create_admin_command)
    app.cli.add_command(test_db_command)
