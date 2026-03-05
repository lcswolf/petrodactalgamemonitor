from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("clan/<slug:slug>/", views.clan_page, name="clan_page"),
]
