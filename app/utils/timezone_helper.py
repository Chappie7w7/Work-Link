from datetime import datetime, timedelta

def get_mexico_time():
    """
    Retorna la hora actual de México (UTC-6)
    """
    # México está en UTC-6 (CST - Central Standard Time)
    utc_now = datetime.utcnow()
    mexico_time = utc_now - timedelta(hours=6)
    return mexico_time
