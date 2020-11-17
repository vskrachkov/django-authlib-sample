from django.http import HttpRequest, HttpResponse


class Client:
    def redirect_to_provider_auth_page(
        self, request: HttpRequest, redirect_uri: str
    ) -> HttpResponse:
        raise NotImplementedError()

    def handle_redirect_from_provider(self, request: HttpRequest) -> dict:
        raise NotImplementedError()
