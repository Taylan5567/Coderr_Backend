from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, status, filters
from .serializers import OrderCreateSerializer, OrderSerializer, OrderStatusUpdateSerializer
from orders_app.models import Order
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.shortcuts import get_object_or_404
from userprofile_app.models import UserProfile



class OrderListCreateView(generics.ListCreateAPIView):
    """
    List and create orders.

    GET:
        Returns a list of orders where the current user is either the customer
        or the business user. Supports ordering by "created_at" (default: newest first).

        Response: 200 OK
            [
              {
                "id": ...,
                "customer_user": ...,
                "business_user": ...,
                "title": "...",
                "revisions": ...,
                "delivery_time_in_days": ...,
                "price": ...,
                "features": [...],
                "offer_type": "...",
                "status": "...",
                "created_at": "...",
                "updated_at": "..."
              },
              ...
            ]

    POST:
        Creates a new order based on a single OfferDetail.

        Expected body:
            {
              "offer_detail_id": <int>
            }

        Rules:
            - Only users with type "customer" can create an order.
            - The order will copy snapshot fields from the OfferDetail.

        Responses:
            201 Created: returns the created order (same shape as GET items)
            400 Bad Request: invalid data
            403 Forbidden: user is not a customer
    """
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Return only orders that belong to the current user, either as customer
        or as business user. This prevents users from seeing other users' orders.
        """
        self = self.request.user
        return Order.objects.filter(Q(customer_user=self) | Q(business_user=self))
    
    def get_serializer_class(self):
        """
        Use OrderCreateSerializer for POST requests and OrderSerializer for GET.
        """
        return OrderCreateSerializer if self.request.method == 'POST' else OrderSerializer
    
    def create(self, request, *args, **kwargs):
        """
        Create a new order from the given OfferDetail id.

        Permissions:
            - The current user must be authenticated and have type "customer".

        Returns:
            201 Created with the created order on success.
            403 Forbidden if the user is not a customer.
            400 Bad Request if validation fails.
        """
        user = request.user
        serializer = OrderCreateSerializer(data=request.data, context={'request': request})
        
        if user.type == 'business':
            return Response({"error": "Only Customer users can create orders."}, status=status.HTTP_403_FORBIDDEN)

        if serializer.is_valid():
            serializer.save()
            read = OrderSerializer(serializer.instance, context={'request': request})
            return Response(read.data, status=status.HTTP_201_CREATED)    
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class OrderPatchView(generics.RetrieveAPIView):
    """
    Update (patch) or delete a single order.

    PATCH /api/orders/<int:id>/:
        Update only the "status" field of an order.
        Body:
            { "status": "<new_status_value>" }

        Permissions:
            - The current user must be authenticated.
            - The current user must be of type "business".
            - The current user must be the business owner of this order.

        Responses:
            200 OK with the updated order.
            403 Forbidden if not the owner or not a business user.
            404 Not Found if the order does not exist.

    DELETE /api/orders/<int:id>/:
        Delete a single order.

        Permissions:
            - The current user must be authenticated.
            - The current user must be admin (is_staff=True).

        Responses:
            204 No Content on success.
            403 Forbidden if the user is not admin.
            404 Not Found if the order does not exist.
    """
    permission_classes = [IsAuthenticated]
    queryset = Order.objects.all()
    serializer_class = OrderStatusUpdateSerializer
    lookup_field = 'id'
    lookup_url_kwarg = 'id'

    def patch(self, request, id):
        """
        Partially update an order's status. Only status updates are allowed
        through this endpoint.

        See the class-level docstring for details on the body and permissions.
        """
        order = self.get_object()
        user = request.user
        data = request.data.copy()

        if user.type != 'business' and order.business_user_id != user.id:
            return Response({"error": "You are not a business user"}, status=status.HTTP_403_FORBIDDEN)

        serializer = OrderStatusUpdateSerializer(order, data=data, partial=True, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            read = OrderSerializer(serializer.instance, context={'request': request})
            return Response(read.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
    def delete(self, request, id):
        """
        Delete an order. Only admins (is_staff=True) are allowed to delete.

        Returns:
            204 No Content on success.
            403 Forbidden if the user is not an admin.
        """
        user = request.user

        if not getattr(user, 'is_staff', False):
            return Response({"error": "You are not an admin"}, status=status.HTTP_403_FORBIDDEN)

        order = get_object_or_404(Order, id=id)
        order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class OrderCountView(APIView):
    """
    Count in-progress orders for a given business user id.

    GET /api/order-count/<int:id>/:
        Path parameter:
            id: the business user's id (can also be named business_user_id in urls.py)

        Behavior:
            - Checks that the referenced user exists and has type "business".
            - Counts orders with status='in_progress' for that business user.

        Responses:
            200 OK: { "order_count": <int> }
            400 Bad Request: missing id parameter
            404 Not Found: user is not a business user or does not exist
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Return the number of in-progress orders for the given business user id.
        """
        business_user_id = kwargs.get('business_user_id') or kwargs.get('id')
        if business_user_id is None:
            return Response({'detail': 'Missing business user id'}, status=status.HTTP_400_BAD_REQUEST)

        business_user = get_object_or_404(UserProfile, id=business_user_id)

        if getattr(business_user, 'type', None) != 'business':
            return Response({'detail': 'User is not a business user'}, status=status.HTTP_404_NOT_FOUND)
        
        count = Order.objects.filter(business_user=business_user, status='in_progress').count()
        return Response({'order_count': count}, status=status.HTTP_200_OK)
    

class OrderCountCompletedView(APIView):
    """
    Count completed orders for a given business user id.

    GET /api/order-count-completed/<int:id>/:
        Path parameter:
            id: the business user's id (can also be named business_user_id in urls.py)

        Behavior:
            - Checks that the referenced user exists and has type "business".
            - Counts orders with status='completed' for that business user.

        Responses:
            200 OK: { "completed_order_count": <int> }
            400 Bad Request: missing id parameter
            404 Not Found: user is not a business user or does not exist
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Return the number of completed orders for the given business user id.
        """
        business_user_id = kwargs.get('business_user_id') or kwargs.get('id')
        if business_user_id is None:
            return Response({'detail': 'Missing business user id'}, status=status.HTTP_400_BAD_REQUEST)

        business_user = get_object_or_404(UserProfile, id=business_user_id)

        if getattr(business_user, 'type', None) != 'business':
            return Response({'detail': 'User is not a business user'}, status=status.HTTP_404_NOT_FOUND)
        
        count = Order.objects.filter(business_user=business_user, status='completed').count()
        return Response({'completed_order_count': count}, status=status.HTTP_200_OK)