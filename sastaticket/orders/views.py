from rest_framework import viewsets
from django.contrib.auth.models import User
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Order
from .serializers import UserSerializer, OrderSerializer

# only admin can manage users 
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]  


# only owner can access their orders
class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# all emails and orders of all users 
class AdminToolKitView(viewsets.ViewSet):
    permission_classes = [IsAdminUser]

    @action(detail=False, methods=["get"])
    def all_emails(self, request):
        emails = list(User.objects.values_list("email", flat=True))
        return Response({"emails": emails})

    @action(detail=False, methods=["post"])
    def orders_by_emails(self, request):
        emails = request.data.get("emails", [])
        orders = Order.objects.filter(user__email__in=emails)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)
