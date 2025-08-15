from django.urls import path
from .views import ReviewsList, ReviewDetail, BaseInformationView


urlpatterns = [
    path('reviews/', ReviewsList.as_view(), name='reviews'),
    path('reviews/<int:id>/', ReviewDetail.as_view(), name='reviews-detail'),
    path('base-info/', BaseInformationView.as_view(), name='base-info'),
]
