import datetime

from dateutil.relativedelta import relativedelta


def calculate_age(*, date_of_birth: datetime.date) -> int:
    return relativedelta(datetime.date.today(),
                         date_of_birth).years

def calculate_premium(*, age: int, type: int) -> (int, int):
    return (age * 100, age * 1000)
