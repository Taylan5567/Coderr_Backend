from django.db import models
from userprofile_app.models import UserProfile

class Review(models.Model):
    """
    A single review made by one user about a business user.

    Relationships:
        business_user (FK to UserProfile):
            The business (seller/provider) being reviewed.
        reviewer (FK to UserProfile):
            The customer (or user) who writes the review.

    Core fields:
        rating (int):
            The numeric rating value. Commonly constrained to 1–5 in the API layer.

    Timestamps:
        created_at (datetime): Automatically set when the review is created.
        updated_at (datetime): Automatically updated on each save.

    Notes:
        - Validation of the rating range (e.g., 1–5) is typically enforced in the serializer.
        - Consider adding a unique constraint if each reviewer should only review a given
          business once (e.g., UniqueConstraint on (business_user, reviewer)).
    """
    business_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='rewiews_as_business')
    reviewer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='reviews_as_reviewer')
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    

class BaseInformation(models.Model):
    """
    Abstract model for aggregate marketplace statistics.

    Fields:
        review_count (int): Total number of reviews in the system.
        average_rating (float): Average rating across all reviews.
        business_profile_count (int): Number of users with business profiles.
        offer_count (int): Total number of offers.

    Usage:
        - Inherit from this model for a concrete table that stores snapshot
          metrics, or use it as a base for admin/reporting dashboards.
    """
    review_count = models.PositiveIntegerField(default=0)
    average_rating = models.FloatField(default=0.0)
    business_profile_count = models.PositiveIntegerField(default=0)
    offer_count = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True