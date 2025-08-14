from rest_framework import serializers
from offers_app.models import Offer, OfferDetail
from django.db.models import Min

class OfferDetailsSerializer(serializers.ModelSerializer):
    """
    Serializer for a single OfferDetail.

    Exposes the basic data of a variant:
    - title
    - number of revisions
    - delivery time in days
    - price
    - features (as a list)
    - variant type (basic, standard, premium)
    """
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
    """
    Serializer for a complete Offer.

    Includes:
    - core fields of the offer (title, image, description, timestamps)
    - all related OfferDetails (read-only)
    
    Note:
    - The field "user" returns an identifier as defined below.
    - The computed fields are derived per object using aggregates.
    """
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
        """
        Return the lowest price among all related OfferDetails.

        Returns:
            A number or None if no details exist.
        """
        return obj.details.aggregate(v=Min('price'))['v']

    def get_delivery_time_in_days(self, obj):
        """
        Return the smallest delivery time (in days) among all related OfferDetails.

        Returns:
            A number or None if no details exist.
        """
        return obj.details.aggregate(v=Min('delivery_time_in_days'))['v']


class OfferCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new Offer with several OfferDetails.

    Expects:
    - title, image, description
    - a list of at least three OfferDetails (field "details")

    Behavior:
    - Validates that at least three details are provided.
    - Creates the Offer first and then all OfferDetails that reference it.
    """
    details = OfferDetailsSerializer(many=True)
    class Meta:
        model = Offer
        fields = [
            'id',
            'title',
            'image',
            'description',
            'details',
        ]

    def validate(self, attrs):
        """
        Validate that a sufficient number of OfferDetails have been provided.

        Requirements:
            At least three details must be present.
        """
        details = attrs.get('details', [])
        if len(details) < 3:
            raise serializers.ValidationError("At least 3 details are required.")
        return attrs

    def create(self, validated_data):
        """
        Create a new Offer and all related OfferDetails.

        Assumptions:
            - The serializer context contains a request with an authenticated user.
        """
        request = self.context.get('request')
        details_data = validated_data.pop('details')
        offer = Offer.objects.create(user=request.user, **validated_data)
        for detail_data in details_data:
            OfferDetail.objects.create(offer=offer, **detail_data)
        return offer
    

class OfferUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an existing Offer.

    Behavior:
    - Updates the Offer fields.
    - Deletes and recreates all related OfferDetails.
    """
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
        """
        Update an existing Offer and all related OfferDetails.

        Assumptions:
            - The serializer context contains a request with an authenticated user.
        """
        details_data = validated_data.pop('details', None)
        offer = super().update(instance, validated_data)
        if details_data is not None:
            offer.details.all().delete()
            OfferDetail.objects.bulk_create([OfferDetail(offer=offer, **d) for d in details_data])
        return offer
    

    def to_representation(self, instance):
        """
        Normalize None values to empty strings for selected optional fields.

        This helps clients avoid extra null checks when rendering.
        """
        data = super().to_representation(instance)
        for space in ["first_name", "last_name", "location", "tel", "description", "working_hours"]:
            if data.get(space) is None:
                data[space] = ""
        return data
    
class OneOfferDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for a single OfferDetail.

    Exposes the basic data of a variant:
    - title
    - number of revisions
    - delivery time in days
    - price
    - features (as a list)
    - variant type (basic, standard, premium)
    """
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
        
    def to_representation(self, instance):
        """
        Normalize None values to empty strings for selected optional fields.

        This helps clients avoid extra null checks when rendering.
        """
        data = super().to_representation(instance)
        for space in ["first_name", "last_name", "location", "tel", "description", "working_hours"]:
            if data.get(space) is None:
                data[space] = ""
        return data