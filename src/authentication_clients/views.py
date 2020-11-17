from typing import Callable

from django.dispatch import Signal
from django.http import HttpResponse, HttpRequest
from django.shortcuts import redirect
from django.urls import reverse

from authentication_clients.client import Client


obtained_user_credentials = Signal(providing_args=["client", "credentials"])


def create_login_view(
    client: Client, callback_view_name: str
) -> Callable[[HttpRequest], HttpResponse]:
    def login(request: HttpRequest) -> HttpResponse:
        redirect_uri = request.build_absolute_uri(reverse(callback_view_name))
        return client.redirect_to_provider_auth_page(request, redirect_uri)

    return login


def create_callback_view(
    client: Client,
    success_page_view_name: str = "",
    obtained_user_credentials_signal: Signal = obtained_user_credentials,
) -> Callable[[HttpRequest], HttpResponse]:
    def callback(request: HttpRequest) -> HttpResponse:
        credentials = client.handle_redirect_from_provider(request)
        obtained_user_credentials_signal.send(
            callback, client=client, credentials=credentials
        )
        return (
            redirect(reverse(success_page_view_name))
            if success_page_view_name
            else redirect("/")
        )

    return callback
