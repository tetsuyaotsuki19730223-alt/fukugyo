from django.contrib import admin
from django import forms
from snippets.models import (
    Profile,
    Mission,
    UserMission,
    CommunityPost,
    AIChatHistory,
    SuccessStory,
    BlogPost,
    Referral,
    DiagnosisResult,
    Diagnosis,
    CoachMission,
    AIChat,
    AIChatLog,
    Roadmap,
    DailyMission,
    SideJob,
    SideJobApply,
    Template,
    TemplatePurchase,
    AISearch,
    Snippet,
)


class ProfileAdminForm(forms.ModelForm):
    email = forms.EmailField(required=False, label="email")

    class Meta:
        model = Profile
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.pk and self.instance.user:
            self.fields["email"].initial = self.instance.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)

        if profile.user:
            profile.user.email = self.cleaned_data.get("email", "")
            if commit:
                profile.user.save()

        if commit:
            profile.save()

        return profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    form = ProfileAdminForm

    list_display = (
        "username_display",
        "email_display",
        "is_premium",
        "xp",
        "level",
        "streak",
        "ai_count",
        "sidejob_type",
        "last_login_date",
    )

    search_fields = (
        "user__username",
        "user__email",
    )

    list_filter = (
        "is_premium",
        "level",
        "sidejob_type",
        "last_login_date",
    )

    ordering = ("-id",)

    fields = (
        "user",
        "email",
        "sidejob_type",
        "is_premium",
        "xp",
        "level",
        "streak",
        "last_login_date",
        "streak_freeze",
        "ai_count",
    )

    autocomplete_fields = ("user",)

    def username_display(self, obj):
        return obj.user.username
    username_display.short_description = "username"

    def email_display(self, obj):
        return obj.user.email
    email_display.short_description = "email"


@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ("title", "mission_type", "xp", "created_at")
    search_fields = ("title", "description")
    list_filter = ("mission_type", "created_at")
    ordering = ("mission_type", "-created_at")


@admin.register(UserMission)
class UserMissionAdmin(admin.ModelAdmin):
    list_display = ("user", "mission", "assigned_date", "completed")
    search_fields = ("user__username", "user__email", "mission__title")
    list_filter = ("completed", "assigned_date", "mission__mission_type")
    ordering = ("-assigned_date", "-id")


@admin.register(CommunityPost)
class CommunityPostAdmin(admin.ModelAdmin):
    list_display = ("user", "short_content", "created_at", "is_edited")
    search_fields = ("user__username", "content")
    list_filter = ("created_at", "is_edited")
    ordering = ("-created_at",)

    def short_content(self, obj):
        return obj.content[:30]
    short_content.short_description = "content"


@admin.register(AIChatHistory)
class AIChatHistoryAdmin(admin.ModelAdmin):
    list_display = ("user", "short_question", "created_at")
    search_fields = ("user__username", "user__email", "question", "answer")
    list_filter = ("created_at",)
    ordering = ("-created_at",)

    def short_question(self, obj):
        return obj.question[:40]
    short_question.short_description = "question"


@admin.register(SuccessStory)
class SuccessStoryAdmin(admin.ModelAdmin):
    list_display = ("name", "job", "sidejob", "income", "created_at")
    search_fields = ("name", "job", "sidejob", "story")
    ordering = ("-created_at",)


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "created_at")
    search_fields = ("title", "slug", "content")
    ordering = ("-created_at",)


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ("user", "code", "invited_count", "created_at")
    search_fields = ("user__username", "user__email", "code")
    ordering = ("-created_at",)


@admin.register(DiagnosisResult)
class DiagnosisResultAdmin(admin.ModelAdmin):
    list_display = ("user", "result", "created_at")
    search_fields = ("user__username", "user__email", "result")
    ordering = ("-created_at",)


@admin.register(Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    list_display = ("user", "result", "created_at")
    search_fields = ("user__username", "user__email", "result")
    ordering = ("-created_at",)


@admin.register(CoachMission)
class CoachMissionAdmin(admin.ModelAdmin):
    list_display = ("title", "xp_reward", "created_at")
    search_fields = ("title", "description")
    ordering = ("-created_at",)


@admin.register(AIChat)
class AIChatAdmin(admin.ModelAdmin):
    list_display = ("user", "short_question", "created_at")
    search_fields = ("user__username", "user__email", "question", "answer")
    ordering = ("-created_at",)

    def short_question(self, obj):
        return obj.question[:40]
    short_question.short_description = "question"


@admin.register(AIChatLog)
class AIChatLogAdmin(admin.ModelAdmin):
    list_display = ("user", "short_question", "created_at")
    search_fields = ("user__username", "user__email", "question", "answer")
    ordering = ("-created_at",)

    def short_question(self, obj):
        return obj.question[:40]
    short_question.short_description = "question"


@admin.register(Roadmap)
class RoadmapAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at")
    search_fields = ("user__username", "user__email", "content")
    ordering = ("-created_at",)


@admin.register(DailyMission)
class DailyMissionAdmin(admin.ModelAdmin):
    list_display = ("user", "content", "created_at")
    search_fields = ("user__username", "user__email", "content")
    ordering = ("-created_at",)


@admin.register(SideJob)
class SideJobAdmin(admin.ModelAdmin):
    list_display = ("title", "income_min", "income_max", "difficulty", "created_at")
    search_fields = ("title", "description")
    ordering = ("-created_at",)


@admin.register(SideJobApply)
class SideJobApplyAdmin(admin.ModelAdmin):
    list_display = ("job", "user", "created_at")
    search_fields = ("job__title", "user__username", "user__email")
    ordering = ("-created_at",)


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "created_by", "created_at")
    search_fields = ("title", "description", "content", "created_by__username")
    ordering = ("-created_at",)


@admin.register(TemplatePurchase)
class TemplatePurchaseAdmin(admin.ModelAdmin):
    list_display = ("template", "user", "created_at")
    search_fields = ("template__title", "user__username", "user__email")
    ordering = ("-created_at",)


@admin.register(AISearch)
class AISearchAdmin(admin.ModelAdmin):
    list_display = ("user", "query", "created_at")
    search_fields = ("user__username", "user__email", "query")
    ordering = ("-created_at",)


@admin.register(Snippet)
class SnippetAdmin(admin.ModelAdmin):
    list_display = ("title", "created_by", "created_at")
    search_fields = ("title", "code", "created_by__username")
    ordering = ("-created_at",)