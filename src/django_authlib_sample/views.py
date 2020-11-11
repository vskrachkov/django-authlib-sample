import json

from authlib.integrations.base_client import BaseOAuth
from authlib.integrations.django_client import DjangoRemoteApp, DjangoIntegration
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import Template, Context
from django.urls import reverse

USERS: dict = {}
SESSION_DATA: dict = {}


class MyIntegration(DjangoIntegration):
    def set_session_data(self, request, key, value):
        print(f"set_session_data: {key} -> {value}")
        SESSION_DATA[key] = value

    def get_session_data(self, request, key):
        print(f"get_session_data: {key}")
        return SESSION_DATA.pop(key, None)


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
    client_id=settings.OAUTH2_GOOGLE_CLIENT_ID,
    client_secret=settings.OAUTH2_GOOGLE_CLIENT_SECRET,
    request_token_url=None,
    request_token_params=None,
    access_token_url=None,
    access_token_params=None,
    refresh_token_url=None,
    refresh_token_params=None,
    authorize_url=None,
    authorize_params=None,
    api_base_url=None,
    client_kwargs={"scope": "email"},
)

google_client: DjangoRemoteApp = oauth.create_client("google")


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
    return google_client.authorize_redirect(request, redirect_uri)


def auth(request):
    token = google_client.authorize_access_token(request)
    user = google_client.parse_id_token(request, token)
    USERS[user["email"]] = user
    return redirect("/")


def logout(request):
    USERS.clear()
    return redirect("/")
