from rest_framework import serializers
from orders_app.models import Order
from offers_app.models import OfferDetail


class OrderSerializer(serializers.ModelSerializer):
    """
    Read serializer for the Order model.

    Purpose:
        This serializer is used to return an order in API responses (for example in GET
        requests after creating or updating an order). It exposes only read-only fields,
        which means it is not intended for creating or updating orders.

    Returned fields:
        id (int): Primary key of the order.
        customer_user (int): User ID of the customer who placed the order.
        business_user (int): User ID of the business user who owns the offer.
        title (str): Snapshot of the offer detail title at the time of ordering.
        revisions (int): Snapshot of the number of revisions included.
        delivery_time_in_days (int): Snapshot of the delivery time in days.
        price (decimal): Snapshot of the price at the time of ordering.
        features (list): Snapshot of the included features.
        offer_type (str): Snapshot of the offer variant (for example "basic", "standard", "premium").
        status (str): Current status of the order (for example "in_progress", "completed").
        created_at (datetime): Creation timestamp of the order.
        updated_at (datetime): Last update timestamp of the order.

    Notes:
        - All fields are marked as read-only via Meta.read_only_fields. This prevents
          accidental writes through this serializer.
        - The foreign key to the original OfferDetail is intentionally not included in
          the output. Consumers should use the snapshot fields above.
    """

    class Meta:
        model = Order
        fields = [
            'id',
            'customer_user',
            'business_user',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields



class OrderCreateSerializer(serializers.Serializer):
    """
    Serializer used to create a new Order from a given OfferDetail.

    Expected input (request data):
        - offer_detail_id (int, required): The primary key of the OfferDetail
          that the user wants to order.

    Behavior:
        - Validates that the given OfferDetail exists.
        - Validates that the current user is a customer.
        - Creates an Order that stores a snapshot of the OfferDetail
          (title, revisions, delivery_time_in_days, price, features, offer_type),
          and links the customer_user, business_user, and offer_detail.
    """
    offer_detail_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Order
        fields = ['id', 'customer_user', 'business_user', 'title', 'revisions', 'delivery_time_in_days',
                   'price', 'features', 'offer_type', 'status', 'created_at', 'updated_at', 'offer_detail_id'
                   ]
        read_only_fields = ['id', 'customer_user', 'business_user', 'title', 'revisions', 'delivery_time_in_days',
                   'price', 'features', 'offer_type', 'status', 'created_at', 'updated_at'
                   ]
        

    def validate_offer_detail_id(self, value):
        """
        Ensure that an OfferDetail with the given id exists.

        Args:
            value (int): The OfferDetail primary key from the request.

        Returns:
            OfferDetail: The found OfferDetail instance (stored for use in create()).

        Raises:
            serializers.ValidationError: If no OfferDetail with this id exists.
        """
        try:
            offer_detail = OfferDetail.objects.get(id=value)
        except OfferDetail.DoesNotExist:
            raise serializers.ValidationError("Offer detail with this ID does not exist.")
        return offer_detail

    def validate(self, attrs):
        """
        Validate request-level rules.

        Rules:
            - The current user must be of type 'customer'.

        Returns:
            dict: The validated attributes.

        Raises:
            serializers.ValidationError: If the user is not a customer.
        """
        user = self.context['request'].user
        if user.type != 'customer':
            raise serializers.ValidationError("Only Customers can create orders.")
        return attrs

    def create(self, validated_data):
        """
        Create and return a new Order.

        Steps:
            1) Read the OfferDetail instance provided by `validate_offer_detail_id`.
            2) Read the current user from the serializer context.
            3) Copy snapshot fields from the OfferDetail.
            4) Link the customer_user (current user), business_user (offer owner),
               and the offer_detail.

        Returns:
            Order: The newly created order instance.
        """
        offer_detail = validated_data.pop('offer_detail_id')
        user = self.context['request'].user

        offer = offer_detail.offer
        return Order.objects.create(
            customer_user = user,
            business_user = offer.user,
            offer_detail = offer_detail,
            title = offer_detail.title,
            revisions = offer_detail.revisions,
            delivery_time_in_days = offer_detail.delivery_time_in_days,
            price = offer_detail.price,
            features = offer_detail.features,
            offer_type = offer_detail.offer_type,
        )
    
    

class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer used to update only the status field of an Order.

    Intended use:
        - PATCH / PUT requests that change the order status (for example,
          from 'in_progress' to 'completed').

    Security tip:
        - Use this serializer in a view that restricts updates to the business
          user who owns the order, and validate that only allowed transitions
          are performed if your business rules require it.
    """

    class Meta:
        model = Order   
        fields = [
            'status',
        ]