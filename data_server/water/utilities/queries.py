def hourly_detail(sensor, start_date, stop_date):
    """Get hourly measurements for n days.
    
    Note the date 00:00 value shows what happened the hour
    before and is recorded at date 00:00.
    """
    query = (
        "SELECT "
        "    STRFTIME('%Y-%m-%d', logged_date) as date_only, "
        "    logged_date, sensor, gauge_value, meter_value "
        "FROM water "
        f"WHERE sensor = \"{sensor}\" "
        f"AND date_only >= \"{start_date}\" "
        f"AND date_only <= \"{stop_date}\" "
        "ORDER BY logged_date ASC"
    )
    return query

    # query = (
    #     "SELECT logged_date, sensor, gauge_value "
    #     "FROM water "
    #     f"WHERE sensor = \"{sensor}\" "
    #     f"AND logged_date >= \"{start_date}\" "
    #     f"AND logged_date <= \"{stop_date}\" "
    #     "ORDER BY logged_date ASC"
    # )
    # return query

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

def daily_total_meter(sensor, start_date):
    """, per day, for n days
    
    A gauge shows current value, a meter shows cumulative.
    Water flow is today's max - yesterday's max.
    """
    pass

def monthly_total_gauge():
    pass

def monthly_total_meter():
    pass
