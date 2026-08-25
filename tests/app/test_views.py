import uuid

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from app.models import Customer, Policy, PolicyState, PolicyStateHistory


@pytest.fixture
def api_client():
    return APIClient()


class TestCustomerView:

    @pytest.mark.django_db
    def test_should_create_customer_successfully(self, api_client):
        data = {"first_name": "Ben", "last_name": "Stokes", "dob": "25-06-1991"}

        response = api_client.post(reverse("customer"), data=data)
        id = response.data.get("id")
        customer = Customer.objects.get(id=id)

        assert response.status_code == 201
        assert response.data["id"] is not None
        assert customer.first_name == data["first_name"]
        assert customer.last_name == data["last_name"]

    @pytest.mark.django_db
    def test_should_throw_error_while_creating_customer_missing_dob(self, api_client):
        data = {"first_name": "Ben", "last_name": "Stokes"}

        response = api_client.post(reverse("customer"), data=data)

        assert response.status_code == 400
        assert response.data["dob"][0] == "This field is required."
        assert Customer.objects.all().count() == 0

    @pytest.mark.django_db
    def test_should_return_search_customer_successfully(self, api_client, customer):
        data = {
            "first_name": "Ben",
            "last_name": "Stokes",
        }
        response = api_client.get(reverse("customer-search"), data=data)

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0].get("first_name") == data["first_name"]

    @pytest.mark.django_db
    def test_should_return_empty_list_when_customer_not_found(self, api_client):
        response = api_client.get(
            reverse("customer-search"),
            data={"first_name": "Nobody"},
        )

        assert response.status_code == 200
        assert response.data == []


class TestQuoteView:

    @pytest.mark.django_db
    def test_should_create_quote_successfully(self, api_client, customer):
        data = {
            "customer_id": customer.id,
            "type": "personal-accident",
        }
        response = api_client.post(reverse("quote"), data=data)
        policy = Policy.objects.get(id=(response.data.get("id")))

        assert response.status_code == 201
        assert policy.state == PolicyState.QUOTED
        assert policy.type == "personal-accident"
        assert policy.customer_id == data["customer_id"]
        assert policy.premium == 200
        assert policy.cover == 200000

    @pytest.mark.django_db
    def test_should_update_quote_successfully(self, api_client, policy):
        api_client.patch(
            reverse("quote"),
            data={"policy_id": policy.id, "status": "quoted"},
        )
        response = api_client.patch(
            reverse("quote"),
            data={"policy_id": policy.id, "status": "accepted"},
        )
        updated_policy = Policy.objects.get(id=policy.id)
        policy_history = PolicyStateHistory.objects.filter(policy=policy)

        assert response.status_code == 200
        assert updated_policy.state == PolicyState.ACCEPTED
        assert updated_policy.customer_id == policy.customer_id
        assert policy_history.count() == 2
        assert policy_history[0].from_state == "new"
        assert policy_history[0].to_state == "quoted"
        assert policy_history[1].from_state == "quoted"
        assert policy_history[1].to_state == "accepted"

    @pytest.mark.django_db
    def test_should_handle_invalid_state_update_transition_quote(self, api_client, policy):
        policy_data = {
            "policy_id": policy.id,
            "status": "active",
        }

        response = api_client.patch(reverse("quote"), data=policy_data)

        assert response.status_code == 400
        assert response.data == {"detail": "Invalid state transition"}

    @pytest.mark.django_db
    def test_should_return_404_when_customer_missing_for_quote(self, api_client):
        response = api_client.post(
            reverse("quote"),
            data={
                "customer_id": uuid.uuid4(),
                "type": "personal-accident",
            },
        )

        assert response.status_code == 404
        assert Policy.objects.count() == 0

    @pytest.mark.django_db
    def test_should_return_400_for_unsupported_product_type(self, api_client, customer):
        response = api_client.post(
            reverse("quote"),
            data={
                "customer_id": customer.id,
                "type": "life",
            },
        )

        assert response.status_code == 400
        assert response.data["detail"] == "Unsupported product type."
        assert Policy.objects.count() == 0

    @pytest.mark.django_db
    def test_should_return_400_for_ineligible_age(self, api_client, young_customer):
        response = api_client.post(
            reverse("quote"),
            data={
                "customer_id": young_customer.id,
                "type": "personal-accident",
            },
        )

        assert response.status_code == 400
        assert "age" in response.data["detail"]
        assert Policy.objects.filter(customer=young_customer).count() == 0

    @pytest.mark.django_db
    def test_should_return_404_when_policy_missing_for_update(self, api_client):
        response = api_client.patch(
            reverse("quote"),
            data={
                "policy_id": uuid.uuid4(),
                "status": "accepted",
            },
        )

        assert response.status_code == 404


class TestPolicyView:

    @pytest.mark.django_db
    def test_should_return_policy_successfully(self, api_client, policy):
        response = api_client.get(reverse("policy-details", args=[policy.id]))

        assert response.status_code == 200

    @pytest.mark.django_db
    def test_should_return_policy_for_given_customer_id_successfully(self, api_client, policy):
        response = api_client.get(
            reverse("policy-for-user"), {"customer_id": policy.customer_id}
        )

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0].get("premium") == 200
        assert response.data[0].get("cover") == 200000
        assert response.data[0].get("type") == "personal-accident"

    @pytest.mark.django_db
    def test_should_return_policy_history_successfully(self, api_client, policy_with_history):
        response = api_client.get(
            reverse("policy-history", args=[policy_with_history.id])
        )

        assert response.status_code == 200
        assert len(response.data) == 1
        assert response.data[0].get("to_state") == "quoted"
        assert response.data[0].get("from_state") == "new"
