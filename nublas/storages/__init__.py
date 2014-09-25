from django.core.exceptions import ImproperlyConfigured
from django.core.files.storage import default_storage
from django.utils.functional import LazyObject
from django.utils.importlib import import_module

from ..conf import settings

__all__ = [ 'default_storage', 'media_storage', 'static_storage', 'private_storage' ]


#==============================================================================
# DIRECTORY_PLACEHOLDER = '.keepme'


#==============================================================================
def get_storage_class(import_path):
    """
    Try to determine storage class at runtime by importing it

    :param import_path: module definition string
    :return: storage class
    """
    try:
        dot = import_path.rindex('.')
    except ValueError:
        raise ImproperlyConfigured("%s isn't a storage module." % import_path)
    module, classname = import_path[:dot], import_path[dot+1:]
    try:
        mod = import_module(module)
    except ImportError as e:
        raise ImproperlyConfigured('Error importing storage module %s: "%s"' % (module, e))
    try:
        return getattr(mod, classname)
    except AttributeError:
        raise ImproperlyConfigured('Storage module "%s" does not define a "%s" class.' % (module, classname))


#==============================================================================
class MediaStorage(LazyObject):
    def _setup(self):
        storage_class = get_storage_class(settings.MEDIA_FILE_STORAGE)
        self._wrapped = storage_class()

media_storage = MediaStorage()


#==============================================================================
class StaticStorage(LazyObject):
    def _setup(self):
        storage_class = get_storage_class(settings.STATIC_FILE_STORAGE)
        self._wrapped = storage_class()

static_storage = StaticStorage()


#==============================================================================
class PrivateStorage(LazyObject):
    def _setup(self):
        storage_class = get_storage_class(settings.PRIVATE_FILE_STORAGE)
        self._wrapped = storage_class()

private_storage = PrivateStorage()
