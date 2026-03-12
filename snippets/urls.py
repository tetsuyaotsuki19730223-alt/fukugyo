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

    # 履歴
    path("ai-history/", views.ai_chat_history, name="ai_history"),

    # ミッション
    path("mission/", views.today_mission, name="today_mission"),
    path("mission/complete/", views.mission_complete, name="mission_complete"),

    # ダッシュボード
    path("dashboard/", views.dashboard, name="dashboard"),

    # ランキング
    path("ranking/", views.ranking, name="ranking"),

    # コミュニティ
    path("community/", views.community, name="community"),

    # 副業案件
    path("sidejobs/", views.sidejob_list, name="sidejob_list"),
    path("sidejobs/apply/<int:job_id>/", views.apply_sidejob, name="apply_sidejob"),

    # テンプレート
    path("templates/", views.template_market, name="template_market"),
    path("templates/buy/<int:template_id>/", views.buy_template, name="buy_template"),

    # 収益シミュレーター
    path("income/", views.income_simulator, name="income"),

    # Stripe
    path("pricing/", views.pricing, name="pricing"),
    path("checkout/", views.create_checkout, name="checkout"),
    path("premium/", views.premium_page, name="premium"),

]