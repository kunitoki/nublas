from __future__ import unicode_literals
from django import forms
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string

from .base import NublasWidgetMixin


#===============================================================================
class TagsWidget(NublasWidgetMixin, forms.Widget):
    template = "widgets/tags.html"

    def __init__(self, *args, **kwargs):
        super(TagsWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs={}):
        final_attrs = self.get_attrs(attrs)
        flat_attrs = forms.widgets.flatatt(self.build_attrs(final_attrs))
        errors = 'has-error' in final_attrs.get('class', '')
        if value and len(value) > 0:
            value = ','.join([ v.tag.name for v in value ])
        print value
        return mark_safe(render_to_string(self.get_template_list(self.template), {
            'name': name,
            'value': value,
            'attrs': flat_attrs,
            'errors': errors,
        }))
