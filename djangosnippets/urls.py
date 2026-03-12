from django.contrib import admin
from django.urls import path, include
from snippets import views  # ← 追加
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),

    path("accounts/login/", auth_views.LoginView.as_view()),
    path("accounts/logout/", auth_views.LogoutView.as_view()),
    
    # トップは診断にする
    #path("", views.diagnosis_start, name="home"),  # ← 追加（これが最優先）

    # それ以外は snippets.urls に回す
    path("", include("snippets.urls")),
]