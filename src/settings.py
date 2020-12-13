from pathlib import Path

from environs import Env

env = Env()
env.read_env()  # read .env file, if it exists

SECRET_KEY = env.str("SECRET_KEY")

OAUTH2 = {
    "GOOGLE": {
        "CLIENT_ID": env.str("OAUTH2_GOOGLE_CLIENT_ID"),
        "CLIENT_SECRET": env.str("OAUTH2_GOOGLE_CLIENT_SECRET"),
        "SCOPE": "openid email",
    },
    "MY_OPENID": {
        "CLIENT_ID": env.str("OAUTH2_MY_OPENID_CLIENT_ID"),
        "CLIENT_SECRET": env.str("OAUTH2_MY_OPENID_CLIENT_SECRET"),
        "SCOPE": "openid email",
    },
    "TWITCH": {
        "CLIENT_ID": env.str("OAUTH2_TWITCH_CLIENT_ID"),
        "CLIENT_SECRET": env.str("OAUTH2_TWITCH_CLIENT_SECRET"),
        "SCOPE": "openid",
    },
    "TEST": {
        "BASE_URL": env.str("OAUTH2_TEST_BASE_URL"),
        "AUTHORIZE_URL": env.str("OAUTH2_TEST_AUTHORIZE_URL"),
        "TOKEN_URL": env.str("OAUTH2_TEST_TOKEN_URL"),
        "CLIENT_ID": env.str("OAUTH2_TEST_CLIENT_ID"),
        "CLIENT_SECRET": env.str("OAUTH2_TEST_CLIENT_SECRET"),
        "SCOPE": "",
    },
}

DEBUG = True

ALLOWED_HOSTS = []

CORE_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
]

PROJECT_APPS = [
    "authentication_clients",
    "authentication_clients.google",
    "authentication_clients.twitch",
    "authentication_clients.steam",
    "authentication_clients.my_oauth2_provider",
    "authentication_clients.my_oidc_provider",
]

INSTALLED_APPS = CORE_APPS + PROJECT_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": Path(__file__).resolve().parent.parent.parent / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = "/static/"
