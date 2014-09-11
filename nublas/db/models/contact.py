import os
import urllib
import datetime
from django.db import models
from django.core.exceptions import ValidationError, NON_FIELD_ERRORS
#from django.core.files.base import ContentFile
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

#from nublas.library.storages import private_storage, DIRECTORY_PLACEHOLDER

from ...conf import settings
from ..base import BaseModel
from ..fields import location
from .utils import BaseModelLinkedToAssociation

__all__ = [ "Address", "Phone", "Email", "Website", "Relationship",
            "ReverseRelationship", "ContactGroup", "Contact", "Subscription" ]


#==============================================================================
@python_2_unicode_compatible
class Address(BaseModel):
    """
        A contact address
    """
    contact = models.ForeignKey('nublas.Contact', related_name='addresses', verbose_name=_('contact'))
    type = models.ForeignKey('nublas.AddressType', verbose_name=_('address type'))
    address = models.CharField(_('address'), max_length=200, blank=True, null=True)
    city = models.CharField(_('city'), max_length=100, blank=True, null=True)
    cap = models.CharField(_('cap'), max_length=20, blank=True, null=True)
    country = models.ForeignKey('nublas.Country', verbose_name=_('country'))
    is_billing = models.BooleanField(_('is billing'), default=False)
    location = location.LocationField(_('location'), blank=True, null=True)
    main = models.BooleanField(_('main address'), default=False)

    UNIQUE_BOOLEAN = [ ('main', ['contact']) ]

    class Meta:
        app_label = 'nublas'
        verbose_name = _('address')
        verbose_name_plural = _('addresses')

    def save(self, *args, **kwargs):
        if not self.location and self.address:
            address = "%s, %s %s %s" % (self.address, self.cap, self.city, self.country)
            self.location = Address.geocode(address)
        super(Address, self).save(*args, **kwargs)

    @staticmethod
    def geocode(address):
        params = urllib.urlencode({'q': address, 'output': 'csv', 'key': settings.GOOGLE_API_KEY, 'oe': 'utf8'})
        request = "http://maps.google.com/maps/geo?%s" % params
        data = urllib.urlopen(request).read()
        dlist = data.split(',')
        if dlist[0] == '200':
            return "%s,%s" % (dlist[2], dlist[3])
        else:
            return None

    def __str__(self):
        return "%s %s %s" % (self.address, self.cap, self.city)


#==============================================================================
@python_2_unicode_compatible
class Phone(BaseModel):
    """
        A contact phone number
    """
    contact = models.ForeignKey('nublas.Contact', related_name='phones', verbose_name=_('contact'))
    number = models.CharField(_('number'), max_length=20)
    kind = models.ForeignKey('nublas.PhoneKind', verbose_name=_('phone kind'))
    type = models.ForeignKey('nublas.PhoneType', verbose_name=_('phone type'))
    main = models.BooleanField(_('main phone'), default=False)

    UNIQUE_BOOLEAN = [ ('main', ['contact']) ]

    class Meta:
        app_label = 'nublas'
        verbose_name = _('phone')
        verbose_name_plural = _('phones')

    def __str__(self):
        return "%s" % self.number


#==============================================================================
@python_2_unicode_compatible
class Email(BaseModel):
    """
        A contact email
    """
    contact = models.ForeignKey('nublas.Contact', related_name='emails', verbose_name=_('contact'))
    address = models.EmailField(_('address'), max_length=200)
    type = models.ForeignKey('nublas.EmailType', verbose_name=_('email type'))
    main = models.BooleanField(_('main email'), default=False)

    UNIQUE_BOOLEAN = [ ('main', ['contact']) ]

    class Meta:
        app_label = 'nublas'
        verbose_name = _('email')
        verbose_name_plural = _('emails')

    def __str__(self):
        return "%s" % self.address


#==============================================================================
@python_2_unicode_compatible
class Website(BaseModel):
    """
        A contact website
    """
    contact = models.ForeignKey('nublas.Contact', related_name='websites', verbose_name=_('contact'))
    url = models.URLField(_('url'))
    type = models.ForeignKey('nublas.WebsiteType', verbose_name=_('website type'))

    class Meta:
        app_label = 'nublas'
        verbose_name = _('website')
        verbose_name_plural = _('websites')

    def __str__(self):
        return "%s" % self.url


