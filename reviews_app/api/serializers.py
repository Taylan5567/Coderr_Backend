from rest_framework import serializers
from reviews_app.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    """
    Read/write serializer for the Review model.

    Purpose:
        - Used to create and return reviews via the API.
        - Ensures that the rating value is within the allowed range.

    Special fields:
        reviewer (read-only):
            Exposes the reviewer's primary key (id) instead of the full nested
            user object. This prevents clients from overriding the reviewer and
            keeps the payload compact.

    Validation:
        - rating must be an integer between 1 and 5 (inclusive).

    Returned/accepted fields:
        All model fields are included via Meta.fields = "__all__".
        The actual field list depends on the Review model definition.
    """
    reviewer = serializers.ReadOnlyField(source='reviewer.id')
    class Meta:
        model = Review
        fields = '__all__'



    
    def validate(self, attrs):
        """
        Object-level validation for a review.

        Ensures:
            - rating is between 1 and 5 (inclusive).

        Raises:
            serializers.ValidationError: if the rating is outside the allowed range.

        Returns:
            dict: the validated attributes.
        """
        if attrs['rating'] < 1 or attrs['rating'] > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")

        review_exists = Review.objects.filter(reviewer=self.context['request'].user, **attrs).exists()
        if review_exists:
            raise serializers.ValidationError("You have already reviewed this item.")

        return attrs


class ReviewUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating an existing review.

    Purpose:
        - Intended for PUT/PATCH operations on a Review instance.
        - Uses the model's fields as defined; consider restricting the field
          set if only specific fields should be editable (for example, only
          'rating' and 'comment').

    Returned/accepted fields:
        All model fields are included via Meta.fields = "__all__".
        Adjust this if your update endpoint should be more restrictive.
    """
    class Meta:
        model = Review
        fields = '__all__'

