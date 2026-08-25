import logging

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Customer, Policy, PolicyState, PolicyStateHistory
from app.serializers import CustomerSerializer, QuoteCreateSerializer, QuoteUpdateSerializer
from app.utils import calculate_age, calculate_premium

logger = logging.getLogger(__name__)


# Create your views here.
class CustomerView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        logger.info(F"Received Create request for customer {request.data}")

        customer_serializer = CustomerSerializer(data=request.data)
        customer_serializer.is_valid(raise_exception=True)
        customer: Customer = customer_serializer.save()

        logger.info(F"Successfully created user with {customer.id}")
        return Response(status=status.HTTP_201_CREATED, content_type="application/json", data={"id": customer.id})


class QuoteView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        logger.info(F"Received request for quote processing {request.data}")

        quote = QuoteCreateSerializer(data=request.data)
        quote.is_valid(raise_exception=True)

        customer = Customer.objects.get(id=quote.validated_data['customer_id'])
        age: int = calculate_age(date_of_birth=customer.dob)
        premium, cover = calculate_premium(age=age, type=quote.validated_data['type'])
        policy = Policy.objects.create(customer=customer, premium=premium, cover=cover,
                                       type=quote.validated_data['type'],
                                       state=PolicyState.QUOTED)

        PolicyStateHistory.objects.create(policy=policy, from_state=PolicyState.NEW,
                                          to_state=PolicyState.QUOTED, note="updated via api")
        logger.info(F"Successfully created quotes with {policy.id}")

        return Response(
            status=status.HTTP_201_CREATED,
            content_type="application/json",
            data={
                "id": policy.id
            }
        )

    def patch(self, request, *args, **kwargs):
        logger.info(F"Received Patch request for quote {request.data}")
        quote = QuoteUpdateSerializer(data=request.data)
        quote.is_valid(raise_exception=True)

        quote_id = quote.validated_data["policy_id"]
        new_state = quote.validated_data["status"]

        policy = Policy.objects.get(id=quote_id)
        prev_state = policy.state
        policy.state = new_state
        policy.save()

        PolicyStateHistory.objects.create(policy=policy, from_state=prev_state,
                                          to_state=new_state, note="updated via api")

        return Response(status=status.HTTP_200_OK, content_type="application/json", data={"id": policy.id})
