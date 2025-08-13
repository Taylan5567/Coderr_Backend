from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status, filters
from .serializers import OrderCreateSerializer, OrderSerializer, OrderStatusUpdateSerializer
from orders_app.models import Order
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Q
from django.shortcuts import get_object_or_404



class OrderListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        self = self.request.user
        return Order.objects.filter(Q(customer_user=self) | Q(business_user=self))
    
    def get_serializer_class(self):
        return OrderCreateSerializer if self.request.method == 'POST' else OrderSerializer
    
    def create(self, request, *args, **kwargs):
        user = request.user
        serializer = OrderCreateSerializer(data=request.data, context={'request': request})
        
        if user.type == 'business':
            return Response({"error": "Only Customer users can create orders."}, status=status.HTTP_403_FORBIDDEN)

        if serializer.is_valid():
            serializer.save()
            read = OrderSerializer(Order.objects.get(id=serializer.data['offer_detail_id']), context={'request': request})
            return Response(read.data, status=status.HTTP_201_CREATED)    
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class OrderPatchView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()
    serializer_class = OrderStatusUpdateSerializer

    def patch(self, request, id):
        order = get_object_or_404(Order, id=id)
        user = request.user
        data = request.data.copy()

        if user.type != 'business' and order.business_user_id != user.id:
            return Response({"error": "You are not a business user"}, status=status.HTTP_403_FORBIDDEN)

        serializer = OrderStatusUpdateSerializer(order, data=data, partial=True, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            read = OrderSerializer(Order.objects.get(id=serializer.data['offer_detail_id']), context={'request': request})
            return Response(read.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    def delete(self, request, id):
        user = request.user

        if not getattr(user, 'is_staff', False):
            return Response({"error": "You are not an admin"}, status=status.HTTP_403_FORBIDDEN)

        order = get_object_or_404(Order, id=id)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
