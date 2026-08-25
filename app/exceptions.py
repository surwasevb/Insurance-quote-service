
class UnsupportedProductType(Exception):
    """Raised when a quote is requested for a `type` we don't price."""


class IneligibleAge(Exception):
    """Raised when the customer's age falls outside any priceable band."""

    def __init__(self, age):
        self.age = age
        super().__init__(f"age {age} is outside insurable age bands")