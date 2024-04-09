from flask import current_app
from sqlalchemy import func, select
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


# IDEA: If date isn't in db, return error or closest match?

##########
# Utilities
##########

def calc_day_start(date_and_time: datetime) -> datetime:
    """This returns the start of the day. This might not be in the db."""
    return datetime.fromisoformat(date_and_time).replace(
        hour=0, minute=0, second=0, microsecond=0)

def calc_day_end(date_and_time: datetime) -> datetime:
    """This returns the end of the day. This might not be in the db."""
    return datetime.fromisoformat(date_and_time) + timedelta(days=1, seconds=-1)

def first_real_date(sensor: str, date_min: datetime) -> datetime:
    """Find exact earliest qualified date in the db"""
    day_start = calc_day_start(date_min)
    with get_db() as session:
        result = session.scalar(
            select(func.min(Water_reading.date))
            .filter(Water_reading.sensor_id == sensor)
            .filter(Water_reading.date >= day_start)
        )
    return result

def last_real_date(sensor: str, date_max: datetime) -> datetime:
    """Find exact last qualified date in the db"""
    day_end = calc_day_end(date_max)
    with get_db() as session:
        result = session.scalar(
            select(func.max(Water_reading.date))
            .filter(Water_reading.sensor_id == sensor)
            .filter(Water_reading.date <= day_end)
        )
    return result        

##########
# Queries
##########

def detail_by_hour(sensor: str, start_date: datetime, stop_date: datetime) -> list[Water_reading]:
    """Get hourly measurements for n days. Day is always 00:00:00 to 23:59:00"""
    current_app.logger.info(f"detail_by_hour: {sensor=}, {start_date=}")
    start = first_real_date(sensor, start_date)
    stop = calc_day_end(stop_date)
    current_app.logger.info(f"{start=}, {stop=}")
    session = get_db()
    details = session.execute(
        select(Water_reading)
        .filter(Water_reading.sensor_id == sensor)
        .filter(Water_reading.date >= start)
        .filter(Water_reading.date <= stop)
    )
    results = [detail["Water_reading"] for detail in details.mappings().all()]
    current_app.logger.info(f"Query results={len(results)}")
    return results

def counter_by_day(sensor: str, start_date: datetime, stop_date: datetime) -> list[Water_reading]:
    """Get total of values, per day, for n days"""
    current_app.logger.info(f"counter_by_day: {sensor=}, {start_date=}")
    start = first_real_date(sensor, start_date)
    stop = last_real_date(sensor, stop_date)
    days_total = (stop - start).days + 1
    current_app.logger.info(f"{start=}, {stop=}, {days_total=}")
    with get_db() as session:
        results = []
        for days in range(days_total):
            day_to_sum = start + timedelta(days=days)
            end_to_sum = day_to_sum + timedelta(days=1)
            counter_start = session.execute(
                select(Water_reading.value)
                .filter(Water_reading.sensor_id == sensor)
                .filter(Water_reading.date == day_to_sum)
            ).first()
            counter_stop = session.execute(
                select(Water_reading.value)
                .filter(Water_reading.sensor_id == sensor)
                .filter(Water_reading.date == end_to_sum)
            ).scalar()
            print(f"\n\n{counter_stop=}, {counter_start._asdict()['value']=}")
            results.append({"sensor_id": sensor, "date": day_to_sum,
                        "value": counter_stop-counter_start[0]})
    current_app.logger.info(f"Query results={len(results)}")
    return results


def counter_by_month(sensor: str, start_date: datetime, stop_date: datetime) -> list[Water_reading]:
    """Get total of values, per month, for n months"""
    current_app.logger.info(f"counter_by_day: {sensor=}, {start_date=}")
    start = first_real_date(sensor, stop_date)
    stop = last_real_date(sensor, stop_date)
    days_total = (stop - start).days + 1
    current_app.logger.info(f"{start=}, {stop=}, {days_total=}")
    session = get_db()
    results = []
    for days in range(days_total):
        day_to_sum = start + timedelta(days=days)
        end_to_sum = day_to_sum + timedelta(days=1)
        counter_start = session.execute(
            select(Water_reading.value)
            .filter(Water_reading.sensor_id == sensor)
            .filter(Water_reading.date == day_to_sum)
        ).first()
        counter_stop = session.execute(
            select(Water_reading.value)
            .filter(Water_reading.sensor_id == sensor)
            .filter(Water_reading.date == end_to_sum)
        ).scalar()
        print(f"\n\n{counter_stop=}, {counter_start._asdict()['value']=}")
        results.append({"sensor_id": sensor, "date": day_to_sum,
                    "value": counter_stop-counter_start[0]})
    current_app.logger.info(f"Query results={len(results)}")
    return results

def daily_total_gauge(sensor, start_date):
    pass

def monthly_total_gauge():
    pass
