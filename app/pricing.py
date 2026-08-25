from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from dateutil.relativedelta import relativedelta

from app.exceptions import IneligibleAgeException, UnsupportedProductType

# Base premium and cover per product type.
PRODUCT_RATES = {
    "personal-accident": {
        "base_premium": Decimal("200.00"),
        "cover": Decimal("200000.00"),
    },
}

# (min_age, max_age, multiplier) - inclusive bounds, checked in order.
# Under-18 and over-65 are priced up or excluded, as a real personal
# accident product would.
AGE_BAND_MULTIPLIERS = [
    (0, 17, None),  # not eligible for this product
    (18, 25, Decimal("1.20")),
    (26, 35, Decimal("1.00")),
    (36, 50, Decimal("1.10")),
    (51, 65, Decimal("1.50")),
    (66, 150, Decimal("2.00")),
]


def calculate_age(*, date_of_birth: date) -> int:
    return relativedelta(date.today(), date_of_birth).years


def get_age_band_multiplier(*, age: int) -> Decimal | None:
    for min_age, max_age, multiplier in AGE_BAND_MULTIPLIERS:
        if min_age <= age <= max_age:
            return multiplier
    return None


def price_policy(policy_type, dob):
    """Return (premium, cover) as Decimals for a product type + date of birth."""
    rates = PRODUCT_RATES.get(policy_type)
    if rates is None:
        raise UnsupportedProductType(policy_type)

    age: int = calculate_age(date_of_birth=dob)
    multiplier = get_age_band_multiplier(age=age)

    if not multiplier:
        raise IneligibleAgeException(age)

    premium = (rates["base_premium"] * multiplier).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    return premium, rates["cover"]
