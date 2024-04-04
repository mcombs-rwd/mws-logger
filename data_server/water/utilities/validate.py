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
