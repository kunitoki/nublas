from django.utils import importlib

__all__ = [ "import_class" ]


#==============================================================================
def import_class(name):
    components = name.split('.')
    mod = importlib.import_module(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod
