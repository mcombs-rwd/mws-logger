from datetime import date, datetime, timedelta
from flask import (Blueprint, current_app, render_template, 
                request, make_response)

from water.utilities.validate import valid_format, valid_mime, valid_sensor
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
    format = valid_format(request.args.get('format'))
    output = render_template(f"exports/{format}.html", observations=observations)
    resp = make_response(output)
    resp.mimetype = valid_mime(format)
    return resp


def build_query(request):
    YMD_HMS = "%Y-%m-%d %H:%M:%S"
    sensor = valid_sensor(request.args.get('sensor'))
    start_date = request.args.get('start', default='', type=str)
    try:
        start_date = datetime.fromisoformat(start_date).strftime(YMD_HMS)
    except:
        start_date = (datetime.now() - timedelta(days=7)).strftime(YMD_HMS)
    end_date = request.args.get('stop', default='', type=str)
    try:
        end_date = datetime.fromisoformat(end_date).strftime(YMD_HMS)
    except:
        end_date = datetime.now().strftime(YMD_HMS)
    current_app.logger.info(f"Export data.")
    # TODO: Add interval to query
    interval = request.args.get('interval', 'day')
    current_app.logger.info(f"{interval=}, {start_date=}, {end_date=}")
    query = (
        "SELECT logged_date, sensor, measurement "
        "FROM water "
        f"WHERE sensor = \"{sensor}\" "
        f"AND logged_date >= \"{start_date}\" "
        f"AND logged_date <= \"{end_date}\" "
        "ORDER BY logged_date ASC"
    )
    current_app.logger.info(f"{query=}")
    return query
