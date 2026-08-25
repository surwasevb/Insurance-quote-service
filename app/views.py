import logging

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from app.exceptions import IneligibleAgeException, UnsupportedProductType
from app.models import Customer, Policy, PolicyState, PolicyStateHistory, VALID_STATE_TRANSITION
from app.pricing import price_policy
from app.serializers import (
    CustomerSerializer,
    PolicySerializer,
    PolicyStateHistorySerializer,
    QuoteCreateSerializer,
    QuoteUpdateSerializer,
)

logger = logging.getLogger(__name__)


# Create your views here.
class CustomerView(APIView):

    def get(self, request, *args, **kwargs):
        logger.info(f"Received GET request for customer {request.data}")
        qs = Customer.objects.all()
        params = request.query_params

        if first_name := params.get("first_name"):
            qs = qs.filter(first_name=first_name)
        if last_name := params.get("last_name"):
            qs = qs.filter(last_name=last_name)

        logger.info(f"Successfully processed GET request for customer {request.data}")

        return Response(
            status=status.HTTP_200_OK,
            content_type="application/json",
            data=CustomerSerializer(qs, many=True).data,
        )

    def post(self, request, *args, **kwargs):
        logger.info(f"Received Create request for customer {request.data}")

        customer_serializer = CustomerSerializer(data=request.data)
        customer_serializer.is_valid(raise_exception=True)
        customer: Customer = customer_serializer.save()

        logger.info(f"Successfully created user with {customer.id}")
        return Response(
            status=status.HTTP_201_CREATED,
            content_type="application/json",
            data={"id": customer.id},
        )


class QuoteView(APIView):

    def post(self, request, *args, **kwargs):
        logger.info(f"Received request for quote processing {request.data}")

        quote = QuoteCreateSerializer(data=request.data)
        quote.is_valid(raise_exception=True)

        customer = get_object_or_404(Customer, id=quote.validated_data["customer_id"])
        try:
            premium, cover = price_policy(
                policy_type=quote.validated_data["type"], dob=customer.dob
            )
            logger.info(
                f"Calculated premium and cover for {customer.id} is {premium} and {cover}"
            )
        except UnsupportedProductType:
            logger.error(f"Invalid product type {quote.validated_data['type']}")
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"detail": "Unsupported product type."},
            )
        except IneligibleAgeException as exc:
            logger.error(f"An ineligible age exception : {customer.dob}")
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"detail": str(exc)},
            )

        with transaction.atomic():
            policy = Policy.objects.create(
                customer=customer,
                premium=premium,
                cover=cover,
                type=quote.validated_data["type"],
                state=PolicyState.QUOTED,
            )
            PolicyStateHistory.objects.create(
                policy=policy,
                from_state=PolicyState.NEW,
                to_state=PolicyState.QUOTED,
                note="updated via api",
            )
        logger.info(f"Successfully created quotes with {policy.id}")

        return Response(
            status=status.HTTP_201_CREATED,
            content_type="application/json",
            data={"id": policy.id},
        )

    def patch(self, request, *args, **kwargs):
        logger.info(f"Received request to update quote status {request.data}")
        quote = QuoteUpdateSerializer(data=request.data)
        quote.is_valid(raise_exception=True)

        quote_id = quote.validated_data["policy_id"]
        new_state = quote.validated_data["status"]

        policy = get_object_or_404(Policy, id=quote_id)
        prev_state = policy.state

        # check for valid transitions of state
        if VALID_STATE_TRANSITION[prev_state] != new_state:
            logger.error(F"Invalid state transition {prev_state} to {new_state}")
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"detail": "Invalid state transition"},
            )

        with transaction.atomic():
            policy.state = new_state
            policy.save()
            PolicyStateHistory.objects.create(
                policy=policy,
                from_state=prev_state,
                to_state=new_state,
                note="updated via api",
            )
        logger.info(
            f"Successfully updated quote with {policy.id} from {prev_state} to {new_state}"
        )

        return Response(
            status=status.HTTP_200_OK,
            content_type="application/json",
            data={"id": policy.id},
        )


class PolicyListView(generics.ListAPIView):
    """GET /api/v1/policies/?customer_id=&type="""

    serializer_class = PolicySerializer

    def get_queryset(self):
        qs = Policy.objects.select_related("customer").all()
        params = self.request.query_params

        if customer_id := params.get("customer_id"):
            logger.info(
                f"Received request to get policy list for customer {customer_id}"
            )
            qs = qs.filter(customer_id=customer_id)
        if policy_type := params.get("type"):
            logger.info(f"Received request to get policy list for type {policy_type}")
            qs = qs.filter(type=policy_type)

        return qs


class PolicyDetailView(generics.RetrieveAPIView):
    """GET /api/v1/policies/<id>/"""

    queryset = Policy.objects.select_related("customer").all()
    serializer_class = PolicySerializer

    lookup_field = "id"


class PolicyHistoryView(generics.ListAPIView):
    """GET /api/v1/policies/<id>/history/"""

    serializer_class = PolicyStateHistorySerializer

    def get_queryset(self):
        policy = get_object_or_404(Policy, pk=self.kwargs["policy_id"])
        logger.info(f"Received request to get policy history for policy {policy.id}")
        return PolicyStateHistory.objects.filter(policy=policy)
