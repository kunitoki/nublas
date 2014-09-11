from ..conf import settings
from ..utils import import_class

__all__ = [ "NonTrashManager", "TrashManager" ]


#==============================================================================
BaseManagerClass = import_class(settings.BASE_MANAGER_CLASS)


#==============================================================================
class NonTrashManager(BaseManagerClass):
    """ Query only objects which have not been trashed. """

    use_for_related_fields = True

    def get_queryset(self):
        queryset = super(NonTrashManager, self).get_queryset()
        return queryset.filter(_trashed__isnull=True)


class TrashManager(BaseManagerClass):
    """ Query only objects which have been trashed. """

    def get_queryset(self):
        queryset = super(TrashManager, self).get_queryset()
        return queryset.filter(_trashed__isnull=False)