#==============================================================================
@python_2_unicode_compatible
class Relationship(BaseModel):
    """
        A contact relationship
    """
    type = models.ForeignKey('nublas.RelationshipType', verbose_name=_('relationship type'))
    from_contact = models.ForeignKey('nublas.Contact', related_name='from_contact', verbose_name=_('from contact'))
    to_contact = models.ForeignKey('nublas.Contact', related_name='to_contact', verbose_name=_('to contact'))

    class Meta:
        app_label = 'nublas'
        unique_together = ('from_contact', 'to_contact', 'type', '_trashed')
        verbose_name = _('relationship')
        verbose_name_plural = _('relationships')

    def validate_unique(self, exclude=None):
        qs = self.__class__._default_manager.filter(
            from_contact=self.from_contact,
            to_contact=self.to_contact,
            type=self.type,
        )
        if not self._state.adding and self.pk is not None:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError({ NON_FIELD_ERRORS: (_('This relationship already exists'),) })

    def __str__(self):
        return "%s %s %s" % (self.type.from_slug,
                             self.to_contact.last_name,
                             self.to_contact.first_name)

@python_2_unicode_compatible
class ReverseRelationship(Relationship):
    """
        A contact reverse relationship
    """
    class Meta:
        proxy = True
        app_label = 'nublas'
        verbose_name = _('reverse relationship')
        verbose_name_plural = _('reverse relationships')

    def __str__(self):
        return "%s %s %s" % (self.type.to_slug,
                             self.from_contact.last_name,
                             self.from_contact.first_name)


#==============================================================================
@python_2_unicode_compatible
class ContactGroup(BaseModel): # TODO - simple through model... check this ?
    contact = models.ForeignKey('nublas.Contact')
    group = models.ForeignKey('nublas.Group')

    class Meta:
        app_label = 'nublas'
        unique_together = ('contact', 'group', '_trashed')
        verbose_name = _('contact group')
        verbose_name_plural = _('contact groups')

    def validate_unique(self, exclude=None):
        qs = self.__class__._default_manager.filter(
            contact=self.contact,
            group=self.group,
        )
        if not self._state.adding and self.pk is not None:
            qs = qs.exclude(pk=self.pk)
        if qs.exists():
            raise ValidationError({ NON_FIELD_ERRORS: (_('The contact is already part of this group'),) })

    def __str__(self):
        return repr(self.group)


