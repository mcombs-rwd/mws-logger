from datetime import datetime, timedelta

YMD_HMS = "%Y-%m-%d %H:%M:%S"

def valid_format(format: str) -> str:
    formats = ['csv', 'json', 'xml']
    default = 0
    print(type(format))
    if not format is None and format.lower() in formats:
        return format.lower()
    return formats[default]

def valid_mime(format: str) -> str:
    if format == "csv":
        return "text/csv"
    if format == "json":
        return "application/json"
    if format == "xml":
        return "application/xml"

def valid_sensor(sensor: str) -> str:
    sensors = ['green_roof', 'rain_gauge']
    default = 0
    if not sensor is None and sensor.lower() in sensors:
        return sensor.lower()
    return sensors[default]

def valid_start_date(start_date: str) -> str:
    global YMD_HMS
    try:
        start_date = datetime.fromisoformat(start_date).strftime(YMD_HMS)
    except:
        start_date = (datetime.now() - timedelta(days=7)).strftime(YMD_HMS)
    return start_date

def valid_stop_date(stop_date: str) -> str:
    global YMD_HMS
    try:
        stop_date = datetime.fromisoformat(stop_date).strftime(YMD_HMS)
    except:
        stop_date = datetime.now().strftime(YMD_HMS)
    return stop_date
