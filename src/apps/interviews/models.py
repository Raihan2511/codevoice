import uuid
from django.db import models
from django.conf import settings

class Question(models.Model):
    """
    Represents a technical question in the system.
    e.g., "Explain the difference between TCP and UDP."
    """
    DIFFICULTY_CHOICES = [
        ('EASY', 'Easy'),
        ('MEDIUM', 'Medium'),
        ('HARD', 'Hard'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    topic = models.CharField(max_length=100)  # e.g., "Network Engineering"
    text = models.TextField()                 # The actual question
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='MEDIUM')
    
    # TEACHER NOTE: 
    # We store "expected key points" so the AI knows how to grade the answer later.
    expected_answer_points = models.TextField(help_text="Bullet points the AI should look for.")

    def __str__(self):
        return f"{self.topic}: {self.text[:50]}..."


class InterviewSession(models.Model):
    """
    Tracks a single user's attempt at an interview.
    """
    STATUS_CHOICES = [
        ('STARTED', 'Started'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    
    # Link to the User who is taking the interview
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='interviews')
    
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='STARTED')
    
    # Final consolidated score (0-100)
    total_score = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.user.username} - {self.start_time.date()}"


class InterviewTurn(models.Model):
    """
    Stores one "Exchange" in the conversation.
    AI asks -> User answers -> AI grades.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(InterviewSession, on_delete=models.CASCADE, related_name='turns')
    question = models.ForeignKey(Question, on_delete=models.SET_NULL, null=True)
    
    # What the AI asked (sometimes it asks follow-ups, not just the base Question)
    ai_message = models.TextField()
    
    # What the User said (Transcript from Deepgram)
    user_transcript = models.TextField(blank=True, null=True)
    
    # Provide a URL/Path to the audio file if we save it
    audio_file = models.FileField(upload_to='recordings/', blank=True, null=True)

    # AI Grading
    score = models.IntegerField(default=0) # 0-10
    feedback = models.TextField(blank=True) # Text explanation of the score

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at'] # Keep the conversation in order