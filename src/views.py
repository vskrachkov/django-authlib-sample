from pprint import pformat
from typing import Any, Optional

from django.dispatch import receiver
from django.http import HttpResponse
from django.shortcuts import redirect
from django.template import Template, Context
from django.urls import reverse

from authentication_clients.views import obtained_user_credentials

CREDENTIALS: list = []


def home(request) -> HttpResponse:
    login_urls = {
        "google": reverse("google_login"),
        "my_provider": reverse("my_provider_login"),
        "steam": reverse("steam_login"),
        "twitch": reverse("twitch_login"),
        "my_openid": reverse("my_openid_login"),
    }

    credentials = pformat(CREDENTIALS, indent=4) if CREDENTIALS else None
    template = Template(
        """
    {% if credentials %}
        <pre>{{ credentials }}</pre>
        <hr>
        <a href="/logout/">logout</a>
    {% else %}
        {% for name, login_url in login_urls.items %}
            <a href="{{ login_url }}">{{ name }}</a>
            </br>
            </br>
        {% endfor %}
    {% endif %}
    """
    )

    return HttpResponse(
        template.render(
            Context({"credentials": credentials, "login_urls": login_urls})
        ),
        content_type="text/html",
    )


@receiver(obtained_user_credentials)
def save_credentials(sender: Any, credentials: Optional[dict] = None, **kwargs) -> None:
    CREDENTIALS.append(credentials)


def logout(request):
    CREDENTIALS.clear()
    return redirect("/")
