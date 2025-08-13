from rest_framework import serializers
from offers_app.models import Offer, OfferDetail


class OfferDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = OfferDetail
        fields = [
            'id',
            'title',
            'revisions',
            'delivery_time_in_days',
            'price',
            'features',
            'offer_type',
            ]

class OfferSerializer(serializers.ModelSerializer):
    details = OfferDetailsSerializer(many=True)
    min_price = serializers.SerializerMethodField()
    delivery_time_in_days  = serializers.SerializerMethodField()
    user = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Offer
        fields = [
            'id',
            'user',
            'title',
            'image',
            'description',
            'created_at',
            'updated_at',
            'details',
            'min_price',
            'min_delivery_time',
        ]

    
    
    def update(self, instance, validated_data):
        details_data = validated_data.pop('details')
        offer = super().update(instance, validated_data)
        for detail_data in details_data:
            OfferDetail.objects.update_or_create(offer=offer, **detail_data)
        return offer
    


class OfferCreateSerializer(serializers.ModelSerializer):
    details = OfferDetailsSerializer(many=True)
    class Meta:
        model = Offer
        fields = [
            'title',
            'image',
            'description',
            'details',
        ]

    def validate(self, attrs):
        details = attrs.get('details', [])
        if len(details) < 3:
            raise serializers.ValidationError("Ein Offer muss mindestens 3 Details haben!")
        return attrs

    def create(self, validated_data):
        request = self.context.get('request')
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(user=request.user, **validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer


class OfferUpdateSerializer(serializers.ModelSerializer):
    details = OfferDetailsSerializer(many=True)
    class Meta:
        model = Offer
        fields = [
            'title',
            'image',
            'description',
            'details',
        ]

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details')
        offer = super().update(instance, validated_data)
        for detail_data in details_data:
            OfferDetail.objects.update_or_create(offer=offer, **detail_data)
        return offer