from django.contrib.auth.models import UserManager, AbstractUser
from django.db import models

class UserProfile(AbstractUser):
    """
    Custom user that supports two account types and extra profile information.

    Account type:
        - "customer": default account type for buyers.
        - "business": account type for sellers/providers.

    Inherited permissions:
        - is_staff / is_superuser: unchanged from AbstractUser and can be used
          to gate admin-only endpoints or actions.

    Additional profile fields:
        file (FileField): optional avatar or document upload.
        location (str): optional free-text location.
        tel (str): optional phone number.
        description (text): optional bio or company description.
        working_hours (str): optional opening/working hours.
        type (choice): 'customer' or 'business'.
        created_at (datetime): timestamp when the profile was created.

    Notes:
        - AbstractUser already defines email, first_name and last_name.
          Overriding them is acceptable but you should keep types compatible.
        - Consider making email unique if you want email-based login:
              email = models.EmailField(unique=True)
          and update AUTHENTICATION_BACKENDS accordingly.
        - File uploads require proper MEDIA_ROOT / MEDIA_URL configuration.
    """

    objects = UserManager()
    TYPE_CHOICES = (
        ("customer", "Customer"),
        ("business", "Business"),
    )

    email = models.EmailField(max_length=255, blank=True)
    file = models.FileField(upload_to="uploads/", null=True, blank=True)
    first_name = models.CharField(max_length=255, null=True, blank=True)
    last_name = models.CharField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    tel = models.CharField(max_length=50, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    working_hours = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="customer")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username 
