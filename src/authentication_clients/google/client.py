from authlib.integrations.base_client import BaseOAuth
from authlib.integrations.django_client import DjangoRemoteApp
from django.conf import settings
from django.http import HttpRequest, HttpResponse

from authentication_clients.client import Client


class GoogleOAuth2Client(Client):
    def __init__(self, oauth: BaseOAuth) -> None:
        oauth.register(
            name="google",
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_id=settings.OAUTH2["GOOGLE"]["CLIENT_ID"],
            client_secret=settings.OAUTH2["GOOGLE"]["CLIENT_SECRET"],
            client_kwargs={"scope": settings.OAUTH2["GOOGLE"]["SCOPE"]},
        )
        self.client: DjangoRemoteApp = oauth.create_client("google")

    def redirect_to_provider_auth_page(
        self, request: HttpRequest, redirect_uri: str
    ) -> HttpResponse:
        return self.client.authorize_redirect(request, redirect_uri)

    def handle_redirect_from_provider(self, request: HttpRequest) -> dict:
        token = self.client.authorize_access_token(request)
        user = self.client.parse_id_token(request, token)
        return {"token": token, "user": user}
