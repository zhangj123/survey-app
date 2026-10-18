from django.urls import path

from . import views

app_name = "pages"

urlpatterns = [
    path("", views.home, name="home"),
    path("apps/", views.apps, name="apps"),
    path("templates/", views.templates, name="templates"),
    path("templates/<slug:slug>/use/", views.use_template, name="use_template"),
]
