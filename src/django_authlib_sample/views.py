import json

from authlib.integrations.base_client import BaseOAuth
from authlib.integrations.django_client import DjangoRemoteApp, DjangoIntegration
from django.conf import settings
from django.http import HttpResponse, HttpRequest
from django.shortcuts import redirect
from django.template import Template, Context
from django.urls import reverse

USERS: list = []
SESSION_DATA: dict = {}


class OAuth2Adapter:
    @staticmethod
    def create_client() -> DjangoRemoteApp:
        raise NotImplementedError()

    def __init__(self, oauth_client: BaseOAuth) -> None:
        raise NotImplementedError()

    def get_client_id(self) -> str:
        raise NotImplementedError()

    def get_client_secret(self) -> str:
        raise NotImplementedError()

    def authorize_redirect(
        self, request: HttpRequest, redirect_uri: str, **kwargs
    ) -> HttpResponse:
        raise NotImplementedError()

    def authorize_access_token(self, request: HttpRequest, **kwargs) -> dict:
        raise NotImplementedError()

    def parse_id_token(self, request: HttpRequest, token: dict) -> dict:
        raise NotImplementedError()


class GoogleOAuth2Adapter(OAuth2Adapter):
    @staticmethod
    def create_client() -> DjangoRemoteApp:
        oauth.register(
            name="google",
            server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
            client_id=settings.OAUTH2["GOOGLE"]["CLIENT_ID"],
            client_secret=settings.OAUTH2["GOOGLE"]["CLIENT_SECRET"],
            client_kwargs={"scope": settings.OAUTH2["GOOGLE"]["SCOPE"]},
        )
        return oauth.create_client("google")

    def __init__(self, oauth_client: BaseOAuth) -> None:
        self.client = self.create_client()

    def get_client_id(self) -> str:
        return self.client.client_id

    def get_client_secret(self) -> str:
        return self.client.client_secret

    def authorize_redirect(
        self, request: HttpRequest, redirect_uri: str, **kwargs
    ) -> HttpResponse:
        return self.client.authorize_redirect(request, redirect_uri,)

    def authorize_access_token(self, request: HttpRequest, **kwargs) -> dict:
        return self.client.authorize_access_token(request)

    def parse_id_token(self, request: HttpRequest, token: dict) -> dict:
        return self.client.parse_id_token(request, token)


class TwitchOAuth2Adapter(OAuth2Adapter):
    @staticmethod
    def create_client() -> DjangoRemoteApp:
        oauth.register(
            name="twitch",
            server_metadata_url="https://id.twitch.tv/oauth2/.well-known/openid-configuration",
            client_id=settings.OAUTH2["TWITCH"]["CLIENT_ID"],
            client_secret=settings.OAUTH2["TWITCH"]["CLIENT_SECRET"],
            client_kwargs={"scope": settings.OAUTH2["TWITCH"]["SCOPE"]},
        )
        return oauth.create_client("twitch")

    def __init__(self, oauth_client: BaseOAuth) -> None:
        self.client = self.create_client()

    def get_client_id(self) -> str:
        return self.client.client_id

    def get_client_secret(self) -> str:
        return self.client.client_secret

    def authorize_redirect(
        self, request: HttpRequest, redirect_uri: str, **kwargs
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

    def authorize_access_token(self, request: HttpRequest, **kwargs) -> dict:
        return self.client.authorize_access_token(
            request,
            **dict(
                client_id=self.get_client_id(), client_secret=self.get_client_secret(),
            ),
        )

    def parse_id_token(self, request: HttpRequest, token: dict) -> dict:
        return self.client.parse_id_token(request, token)


class MyIntegration(DjangoIntegration):
    def set_session_data(self, request, key, value):
        print(f"set_session_data: {key} -> {value}")
        SESSION_DATA[key] = value

    def get_session_data(self, request, key):
        val = SESSION_DATA.pop(key, None)
        print(f"get_session_data: {key} -> {val}")
        return val


class MyRemoteApp(DjangoRemoteApp):
    def save_authorize_data(self, request, **kwargs):
        print(f"save_authorize_data: {kwargs}")
        return super().save_authorize_data(request, **kwargs)


class OAuth(BaseOAuth):
    framework_integration_cls = MyIntegration
    framework_client_cls = MyRemoteApp


oauth = OAuth()
google_client: OAuth2Adapter = GoogleOAuth2Adapter(oauth)
twitch_client: OAuth2Adapter = TwitchOAuth2Adapter(oauth)
client = google_client


def home(request) -> HttpResponse:
    user = json.dumps(USERS) if USERS else None
    template = Template(
        """
    {% if user %}
        <pre>{{ user }}</pre>
        <hr>
        <a href="/logout/">logout</a>
    {% else %}
        <a href="/login/">login</a>
    {% endif %}
    """
    )

    return HttpResponse(
        template.render(Context({"user": user})), content_type="text/html"
    )


def login(request):
    redirect_uri = request.build_absolute_uri(reverse("auth"))
    return client.authorize_redirect(
        request,
        redirect_uri,
        **dict(
            claims=json.dumps({"id_token": {"email": None, "email_verified": None}}),
        ),
    )


def auth(request):
    token = client.authorize_access_token(
        request,
        **dict(
            client_id=client.get_client_id(), client_secret=client.get_client_secret()
        ),
    )
    user = client.parse_id_token(request, token)
    USERS.append({"token": token, "user": user})
    return redirect("/")


def logout(request):
    USERS.clear()
    return redirect("/")
