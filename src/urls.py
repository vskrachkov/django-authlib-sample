from django.urls import path

import views
from authentication_clients.client import Client
from authentication_clients.google.client import GoogleOAuth2Client
from authentication_clients.my_oauth2_provider.client import MyOAuth2ProviderClient
from authentication_clients.my_oidc_provider.client import MyOpenIdOAuth2Client
from authentication_clients.oauth2 import get_oauth2
from authentication_clients.steam.client import SteamOpenIDClient
from authentication_clients.twitch.client import TwitchOAuth2Client
from authentication_clients.views import create_login_view, create_callback_view

_oauth2 = get_oauth2()
_google_client: Client = GoogleOAuth2Client(_oauth2)
_my_openid_client: Client = MyOpenIdOAuth2Client(_oauth2)
_my_provider_client: Client = MyOAuth2ProviderClient(_oauth2)
_steam_client: Client = SteamOpenIDClient()
_twitch_client: Client = TwitchOAuth2Client(_oauth2)

urlpatterns = [
    path("", views.home),
    path(
        "login_google/",
        create_login_view(_google_client, "google_callback"),
        name="google_login",
    ),
    path(
        "google_callback/", create_callback_view(_google_client), name="google_callback"
    ),
    path(
        "login_my_openid/",
        create_login_view(_my_openid_client, "my_openid_callback"),
        name="my_openid_login",
    ),
    path(
        "my_openid_callback/", create_callback_view(_my_openid_client), name="my_openid_callback"
    ),
    path(
        "login_my_provider/",
        create_login_view(_my_provider_client, "my_provider_callback"),
        name="my_provider_login",
    ),
    path(
        "my_provider_callback/",
        create_callback_view(_my_provider_client),
        name="my_provider_callback",
    ),
    path(
        "login_steam/",
        create_login_view(_steam_client, "steam_callback"),
        name="steam_login",
    ),
    path(
        "steam_callback/", create_callback_view(_steam_client), name="steam_callback",
    ),
    path(
        "login_twitch/",
        create_login_view(_twitch_client, "twitch_callback"),
        name="twitch_login",
    ),
    path(
        "twitch_callback/",
        create_callback_view(_twitch_client),
        name="twitch_callback",
    ),
    path("logout/", views.logout),
]
