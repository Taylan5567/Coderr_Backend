from django.db import models
from userprofile_app.models import UserProfile

class Review(models.Model):
    business_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='rewiews_as_business')
    reviewer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='reviews_as_reviewer')
    rating = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    

class BaseInformation(models.Model):
    review_count = models.PositiveIntegerField(default=0)
    average_rating = models.FloatField(default=0.0)
    business_profile_count = models.PositiveIntegerField(default=0)
    offer_count = models.PositiveIntegerField(default=0)

    class Meta:
        abstract = True