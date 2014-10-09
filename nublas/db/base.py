import uuid
from django.db import models
from django.forms.models import model_to_dict
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone

from ..conf import settings
from ..utils import import_class
from .managers import NonTrashManager, TrashManager
from .fields import uniqueid as uuidfields
from .fields import date as datefields

from taggit.managers import TaggableManager

__all__ = [ "BaseModel" ]


#==============================================================================
class BaseModelUtilMixin(object):
    def get_model(self):
        """ Returns the model meta """
        return self._meta

    def get_name(self):
        """ Returns the singular name of the model """
        return "%s" % self._meta.name

    def get_verbose_name(self):
        """ Returns the singular verbose name of the model """
        return "%s" % self._meta.verbose_name

    def get_fields(self):
        """ Get all fields and their display strings """
        return [(f, self.get_field_display(f)) for f in self._meta.fields]

    def get_field_display(self, field):
        """
        Override function to obtain field values to be used in display lists

        :param field: field instance to display
        :return: string display of field
        """
        return field.value_to_string(self)

    def get_field_by_name(self, field_name):
        """
        Return a field object by name

        :param field_name: field name
        :return: field instance
        """
        return self._meta.get_field_by_name(field_name)

    def to_dict(self, fields=None, exclude=None):
        """
        Return the model instance as a dictionary

        :param fields: which fields to use
        :param exclude: which fields to exclude
        :return: dict()
        """
        return model_to_dict(self, fields=fields, exclude=exclude)


#==============================================================================
class BaseModel(BaseModelUtilMixin, import_class(settings.BASE_MODEL_CLASS)):
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

    def _unique_boolean_pre_save(self):
        unique_boolean = getattr(self, 'UNIQUE_BOOLEAN', [])
        for field in unique_boolean:
            # build filter
            filter_kwargs = { field[0]: True }
            for arg in field[1]:
                if getattr(self, arg):
                    filter_kwargs[arg] = getattr(self, arg)
            print(filter_kwargs)
            # main logic
            if getattr(self, field[0]):
                print("Setting true")
                tmp = self.__class__.objects.filter(**filter_kwargs).exclude(pk=self.pk)
                for t in tmp:
                    setattr(t, field[0], False)
                    t.save()
            else:
                if self.__class__.objects.filter(**filter_kwargs).count() == 0:
                    setattr(self, field[0], True)

    def _unique_boolean_pre_delete(self):
        unique_boolean = getattr(self, 'UNIQUE_BOOLEAN', [])
        for field in unique_boolean:
            # build filter
            filter_kwargs = { field[0]: True }
            for arg in field[1]:
                if getattr(self, arg):
                    filter_kwargs[arg] = getattr(self, arg)
            # main logic
            tmp = self.__class__.objects.filter(**filter_kwargs)
            if len(tmp) > 0:
                setattr(tmp[0], field[0], True)
                tmp[0].save()

    class Meta:
        abstract = True
