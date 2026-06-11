from django.db import models


class User(models.Model):
    """
    Mirrors the Mongoose UserSchema.
    Note: This is a custom user table for Firebase-authenticated users,
    NOT Django's built-in auth.User.
    """
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=50, default='user')
    photo_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'users'

    def __str__(self):
        return f"{self.name} <{self.email}>"


class Resume(models.Model):
    """
    Mirrors the Mongoose ResumeSchema.
    user field stores email/uid string (same as original — guest-friendly).
    """
    user = models.CharField(max_length=255, default='guest')
    resume_name = models.CharField(max_length=255)
    job_desc = models.TextField()
    score = models.CharField(max_length=10, blank=True, null=True)
    feedback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'resumes'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.resume_name} (user={self.user}, score={self.score})"
