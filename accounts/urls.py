from django.urls import path

from . import scan, views

app_name = "accounts"

urlpatterns = [
    path("login/", views.AppLoginView.as_view(), name="login"),
    path("logout/", views.AppLogoutView.as_view(), name="logout"),
    path("register/", views.register, name="register"),
    path("login/qr/<uuid:pk>/image.svg", scan.qr_image, name="qr_image"),
    path("login/qr/<uuid:pk>/status/", scan.qr_status, name="qr_status"),
    path("login/qr/<uuid:pk>/claim/", scan.qr_claim, name="qr_claim"),
    path("login/qr/<uuid:pk>/", scan.qr_confirm, name="qr_confirm"),
    path("login/qr/wechat/", scan.qr_create, {"provider": "wechat"}, name="qr_create_wechat"),
    path("login/qr/qq/", scan.qr_create, {"provider": "qq"}, name="qr_create_qq"),
]
