from django.db import models
from django.utils import timezone

__all__ = [ "AddedDateTimeField", "ModifiedDateTimeField" ]


#==============================================================================
class AddedDateTimeField(models.DateTimeField):
    def __init__(self, *args, **kwargs):
        defaults = {
            'null': True,
            'blank': True,
            'editable': False
        }
        defaults.update(kwargs)
        super(AddedDateTimeField, self).__init__(*args, **defaults)

    def get_internal_type(self):
        return models.DateTimeField.__name__

    def pre_save(self, model_instance, add):
        if add or model_instance.pk is None:
            val = timezone.now()
            setattr(model_instance, self.attname, val)
            return val
        else:
            return getattr(model_instance, self.attname)

    def deconstruct(self):
        name, path, args, kwargs = super(AddedDateTimeField, self).deconstruct()
        del kwargs["null"]
        del kwargs["blank"]
        del kwargs["editable"]
        return name, path, args, kwargs


#==============================================================================
class ModifiedDateTimeField(models.DateTimeField):
    def __init__(self, *args, **kwargs):
        defaults = {
            'null': True,
            'blank': True,
            'editable': False
        }
        defaults.update(kwargs)
        super(ModifiedDateTimeField, self).__init__(*args, **defaults)

    def get_internal_type(self):
        return models.DateTimeField.__name__

    def pre_save(self, model_instance, add):
        val = timezone.now()
        setattr(model_instance, self.attname, val)
        return val

    def deconstruct(self):
        name, path, args, kwargs = super(ModifiedDateTimeField, self).deconstruct()
        del kwargs["null"]
        del kwargs["blank"]
        del kwargs["editable"]
        return name, path, args, kwargs
