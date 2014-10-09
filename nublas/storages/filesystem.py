import os
import errno
import shutil

from django.core.files.storage import FileSystemStorage

from ..conf import settings


#==============================================================================
class FilesystemStorageDirectoryAware(FileSystemStorage):

    def delete(self, name):
        assert name, "The name argument is not allowed to be empty."
        name = self.path(name)
        # If it's a directory, remove the entire tree.
        # If the file exists, delete it from the filesystem.
        # Note that there is a race between os.path.exists and os.remove:
        # if os.remove fails with ENOENT, the file was removed
        # concurrently, and we can continue normally.
        if os.path.exists(name):
            if os.path.isdir(name):
                shutil.rmtree(name)
            else:
                try:
                    os.remove(name)
                except OSError as e:
                    if e.errno != errno.ENOENT:
                        raise


#==============================================================================
class MediaStorage(FilesystemStorageDirectoryAware):
    """
    Storage for uploaded media files.
    The folder is defined in settings.MEDIA_ROOT
    """

    def __init__(self, *args, **kwargs):
        kwargs['location'] = settings.MEDIA_ROOT
        super(MediaStorage, self).__init__(*args, **kwargs)


#==============================================================================
class StaticStorage(FilesystemStorageDirectoryAware):
    """
    Storage for static files.
    The folder is defined in settings.STATIC_ROOT
    """

    def __init__(self, *args, **kwargs):
        kwargs['location'] = settings.STATIC_ROOT
        super(StaticStorage, self).__init__(*args, **kwargs)


#==============================================================================
class PrivateStorage(FilesystemStorageDirectoryAware):
    """
    Storage for private files.
    The folder is defined in settings.PRIVATE_ROOT
    """

    def __init__(self, *args, **kwargs):
        kwargs['location'] = settings.PRIVATE_ROOT
        super(PrivateStorage, self).__init__(*args, **kwargs)
