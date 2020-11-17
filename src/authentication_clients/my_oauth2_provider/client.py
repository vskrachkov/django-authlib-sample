from authlib.integrations.base_client import BaseOAuth
from authlib.integrations.django_client import DjangoRemoteApp
from django.conf import settings
from django.http import HttpResponse, HttpRequest

from authentication_clients.client import Client


class MyOAuth2ProviderClient(Client):
    def __init__(self, oauth: BaseOAuth) -> None:
        oauth.register(
            name="test",
            api_base_url=settings.OAUTH2["TEST"]["BASE_URL"],
            authorize_url=settings.OAUTH2["TEST"]["AUTHORIZE_URL"],
            token_endpoint=settings.OAUTH2["TEST"]["TOKEN_URL"],
            client_id=settings.OAUTH2["TEST"]["CLIENT_ID"],
            client_secret=settings.OAUTH2["TEST"]["CLIENT_SECRET"],
            client_kwargs={"scope": settings.OAUTH2["TEST"]["SCOPE"]},
        )
        self.client: DjangoRemoteApp = oauth.create_client("test")

    def redirect_to_provider_auth_page(
        self, request: HttpRequest, redirect_uri: str
    ) -> HttpResponse:
        return self.client.authorize_redirect(request, redirect_uri)

    def handle_redirect_from_provider(self, request: HttpRequest) -> dict:
        token = self.client.authorize_access_token(request)
        user = self.client.get(
            f"{self.client.api_base_url}/users/me/", token=token
        ).json()
        return {"token": token, "user": user}
