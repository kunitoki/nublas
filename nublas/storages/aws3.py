import sys
from ..conf import settings

try:
    from storages.backends.s3boto import S3BotoStorage
except ImportError as exc:
    sys.stderr.write("Error: failed to import S3BotoStorage module ({})".format(exc))


#==============================================================================
class MediaStorage(S3BotoStorage):
    """
    Storage for uploaded media files.
    The folder is defined in settings.AWS_MEDIA_S3_PATH
    """

    def __init__(self, *args, **kwargs):
        kwargs['location'] = settings.AWS_MEDIA_S3_PATH
        super(MediaStorage, self).__init__(*args, **kwargs)


#==============================================================================
class StaticStorage(S3BotoStorage):
    """
    Storage for static files.
    The folder is defined in settings.AWS_STATIC_S3_PATH
    """

    def __init__(self, *args, **kwargs):
        kwargs['location'] = settings.AWS_STATIC_S3_PATH
        super(StaticStorage, self).__init__(*args, **kwargs)


#==============================================================================
class PrivateStorage(S3BotoStorage):
    """
    Storage for private files.
    The folder is defined in settings.AWS_PRIVATE_S3_PATH
    """

    def __init__(self, *args, **kwargs):
        kwargs['location'] = settings.AWS_PRIVATE_S3_PATH
        kwargs['acl'] = 'private'
        super(PrivateStorage, self).__init__(*args, **kwargs)
