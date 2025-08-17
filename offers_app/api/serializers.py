from rest_framework import serializers
from offers_app.models import Offer, OfferDetail
from django.db.models import Min
from userprofile_app.models import UserProfile
from rest_framework.exceptions import ValidationError

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


class UserDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for user details.

    Exposes the basic data of a user:
    - first name
    - last name
    - usernameS
    """
    class Meta:
        model = UserProfile
        fields = [
            'first_name',
            'last_name',
            'username'
        ]

class OfferDetailLinkSerializer(serializers.ModelSerializer):
    """
    Serializer for a single OfferDetail.

    Exposes the basic data of a variant:
    - id
    - title
    - number of revisions
    - delivery time in days
    - price
    - features (as a list)
    - variant type (basic, standard, premium)
    """
    url = serializers.HyperlinkedIdentityField(
        view_name='one-offer-details',
        lookup_field='id'
    )

    class Meta:
        model = OfferDetail
        fields = ['id', 'url']


    def get_details(self, obj):
        result = []
        for detail in obj.details.all():
            item = {
                "id": detail.id,
                "url": f"/offerdetails/{detail.id}/"
            }
            result.append(item)
        return result




class OfferSerializer(serializers.ModelSerializer):
    """
    Serializer for a single Offer.

    Exposes the basic data of an offer:
    - id
    - title
    - image
    - description
    - details
    """
    details = OfferDetailLinkSerializer(many=True, read_only=True)
    min_price = serializers.SerializerMethodField()
    min_delivery_time = serializers.SerializerMethodField()
    user = serializers.IntegerField(source='user_id', read_only=True)
    user_details = UserDetailSerializer(source='user', read_only=True)

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
            'user_details',
        ]

    def get_min_price(self, obj):
        return obj.details.aggregate(min=Min('price'))['min']

    def get_min_delivery_time(self, obj):
        return obj.details.aggregate(min=Min('delivery_time_in_days'))['min']



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
    image = serializers.ImageField(required=False)
    description = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Offer
        fields = [
            'id',
            'title',
            'image',
            'description',
            'details',
        ]

    def update(self, instance, validated_data):
        details_data = validated_data.pop('details', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if details_data is not None:
    
            existing_details = {}
            for detail in instance.details.all():
                existing_details[detail.offer_type] = detail
                
            for detail in details_data:
                offer_type = detail.get('offer_type')
                if offer_type in existing_details:
                    detail_instance = existing_details[offer_type]
                    for attr, value in detail.items():
                        setattr(detail_instance, attr, value)
                    detail_instance.save()
                else:
                    raise serializers.ValidationError(
                        f"OfferDetail with type '{offer_type}' does not exist for this offer."
                    )

        return instance

        

    def to_representation(self, instance):
        """
        Normalize None values to empty strings for selected optional fields.

        This helps clients avoid extra null checks when rendering.
        """
        data = super().to_representation(instance)
        for space in ["title", "description"]:
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
        

