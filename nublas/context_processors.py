from .conf import settings as _settings


#==============================================================================
def settings(request):
    """
    Context processor that enable usage of nublas settings inside templates

    :param request:
    :return:
    """
    return { 'settings': _settings }
