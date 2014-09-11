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
    def AUTH_USER_MODEL(self):
        return getattr(django_settings, 'AUTH_USER_MODEL', 'auth.User')

    @settings_property
    def INSTALLED_APPS(self):
        return getattr(django_settings, 'INSTALLED_APPS', ())

    """ nublas settings variables """
    @settings_property
    def ENABLE_MULTILANGUAGE(self):
        return getattr(self.settings, 'ENABLE_MULTILANGUAGE', True)

    @settings_property
    def BASE_MODEL_CLASS(self):
        return getattr(self.settings, 'BASE_MODEL_CLASS', 'django.db.models.Model')

    @settings_property
    def BASE_MANAGER_CLASS(self):
        return getattr(self.settings, 'BASE_MANAGER_CLASS', 'django.db.models.Manager')

    @settings_property
    def GOOGLE_API_KEY(self):
        return getattr(self.settings, 'GOOGLE_API_KEY', '')

    @settings_property
    def CUSTOM_FIELD_TYPES(self):
        return dict({
            '1':     'django.forms.fields.CharField',
        }, **getattr(self.settings, 'CUSTOM_FIELD_TYPES', {}))


#==============================================================================
settings = LazySettingsDict()
