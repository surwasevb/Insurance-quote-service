from rest_framework import serializers

from app.models import Customer


class CustomerSerializer(serializers.ModelSerializer):
    dob = serializers.DateField(required=True, format="%d-%m-%Y")

    class Meta:
        model = Customer
        fields = ["first_name", "last_name", "dob"]
