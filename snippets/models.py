from django.db import models
from django.contrib.auth.models import User
import uuid

class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    xp = models.IntegerField(default=0)

    level = models.IntegerField(default=1)

    streak = models.IntegerField(default=0)

    last_login_date = models.DateField(null=True, blank=True)
    
    is_premium = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Snippet(models.Model):

    title = models.CharField(max_length=200)

    code = models.TextField()

    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class CoachMission(models.Model):

    title = models.CharField(max_length=200)

    description = models.TextField(blank=True)

    xp_reward = models.IntegerField(default=20)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
class DiagnosisResult(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    result = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.result
    

class Diagnosis(models.Model):

    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
    )

    result = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)


class Referral(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    code = models.CharField(max_length=50, unique=True)

    invited_count = models.IntegerField(default=0)

    def save(self, *args, **kwargs):

        if not self.code:

            self.code = uuid.uuid4().hex[:8]

        super().save(*args, **kwargs)


class Roadmap(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

class AIChat(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    question = models.TextField()

    answer = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

def add_xp(profile, xp):

    profile.xp += xp

    profile.level = profile.xp // 100 + 1

    profile.save()

class DailyMission(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    content = models.TextField()

    created_at = models.DateField(auto_now_add=True)

class SideJob(models.Model):

    title = models.CharField(max_length=200)

    description = models.TextField()

    reward = models.IntegerField()

    created_at = models.DateTimeField(auto_now_add=True)

class SideJobApply(models.Model):

    job = models.ForeignKey(SideJob, on_delete=models.CASCADE)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

class CommunityPost(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

class Template(models.Model):

    title = models.CharField(max_length=200)

    description = models.TextField()

    price = models.IntegerField()

    content = models.TextField()

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

class TemplatePurchase(models.Model):

    template = models.ForeignKey(Template, on_delete=models.CASCADE)

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

class Mission(models.Model):

    title = models.CharField(max_length=200)

    xp = models.IntegerField(default=10)

    def __str__(self):
        return self.title