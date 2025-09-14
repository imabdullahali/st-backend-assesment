from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, OrderViewSet, AdminToolKitView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename="users")
router.register(r'orders', OrderViewSet, basename="orders")
router.register(r'admin-tools', AdminToolKitView, basename="admin-tools")

urlpatterns = [
    path('', include(router.urls)),
]
