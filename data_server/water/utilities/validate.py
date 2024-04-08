from datetime import datetime, timedelta

YMD_HMS = "%Y-%m-%d %H:%M:%S"

def valid_format(format: str) -> str:
    formats = ['csv', 'json', 'xml']
    return select_in_list(format, formats, 'csv')

def valid_mime(format: str) -> str:
    if format == "csv":
        return "text/csv"
    if format == "json":
        return "application/json"
    if format == "xml":
        return "application/xml"

def valid_sensor(sensor: str) -> str:
    sensors = ['green_roof', 'rain_gauge']
    return select_in_list(sensor, sensors, 'rain_gauge')

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

def valid_resolution(resolution: str) -> str:
    # IDEA: Change to by_hour, by_day, by_month
    resolutions = ['hourly', 'daily', 'weekly', 'monthly']
    return select_in_list(resolution, resolutions, 'hourly')

def select_in_list(item: str, items: list, default: str = '') -> str:
    if not item is None and item.lower() in items:
        return item.lower()
    return default
