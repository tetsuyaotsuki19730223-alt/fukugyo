from django.urls import path
from . import views


urlpatterns = [

    #path("", views.landing, name="home"),

    path("", views.home),

    path("signup/", views.signup_view, name="signup"),

    path("mission/", views.today_mission, name="today_mission"),
    path("mission/complete/", views.mission_complete, name="mission_complete"),

    path("ranking/", views.ranking, name="ranking"),

    #path("diagnosis/", views.diagnosis_start, name="diagnosis_start"),
    path("diagnosis/", views.diagnosis),
    path("history/", views.history),
    path("diagnosis/result/", views.diagnosis_result, name="diagnosis_result"),
    path(
        "diagnosis/share-image/",
        views.diagnosis_share_image,
        name="diagnosis_share_image"
    ),
    
    path("ai-chat/", views.ai_chat, name="ai_chat"),
    path("ai-blog/", views.ai_blog_generator, name="ai_blog_generator"),
    path("ai-history/", views.ai_chat_history, name="ai_chat_history"),
    path("ai-roadmap/", views.ai_roadmap, name="ai_roadmap"),
    path("ai-coach/", views.ai_coach, name="ai_coach"),
    path("roadmap/", views.ai_roadmap, name="ai_roadmap"),

    path("create-checkout-session/", views.create_checkout_session),
    path("pricing/", views.pricing, name="pricing"),
    path("premium/", views.premium_page, name="premium_page"),
    path("dashboard/", views.dashboard, name="dashboard"),

    path("ideas/", views.ai_sidejob_ideas, name="ai_sidejob_ideas"),

    path(
        "roadmap/pdf/",
        views.download_roadmap_pdf,
        name="roadmap_pdf"
    ),

    path("sidejobs/", views.sidejob_list, name="sidejob_list"),
    path("sidejobs/apply/<int:job_id>/", views.apply_sidejob, name="apply_sidejob"),

    path("community/", views.community, name="community"),

    path("templates/", views.template_market, name="template_market"),
    path("templates/buy/<int:template_id>/", views.buy_template, name="buy_template"),

    #path("type-diagnosis/", views.type_diagnosis, name="type_diagnosis"),
    path("type-diagnosis/", views.type_diagnosis),
    path("type-result/", views.type_result, name="type_result"),

    path("checkout/", views.create_checkout, name="checkout"),

    path("income/", views.income_simulator, name="income"),
]