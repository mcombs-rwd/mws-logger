from flask import current_app
from sqlalchemy import select, extract
from datetime import datetime, timedelta

from water.models import Water_reading, Sensor
from water.database import get_db

"""About time and samples

I use the SNMP definitions of counters and gauges.

Gauges have a rate, and the measurement is valid at the time it is observed.
If the speedometer reads 60 mph and you check it hourly, you don't know if
the car traveled 60 mph, it may have stopped immediately after the sample.
To get a more accurate value for distance, sample more often.

Counters are cumulative but it takes two samples to determine the value.
If a odometer reads 15000 at 8am and 15060 at 9am, then the distance is
60 miles and the rate was 60 mph.

When calculating flow for the day with meters:
* The 00:00 sample is the gallons at the start of the day
* The 23:59 sample is gallons at the end of the day
Since we don't log 23:59, we use the 00:00 sample from the next day.
"""


def hourly_detail(sensor: str, start_date: datetime, stop_date: datetime) -> list[Water_reading]:
    """Get hourly measurements for n days. Day is always 00:00:00 to 23:59:00"""
    current_app.logger.info(f"hourly_detail: {sensor=}, {start_date=}")
    start = datetime.fromisoformat(start_date)
    stop = datetime.fromisoformat(stop_date) + timedelta(days=1, seconds=-1)
    current_app.logger.info(f"{start=}, {stop=}")
    session = get_db()
    details = session.execute(
        select(Water_reading)
        .filter(Water_reading.sensor_id==sensor)
        .filter(Water_reading.date >= start)
        .filter(Water_reading.date <= stop)
    )
    results=[detail["Water_reading"] for detail in details.mappings().all()]
    current_app.logger.info(f"Query results={len(results)}")
    return results

def daily_total_meter(sensor: str, start_date: datetime, stop_date: datetime) -> list[Water_reading]:
    """Get total of values, per day, for n days"""
    current_app.logger.info(f"hourly_detail: {sensor=}, {start_date=}")
    start = datetime.fromisoformat(start_date)
    stop = datetime.fromisoformat(stop_date) + timedelta(days=1, seconds=-1)
    current_app.logger.info(f"{start=}, {stop=}")
    session = get_db()
    details = session.execute(
        select(Water_reading)
        .filter( Water_reading.sensor_id=='green_roof')
    )
    results=[detail["Water_reading"] for detail in details.mappings().all()]
    current_app.logger.info(f"Query results={len(results)}")
    return results

def monthly_total_meter():
    pass

def daily_total_gauge(sensor, start_date):
    """Add up all hourly measurements, per day, for n days

    A gauge shows current value, a meter shows cumulative.
    This adds up all hourly measurements for the day.
    """
    start_date = f"{start_date} 00:00:00"
    stop_date = f"{start_date+1} 00:00:00"
    query = (
        "SELECT logged_date, sensor, gauge_value "
        "FROM water "
        f"WHERE sensor = \"{sensor}\" "
        f"AND logged_date >= \"{start_date}\" "
        f"AND logged_date <= \"{stop_date}\" "
        "ORDER BY logged_date ASC"
    )
    return query


def monthly_total_gauge():
    pass
