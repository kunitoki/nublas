import re
from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from ...conf import settings
from ..base import BaseModel
from ..fields import color
from .utils import BaseModelLinkedToAssociation

__all__ = [ "Calendar", "Event", "ContactAppointment" ]


#==============================================================================
@python_2_unicode_compatible
class Calendar(BaseModelLinkedToAssociation('calendars')):
    name = models.CharField(_('name'), max_length=50)
    colour = color.RGBColorField(_('colour'), default='#ff0000')
    is_public = models.BooleanField(_('is public'), default=True)
    is_enabled = models.BooleanField(_('is enabled'), default=True)

    #def colored_list(self):
    #    return '<div style="width:16px;height:16px;background-color: %s;border:1px solid #CCCCCC;"></div>' % (self.colour)
    #colored_list.allow_tags = True
    #colored_list.admin_order_field = 'colour'
    #colored_list.short_description = _('Colour')

    class Meta:
        app_label = 'nublas'
        verbose_name = _("calendar")
        verbose_name_plural = _("calendars")

    def unique_identifier(self):
        calendar_name = '%s-%s' % (self.name, self.uuid)
        return re.sub(r'\s', '-', calendar_name).lower() # TODO - strip spaces

    def __str__(self):
        if self.public:
            return _("%(name)s (Public)") % {'name': self.name}
        else:
            return self.name


#==============================================================================
@python_2_unicode_compatible
class Event(BaseModel):
    title = models.CharField(_('title'), max_length=200)
    details = models.TextField(_('details'), blank=True, null=True)
    calendar = models.ForeignKey('nublas.Calendar', default=1, limit_choices_to = { 'is_enabled__exact': True }, verbose_name=_('calendar'))
    start_date = models.DateTimeField(_('start date'))
    end_date = models.DateTimeField(_('end date'))
    allday = models.BooleanField(_('all day'), default=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='event_owner', null=True, blank=True, verbose_name=_('owner'))
    contacts = models.ManyToManyField('nublas.Contact', through='nublas.ContactAppointment', related_name='events', verbose_name=_('contacts'))
    # TODO - dogs should be visible only if we have the constraint
    #dogs = models.ManyToManyField('backend.Dog', through='DogAppointment', related_name='events', verbose_name=_('dogs'))
    # TODO - public registration boolean
    # TODO - expected cost float
    # TODO - payed boolean

    class Meta:
        app_label = 'nublas'
        verbose_name = _("event")
        verbose_name_plural = _("events")

    def save(self, *args, **kwargs):
        if self.end_date is None:
            self.end_date = self.start_date
        super(Event, self).save(*args, **kwargs)

    def __str__(self):
        return "%s" % self.title


#==============================================================================
@python_2_unicode_compatible
class ContactAppointment(BaseModel):
    event = models.ForeignKey('nublas.Event', verbose_name=_('event'))
    contact = models.ForeignKey('nublas.Contact', verbose_name=_('contact'))
    info = models.TextField(_('info'), blank=True, null=True)
    #price = fields.CurrencyField(_('price'),blank=True, null=True)
    #payed = models.BooleanField(_('payed'), default=True)
    attended = models.BooleanField(_('attended'), default=True)

    class Meta:
        app_label = 'nublas'
        verbose_name = _("contact appointment")
        verbose_name_plural = _("contact appointments")

    def __str__(self):
        return _("%(last_name)s %(first_name)s") % {
            'last_name': self.contact.last_name,
            'first_name': self.contact.first_name }
