import json

from authlib.integrations.base_client import BaseOAuth
from authlib.integrations.django_client import DjangoRemoteApp
from django.conf import settings
from django.http import HttpResponse, HttpRequest

from authentication_clients.client import Client


class TwitchOAuth2Client(Client):
    def __init__(self, oauth: BaseOAuth) -> None:
        oauth.register(
            name="twitch",
            server_metadata_url="https://id.twitch.tv/oauth2/.well-known/openid-configuration",
            client_id=settings.OAUTH2["TWITCH"]["CLIENT_ID"],
            client_secret=settings.OAUTH2["TWITCH"]["CLIENT_SECRET"],
            client_kwargs={"scope": settings.OAUTH2["TWITCH"]["SCOPE"]},
        )
        self.client: DjangoRemoteApp = oauth.create_client("twitch")

    def redirect_to_provider_auth_page(
        self, request: HttpRequest, redirect_uri: str
    ) -> HttpResponse:
        return self.client.authorize_redirect(
            request,
            redirect_uri,
            **dict(
                claims=json.dumps(
                    {"id_token": {"email": None, "email_verified": None}}
                ),
            ),
        )

    def handle_redirect_from_provider(self, request: HttpRequest) -> dict:
        token = self.client.authorize_access_token(
            request,
            **dict(
                client_id=self.client.client_id,
                client_secret=self.client.client_secret,
            ),
        )
        user = self.client.parse_id_token(request, token)
        return {"token": token, "user": user}
