from django.urls import path
from .views import OfferListView, OfferDetailsView, OneOfferDetailsView

urlpatterns = [
    path('offers/', OfferListView.as_view(), name='offers'),
    path('offers/<int:id>/', OfferDetailsView.as_view(), name='offer-detail'),
    path('offerdetails/<int:id>/', OneOfferDetailsView.as_view(), name='one-offer-details'),
]
