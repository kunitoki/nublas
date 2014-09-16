import os
from django import template
from django.template import Template, TemplateSyntaxError, TemplateDoesNotExist
from django.template.loader_tags import ExtendsNode
from django.template.loader import find_template_loader

register = template.Library()


#===============================================================================
@register.simple_tag
def nublas_field(fld, **kwargs):
    """
        Simple tag to express better form fields in templates

        If you need to pass data-variables just use _ (underscore) instead of -

        Usage:
            {% nublas_field form.name class="w95" data_role="tagsinput" %}
    """
    nkwargs = {}
    for key, value in kwargs.iteritems():
        nkwargs[key.replace("_", "-")] = value

    if hasattr(fld, 'show_hidden_initial') and fld.show_hidden_initial:
        return fld.as_widget(attrs=nkwargs) + fld.as_hidden(only_initial=True)
    return fld.as_widget(attrs=nkwargs)

