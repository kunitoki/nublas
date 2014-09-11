from django.db import models

__all__ = [ "LocationField" ]


#==============================================================================
class LocationField(models.CharField):
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 200)
        super(LocationField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        if value:
            a, b = value.split(',')
            try:
                lat, lng = float(a), float(b)
                return "%f,%f" % (lat, lng)
            except ValueError:
                pass
        return None

    def deconstruct(self):
        name, path, args, kwargs = super(LocationField, self).deconstruct()
        del kwargs["max_length"]
        return name, path, args, kwargs
