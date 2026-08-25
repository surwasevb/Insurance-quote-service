import datetime

from rest_framework.test import APITestCase

from app.models import Customer, Policy, PolicyState, PolicyStateHistory


class TestCustomerView(APITestCase):


    def test_should_create_customer_successfully(self):

        data =  {
                "first_name": "Ben",
                "last_name": "Stokes",
                "dob": "25-06-1991"

        }

        response = self.client.post(path="/api/v1/create_customer/", data=data)
        id = response.data.get("id")
        customer  = Customer.objects.get(id=id)


        assert response.status_code == 200
        assert response.data["id"] is not None
        assert customer.first_name == data["first_name"]
        assert customer.last_name == data["last_name"]
        assert customer.dob == datetime.date.strptime(data["dob"], "%d-%m-%Y")

    def test_should_throw_error_while_creating_customer_missing_dob(self):
        data = {
            "first_name": "Ben",
            "last_name": "Stokes"
        }

        response = self.client.post(path="/api/v1/create_customer/", data=data)

        assert response.status_code == 400
        assert response.data['dob'][0] == 'This field is required.'
        assert Customer.objects.all().count() == 0


class TestQuoteView(APITestCase):

    def setUp(self):
        Customer.objects.create(first_name="Ben", last_name="Stokes", dob=datetime.date.strptime( "25-06-1991", "%d-%m-%Y"))

    def test_should_create_quote_successfully(self):
        data = {
            "customer_id": Customer.objects.all()[0].id,
            "type": "personal-accident"
        }
        response = self.client.post(path="/api/v1/quote/", data=data)
        policy = Policy.objects.get(id=(response.data.get("id")))

        assert response.status_code == 201
        assert policy.state == PolicyState.QUOTED
        assert policy.type == "personal-accident"
        assert policy.customer_id == data["customer_id"]
        assert policy.premium == 3500
        assert policy.cover == 35000

    def test_should_update_quote_successfully(self):
        data = {
            "customer_id": Customer.objects.all()[0].id,
            "type": "personal-accident"
        }
        response_policy = self.client.post(path="/api/v1/quote/", data=data)

        policy_data = {
            "policy_id": response_policy.data.get("id"),
            "status": "accepted"
        }

        response = self.client.patch(path="/api/v1/quote/", data=policy_data)
        policy = Policy.objects.get(id=response_policy.data.get("id"))
        policy_history = PolicyStateHistory.objects.filter(policy=policy)

        assert response.status_code == 200
        assert policy.state == PolicyState.ACCEPTED
        assert policy.customer_id == data["customer_id"]
        assert policy_history.count() == 2
        assert policy_history[0].from_state == 'new'
        assert policy_history[0].to_state == 'quoted'
        assert policy_history[1].from_state == 'quoted'
        assert policy_history[1].to_state == 'accepted'


