from rest_framework import serializers
from reviews_app.models import Review, BaseInformation


class ReviewSerializer(serializers.ModelSerializer):
    reviewer = serializers.ReadOnlyField(source='reviewer.id')
    class Meta:
        model = Review
        fields = '__all__'



    
    def validate(self, attrs):
        if attrs['rating'] < 1 or attrs['rating'] > 5:
            raise serializers.ValidationError("Rating must be between 1 and 5.")
        return attrs
    


class ReviewUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

