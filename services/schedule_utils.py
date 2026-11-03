import datetime
import random

IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))


def now_ist():
    """Current time in India Standard Time (aware)."""
    return datetime.datetime.now(IST)


def detect_slot(when=None) -> str:
    moment = when or now_ist()
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=IST)
    else:
        moment = moment.astimezone(IST)
    if moment.weekday() in (5, 6):
        return "weekend"
    hour = moment.hour
    if hour < 12:
        return "morning"
    if hour < 17:
        return "afternoon"
    return "evening"


def weekend_kind_for_tests(weekday: int) -> str:
    if weekday == 5:
        return "quiz"
    if weekday == 6:
        return "poll"
    return random.choice(["quiz", "poll"])
