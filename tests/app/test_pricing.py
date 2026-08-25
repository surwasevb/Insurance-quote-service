import datetime
from decimal import Decimal

import pytest

from app.exceptions import IneligibleAge, UnsupportedProductType
from app.pricing import price_policy, calculate_age

TODAY = datetime.date.today()


def _dob_at_age(age: int) -> datetime.date:
    return TODAY - datetime.timedelta(days=int(age * 365.2425))


class TestEligibleAges:
    def test_age_10(self):
        with pytest.raises(IneligibleAge):
            price_policy("personal-accident", _dob_at_age(10))

    def test_age_18(self):
        premium, cover = price_policy("personal-accident", _dob_at_age(18))
        assert premium == Decimal("240.00")
        assert cover == Decimal("200000.00")


    def test_unknown_type_raises(self):
        with pytest.raises(UnsupportedProductType):
            price_policy("life", _dob_at_age(30))

    def test_age_36(self):
        premium, cover = price_policy("personal-accident", _dob_at_age(36))
        assert premium == Decimal("220.00")

    def test_age_80(self):
        premium, cover = price_policy("personal-accident", _dob_at_age(80))
        assert premium == Decimal("400.00")

    def test_calculate_age(self) -> Decimal:
        assert calculate_age(date_of_birth=datetime.date(day=29,month=9,year=1990)) == 35
