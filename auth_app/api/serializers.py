from rest_framework import serializers
from userprofile_app.models import UserProfile
from django.contrib.auth import get_user_model

User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for registering a new user.
    Includes password confirmation with `repeated_password`.
    """

    repeated_password = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(choices=UserProfile.TYPE_CHOICES, write_only=True)

    class Meta:
        model = User 
        fields = ['username', 'email', 'password', 'repeated_password', 'type']
        extra_kwargs = {
            'password': {
                'write_only': True 
            }
        }

    def save(self, **kwargs):
        """
        Save method to manually create a User object.

        1. Checks if a user with the given email already exists.
        2. Creates a new User instance (not yet saved).
        3. Checks if passwords match.
        4. Hashes the password and saves the user.

        :raises serializers.ValidationError: If a user with the given email already exists or if passwords don't match.
        :return: The created User object.
        """
        pw = self.validated_data['password']
        repeated_pw = self.validated_data['repeated_password']
        email = self.validated_data['email']
        username = self.validated_data['username']

        user = UserProfile(
            email=email,           
            username=username,
            type=self.validated_data['type']
        )

        if pw != repeated_pw:
            raise serializers.ValidationError({'error': 'Password dont match'})

        
        user.save()
        return user


    def validate_email(self, value):
        """
        Validates that the given email does not already exist in the User model.

        :param value: The email address to validate.
        :type value: str
        :raises serializers.ValidationError: If the email already exists in the database.
        :return: The validated email value if it's unique.
        :rtype: str
        """

        if UserProfile.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value
    
