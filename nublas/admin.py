from django.contrib import admin

from .conf import settings
from .models import *

BaseAdmin = admin.ModelAdmin


#==============================================================================
def tabular_inline(model_class, foreignkey=None):
    if foreignkey:
        class InnerModelInline(admin.TabularInline):
            model = model_class
            fk_name = foreignkey
            extra = 0
        return InnerModelInline
    else:
        class InnerModelInline(admin.TabularInline):
            model = model_class
            extra = 0
        return InnerModelInline

def stacked_inline(model_class, foreignkey=None):
    if foreignkey:
        class InnerModelInline(admin.StackedInline):
            model = model_class
            fk_name = foreignkey
            extra = 0
        return InnerModelInline
    else:
        class InnerModelInline(admin.StackedInline):
            model = model_class
            extra = 0
        return InnerModelInline


#==============================================================================
class AssociationAdmin(BaseAdmin):
    inlines = [tabular_inline(Collaborator),
               tabular_inline(Group),
               tabular_inline(Contact),
               tabular_inline(Country),
               tabular_inline(AddressType),
               tabular_inline(PhoneType),
               tabular_inline(PhoneKind),
               tabular_inline(EmailType),
               tabular_inline(WebsiteType),
               tabular_inline(RelationshipType),
               tabular_inline(ContactType),
               tabular_inline(PrefixType),
               tabular_inline(SuffixType),
               tabular_inline(GenderType),
               tabular_inline(SubscriptionType),
               tabular_inline(Calendar),
    ]

#==============================================================================
class ContactAdmin(BaseAdmin):
    inlines = [stacked_inline(Address),
               tabular_inline(Phone),
               tabular_inline(Email),
               tabular_inline(Website),
               tabular_inline(Contact.groups.through),
               tabular_inline(Relationship, 'from_contact'),
               tabular_inline(ReverseRelationship, 'to_contact'),
               tabular_inline(Subscription),
    ]


#==============================================================================
if settings.ENABLE_ADMIN:
    admin.site.register(Association, AssociationAdmin)
    admin.site.register(Contact, ContactAdmin)
