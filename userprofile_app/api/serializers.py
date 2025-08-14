from rest_framework import serializers
from ..models import UserProfile

class ProfileSerializer(serializers.ModelSerializer):
    """
    Full read serializer for a user profile with write-only inputs.

    Exposed fields:
        user (int, read-only): Primary key of the profile (source='id').
        username (str, read-only): Username of the profile's user.
        first_name (str, write-only): First name; accepted on input, not returned.
        last_name (str, write-only): Last name; accepted on input, not returned.
        email (str, write-only): Email address; accepted on input, not returned.
        type (choice, write-only): Account type per UserProfile.TYPE_CHOICES.
        file (file): Optional avatar or attachment field from the model.
        location (str): Optional location text.
        tel (str): Optional phone number.
        description (str): Optional bio/description.
        working_hours (str): Optional working hours text.
        created_at (datetime, read-only): Mapped from `date_joined`.

    Notes:
        - The method `to_representation()` normalizes several optional fields
          by replacing None with "" for client convenience.
        - With `read_only_fields = fields` every field is read-only. If you
          require writes, adjust `read_only_fields` accordingly.
    """
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
        """
        Return the profile's primary key for the `user` field.

        This is redundant with `source='id'` but kept for compatibility.
        """
        return obj.id

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

class ProfilePatchSerializer(serializers.ModelSerializer):
    """
    Partial-update serializer for user profiles (PATCH).

    Behavior:
        - Updates only selected fields in `update()`: first_name, last_name,
          location, tel, description, working_hours.
        - Does not modify username, email, type, or file in this method.

    Exposed fields:
        Same as ProfileSerializer; however, writes are effectively limited by
        the custom `update()` implementation below.
    """
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
        """
        Apply partial updates to a subset of fields.

        Fields updated:
            first_name, last_name, location, tel, description, working_hours.

        Returns:
            The updated UserProfile instance.
        """
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.location = validated_data.get('location', instance.location)
        instance.tel = validated_data.get('tel', instance.tel)
        instance.description = validated_data.get('description', instance.description)
        instance.working_hours = validated_data.get('working_hours', instance.working_hours)
        instance.save()
        return instance
    

class ProfileDetailsSerializer(serializers.ModelSerializer):
    """
    Read-only details serializer for user profiles.

    Intended use:
        - Retrieve/display a user's profile data without write operations.

    Exposed fields:
        Same field list as ProfileSerializer for consistency, but typically
        used in GET endpoints only.
    """
    user = serializers.IntegerField(source='id', read_only=True)
    class Meta:
        model = UserProfile
        fields = [
            'user','username', 'first_name', 'last_name', 'file',
            'location', 'tel', 'description', 'working_hours', 'type',
            'email', 'created_at',
        ]