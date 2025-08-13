from django.urls import path
from .views import OrderListCreateView, OrderPatchView, OrderCountView, OrderCountCompletedView

urlpatterns = [
    path('orders/', OrderListCreateView.as_view(), name='orders'),
    path('orders/<int:id>/', OrderPatchView.as_view(), name='order-patch'),
    path('order-count/<int:business_user_id>/', OrderCountView.as_view(), name='order-count'),
    path('completed-order-count/<int:business_user_id>/', OrderCountCompletedView.as_view(), name='order-count-completed')
]
