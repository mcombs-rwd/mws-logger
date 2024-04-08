from dotenv import load_dotenv
from flask import Flask
import os
import sqlalchemy
import sqlite3

import database, errors, pages

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config.from_prefixed_env()
    # app.logger.setLevel("INFO")
    app.logger.debug(f"Using database: {os.getenv('FLASK_DATABASE')}")
    app.logger.debug(f"{sqlite3.sqlite_version=}")
    app.logger.debug(f"{sqlalchemy.__version__=}")
    app.register_blueprint(pages.bp)
    app.register_error_handler(404, errors.page_not_found)
    database.init_app(app)

    return app
