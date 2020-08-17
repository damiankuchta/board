from boards_project.settings.base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = [".herokuapp.com"]

INSTALLED_APPS += \
    ("whitenoise.runserver_nostatic",)

MIDDLEWARE += \
    ('whitenoise.middleware.WhiteNoiseMiddleware',
     'reports_warrnings_bans_app.middleware.is_user_banned.IsUserBanned',
     )

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
