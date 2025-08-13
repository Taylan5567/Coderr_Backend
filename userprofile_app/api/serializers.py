from rest_framework import serializers
from ..models import UserProfile

class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='id', read_only=True)
    username = serializers.CharField(read_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    type = serializers.ChoiceField(choices=UserProfile.TYPE_CHOICES, write_only=True)
    created_at = serializers.DateTimeField(source='date_joined', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'user','username', 'first_name', 'last_name', 'file',
            'location', 'tel', 'description', 'working_hours', 'type',
            'email', 'created_at',
        ]
        read_only_fields = fields  


    def get_user(self, obj):
        return obj.id

    def to_representation(self, instance):
        data = super().to_representation(instance)
        for space in ["first_name", "last_name", "location", "tel", "description", "working_hours"]:
            if data.get(space) is None:
                data[space] = ""
        return data

class ProfilePatchSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='id', read_only=True)
    type = serializers.CharField(write_only=True)
    class Meta:
        model = UserProfile
        fields = [
            'user','username', 'first_name', 'last_name', 'file',
            'location', 'tel', 'description', 'working_hours', 'type',
            'email', 'created_at',
        ]


    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.location = validated_data.get('location', instance.location)
        instance.tel = validated_data.get('tel', instance.tel)
        instance.description = validated_data.get('description', instance.description)
        instance.working_hours = validated_data.get('working_hours', instance.working_hours)
        instance.save()
        return instance
    

class ProfileDetailsSerializer(serializers.ModelSerializer):
    user = serializers.IntegerField(source='id', read_only=True)
    class Meta:
        model = UserProfile
        fields = [
            'user','username', 'first_name', 'last_name', 'file',
            'location', 'tel', 'description', 'working_hours', 'type',
            'email', 'created_at',
        ]