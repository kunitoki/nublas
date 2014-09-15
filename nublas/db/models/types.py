from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from .utils import BaseModelLinkedToAssociation

__all__ = [ "Country", "AddressType", "PhoneType", "PhoneKind", "EmailType",
            "WebsiteType", "RelationshipType", "ReverseRelationshipType",
            "ContactType", "PrefixType", "SuffixType", "GenderType",
            "SubscriptionType" ]


#==============================================================================
@python_2_unicode_compatible
class Country(BaseModelLinkedToAssociation('countries')):
    """
        A country
    """
    name = models.CharField(_('name'), max_length=100)
    iso3166 = models.CharField(_('iso3166'), max_length=2)
    is_enabled = models.BooleanField(_('enabled'), default=True)

    class Meta:
        app_label = 'nublas'
        verbose_name = _('country')
        verbose_name_plural = _('countries')
        ordering = [ 'name' ]

    def __str__(self):
        return self.name


#==============================================================================
@python_2_unicode_compatible
class AddressType(BaseModelLinkedToAssociation('address_types')):
    """
        An address type, this usually can be 'Home', 'Work'...
    """
    name = models.CharField(_('name'), max_length=100)

    class Meta:
        app_label = 'nublas'
        verbose_name = _('address type')
        verbose_name_plural = _('address types')
        ordering = [ 'name' ]

    def __str__(self):
        return self.name


#==============================================================================
@python_2_unicode_compatible
class PhoneType(BaseModelLinkedToAssociation('phone_types')):
    """
        A phone type, this usually can be 'Home', 'Work'...
    """
    name = models.CharField(_('name'), max_length=100)

    class Meta:
        app_label = 'nublas'
        verbose_name = _('phone type')
        verbose_name_plural = _('phone types')
        ordering = [ 'name' ]

    def __str__(self):
        return self.name

@python_2_unicode_compatible
class PhoneKind(BaseModelLinkedToAssociation('phone_kinds')):
    """
        A phone kind, typically we use this for 'Phone', 'Cellular', 'Fax'...
    """
    name = models.CharField(_('name'), max_length=100)

    class Meta:
        app_label = 'nublas'
        verbose_name = _('phone kind')
        verbose_name_plural = _('phone kinds')
        ordering = [ 'name' ]

    def __str__(self):
        return self.name


#==============================================================================
@python_2_unicode_compatible
class EmailType(BaseModelLinkedToAssociation('email_types')):
    """
        An email address type, this usually can be 'Personal', 'Work'...
    """
    name = models.CharField(_('name'), max_length=100)

    class Meta:
        app_label = 'nublas'
        verbose_name = _('email type')
        verbose_name_plural = _('email types')
        ordering = [ 'name' ]

    def __str__(self):
        return self.name


#==============================================================================
@python_2_unicode_compatible
class WebsiteType(BaseModelLinkedToAssociation('website_types')):
    """
        A website type, this usually can be 'Personal', 'Work'...
    """
    name = models.CharField(_('name'), max_length=100)

    class Meta:
        app_label = 'nublas'
        verbose_name = _('website type')
        verbose_name_plural = _('website types')
        ordering = [ 'name' ]

    def __str__(self):
        return self.name


#==============================================================================
@python_2_unicode_compatible
class RelationshipType(BaseModelLinkedToAssociation('relationship_types')):
    """
        Represent a type of relationship
    """
    name = models.CharField(_('name'), max_length=100)
    from_slug = models.CharField(_('from slug'), max_length=100,
        help_text=_("Denote the relationship from the contact, i.e. 'following'"))
    to_slug = models.CharField(_('to slug'), max_length=100,
        help_text=_("Denote the relationship to the contact, i.e. 'followers'"))
    reverse = models.CharField(_('reverse'), max_length=100)
    symmetrical_slug = models.CharField(_('symmetrical slug'), max_length=100, blank=True, null=True,
        help_text=_("When a mutual relationship exists, i.e. 'friends'"))

    class Meta:
        app_label = 'nublas'
        verbose_name = _('relationship type')
        verbose_name_plural = _('relationship types')
        ordering = [ 'name' ]

    def __str__(self):
        return self.symmetrical_slug if self.symmetrical_slug else self.from_slug

@python_2_unicode_compatible
class ReverseRelationshipType(RelationshipType):
    """
        Represent a reverse type of relationship (proxy model)
    """
    class Meta:
        proxy = True
        app_label = 'nublas'
        verbose_name = _('relationship type')
        verbose_name_plural = _('relationship types')
        ordering = [ 'name' ]

    def __str__(self):
        return self.symmetrical_slug if self.symmetrical_slug else self.to_slug


