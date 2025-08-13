from rest_framework import serializers
from orders_app.models import Order
from offers_app.models import OfferDetail


class OrderSerializer(serializers.ModelSerializer):

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
        try:
            offer_detail = OfferDetail.objects.get(id=value)
        except OfferDetail.DoesNotExist:
            raise serializers.ValidationError("Offer detail with this ID does not exist.")
        return offer_detail

    def validate(self, attrs):
        user = self.context['request'].user
        if user.type != 'customer':
            raise serializers.ValidationError("Only Customers can create orders.")
        return attrs

    def create(self, validated_data):
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

    class Meta:
        model = Order   
        fields = [
            'status',
        ]