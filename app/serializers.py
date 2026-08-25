from rest_framework import serializers

from app.models import Customer, Policy, PolicyState, PolicyStateHistory


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
    status = serializers.ChoiceField(required=True, choices=PolicyState.choices)


class PolicySerializer(serializers.ModelSerializer):
    customer = CustomerSerializer(read_only=True)

    class Meta:
        model = Policy
        fields = [
            "id",
            "customer",
            "type",
            "premium",
            "cover",
            "state",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class PolicyStateHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PolicyStateHistory
        fields = ["from_state", "to_state", "changed_at"]