#==============================================================================
@python_2_unicode_compatible
class Contact(BaseModelLinkedToAssociation('contacts')):
    """
        The basic association contact.
    """
    first_name = models.CharField(_('first name'), max_length=100)
    middle_name = models.CharField(_('middle name'), max_length=100, blank=True, null=True)
    last_name = models.CharField(_('last name'), max_length=100)
    nickname = models.CharField(_('nickname'), max_length=100, blank=True, null=True)
    prefix = models.ForeignKey('nublas.PrefixType', blank=True, null=True, verbose_name=_('prefix'))
    suffix = models.ForeignKey('nublas.SuffixType', blank=True, null=True, verbose_name=_('suffix'))
    type = models.ForeignKey('nublas.ContactType', blank=True, null=True, verbose_name=_('contact type'))
    gender = models.ForeignKey('nublas.GenderType', blank=True, null=True, verbose_name=_('gender'))
    # TODO - nationality
    birth_date = models.DateField(_('birth date'), blank=True, null=True)
    # TODO - place of birth (useful for fiscal code)
    deceased = models.BooleanField(_('deceased'), default=False)
    decease_date = models.DateField(_('decease date'), blank=True, null=True)
    is_active = models.BooleanField(_('is active'), default=True)
    dont_call = models.BooleanField(_("don't call"), default=False)
    dont_sms = models.BooleanField(_("don't sms"), default=False)
    dont_mail = models.BooleanField(_("don't mail"), default=False)
    dont_post = models.BooleanField(_("don't post"), default=False)
    notes = models.TextField(_('notes'), blank=True, null=True)
    groups = models.ManyToManyField('nublas.Group', through='nublas.ContactGroup', related_name='groups', verbose_name=_('groups'))
    # TODO - add photo of contact (enable gravatars?)

    class Meta:
        app_label = 'nublas'
        verbose_name = _('contact')
        verbose_name_plural = _('contacts')

    def main_address(self):
        objects = self.addresses.all()
        if len(objects):
            for o in objects:
                if o.main: return repr(o)
            return repr(objects[0])
        return None

    def main_phone(self):
        objects = self.phones.all()
        if len(objects):
            for o in objects:
                if o.main: return repr(o)
            return repr(objects[0])
        return None

    def main_email(self):
        objects = self.emails.all()
        if len(objects):
            for o in objects:
                if o.main: return repr(o)
            return repr(objects[0])
        return None

    def group_list(self):
        objects = self.groups.all()
        if len(objects):
            return ', '.join(sorted([o.group.name for o in objects]))
        return None

    #def get_documents_root(self):
    #    return "%s/" % os.path.join(self.association.get_documents_root(), 'contacts', '%s' % self.uuid)

    #def get_documents_path(self):
    #    path = "%s/" % os.path.join(self.get_documents_root(), 'files')
    #    p = os.path.join(path, DIRECTORY_PLACEHOLDER)
    #    if not private_storage.exists(p):
    #        private_storage.save(p, ContentFile(''))
    #    return path

    #def get_documents_disksize(self):
    #    return self.association.get_documents_disksize()

    #def get_private_storage(self):
    #    return self.association.get_private_storage()

    def __str__(self):
        return "%s %s" % (self.last_name, self.first_name)


#==============================================================================
#@python_2_unicode_compatible
#class Contribution(BaseModel):
#    STATUS_DONE = 1
#    STATUS_WAITING = 2
#    STATUS_FAILED = 3
#    STATUS_CANCELLED = 4
#    STATUS_CHOICES = (
#        (STATUS_DONE, _('Completed')),
#        (STATUS_WAITING, _('Waiting')),
#        (STATUS_FAILED, _('Failed')),
#        (STATUS_CANCELLED, _('Cancelled')),
#    )
#
#    contact = models.ForeignKey(Contact, verbose_name=_('contact'))
#    type = models.ForeignKey(ContributionType, verbose_name=_('type'))
#    payment_type = models.ForeignKey(PaymentType, verbose_name=_('payment type'))
#    amount = models.DecimalField(max_digits=30, decimal_places=2, verbose_name=_('amount'), default=0.00)
#    when = models.DateField(_('when'), default=datetime.date.today)
#    status = models.PositiveIntegerField(_('status'), choices=STATUS_CHOICES, default=STATUS_DONE)
#    transaction = models.CharField(_('transaction'), max_length=200, blank=True, null=True)
#
#    class Meta:
#        app_label = 'backend'
#        verbose_name = _('contribution')
#        verbose_name_plural = _('contributions')
#
#    def save(self, *args, **kwargs):
#        super(Contribution, self).save(*args, **kwargs)
#
#    def __str__(self):
#        return self.type.name


