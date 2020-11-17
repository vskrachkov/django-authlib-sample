from authlib.integrations.base_client import BaseOAuth
from authlib.integrations.django_client import DjangoIntegration, DjangoRemoteApp

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


def get_oauth2() -> BaseOAuth:
    return OAuth()
