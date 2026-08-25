import datetime
import uuid

from django.urls import reverse
from rest_framework.test import APITestCase

from app.models import Customer, Policy, PolicyState, PolicyStateHistory


class TestCustomerView(APITestCase):

    def test_should_create_customer_successfully(self):
        data = {"first_name": "Ben", "last_name": "Stokes", "dob": "25-06-1991"}

        response = self.client.post(reverse("customer"), data=data)
        id = response.data.get("id")
        customer = Customer.objects.get(id=id)

        assert response.status_code == 201
        assert response.data["id"] is not None
        assert customer.first_name == data["first_name"]
        assert customer.last_name == data["last_name"]
        assert customer.dob == datetime.date.strptime(data["dob"], "%d-%m-%Y")

    def test_should_throw_error_while_creating_customer_missing_dob(self):
        data = {"first_name": "Ben", "last_name": "Stokes"}

        response = self.client.post(reverse("customer"), data=data)

        assert response.status_code == 400
        assert response.data["dob"][0] == "This field is required."
        assert Customer.objects.all().count() == 0

    def test_should_return_search_customer_successfully(self):
        data = {
            "first_name": "Ben",
            "last_name": "Stokes",
        }
        Customer.objects.create(
            first_name="Ben",
            last_name="Stokes",
            dob=datetime.date.strptime("25-06-1991", "%d-%m-%Y"),
        )
        response = self.client.get(reverse("customer-search"), data=data)

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0].get("first_name") == data["first_name"]

    def test_should_return_empty_list_when_customer_not_found(self):
        response = self.client.get(
            reverse("customer-search"),
            data={"first_name": "Nobody"},
        )

        assert response.status_code == 200
        assert response.data == []


class TestQuoteView(APITestCase):

    def setUp(self):
        Customer.objects.create(
            first_name="Ben",
            last_name="Stokes",
            dob=datetime.date.strptime("25-06-1991", "%d-%m-%Y"),
        )

    def test_should_create_quote_successfully(self):
        data = {
            "customer_id": Customer.objects.all()[0].id,
            "type": "personal-accident",
        }
        response = self.client.post(reverse("quote"), data=data)
        policy = Policy.objects.get(id=(response.data.get("id")))

        assert response.status_code == 201
        assert policy.state == PolicyState.QUOTED
        assert policy.type == "personal-accident"
        assert policy.customer_id == data["customer_id"]
        assert policy.premium == 200
        assert policy.cover == 200000

    def test_should_update_quote_successfully(self):
        data = {
            "customer_id": Customer.objects.all()[0].id,
            "type": "personal-accident",
        }
        response_policy = self.client.post(reverse("quote"), data=data)

        policy_data = {
            "policy_id": response_policy.data.get("id"),
            "status": "accepted",
        }

        response = self.client.patch(reverse("quote"), data=policy_data)
        policy = Policy.objects.get(id=response_policy.data.get("id"))
        policy_history = PolicyStateHistory.objects.filter(policy=policy)

        assert response.status_code == 200
        assert policy.state == PolicyState.ACCEPTED
        assert policy.customer_id == data["customer_id"]
        assert policy_history.count() == 2
        assert policy_history[0].from_state == "new"
        assert policy_history[0].to_state == "quoted"
        assert policy_history[1].from_state == "quoted"
        assert policy_history[1].to_state == "accepted"

    def test_should_handle_invalid_state_update_transition_quote(self):
        data = {
            "customer_id": Customer.objects.all()[0].id,
            "type": "personal-accident",
        }
        response_policy = self.client.post(reverse("quote"), data=data)

        policy_data = {
            "policy_id": response_policy.data.get("id"),
            "status": "active",
        }

        response = self.client.patch(reverse("quote"), data=policy_data)
        policy = Policy.objects.get(id=response_policy.data.get("id"))
        PolicyStateHistory.objects.filter(policy=policy)

        assert response.status_code == 400
        assert response.data == {'detail': 'Invalid state transition'}

    def test_should_return_404_when_customer_missing_for_quote(self):
        response = self.client.post(
            reverse("quote"),
            data={
                "customer_id": uuid.uuid4(),
                "type": "personal-accident",
            },
        )

        assert response.status_code == 404
        assert Policy.objects.count() == 0

    def test_should_return_400_for_unsupported_product_type(self):
        response = self.client.post(
            reverse("quote"),
            data={
                "customer_id": Customer.objects.all()[0].id,
                "type": "life",
            },
        )

        assert response.status_code == 400
        assert response.data["detail"] == "Unsupported product type."
        assert Policy.objects.count() == 0

    def test_should_return_400_for_ineligible_age(self):
        customer = Customer.objects.create(
            first_name="Young",
            last_name="Person",
            dob=datetime.date.today() - datetime.timedelta(days=365 * 10),
        )
        response = self.client.post(
            reverse("quote"),
            data={
                "customer_id": customer.id,
                "type": "personal-accident",
            },
        )

        assert response.status_code == 400
        assert "age" in response.data["detail"]
        assert Policy.objects.filter(customer=customer).count() == 0

    def test_should_return_404_when_policy_missing_for_update(self):
        response = self.client.patch(
            reverse("quote"),
            data={
                "policy_id": uuid.uuid4(),
                "status": "accepted",
            },
        )

        assert response.status_code == 404


class TestPolicyView(APITestCase):

    def setUp(self):
        customer = Customer.objects.create(
            first_name="Ben",
            last_name="Stokes",
            dob=datetime.date.strptime("25-06-1991", "%d-%m-%Y"),
        )
        Policy.objects.create(
            customer=customer, type="personal-accident", premium=3500, cover=3500
        )

    def test_should_return_policy_successfully(self):
        policy_id = Policy.objects.all()[0].id

        response = self.client.get(reverse("policy-details", args=[policy_id]))

        assert response.status_code == 200

    def test_should_return_policy_for_given_customer_id_successfully(self):
        customer_id = Customer.objects.all()[0].id

        response = self.client.get(
            reverse("policy-for-user"), {"customer_id": customer_id}
        )

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0].get("premium") == 3500
        assert response.data[0].get("cover") == 3500
        assert response.data[0].get("type") == "personal-accident"

    def test_should_return_policy_history_successfully(self):
        policy = Policy.objects.all()[0]
        PolicyStateHistory.objects.create(
            policy=policy, to_state=PolicyState.ACCEPTED, from_state=PolicyState.QUOTED
        )

        response = self.client.get(reverse("policy-history", args=[policy.id]))

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0].get("to_state") == "accepted"
        assert response.data[0].get("from_state") == "quoted"
