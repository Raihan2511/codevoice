from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # TEACHER NOTE: 
    # We must explicitly set the name because our app is inside the 'apps' folder.
    # This matches what we put in INSTALLED_APPS in settings.py.
    name = 'apps.users'
    label = 'users'  # This allows us to refer to it as just 'users' (like in AUTH_USER_MODEL)