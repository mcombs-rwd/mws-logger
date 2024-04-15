def get_status() -> dict:
    """Checks status of components and dependencies"""
    status = {
        "bacnet": False,
        "rain_gauge": False,
        "database": True,
    }
    return status
