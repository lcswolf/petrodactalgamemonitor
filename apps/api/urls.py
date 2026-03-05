from django.urls import path
from . import views

urlpatterns = [
    path("servers/", views.servers_list, name="api_servers_list"),
    path("servers/<int:server_id>/status/", views.server_status, name="api_server_status"),
    path("clans/<slug:slug>/status/", views.clan_status, name="api_clan_status"),
]
