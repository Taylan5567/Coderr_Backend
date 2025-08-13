from rest_framework import serializers
from offers_app.models import Offer, OfferDetail
from django.db.models import Min

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
    details = OfferDetailsSerializer(many=True, read_only=True)
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
            'delivery_time_in_days',
        ]
    
    
    def get_min_price(self, obj):
        return obj.details.aggregate(v=Min('price'))['v']

    def get_delivery_time_in_days(self, obj):
        return obj.details.aggregate(v=Min('delivery_time_in_days'))['v']


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
            raise serializers.ValidationError("At least 3 details are required.")
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
    offer_type = serializers.ChoiceField(choices=OfferDetail.OFFER_TYPE, required=False)
    class Meta:
        model = Offer
        fields = [
            'title',
            'image',
            'description',
            'details',
            'offer_type',
        ]

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)
        offer = super().update(instance, validated_data)
        if details_data is not None:
            offer.details.all().delete()
            OfferDetail.objects.bulk_create([OfferDetail(offer=offer, **d) for d in details_data])
        return offer
    
class OneOfferDetailSerializer(serializers.ModelSerializer):
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