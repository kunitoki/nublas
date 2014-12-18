from __future__ import unicode_literals
from ..skins import get_skin_relative_path

__all__ = [ "NublasWidgetMixin" ]


#===============================================================================
class NublasWidgetMixin(object):

    def get_template_list(self, widget_template):
        return [ get_skin_relative_path(widget_template),
                 "nublas/%s" % widget_template ]

    def get_attrs(self, attrs={}):
        final_attrs = dict(**self.attrs)
        for k, v in attrs.items():
            if k == 'class' and 'class' in final_attrs:
                final_attrs['class'] += ' %s' % v
            else:
                final_attrs[k] = v
        if 'id' in final_attrs:
            del final_attrs['id']
        return final_attrs
