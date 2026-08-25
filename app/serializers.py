from rest_framework import serializers

from app.models import Customer, PolicyState


class CustomerSerializer(serializers.ModelSerializer):
    dob = serializers.DateField(required=True, format="%d-%m-%Y")

    class Meta:
        model = Customer
        fields = ["first_name", "last_name", "dob"]

class QuoteCreateSerializer(serializers.Serializer):
    customer_id = serializers.UUIDField(required=True)
    type = serializers.CharField(required=True)


class QuoteUpdateSerializer(serializers.Serializer):
    policy_id = serializers.UUIDField(required=True)
    status = serializers.ChoiceField(required=True, choices = PolicyState.choices)