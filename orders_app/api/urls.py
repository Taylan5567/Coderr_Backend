from django.urls import path
from .views import OrderListCreateView, OrderPatchView

urlpatterns = [
    path('orders/', OrderListCreateView.as_view(), name='orders'),
    path('orders/<int:id>/', OrderPatchView.as_view(), name='order-detail'),
]
