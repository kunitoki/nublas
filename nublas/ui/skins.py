from ..conf import settings


#==============================================================================
def get_skin_relative_path(path):
    return "nublas/skins/%s/%s" % (settings.FRONTEND_SKIN, path)
