import logging

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Customer
from app.serializers import CustomerSerializer

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
        return Response(status=200, content_type="application/json", data={"id": customer.id})
