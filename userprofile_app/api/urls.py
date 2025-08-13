from django.urls import path
from .views import ProfileDetailView, BusinessView, CustomerView

urlpatterns = [
    path('profile/<int:pk>/', ProfileDetailView.as_view(), name='profile'),
    path('profiles/business/', BusinessView.as_view(), name='business'),
    path('profiles/customer/', CustomerView.as_view(), name='customer'),
]
