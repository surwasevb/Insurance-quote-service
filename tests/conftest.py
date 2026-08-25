import datetime

import pytest
from dateutil.relativedelta import relativedelta


@pytest.fixture
def dob_at_age():
    """Return a date of birth for a given age from today."""

    def _factory(age: int) -> datetime.date:
        return datetime.date.today() - relativedelta(years=age)

    return _factory


@pytest.fixture
def customer(db):
    from app.models import Customer

    return Customer.objects.create(
        first_name="Ben",
        last_name="Stokes",
        dob=datetime.date(day=25, month=6, year=1991),
    )


@pytest.fixture
def young_customer(db):
    from app.models import Customer

    return Customer.objects.create(
        first_name="Young",
        last_name="Person",
        dob=datetime.date.today() - datetime.timedelta(days=365 * 10),
    )


@pytest.fixture
def policy(customer):
    from app.models import Policy

    return Policy.objects.create(
        customer=customer,
        type="personal-accident",
        premium=200,
        cover=200000,
    )


@pytest.fixture
def policy_with_history(policy):
    from app.models import PolicyState, PolicyStateHistory

    PolicyStateHistory.objects.create(
        policy=policy,
        from_state=PolicyState.NEW,
        to_state=PolicyState.QUOTED,
        note="quoted",
    )
    return policy
