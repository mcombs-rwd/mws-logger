from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, current_app

from water.database import get_db
bp = Blueprint("pages", __name__)


@bp.route("/")
def home():
    return render_template("pages/home.html")


@bp.route("/help")
def help():
    return render_template("pages/help.html")


@bp.route("/rain-api", methods=["GET"])
def rain_api():
    # TODO: Add 'summary' option to API
    db = get_db()
    query = build_query(request)
    observations = db.execute(query).fetchall()
    if not observations:
        return render_template("pages/error.html",
                error_message="No data found.")
    format = request.args.get('format', 'CSV').lower()
    if format == 'csv':
        return render_template("exports/csv.html", observations=observations)
    elif format == 'json':
        return render_template("exports/json.html", observations=observations)
    elif format == 'xml':
        return render_template("exports/xml.html", observations=observations)
    else:
        return render_template("pages/error.html",
                error_message=f"Incorrect output format: {format}")


def build_query(request):
    sensor = request.args.get('sensor', 'green_roof')
    # TODO: Add interval to query
    # TODO: Add start & stop date to query
    interval = request.args.get('interval', 'day')
    start_date = request.args.get('start', datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d %H:%M")
    end_date = request.args.get('stop', datetime.now()).strftime("%Y-%m-%d %H:%M")
    current_app.logger.info(f"Export data.")
    current_app.logger.info(f"{interval=}, {start_date=}, {end_date=}")
    query = (
        "SELECT logged_date, sensor, measurement "
        "FROM water "
        f"WHERE sensor = '{sensor}' "
        "ORDER BY logged_date ASC"
    )
    current_app.logger.info(f"{query=}")
    return query
