import os
from django.db import models
from django.core.files.base import ContentFile
from django.utils.translation import ugettext as _

from ...conf import settings
from ...storages import private_storage
from ..base import BaseModel


#==============================================================================
def BaseModelLinkedToAssociation(related_name=None):
    """
    Build helper to build a custom model that relates to an association
    """
    kwargs = { 'verbose_name': _('association') }
    if related_name:
        kwargs.update({ 'related_name': related_name })

    class AssociationBaseModel(BaseModel):
        association = models.ForeignKey('nublas.Association', **kwargs)
        class Meta:
            abstract = True

    return AssociationBaseModel


#===============================================================================
class BaseModelFileRepositoryMixin(object):

    def repository_root(self):
        """
        Exampl implementation

            return "%s/" % os.path.join('associations', '%s' % self.uuid)

        :return:
        """
        raise NotImplementedError()

    def repository_path(self):
        path = "%s/" % os.path.join(self.repository_root(), 'files')
        # create repository path if doesn't exists
        if not private_storage.exists(path):
            placeholder = os.path.join(path, settings.STORAGE_DIRECTORY_PLACEHOLDER)
            private_storage.save(placeholder, ContentFile(''))
        return path

    def repository_listdir(self, path):
        subpath = os.path.join(self.repository_path(), path)
        if private_storage.exists(subpath):
            return private_storage.listdir(subpath)
        return None, None

    def repository_open_file(self, path, mode='rb'):
        subpath = os.path.join(self.repository_path(), path)
        if private_storage.exists(subpath):
            return private_storage.open(subpath, mode)
        return None

    def repository_write_file(self, path, f):
        subpath = os.path.join(self.repository_path(), path)
        #subpath = private_storage.get_valid_name(subpath)
        if private_storage.exists(subpath):
            private_storage.delete(subpath)
        private_storage.save(subpath, f)
        return True

    def repository_create_file(self, path):
        subpath = os.path.join(self.repository_path(), path)
        #subpath = private_storage.get_valid_name(subpath)
        if not private_storage.exists(subpath):
            private_storage.save(subpath, ContentFile(''))
            return True
        return False

    def repository_move_file(self, src, dst):
        src = os.path.join(self.repository_path(), src)
        dst = os.path.join(self.repository_path(), dst)
        if private_storage.exists(src):
            if private_storage.exists(dst):
                private_storage.delete(dst)
            private_storage.save(dst, private_storage.open(src))
            private_storage.delete(src)
            return True
        return False

    def repository_create_folder(self, path):
        subpath = os.path.join(self.repository_path(), path, settings.STORAGE_DIRECTORY_PLACEHOLDER)
        if not private_storage.exists(subpath):
            private_storage.save(subpath, ContentFile(''))
            return True
        return False

    def repository_delete_path(self, path):
        subpath = os.path.join(self.repository_path(), path)
        if private_storage.exists(subpath):
            private_storage.delete(subpath)
            return True
        return False

    def repository_disk_size(self):
        path = self.repository_root()
        if private_storage.exists(path):
            return private_storage.size(path)
        return 0
