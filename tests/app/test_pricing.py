import datetime
from decimal import Decimal

import pytest

from app.exceptions import IneligibleAgeException, UnsupportedProductType
from app.pricing import calculate_age, price_policy


class TestEligibleAges:
    def test_age_10(self, dob_at_age):
        with pytest.raises(IneligibleAgeException):
            price_policy("personal-accident", dob_at_age(10))

    def test_age_18(self, dob_at_age):
        premium, cover = price_policy("personal-accident", dob_at_age(18))
        assert premium == Decimal("240.00")
        assert cover == Decimal("200000.00")

    def test_unknown_type_raises(self, dob_at_age):
        with pytest.raises(UnsupportedProductType):
            price_policy("life", dob_at_age(30))

    def test_age_36(self, dob_at_age):
        premium, cover = price_policy("personal-accident", dob_at_age(37))
        assert premium == Decimal("220.00")
        assert cover == Decimal("200000.00")

    def test_age_80(self, dob_at_age):
        premium, cover = price_policy("personal-accident", dob_at_age(80))
        assert premium == Decimal("400.00")

    def test_calculate_age(self):
        assert (
            calculate_age(date_of_birth=datetime.date(day=29, month=9, year=1990)) == 35
        )
