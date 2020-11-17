import http
from typing import Final

import requests
from django.http import HttpResponse, HttpRequest
from django.utils.http import urlencode

from authentication_clients.client import Client


class SteamOpenIDClient(Client):
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
