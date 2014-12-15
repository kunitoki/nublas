from __future__ import unicode_literals
from django import forms
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string


#===============================================================================
class TagsWidget(forms.Widget):
    template = "nublas/widgets/tags.html"

    def __init__(self, *args, **kwargs):
        super(TagsWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs={}):
        final_attrs = dict(**self.attrs)
        for k, v in attrs.items():
            if k == 'class' and 'class' in final_attrs:
                final_attrs['class'] += ' %s' % v
            else:
                final_attrs[k] = v
        if value:
            value = ','.join([ v.tag.name for v in value ])
        flat_attrs = forms.widgets.flatatt(self.build_attrs(final_attrs))
        errors = 'has-error' in final_attrs.get('class', '')
        return mark_safe(render_to_string(self.template, {
            'name': name,
            'value': value,
            'attrs': flat_attrs,
            'errors': errors,
        }))
