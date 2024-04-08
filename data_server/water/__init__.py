from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
import os
# import sqlalchemy
# import sqlite3

from water import errors, pages

load_dotenv()

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

def create_app():
    # app.logger.setLevel("INFO")
    app = Flask(__name__)
    app.config.from_prefixed_env()
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    db.init_app(app)
    app.register_blueprint(pages.bp)
    app.register_error_handler(404, errors.page_not_found)
    # app.logger.debug(f"Using database: {os.getenv('FLASK_DATABASE')}")
    # app.logger.debug(f"{sqlite3.sqlite_version=}")
    # app.logger.debug(f"{sqlalchemy.__version__=}")

    return app
