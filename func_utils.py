from datetime import datetime


def get_current_time():
    now = datetime.now()
    hour = str(now.hour).zfill(2)
    minute = str(now.minute).zfill(2)
    second = str(now.second).zfill(2)
    return f"[{hour}:{minute}:{second}]"


# test git