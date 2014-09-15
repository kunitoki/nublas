from django import template

register = template.Library()


#===============================================================================
@register.filter
def classname(obj):
    """
    Returns the classname of a variable
    """
    return obj.__class__.__name__.lower()

@register.filter
def classname_equals(obj, clazzname):
    """
    Returns if a variable has a classname
    """
    if clazzname.lower() == obj.__class__.__name__.lower():
        return True
    else:
        return False
