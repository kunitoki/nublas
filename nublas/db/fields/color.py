import re
from django.db import models
from django.core.validators import RegexValidator
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _


#==============================================================================
color_re = re.compile('^\#([a-fA-F0-9]{6}|[a-fA-F0-9]{3})$')
validate_color = RegexValidator(color_re, _("Enter a valid color."), 'invalid')


#==============================================================================
class RGBColorField(models.CharField):
    default_validators = [validate_color]

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 7
        super(RGBColorField, self).__init__(*args, **kwargs)

    def clean(self, value, model_instance):
        if value[0] != '#':
            value = '#' + value
        value = super(RGBColorField, self).clean(value, model_instance)
        return smart_unicode(value)

    def deconstruct(self):
        name, path, args, kwargs = super(RGBColorField, self).deconstruct()
        del kwargs["max_length"]
        return name, path, args, kwargs
