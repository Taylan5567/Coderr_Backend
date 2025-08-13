from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from offers_app.models import Offer, OfferDetail
from .serializers import OfferDetailsSerializer, OfferSerializer, OfferUpdateSerializer, OfferCreateSerializer, OneOfferDetailSerializer
from rest_framework.generics import ListCreateAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics
from .permissions import IsBusinessUser
from rest_framework import filters
from django.db.models import Min



class PageNumberSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 5

class OfferListView(generics.ListCreateAPIView):
    queryset = Offer.objects.all()
    serializer_class = OfferSerializer
    pagination_class = PageNumberSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description']
    ordering_fields = ['updated_at', 'min_price']
    ordering = ['updated_at', 'min_price']

    def get_serializer_class(self):
        return OfferCreateSerializer if self.request.method == 'POST' else OfferSerializer

    def get_queryset(self):
        queryset = Offer.objects.annotate(
            min_price=Min('details__price'),
            delivery_time_in_days=Min('details__delivery_time_in_days'),
        )

        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)

        price = self.request.query_params.get('price')
        if price:
            queryset = queryset.filter(min_price__gte=price)  # auf Annotation filtern

        return queryset
    
    def post(self, request):
        user = request.user
        serializer = OfferCreateSerializer(data=request.data, context={'request': request})
        
        if not getattr(user, 'is_authenticated', False) or getattr(user, 'type', None) != 'business':
            return Response({"error": "Only business users can create offers."}, status=status.HTTP_403_FORBIDDEN)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)    
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class OfferDetailsView(generics.RetrieveAPIView):
    serializer_class = OfferSerializer
    permission_classes = [IsAuthenticated]
    lookup_url_kwarg = 'id' 

    def get_serializer_class(self):
        return OfferUpdateSerializer if self.request.method in ('PATCH', 'PUT') else OfferSerializer

    def get_queryset(self):
        return Offer.objects.annotate(
            min_price=Min('details__price'),
            delivery_time_in_days=Min('details__delivery_time_in_days'),
        )    

    def patch(self, request, id):
        offer = get_object_or_404(Offer, id=id)
        user = request.user
        data = request.data.copy()

        is_owner = offer.user_id == user.id

        if not is_owner:
            return Response({"error": "You are not the owner of this offer."}, status=status.HTTP_403_FORBIDDEN)

        serializer = OfferUpdateSerializer(offer, data=data, partial=True, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, id):
        offer = get_object_or_404(Offer, id=id)
        user = request.user
        data = request.data.copy()

        is_owner = offer.user_id == user.id

        if not is_owner:
            return Response({"error": "You are not the owner of this offer."}, status=status.HTTP_403_FORBIDDEN)

        offer.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class OneOfferDetailsView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = OfferDetail.objects.all()
    serializer_class = OneOfferDetailSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'id'