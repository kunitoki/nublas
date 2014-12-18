from __future__ import unicode_literals
from django import forms
from django.forms.widgets import Select, SelectMultiple
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string

from .base import NublasWidgetMixin

__all__ = [ "SelectWidget" ]


#==============================================================================
class SelectWidget(NublasWidgetMixin, Select):
    template = "nublas/widgets/select.html"
    placeholder = None
    allow_clear = True

    def __init__(self, placeholder=None, allow_clear=True, template=None, *args, **kwargs):
        """
        url: a custom URL that returns JSON with format [(value, label),(value,
        label),...].

        initial_display: initial_display is the initial content of the autocomplete
        box, eg. "John Smith".

        model: model name where to get value display

        template: template path to use when rendering the widget
        """
        self.placeholder = placeholder
        self.allow_clear = allow_clear
        if template:
            self.template = template
        super(SelectWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs={}, choices=(), **kwargs):
        html = super(SelectWidget, self).render(name, value, attrs, choices, **kwargs)
        final_attrs = self.get_attrs(attrs)
        flat_attrs = forms.widgets.flatatt(self.build_attrs(final_attrs))
        errors = 'has-error' in final_attrs.get('class', '')
        return mark_safe(html + render_to_string(self.get_template_list(self.template), {
            'name': name,
            'value': value,
            'placeholder': self.placeholder,
            'allow_clear': self.allow_clear,
            'attrs': flat_attrs,
            'errors': errors,
        }))