#==============================================================================
@python_2_unicode_compatible
class ContactType(BaseModelLinkedToAssociation('contact_types')):
    """
        A contact type, this usually can be 'Individual', 'Organization'...
    """
    name = models.CharField(_('name'), max_length=100)
    # TODO - is this really needed ?
    parent_type = models.ForeignKey('self', blank=True, null=True,
                                    related_name='child_type', verbose_name=_('parent'))

    class Meta:
        app_label = 'nublas'
        verbose_name = _('contact type')
        verbose_name_plural = _('contact types')
        ordering = [ 'name' ]

    def __str__(self):
        return self.name


#==============================================================================
@python_2_unicode_compatible
class PrefixType(BaseModelLinkedToAssociation('prefix_types')):
    """
        A prefix type, this usually can be 'Mr.', 'Mrs.'...
    """
    name = models.CharField(_('name'), max_length=100)

    class Meta:
        app_label = 'nublas'
        verbose_name = _('prefix type')
        verbose_name_plural = _('prefix types')
        ordering = [ 'name' ]

    def __str__(self):
        return self.name


#==============================================================================
@python_2_unicode_compatible
class SuffixType(BaseModelLinkedToAssociation('suffix_types')):
    """
        A suffix type, this usually can be 'Jr.', 'I', 'II'...
    """
    name = models.CharField(_('name'), max_length=100)

    class Meta:
        app_label = 'nublas'
        verbose_name = _('suffix type')
        verbose_name_plural = _('suffix types')
        ordering = [ 'name' ]

    def __str__(self):
        return self.name


#==============================================================================
@python_2_unicode_compatible
class GenderType(BaseModelLinkedToAssociation('gender_types')):
    """
        A gender type, common values are 'Male', 'Female'
    """
    name = models.CharField(_('name'), max_length=100)

    class Meta:
        app_label = 'nublas'
        verbose_name = _('gender type')
        verbose_name_plural = _('gender types')
        ordering = [ 'name' ]

    def __str__(self):
        return self.name


#==============================================================================
@python_2_unicode_compatible
class SubscriptionType(BaseModelLinkedToAssociation('subscription_types')):

    PERIODIC_FIXED = 1
    PERIODIC_LENGTH = 2
    PERIODIC_CHOICES = (
        (PERIODIC_FIXED,  _('Fixed start')),
        (PERIODIC_LENGTH, _('Fixed length')),
    )

    LENGTH_DAYS = 1
    LENGTH_WEEKS = 2
    LENGTH_MONTHS = 3
    LENGTH_YEARS = 4
    LENGTH_CHOICES = (
        (LENGTH_DAYS,   _('Days')),
        (LENGTH_WEEKS,  _('Weeks')),
        (LENGTH_MONTHS, _('Months')),
        (LENGTH_YEARS,  _('Years')),
    )

    MONTHS_CHOICES = (
        (1,  _('January')),
        (2,  _('February')),
        (3,  _('March')),
        (4,  _('April')),
        (5,  _('May')),
        (6,  _('June')),
        (7,  _('July')),
        (8,  _('August')),
        (9,  _('September')),
        (10, _('October')),
        (11, _('November')),
        (12, _('December')),
    )

    DAYS_CHOICES = tuple((d, str(d)) for d in range(1, 32))

    name = models.CharField(_('name'), max_length=200)
    description = models.TextField(_('description'), blank=True, null=True)
    minimum_cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('minimum cost'), default=0.00)
    #contribution_type = models.ForeignKey(ContributionType, verbose_name=_('contribution type'))
    length = models.PositiveIntegerField(_('length'), default=1)
    length_type = models.PositiveIntegerField(_('length type'), choices=LENGTH_CHOICES, default=LENGTH_YEARS)
    period = models.PositiveIntegerField(_('period'), choices=PERIODIC_CHOICES, default=PERIODIC_FIXED)
    from_month = models.PositiveIntegerField(_('from month'), choices=MONTHS_CHOICES, default=1)
    from_day = models.PositiveIntegerField(_('from day'), choices=DAYS_CHOICES, default=1)
    to_month = models.PositiveIntegerField(_('to month'), choices=MONTHS_CHOICES, default=12)
    to_day = models.PositiveIntegerField(_('to day'), choices=DAYS_CHOICES, default=31)

    # TODO - contribution handling ?
    # TODO - mail at expiration ?
    # TODO - mailing templates ?

    class Meta:
        app_label = 'nublas'
        verbose_name = _('subscription type')
        verbose_name_plural = _('subscription types')
        ordering = [ 'name' ]

    def __str__(self):
        return self.name
