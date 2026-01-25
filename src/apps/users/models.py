import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Custom User Model for CodeVoice.
    Inherits from Django's AbstractUser to keep username, password, email, etc.
    """
    
    # TEACHER NOTE: 
    # We use UUIDs (e.g., 'a1b2-c3d4-...') instead of Integers (1, 2, 3) for IDs.
    # This is much more secure for public-facing apps (prevents ID guessing).
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # We can add custom fields here later, for example:
    # bio = models.TextField(blank=True)
    # interview_count = models.IntegerField(default=0)

    def __str__(self):
        return self.username