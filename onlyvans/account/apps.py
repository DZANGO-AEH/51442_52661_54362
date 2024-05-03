from django.apps import AppConfig


class AccountConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'account'

class UsersConfig(AppConfig):
    name = 'users'
    def ready(self):
        import users.signals