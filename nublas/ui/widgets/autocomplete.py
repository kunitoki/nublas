from __future__ import unicode_literals
from django import forms
from django.forms.widgets import Select, SelectMultiple
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string

from .base import NublasWidgetMixin
from ..skins import get_skin_relative_path

__all__ = [ "AutoCompleteWidget", "AutoCompleteMultipleWidget" ]

"""
Example view:

    def get_json(request):
        result = []
        searchtext = request.GET['q']
        if len(searchtext) >= 3:
            di = {'%s__istartswith' % fieldname: searchtext}
            items = Model.objects.filter(**di).order_by(fieldname)[:10]
            for item in items:
                result.append((item.pk, str(item)))
        return HttpResponse(simplejson.dumps(result))
"""


#==============================================================================
class AutoCompleteWidget(NublasWidgetMixin, Select):
    input_type = 'autocomplete'
    url = None
    initial_display = None
    placeholder = None
    allow_clear = True
    model = None
    min_length = 2
    template = "widgets/autocomplete.html"

    def __init__(self, url, initial_display=None, placeholder=None, allow_clear=True,
                 model=None, template=None, *args, **kwargs):
        """
        url: a custom URL that returns JSON with format [(value, label),(value,
        label),...].

        initial_display: initial_display is the initial content of the autocomplete
        box, eg. "John Smith".

        model: model name where to get value display

        template: template path to use when rendering the widget
        """
        self.url = url
        self.initial_display = initial_display
        self.placeholder = placeholder
        self.allow_clear = allow_clear
        self.model = model
        if template:
            self.template = template
        super(AutoCompleteWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs={}, choices=(), **kwargs):
        final_attrs = self.get_attrs(attrs)
        flat_attrs = forms.widgets.flatatt(self.build_attrs(final_attrs))
        errors = 'has-error' in final_attrs.get('class', '')

        display = ''
        if self.initial_display:
            display = self.initial_display
        else:
            if self.model and value:
                display = "%s" % self.model.objects.get(pk=value)

        return mark_safe(render_to_string(self.get_template_list(self.template), {
            'name': name,
            'value': value,
            'url': self.url,
            'display': display,
            'placeholder': self.placeholder,
            'allow_clear': self.allow_clear,
            'min_length': self.min_length,
            'attrs': flat_attrs,
            'errors': errors,
        }))


#==============================================================================
class AutoCompleteMultipleWidget(NublasWidgetMixin, SelectMultiple):
    input_type = 'autocomplete_multiple'
    url = None
    initial_display = None
    model = None
    min_length = 2
    template = "widgets/autocomplete_multiple.html"

    def __init__(self, url, initial_display=None, model=None, template=None, *args, **kwargs):
        """
        url: a custom URL that returns JSON with format [(value, label),(value,
        label),...].

        initial_display: if url is provided then initial_display is a
        dictionary containing the initial content of the autocomplete box, eg.
        {1:"John Smith", 2:"Sarah Connor"}. The key is the primary key of the
        referenced item.

        model: the model that the queryset objects are instances of. Used
        internally.
        """
        self.url = url
        self.initial_display = initial_display
        self.model = model
        if template:
            self.template = template
        super(AutoCompleteMultipleWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, attrs={}, choices=()):
        final_attrs = self.get_attrs(attrs)
        flat_attrs = forms.widgets.flatatt(self.build_attrs(final_attrs))
        errors = 'has-error' in final_attrs.get('class', '')

        display = ''
        if self.initial_display:
            display = self.initial_display
        else:
            if self.model and value:
                display = {}
                objs = self.model.objects.filter(pk__in=value)
                for o in objs:
                    display[o.pk] = "%s" % o

        value_display = []
        for v in value:
            value_display.append([v, "%s" % choices.get(pk=v)])

        return mark_safe(render_to_string(self.get_template_list(self.template), {
            'name': name,
            'url': self.url,
            'display': display,
            'value': value or [],
            'value_display': value_display,
            'min_length': self.min_length,
            'attrs': flat_attrs,
            'errors': errors,
        }))
