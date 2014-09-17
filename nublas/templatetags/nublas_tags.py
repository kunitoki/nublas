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


#==============================================================================
class RangeNode(template.Node):
    def __init__(self, parser, range_args, context_name):
        self.template_parser = parser
        self.range_args = range_args
        self.context_name = context_name

    def render(self, context):
        resolved_ranges = []
        for arg in self.range_args:
            compiled_arg = self.template_parser.compile_filter(arg)
            resolved_ranges.append(compiled_arg.resolve(context, ignore_failures=True))
        context[self.context_name] = range(*resolved_ranges)
        return ""

@register.tag
def nublas_xrange(parser, token):
    """
    Accepts the same arguments as the 'range' builtin and creates
    a list containing the result of 'range'.

    Syntax:
        {% nublas_xrange [start,] stop[, step] as context_name %}

    For example:
        {% nublas_xrange 5 10 2 as some_range %}
        {% for i in some_range %}
          {{ i }}: Something I want to repeat\n
        {% endfor %}

    Produces:
        5: Something I want to repeat
        7: Something I want to repeat
        9: Something I want to repeat
    """

    tokens = token.split_contents()
    fnctl = tokens.pop(0)

    def error():
        raise template.TemplateSyntaxError, "%s accepts the syntax: {%% %s [start,] " +\
                "stop[, step] as context_name %%}, where 'start', 'stop' " +\
                "and 'step' must all be integers." %(fnctl, fnctl)

    range_args = []
    while True:
        if len(tokens) < 2:
            error()
        token = tokens.pop(0)
        if token == "as":
            break
        range_args.append(token)

    if len(tokens) != 1:
        error()

    context_name = tokens.pop()
    return RangeNode(parser, range_args, context_name)
