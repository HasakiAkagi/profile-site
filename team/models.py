from django.db import models
from django.conf import settings
from profiles.models import Profile

class Team(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    name = models.CharField(max_length=100)
    leader_name = models.CharField(max_length=100, blank=True)
    memo = models.TextField(blank=True)
    self_included = models.BooleanField(default=False)
    members = models.ManyToManyField(Profile, related_name='teams', blank=True)

    def __str__(self):
        return self.name
