import click
from datetime import datetime, timedelta
from flask import current_app, g
from random import randrange
import sqlite3

"""Create and populate db

Enter `python -m flask --app water <command>`.
<command> can be `init-db` or `add-test-data`.
"""

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(add_test_command)

@click.command("init-db")
def init_db_command():
    db = get_db()
    with current_app.open_resource("./sql-statements/schema.sql") as f:
        db.executescript(f.read().decode("utf-8"))
    click.echo("You have initialized the database.")
    click.echo("You can load test data with `add-test-data`.")

@click.command("add-test-data")
def add_test_command():
    start_date = datetime.fromisoformat("2024-03-01 00:00:00") # yyyy-mm-dd hh:mm:ss
    db = get_db()
    for sensor in ['green_roof', 'rain_gauge']:
        meter_value = 0
        for days in range(61):
            for hours in range(24):
                logged_date = start_date + timedelta(days=days, hours=hours)
                gauge_value = randrange(0, 50, 1)
                meter_value += gauge_value
                db.execute(
                    "INSERT INTO water (logged_date, sensor, gauge_value, meter_value) VALUES (?, ?, ?, ?)",
                    (logged_date.isoformat(sep=" "), sensor, gauge_value, meter_value)
                )
    db.commit()
    click.echo("You have loaded test data into the database!")

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()
