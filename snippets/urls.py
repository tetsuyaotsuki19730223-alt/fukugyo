from django.urls import path
from . import views

urlpatterns = [

    # トップ
    path("", views.home, name="home"),

    # アカウント
    path("signup/", views.signup_view, name="signup"),

    # AI診断
    path("diagnosis/", views.diagnosis, name="diagnosis"),
    path("history/", views.history, name="history"),

    # 副業タイプ診断
    path("type-diagnosis/", views.type_diagnosis, name="type_diagnosis"),
    path("type-result/", views.type_result, name="type_result"),

    # AI機能
    path("ai-chat/", views.ai_chat, name="ai_chat"),
    path("ai-blog/", views.ai_blog_generator, name="ai_blog"),
    path("ai-roadmap/", views.ai_roadmap, name="ai_roadmap"),
    path("ideas/", views.ai_sidejob_ideas, name="ideas"),
    path("ai-search/", views.ai_search, name="ai_search"),
    path("ai-diagnosis/", views.ai_diagnosis, name="ai_diagnosis"),

    # 履歴
    path("ai-history/", views.ai_chat_history, name="ai_history"),

    # ミッション
    path("mission/", views.today_mission, name="today_mission"),
    path("mission/complete/", views.mission_complete, name="mission_complete"),

    # ダッシュボード
    path("dashboard/", views.dashboard, name="dashboard"),

    # ランキング
    path("ranking/", views.ranking, name="ranking"),
    path("sidejob-ranking/", views.sidejob_ranking, name="sidejob_ranking"),

    # コミュニティ
    path("community/", views.community, name="community"),

    # 副業案件
    #path("sidejobs/", views.sidejob_list, name="sidejob_list"),
    #path("sidejobs/apply/<int:job_id>/", views.apply_sidejob, name="apply_sidejob"),
    #path("sidejobs/<int:id>/", views.sidejob_detail),

    # テンプレート
    path("templates/", views.template_market, name="template_market"),
    path("templates/buy/<int:template_id>/", views.buy_template, name="buy_template"),

    # 収益シミュレーター
    path("income/", views.income_simulator, name="income"),

    # Stripe
    path("pricing/", views.pricing, name="pricing"),
    path("checkout/", views.create_checkout, name="checkout"),
    path("premium/", views.premium_page, name="premium"),
    path("stripe/webhook/", views.stripe_webhook),

    path("success/", views.success_list, name="success"),

    path("start/", views.start_page, name="start"),

    path("dashboard-preview/", views.dashboard_preview, name="dashboard_preview"),

    path(
        "diagnosis/share-image/",
        views.diagnosis_share_image,
        name="diagnosis_share_image"
    ),

    path("privacy/", views.privacy, name="privacy"),
    path("terms/", views.terms, name="terms"),
    path("legal/", views.legal, name="legal"),

    path("billing/", views.customer_portal),
]