import json
from typing import Final

import http
import requests
from authlib.integrations.base_client import BaseOAuth
from authlib.integrations.django_client import DjangoRemoteApp, DjangoIntegration
from django.conf import settings
from django.http import HttpResponse, HttpRequest
from django.shortcuts import redirect
from django.template import Template, Context
from django.urls import reverse
from django.utils.http import urlencode

USERS: list = []
SESSION_DATA: dict = {}


class OpenAuthClient:
    def redirect_to_provider_auth_page(
        self, request: HttpRequest, redirect_uri: str
    ) -> HttpResponse:
        raise NotImplementedError()

    def handle_redirect_from_provider(self, request: HttpRequest) -> dict:
        raise NotImplementedError()


class RegularOAuth2Adapter(OpenAuthClient):
    def __init__(self, oauth: BaseOAuth) -> None:
        oauth.register(
            name="test",
            authorize_url=settings.OAUTH2["TEST"]["AUTHORIZE_URL"],
            token_endpoint=settings.OAUTH2["TEST"]["TOKEN_URL"],
            client_id=settings.OAUTH2["TEST"]["CLIENT_ID"],
            client_secret=settings.OAUTH2["TEST"]["CLIENT_SECRET"],
            client_kwargs={"scope": settings.OAUTH2["TEST"]["SCOPE"]},
        )
        self.client: DjangoRemoteApp = oauth.create_client("test")

    def redirect_to_provider_auth_page(self, request: HttpRequest, redirect_uri: str) -> HttpResponse:
        return self.client.authorize_redirect(request, redirect_uri)

    def handle_redirect_from_provider(self, request: HttpRequest) -> dict:
        token = self.client.authorize_access_token(request)
        return {"token": token, "user": None}


class SteamOpenID(OpenAuthClient):
    LOGIN_URL: Final[str] = "https://steamcommunity.com/openid/login"

    def redirect_to_provider_auth_page(
        self, request: HttpRequest, redirect_uri: str
    ) -> HttpResponse:
        query_params = {
            "openid.ns": "http://specs.openid.net/auth/2.0",
            "openid.mode": "checkid_setup",
            "openid.return_to": redirect_uri,
            "openid.realm": redirect_uri,
            "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
            "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select",
        }

        response = HttpResponse()
        response["Location"] = f"{self.LOGIN_URL}?{urlencode(query_params)}"
        response["Content-Type"] = "application/x-www-form-urlencoded"
        response.status_code = http.HTTPStatus.FOUND
        return response

    def handle_redirect_from_provider(self, request: HttpRequest) -> dict:
        query_params: dict = request.GET.dict()
        print(query_params)
        self._query_params_is_valid(query_params)
        return {"token": None, "user": query_params}

    def _query_params_is_valid(self, query_params):
        validation_query_params = {
            "openid.assoc_handle": query_params["openid.assoc_handle"],
            "openid.signed": query_params["openid.signed"],
            "openid.sig": query_params["openid.sig"],
            "openid.ns": query_params["openid.ns"],
        }
        signed_params = query_params["openid.signed"].split(",")
        for param in signed_params:
            open_id_param = f"openid.{param}"
            if query_params[open_id_param] not in validation_query_params:
                validation_query_params[open_id_param] = query_params[open_id_param]
        validation_query_params["openid.mode"] = "check_authentication"
        response = requests.post(self.LOGIN_URL, validation_query_params)
        return "is_valid:true" in response.text


class GoogleOAuth2Adapter(OpenAuthClient):
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


class TwitchOAuth2Adapter(OpenAuthClient):
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


oauth_ = OAuth()
google_client: OpenAuthClient = GoogleOAuth2Adapter(oauth_)
twitch_client: OpenAuthClient = TwitchOAuth2Adapter(oauth_)
TEST_client: OpenAuthClient = RegularOAuth2Adapter(oauth_)
steam_client: OpenAuthClient = SteamOpenID()
client = TEST_client


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


def login(request: HttpRequest) -> HttpResponse:
    redirect_uri = request.build_absolute_uri(reverse("auth"))
    return client.redirect_to_provider_auth_page(request, redirect_uri)


def auth(request: HttpRequest) -> HttpResponse:
    credentials = client.handle_redirect_from_provider(request)
    USERS.append(credentials)
    return redirect("/")


def logout(request):
    USERS.clear()
    return redirect("/")
