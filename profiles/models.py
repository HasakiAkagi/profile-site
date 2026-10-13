from django.db import models
from django.conf import settings

class Profile(models.Model):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='profiles'
    )
    photo = models.ImageField(upload_to='profiles/', blank=True, null=True)
    name = models.CharField(max_length=100)
    mbti = models.CharField(max_length=10)
    hobby = models.CharField(max_length=100, blank=True)
    skill = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    relationship = models.CharField(max_length=100, blank=True)
    talk = models.TextField(blank=True)

    def __str__(self):
        return self.name
