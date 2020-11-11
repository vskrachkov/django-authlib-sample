import json

from authlib.integrations.base_client import BaseOAuth
from authlib.integrations.django_client import DjangoRemoteApp, DjangoIntegration
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import Template, Context
from django.urls import reverse

USERS: list = []
SESSION_DATA: dict = {}


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

oauth.register(
    name="google",
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_id=settings.OAUTH2["GOOGLE"]["CLIENT_ID"],
    client_secret=settings.OAUTH2["GOOGLE"]["CLIENT_SECRET"],
    client_kwargs={"scope": settings.OAUTH2["GOOGLE"]["SCOPE"]},
)
oauth.register(
    name="twitch",
    server_metadata_url="https://id.twitch.tv/oauth2/.well-known/openid-configuration",
    client_id=settings.OAUTH2["TWITCH"]["CLIENT_ID"],
    client_secret=settings.OAUTH2["TWITCH"]["CLIENT_SECRET"],
    client_kwargs={"scope": settings.OAUTH2["TWITCH"]["SCOPE"]},
)

google_client: DjangoRemoteApp = oauth.create_client("google")
twitch_client: DjangoRemoteApp = oauth.create_client("twitch")
client = twitch_client


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
        request, **dict(client_id=client.client_id, client_secret=client.client_secret),
    )
    user = client.parse_id_token(request, token)
    USERS.append({"token": token, "user": user})
    return redirect("/")


def logout(request):
    USERS.clear()
    return redirect("/")
