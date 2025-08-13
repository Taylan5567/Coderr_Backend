from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from offers_app.models import Offer
from .serializers import OfferDetailsSerializer, OfferSerializer, OfferUpdateSerializer, OfferCreateSerializer
from rest_framework.generics import ListCreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics



class PageNumberSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 5


class OfferListCreateView(APIView):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    pagination_class = PageNumberSetPagination
    permission_classes = [IsAuthenticated]
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']
    ordering = ['updated_at', 'min_price']

    def get(self, request):
        queryset = Offer.objects.all()

        creator_id = self.request.query_params.get('creator_id')
        if creator_id is not None:
            queryset = queryset.filter(user_id=creator_id)

        min_price = self.request.query_params.get('min_price')
        if min_price is not None:
            queryset = queryset.filter(min_price__gte=min_price)

        delivery_time_in_days  = self.request.query_params.get('delivery_time_in_days ')
        if delivery_time_in_days  is not None:
            queryset = queryset.filter(delivery_time_in_days=delivery_time_in_days )

        serializer = OfferSerializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = OfferCreateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

