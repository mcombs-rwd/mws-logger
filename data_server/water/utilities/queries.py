def hourly_query(sensor, start_date, stop_date):
    query = (
        "SELECT logged_date, sensor, measurement "
        "FROM water "
        f"WHERE sensor = \"{sensor}\" "
        f"AND logged_date >= \"{start_date}\" "
        f"AND logged_date <= \"{stop_date}\" "
        "ORDER BY logged_date ASC"
    )
    return query
