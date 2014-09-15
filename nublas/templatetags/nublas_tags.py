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
        Simple tag to express better form fields in templates;

        Usage:
            {% nublas_field form.name class="w95" %}
    """
    if hasattr(fld, 'show_hidden_initial') and fld.show_hidden_initial:
        return fld.as_widget(attrs=kwargs) + fld.as_hidden(only_initial=True)
    return fld.as_widget(attrs=kwargs)

