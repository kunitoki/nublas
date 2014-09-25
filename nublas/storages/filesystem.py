from django.core.files.storage import FileSystemStorage

from ..conf import settings


#==============================================================================
class MediaStorage(FileSystemStorage):
    """
    Storage for uploaded media files.
    The folder is defined in settings.MEDIA_ROOT
    """

    def __init__(self, *args, **kwargs):
        kwargs['location'] = settings.MEDIA_ROOT
        super(MediaStorage, self).__init__(*args, **kwargs)


#==============================================================================
class StaticStorage(FileSystemStorage):
    """
    Storage for static files.
    The folder is defined in settings.STATIC_ROOT
    """

    def __init__(self, *args, **kwargs):
        kwargs['location'] = settings.STATIC_ROOT
        super(StaticStorage, self).__init__(*args, **kwargs)


#==============================================================================
class PrivateStorage(FileSystemStorage):
    """
    Storage for private files.
    The folder is defined in settings.PRIVATE_ROOT
    """

    def __init__(self, *args, **kwargs):
        kwargs['location'] = settings.PRIVATE_ROOT
        super(PrivateStorage, self).__init__(*args, **kwargs)
