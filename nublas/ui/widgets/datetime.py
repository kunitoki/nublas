from __future__ import unicode_literals
from django import forms
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string

from .base import NublasWidgetMixin


#===============================================================================
class TimeWidget(NublasWidgetMixin, forms.TimeInput):
    template = "nublas/widgets/time.html"

    def __init__(self, *args, **kwargs):
        kwargs['format'] = '%H:%M'
        super(TimeWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs={}):
        super(TimeWidget, self).render(name, value, attrs)
        final_attrs = self.get_attrs(attrs)
        flat_attrs = forms.widgets.flatatt(self.build_attrs(final_attrs))
        errors = 'has-error' in final_attrs.get('class', '')
        return mark_safe(render_to_string(self.get_template_list(self.template), {
            'name': name,
            'value': value,
            'attrs': flat_attrs,
            'errors': errors,
        }))


#===============================================================================
class DateWidget(NublasWidgetMixin, forms.DateInput):
    template = "nublas/widgets/date.html"

    def __init__(self, *args, **kwargs):
        kwargs['format'] = '%Y-%m-%d'
        super(DateWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs={}):
        super(DateWidget, self).render(name, value, attrs)
        final_attrs = self.get_attrs(attrs)
        flat_attrs = forms.widgets.flatatt(self.build_attrs(final_attrs))
        errors = 'has-error' in final_attrs.get('class', '')
        return mark_safe(render_to_string(self.get_template_list(self.template), {
            'name': name,
            'value': value,
            'attrs': flat_attrs,
            'errors': errors,
        }))


#===============================================================================
class DateTimeWidget(NublasWidgetMixin, forms.DateTimeInput):
    template = "nublas/widgets/datetime.html"

    def __init__(self, *args, **kwargs):
        kwargs['format'] = '%Y-%m-%d %H:%M'
        super(DateTimeWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs={}):
        super(DateTimeWidget, self).render(name, value, attrs)
        final_attrs = self.get_attrs(attrs)
        flat_attrs = forms.widgets.flatatt(self.build_attrs(final_attrs))
        errors = 'has-error' in final_attrs.get('class', '')
        return mark_safe(render_to_string(self.get_template_list(self.template), {
            'name': name,
            'value': value,
            'attrs': flat_attrs,
            'errors': errors,
        }))
