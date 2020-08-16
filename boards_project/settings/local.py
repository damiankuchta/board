from .base import *

try:
    from .secret import *
except:
    pass

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS = []
INSTALLED_APPS += ("debug_toolbar",)
INTERNAL_IPS = ("127.0.0.1",)
MIDDLEWARE += \
    ("debug_toolbar.middleware.DebugToolbarMiddleware",
     'reports_warrnings_bans_app.middleware.is_user_banned.IsUserBanned',
     )