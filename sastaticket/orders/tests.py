import pytest
from django.contrib.auth.models import User
from orders.models import Order
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

pytestmark = pytest.mark.django_db

class TestOrderModel(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.order = Order.objects.create(
            user=self.user, product_name="Ticket", quantity=1, price=1000
        )

    def test_order_belongs_to_user(self):
        self.assertEqual(self.order.user.username, "testuser")
        self.assertEqual(self.order.product_name, "Ticket")


class TestOrderPermissions(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="user1", password="12345")
        self.other_user = User.objects.create_user(username="user2", password="12345")

        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    def test_user_cannot_see_other_users_orders(self):
        Order.objects.create(
            user=self.other_user, product_name="IPhone", quantity=1, price=500
        )
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("IPhone", [order["product_name"] for order in response.data])

    def test_user_can_see_their_own_orders(self):
        Order.objects.create(
            user=self.user, product_name="Panadol", quantity=2, price=800
        )
        response = self.client.get("/api/orders/")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(order["product_name"] == "Panadol" for order in response.data))


class TestAdminToolsAPI(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            username="admin", email="admin@sastaticket.com", password="adminpass"
        )
        refresh = RefreshToken.for_user(self.admin)
        access_token = str(refresh.access_token)

        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    def test_all_emails_endpoint(self):
        response = self.client.get("/api/admin-tools/all_emails/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("emails", response.data)
        self.assertIn("admin@sastaticket.com", response.data["emails"])

    def test_orders_by_emails_endpoint(self):
        user = User.objects.create_user(username="ali", email="ali@sastaticket.com", password="12345")
        Order.objects.create(user=user, product_name="bike", quantity=1, price=50)

        response = self.client.post(
        "/api/admin-tools/orders_by_emails/",
        {"emails": ["ali@sastaticket.com"]},
        format="json" 
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(order["product_name"] == "bike" for order in response.data))
