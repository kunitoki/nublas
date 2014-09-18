import sys
from django.conf import settings as django_settings
from django.utils.functional import cached_property as settings_property


#==============================================================================
# Do not cache properties when in test mode
if 'test' in sys.argv:
    settings_property = property


#==============================================================================
# Helper class for lazy settings
class LazySettingsDict(object):

    @settings_property
    def settings(self):
        return getattr(django_settings, 'NUBLAS_SETTINGS', {})


    """ django settings variables """
    @settings_property
    def DEBUG(self):
        return getattr(django_settings, 'DEBUG', True)

    @settings_property
    def AUTH_USER_MODEL(self):
        return getattr(django_settings, 'AUTH_USER_MODEL', 'auth.User')

    @settings_property
    def LANGUAGES(self):
        return getattr(django_settings, 'LANGUAGES', ())

    @settings_property
    def INSTALLED_APPS(self):
        return getattr(django_settings, 'INSTALLED_APPS', ())


    """ nublas settings variables """
    @settings_property
    def ENABLE_MULTILANGUAGE(self):
        return self.settings.get('ENABLE_MULTILANGUAGE', True)

    @settings_property
    def ENABLE_USER_LOGIN(self):
        return self.settings.get('ENABLE_USER_LOGIN', True)

    @settings_property
    def ENABLE_USER_REGISTRATION(self):
        return self.settings.get('ENABLE_USER_REGISTRATION', False)

    @settings_property
    def ENABLE_ADMIN(self):
        return self.settings.get('ENABLE_ADMIN', True)

    @settings_property
    def FRONTEND_SKIN(self):
        return self.settings.get('FRONTEND_SKIN', 'default')

    @settings_property
    def INDEX_URL(self):
        print self.settings.get('INDEX_URL', '/')
        return self.settings.get('INDEX_URL', '/')

    @settings_property
    def LOGIN_URL(self):
        return self.settings.get('LOGIN_URL', django_settings.LOGIN_URL)

    @settings_property
    def LOGOUT_URL(self):
        return self.settings.get('LOGOUT_URL', django_settings.LOGOUT_URL)

    @settings_property
    def LOGIN_REDIRECT_URL(self):
        return self.settings.get('LOGIN_REDIRECT_URL', django_settings.LOGIN_REDIRECT_URL)

    @settings_property
    def AUTH_PASSWORD_MIN_LENGTH(self):
        return self.settings.get('AUTH_PASSWORD_MIN_LENGTH', 8)

    @settings_property
    def BASE_MODEL_CLASS(self):
        return self.settings.get('BASE_MODEL_CLASS', 'django.db.models.Model')

    @settings_property
    def BASE_MANAGER_CLASS(self):
        return self.settings.get('BASE_MANAGER_CLASS', 'django.db.models.Manager')

    @settings_property
    def GOOGLE_API_KEY(self):
        return self.settings.get('GOOGLE_API_KEY', '')


    """ Unused """
    @settings_property
    def CUSTOM_FIELD_TYPES(self):
        return dict({
            '1':     'django.forms.fields.CharField',
        }, **self.settings.get('CUSTOM_FIELD_TYPES', {}))


#==============================================================================
settings = LazySettingsDict()