#==============================================================================
@python_2_unicode_compatible
class Subscription(BaseModel):

    STATUS_FUTURE = 1
    STATUS_CURRENT = 2
    STATUS_EXPIRED = 3
    STATUS_CHOICES = (
        (STATUS_FUTURE, _('Future')),
        (STATUS_CURRENT, _('Current')),
        (STATUS_EXPIRED, _('Expired')),
    )

    contact = models.ForeignKey('nublas.Contact', related_name='subscriptions', verbose_name=_('contact'))
    type = models.ForeignKey('nublas.SubscriptionType', verbose_name=_('type'))
    from_date = models.DateField(_('from date'), default=datetime.date.today)
    to_date = models.DateField(_('to date'), blank=True, null=True) # should take type into account
    number = models.CharField(_('number'), max_length=100, blank=True, null=True)
    source = models.CharField(_('source'), max_length=100, blank=True, null=True)
    notes = models.TextField(_('notes'), blank=True, null=True)
    has_contribution = models.BooleanField(_('has contribution'), default=False)

    # this fields should update the contribution stuff
    #contrib_type = models.ForeignKey(ContributionType, verbose_name=_('type'), blank=True, null=True)
    #contrib_payment_type = models.ForeignKey(PaymentType, verbose_name=_('payment type'), blank=True, null=True)
    #contrib_amount = models.DecimalField(max_digits=30, decimal_places=2, verbose_name=_('amount'), default=0.00, blank=True, null=True)
    #contrib_when = models.DateField(_('when'), blank=True, null=True)
    #contrib_status = models.PositiveIntegerField(_('status'), choices=Contribution.STATUS_CHOICES, default=Contribution.STATUS_DONE, blank=True, null=True)
    #contrib_transaction = models.CharField(_('transaction'), max_length=200, blank=True, null=True)
    #contrib_send_receipt = models.BooleanField(_('send receipt'), default=False)
    #contrib_mail_sent = models.BooleanField(_('mail sent'), default=False, editable=False)
    #contribution = models.ForeignKey(Contribution, related_name='contribution', verbose_name=_('contribution'), blank=True, null=True)

    class Meta:
        app_label = 'nublas'
        verbose_name = _('subscription')
        verbose_name_plural = _('subscriptions')

    def save(self, *args, **kwargs):
        # check date ranges (and swap if necessary)
        if self.to_date:
            if self.to_date < self.from_date:
                self.to_date, self.from_date = self.from_date, self.to_date

        if self.has_contribution:
            pass
            #contrib = self.contribution
            #if not contrib:
            #    contrib = Contribution()
            #contrib.contact = self.contact
            #contrib.type = self.contrib_type
            #contrib.payment_type = self.contrib_payment_type
            #contrib.amount = self.contrib_amount
            #contrib.when = self.contrib_when
            #contrib.status = self.contrib_status
            #contrib.transaction = self.contrib_transaction
            #contrib.save()
            #self.contribution = contrib
            #
            ## send receipt to the contact
            #if self.contrib_send_receipt:
            #    self.contrib_send_receipt = False
            #    mail = MailTemplate.objects.get(action=MailTemplate.ACTION_RECEIPT, default=True)
            #    retval = mail.single_send_email(self.contact, { 'contrib': contrib })
            #    if not retval:
            #        self.contrib_mail_sent = True
        else:
            pass
            #if self.contribution:
            #    self.contribution.delete()
            #    self.contribution = None
        super(Subscription, self).save(*args, **kwargs)

    def to_date_real(self):
        from .types import SubscriptionType
        if self.to_date:
            return self.to_date
        if self.type.period == SubscriptionType.PERIODIC_FIXED:
            return datetime.date(self.from_date.year, self.type.to_month, self.type.to_day)
        else: # self.type.period == SubscriptionType.PERIODIC_LENGTH
            if self.type.length_type == SubscriptionType.LENGTH_DAYS:
                delta = datetime.timedelta(days=self.type.length)
            elif self.type.length_type == SubscriptionType.LENGTH_WEEKS:
                delta = datetime.timedelta(days=7)
            elif self.type.length_type == SubscriptionType.LENGTH_MONTHS:
                delta = datetime.timedelta(days=30)
            elif self.type.length_type == SubscriptionType.LENGTH_YEARS:
                delta = datetime.timedelta(days=365)
            return self.from_date + delta

    def status(self):
        from_date = self.from_date
        to_date = self.to_date_real()
        today = datetime.date.today()
        if today < from_date:
            return Subscription.STATUS_FUTURE
        elif today >= from_date and today <= to_date:
            return Subscription.STATUS_CURRENT
        return Subscription.STATUS_EXPIRED

    def status_text(self):
        return Subscription.STATUS_CHOICES[self.status() - 1][1]

    def __str__(self):
        return _('%(status)s: %(typename)s from %(from_date)s to %(to_date)s') % \
                    ({ 'status': self.status_text(),
                       'typename': self.type.name,
                       'from_date': self.from_date,
                       'to_date': self.to_date_real() })
