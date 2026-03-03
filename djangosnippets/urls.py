from django.contrib import admin
from django.urls import path, include
from snippets import views  # ← 追加

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),

    # トップは診断にする
    path("", views.diagnosis_start, name="home"),  # ← 追加（これが最優先）

    # それ以外は snippets.urls に回す
    path("", include("snippets.urls")),
]