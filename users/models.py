from django.db import models
from django.contrib.auth.models import User

class CareerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    highest_education = models.CharField(max_length=100, blank=True)
    field_of_study = models.CharField(max_length=100, blank=True)
    university = models.CharField(max_length=150, blank=True)
    skills = models.TextField(blank=True, help_text='Comma separated skills')
    interests = models.TextField(blank=True, help_text='Comma separated interests')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    academic_background = models.TextField(blank=True, null=True)
    career_goals = models.TextField(blank=True, null=True)

    is_completed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
    # Ensure we save lists as comma-separated strings
        if isinstance(self.skills, list):
            self.skills = ', '.join(self.skills)
        if isinstance(self.interests, list):
            self.interests = ', '.join(self.interests)
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s Career Profile"




class IncompleteProfileAccessLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    attempted_path = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} tried to access {self.attempted_path} at {self.timestamp}"