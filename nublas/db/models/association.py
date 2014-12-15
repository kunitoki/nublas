import os
import uuid
from django.db import models, transaction
from django.db.models import signals, Q
from django.db.models.loading import get_model
from django.core import serializers
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.core.files.base import ContentFile
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext as _

from ...conf import settings
from ..base import BaseModel
from .utils import BaseModelLinkedToAssociation, BaseModelFileRepositoryMixin
#from nublas.library.custom.models import build_custom_field_model, build_custom_value_model

__all__ = [ "Association", "Collaborator", "Group" ]


#==============================================================================
@python_2_unicode_compatible
class Association(BaseModel, BaseModelFileRepositoryMixin):
    """
    Basic association
    """
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'), blank=True, null=True)
    website = models.URLField(_('website'), blank=True, null=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='associations', verbose_name=_('owner'))
    collaborators = models.ManyToManyField(settings.AUTH_USER_MODEL, through='nublas.Collaborator', related_name='collaborators', verbose_name=_('collaborators'))
    # TODO - logo image
    # TODO - Partita IVA (???)
    # TODO - Codice Fiscale (???)
    # TODO - default email
    # TODO - default phone
    # TODO - bank name
    # TODO - bank address
    # TODO - bank IBAN
    # TODO - president name and surname (or contact ?)
    # TODO - president address
    # TODO - president phone
    # TODO - president email

    class Meta:
        app_label = 'nublas'
        verbose_name = _('association')
        verbose_name_plural = _('associations')
        permissions = (
            ('view_contacts', _("Can view contacts")),
        )

    def repository_root(self):
        return "%s/" % os.path.join('associations', '%s' % self.uuid)

    @staticmethod
    def get_object_or_404(uuid_value, user):
        # This returns an association in which a user work on
        return get_object_or_404(Association,
                                 Q(_uuid=uuid_value) & (Q(owner=user) | Q(collaborators=user)))

    def __str__(self):
        return self.name


# Signal for populate base types in empty association
@receiver(signals.post_save, sender=Association, dispatch_uid="populate_empty_association")
def populate_empty_association(sender, instance, created, **kwargs):
    if created:
        with transaction.atomic():
            # TODO - fill taking into account the user preferred language
            lang = 'it'
            data = render_to_string('nublas/fixtures/new_association.%s.json' % lang,
                                    { 'object': instance.pk })
            for obj in serializers.deserialize("json", data, ensure_ascii=False):
                obj.save()
            instance.repository_path()
    # TODO - what to do when the instance is trashed only ? move to thrash too
    #else:
    #    if instance.trashed:
    #        remove_path(instance.repository_path())


# Signal for delete file structure
@receiver(signals.post_delete, sender=Association, dispatch_uid="delete_association_files")
def delete_association_files(sender, instance, **kwargs):
    # TODO - implement deleting association files
    # instance.delete_documents_root()
    pass


#==============================================================================
@python_2_unicode_compatible
class Collaborator(BaseModelLinkedToAssociation()):
    """
        A user partner of the association's owner
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'))

    class Meta:
        verbose_name = _('collaborator')
        verbose_name_plural = _('collaborators')

    def __str__(self):
        return self.user.username


#==============================================================================
@python_2_unicode_compatible
class Group(BaseModelLinkedToAssociation('groups')):
    name = models.CharField(_('name'), max_length=100)

    class Meta:
        verbose_name = _('group')
        verbose_name_plural = _('groups')

    def get_contacts(self):
        contact_model = get_model('nublas', 'Contact')
        return contact_model.objects.filter(association=self.association,
                                            groups__pk__in=[self.pk])

    def contact_count(self):
        contact_model = get_model('nublas', 'Contact')
        return contact_model.objects.filter(association=self.association,
                                            groups__pk__in=[self.pk]).count()

    def __str__(self):
        return self.name
