import os
import uuid
from django.db import models, transaction
from django.db.models import signals, get_model, Q
from django.core import serializers
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
from django.core.files.base import ContentFile
from django.contrib.contenttypes.models import ContentType
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from ...conf import settings
from ..base import BaseModel
from .utils import BaseModelLinkedToAssociation
#from nublas.library.custom.models import build_custom_field_model, build_custom_value_model
#from nublas.library.storages import private_storage, DIRECTORY_PLACEHOLDER

__all__ = [ "Association", "Collaborator", "Group" ]


#==============================================================================
#PRIVATE_ROOT = getattr(settings, 'PRIVATE_ROOT', '') # TODO - check default


#==============================================================================
@python_2_unicode_compatible
class Association(BaseModel):
    """
    Basic association
    """
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'), blank=True, null=True)
    website = models.URLField(_('website'), blank=True, null=True)
    holder = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='associations', verbose_name=_('holder'))
    #collaborators = models.ManyToManyField(settings.AUTH_USER_MODEL, through='backend.Collaborator', related_name='collaborators', verbose_name=_('collaborators'))
    #main = models.BooleanField(_('main association')) # TODO - or keep out !?
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

    #def get_documents_root(self):
    #    return "%s/" % os.path.join('associations', '%s' % self.uuid)
    #
    #def get_documents_path(self):
    #    path = "%s/" % os.path.join(self.get_documents_root(), 'files')
    #    p = os.path.join(path, DIRECTORY_PLACEHOLDER)
    #    if not private_storage.exists(p):
    #        private_storage.save(p, ContentFile(''))
    #    return path
    #
    #def get_documents_disksize(self):
    #    root = self.get_documents_root()
    #    if private_storage.exists(root):
    #        return private_storage.size(root)
    #    else:
    #        return 0
    #
    #def delete_documents_root(self):
    #    root = self.get_documents_root()
    #    if private_storage.exists(root):
    #        private_storage.delete(root)

    @staticmethod
    def get_object_or_404(uuid, user):
        # This returns an association in which a user work on
        return get_object_or_404(Association,
                                 Q(_uuid=uuid) & (Q(holder=user) | Q(collaborators=user)))

    def __str__(self):
        return self.name

# Signal for populate base types in empty association
#@receiver(signals.post_save, sender=Association, dispatch_uid="populate_empty_association")
#def populate_empty_association(sender, instance, created, **kwargs):
#    if created:
#        with transaction.commit_on_success():
#            # TODO - fill taking into account the user preferred language
#            data = render_to_string('nublas/core/association/fixtures/new_association.it.json', { 'object': instance.pk })
#            for obj in serializers.deserialize("json", data, ensure_ascii=False):
#                obj.save()
#            instance.get_documents_path()
#    # TODO - what to do when the instance is trashed only ? move to thrash too
#    #else:
#    #    if instance.trashed:
#    #        remove_path(instance.get_documents_root())


# Signal for delete file structure
#@receiver(signals.post_delete, sender=Association, dispatch_uid="delete_association_files")
#def delete_association_files(sender, instance, **kwargs):
#    instance.delete_documents_root()


#==============================================================================
@python_2_unicode_compatible
class Collaborator(BaseModelLinkedToAssociation()):
    """
        A user partner of the association's holder
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'))

    class Meta:
        app_label = 'nublas'
        verbose_name = _('collaborator')
        verbose_name_plural = _('collaborators')

    def __str__(self):
        return self.user.username


#==============================================================================
@python_2_unicode_compatible
class Group(BaseModelLinkedToAssociation('groups')):
    name = models.CharField(_('name'), max_length=100)

    class Meta:
        app_label = 'nublas'
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
