from django import template
from django.templatetags.static import StaticNode
from django.contrib.staticfiles.storage import staticfiles_storage

from ..ui.skins import get_skin_relative_path

register = template.Library()


#==============================================================================
def static(path):
    return staticfiles_storage.url(get_skin_relative_path(path))


class StaticFilesNode(StaticNode):
    def url(self, context):
        path = self.path.resolve(context)
        return static(path)


@register.tag
def nublas_static(parser, token):
    """
    A template tag that returns the URL to a file
    using staticfiles' storage backend

    Usage::

        {% nublas_static path [as varname] %}

    Examples::

        {% nublas_static "myapp/css/base.css" %}
        {% nublas_static variable_with_path %}
        {% nublas_static "myapp/css/base.css" as admin_base_css %}
        {% nublas_static variable_with_path as varname %}

    """
    return StaticFilesNode.handle_token(parser, token)
