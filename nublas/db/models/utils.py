from django.db import models
from django.utils.translation import ugettext_lazy as _

from ..base import BaseModel


#==============================================================================
def BaseModelLinkedToAssociation(related_name=None):
    """
    Build helper to build a custom model that relates to an association
    """
    kwargs = { 'verbose_name': _('association') }
    if related_name:
        kwargs.update({ 'related_name': related_name })

    class AssociationBaseModel(BaseModel):
        association = models.ForeignKey('nublas.Association', **kwargs)
        class Meta:
            abstract = True

    return AssociationBaseModel
