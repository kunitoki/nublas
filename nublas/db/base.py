import uuid
from django.db import models
from django.utils.translation import ugettext as _
from django.utils import timezone

from ..conf import settings
from ..utils import import_class
from .managers import NonTrashManager, TrashManager
from .mixins import UniqueBooleanModelMixin, UtilityModelMixin
from .fields import uniqueid as uuidfields
from .fields import date as datefields

from taggit.managers import TaggableManager

__all__ = [ "BaseModel" ]


#==============================================================================
class BaseModel(UtilityModelMixin, UniqueBooleanModelMixin, import_class(settings.BASE_MODEL_CLASS)):
    """
    Model that uses a uuid identifier as the primary key

    Model that provides common introspection methods especially useful in
    templates and rendering code.

    An abstract base class model that provides self-managed "created" and
    "modified" fields.

    A trash bin that allows them to recover deleted content,
    as is e.g. the case in WordPress. This is that thing.

    Tagging support for models by using the tags manager.
    Something like:
        apple.tags.add() / all() / remove(name) / filter(tags__name__in=['red'])

    """
    _uuid = uuidfields.UUIDField(auto=True, default=uuid.uuid4, db_index=True, db_column='uuid')
    _created = datefields.AddedDateTimeField(_('created'), db_column='created')
    _modified = datefields.ModifiedDateTimeField(_('modified'), db_column='modified')
    _trashed = models.DateTimeField(_('trashed'), db_column='trashed', editable=False, blank=True, null=True)

    objects = NonTrashManager()
    trash = TrashManager()
    tags = TaggableManager(blank=True)

    @property
    def uuid(self):
        return self._uuid

    @property
    def created(self):
        return self._created

    @property
    def modified(self):
        return self._modified

    @property
    def trashed(self):
        return self._trashed

    @property
    def is_thrashed(self):
        return True if self._trashed else False

    def save(self, *args, **kwargs):
        self._unique_boolean_pre_save()
        super(BaseModel, self).save(*args, **kwargs)

    def delete(self):
        self._unique_boolean_pre_delete()
        if not self._trashed:
            self._trashed = timezone.now()
            self.save()

    def delete_permanently(self):
        super(BaseModel, self).delete()

    class Meta:
        abstract = True
