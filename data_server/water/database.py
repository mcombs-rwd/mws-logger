import click
from datetime import datetime, timedelta
from flask import current_app, g
from pathlib import Path
from random import randrange
import sqlite3
import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker

from models import (Base, Water_reading, Sensor)

"""Create and populate db

Enter `python -m flask --app water <command>`.
<command> can be `init-db` or `add-test-data`.
"""

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db)
    # app.cli.add_command(add_test_data)

# @click.command("init-db")
def init_db():
    db_filepath = Path("water.sqlite")
    if db_filepath.exists():
        db_filepath.unlink()

    engine = sa.create_engine("sqlite:///" + str(db_filepath), echo=True)
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    click.echo("You have initialized the database.")
    click.echo("You can load test data with `add-test-data`.")

# # @click.command("add-test-data")
# def add_test_data():
#     start_date = datetime.fromisoformat("2024-03-01 00:00:00") # yyyy-mm-dd hh:mm:ss
#     water_meter = Sensor(id="green_roof", name="Green Roof", )
#     db = get_db()
#     for sensor in ['green_roof', 'rain_gauge']:
#         meter_value = 0
#         for days in range(61):
#             for hours in range(24):
#                 logged_date = start_date + timedelta(days=days, hours=hours)
#                 gauge_value = randrange(0, 50, 1)
#                 meter_value += gauge_value
#                 db.execute(
#                     "INSERT INTO water (logged_date, sensor, gauge_value, meter_value) VALUES (?, ?, ?, ?)",
#                     (logged_date.isoformat(sep=" "), sensor, gauge_value, meter_value)
#                 )
#     db.commit()
#     click.echo("You have loaded test data into the database!")

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

if __name__ == "__main__":
    init_db_command()
