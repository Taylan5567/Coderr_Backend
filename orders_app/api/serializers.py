from rest_framework import serializers
from orders_app.models import Order
from offers_app.models import OfferDetail


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = '__all__'



class OrderCreateSerializer(serializers.Serializer):
    offer_detail_id = serializers.IntegerField()
    
    class Meta:
        model = Order
        fields = ['id', 'customer_user', 'business_user', 'title', 'revisions', 'delivery_time_in_days',
                   'price', 'features', 'offer_type', 'status', 'created_at', 'updated_at', 'offer_detail_id'
                   ]
        read_only_fields = ['id', 'customer_user', 'business_user', 'title', 'revisions', 'delivery_time_in_days',
                   'price', 'features', 'offer_type', 'status', 'created_at', 'updated_at'
                   ]
        

    def validate_offer_detail_id(self, value):
        if not OfferDetail.objects.filter(id=value).exists():
            raise serializers.ValidationError("Offer detail does not exist.")
        return value

    def create(self, validated_data):
        request = self.context['request']
        customer = request.user
        offer_detail = (OfferDetail.objects
                        .select_related('offer__user')
                        .get(id=validated_data['offer_detail_id']))

        if offer_detail.offer.user_id == customer.id:
            raise serializers.ValidationError("You cannot order your own offer.")

        order = Order.objects.create(
            customer_user=customer,
            business_user=offer_detail.offer.user,
            offer_detail=offer_detail,
            title=offer_detail.title,
            revisions=offer_detail.revisions,
            delivery_time_in_days=offer_detail.delivery_time_in_days,
            price=offer_detail.price,
            features=offer_detail.features,
            offer_type=offer_detail.offer_type,
            status='in_progress',
        )
        return order
    
    

class OrderStatusUpdateSerializer(serializers.ModelSerializer):
    offer_detail_id = serializers.IntegerField()

    class Meta:
        model = Order
        fields = ['id', 'customer_user', 'business_user', 'title', 'revisions', 'delivery_time_in_days',
                   'price', 'features', 'offer_type', 'status', 'created_at', 'updated_at', 'offer_detail_id'
                   ]
        read_only_fields = ['id', 'customer_user', 'business_user', 'title', 'revisions', 'delivery_time_in_days',
                   'price', 'features', 'offer_type', 'created_at', 'updated_at'
                   ]