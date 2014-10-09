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

    """ Return the properties """
    def get_property(self, name, default):
        return self.settings.get(name, default)

    def get_property_fallback(self, name, default):
        return self.settings.get(name, getattr(django_settings, name, default))

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

    # Features enablement
    @settings_property
    def ENABLE_MULTILANGUAGE(self):
        return self.get_property('ENABLE_MULTILANGUAGE', True)

    @settings_property
    def ENABLE_USER_LOGIN(self):
        return self.get_property('ENABLE_USER_LOGIN', True)

    @settings_property
    def ENABLE_USER_REGISTRATION(self):
        return self.get_property('ENABLE_USER_REGISTRATION', False)

    @settings_property
    def ENABLE_ADMIN(self):
        return self.get_property('ENABLE_ADMIN', True)


    # Filesystem and storages
    @settings_property
    def MEDIA_FILE_STORAGE(self):
        return self.get_property('MEDIA_FILE_STORAGE', 'nublas.storages.filesystem.MediaStorage')

    @settings_property
    def MEDIA_ROOT(self):
        return self.get_property_fallback('MEDIA_ROOT', None)

    @settings_property
    def MEDIA_URL(self):
        return self.get_property_fallback('MEDIA_URL', '/media/')

    @settings_property
    def STATIC_FILE_STORAGE(self):
        return self.get_property('STATIC_FILE_STORAGE', 'nublas.storages.filesystem.StaticStorage')

    @settings_property
    def STATIC_ROOT(self):
        return self.get_property_fallback('STATIC_ROOT', None)

    @settings_property
    def STATIC_URL(self):
        return self.get_property_fallback('STATIC_URL', '/static/')

    @settings_property
    def PRIVATE_FILE_STORAGE(self):
        return self.get_property('PRIVATE_FILE_STORAGE', 'nublas.storages.filesystem.PrivateStorage')

    @settings_property
    def PRIVATE_ROOT(self):
        return self.get_property('PRIVATE_ROOT', None)


    # Skinning
    @settings_property
    def FRONTEND_SKIN(self):
        return self.get_property('FRONTEND_SKIN', 'default')

    @settings_property
    def FRONTEND_SKIN_OPTIONS(self):
        return dict({
            'is_fluid':            False,
            'company_name':        'Your Company',
            'company_url':         '#',
            'company_tos_url':     '#',
            'company_privacy_url': '#',
        }, **self.settings.get('FRONTEND_SKIN_OPTIONS', {}))


    # Urls definitions
    @settings_property
    def INDEX_URL(self):
        return self.get_property('INDEX_URL', '/')

    @settings_property
    def LOGIN_URL(self):
        return self.get_property_fallback('LOGIN_URL', '/auth/login/')

    @settings_property
    def LOGOUT_URL(self):
        return self.get_property_fallback('LOGOUT_URL', '/auth/logout/')

    @settings_property
    def LOGIN_REDIRECT_URL(self):
        return self.get_property_fallback('LOGIN_REDIRECT_URL', '/')


    # Login/Logout
    @settings_property
    def AUTH_PASSWORD_MIN_LENGTH(self):
        return self.get_property('AUTH_PASSWORD_MIN_LENGTH', 8)


    # Model classes
    @settings_property
    def BASE_MODEL_CLASS(self):
        return self.get_property('BASE_MODEL_CLASS', 'django.db.models.Model')

    @settings_property
    def BASE_MANAGER_CLASS(self):
        return self.get_property('BASE_MANAGER_CLASS', 'django.db.models.Manager')


    # Api keys
    @settings_property
    def GOOGLE_API_KEY(self):
        return self.get_property('GOOGLE_API_KEY', '')


    # Constants
    @settings_property
    def STORAGE_DIRECTORY_PLACEHOLDER(self):
        return '.keepme'


    """ Unused """
    @settings_property
    def CUSTOM_FIELD_TYPES(self):
        return dict({
            '1':     'django.forms.fields.CharField',
        }, **self.settings.get('CUSTOM_FIELD_TYPES', {}))


#==============================================================================
settings = LazySettingsDict()
