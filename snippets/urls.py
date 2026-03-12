from django.urls import path
from . import views

urlpatterns = [

    path("", views.home),

    path("signup/", views.signup_view, name="signup"),

    path("mission/", views.today_mission, name="today_mission"),
    path("mission/complete/", views.mission_complete, name="mission_complete"),

    path("ranking/", views.ranking, name="ranking"),

    path("diagnosis/", views.diagnosis),

    path("history/", views.history),

    path("type-diagnosis/", views.type_diagnosis),

    path("type-result/", views.type_result, name="type_result"),

]