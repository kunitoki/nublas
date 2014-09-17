from django.conf.urls import patterns, include, url

from .ui.views.home import *
from .ui.views.association import *
from .ui.views.contact import *


#==============================================================================
urlpatterns = patterns('',
    url(r'^$', HomeView.as_view(), name='home'),
    url(r'^dashboard/$', DashboardView.as_view(), name='dashboard'),
)


#==============================================================================
urlpatterns += patterns('',
    # association editing
    url(r'^association/list/$', AssociationListView.as_view(), name='association_list'),
    url(r'^association/add/$', AssociationAddView.as_view(), name='association_add'),
    url(r'^association/(?P<association>[a-fA-F0-9]{32})/details/$', AssociationDetailsView.as_view(), name='association_details'),
    url(r'^association/(?P<association>[a-fA-F0-9]{32})/edit/$', AssociationEditView.as_view(), name='association_edit'),
    url(r'^association/(?P<association>[a-fA-F0-9]{32})/delete/$', AssociationDeleteView.as_view(), name='association_delete'),

    # association contacts handling
    url(r'^association/(?P<association>[a-fA-F0-9]{32})/contacts/$', AssociationContactListView.as_view(), name='association_contacts'),
    url(r'^association/(?P<association>[a-fA-F0-9]{32})/contacts/action/$', AssociationContactListActionView.as_view(), name='association_contacts_action'),

    # association file handling
    #url(r'^association/(?P<association>[a-fA-F0-9]{32})/files/$', AssociationFilesView.as_view(), name='association_files'),
    #url(r'^association/(?P<association>[a-fA-F0-9]{32})/fileserve/$', AssociationFileServeView.as_view(), name='association_fileserve'),

    # association agenda handling
    url(r'^association/(?P<association>[a-fA-F0-9]{32})/agenda/$', AssociationAgendaView.as_view(), name='association_agenda'),
    url(r'^association/(?P<association>[a-fA-F0-9]{32})/agenda/latest/$', AssociationAgendaLatestView.as_view(), name='association_agenda_latest'),

    # association custom fields
    #url(r'^(?P<association>[a-fA-F0-9]{32})/custom/$', AssociationCustomView.as_view(), name='association_custom'),
    #url(r'^(?P<association>[a-fA-F0-9]{32})/custom/add/$', AssociationCustomAddView.as_view(), name='association_custom_add'),
    #url(r'^custom/(?P<object>[a-fA-F0-9]{32})/edit/$', AssociationCustomEditView.as_view(), name='association_custom_edit'),
    #url(r'^custom/(?P<object>[a-fA-F0-9]{32})/delete/$', AssociationCustomDeleteView.as_view(), name='association_custom_delete'),

    # association settings
    url(r'^association/(?P<association>[a-fA-F0-9]{32})/settings/$', AssociationSettingsView.as_view(), name='association_settings'),

    # TODO - add specific settings
)


#==============================================================================
urlpatterns += patterns('',
    # globals
    url(r'^association/(?P<association>[a-fA-F0-9]{32})/contact/add/$', ContactAddView.as_view(), name='contact_add'),
    url(r'^association/(?P<association>[a-fA-F0-9]{32})/contact/autocomplete/$', ContactAutoCompleteView.as_view(), name='contact_search_autocomplete'),

    # details
    url(r'^contact/(?P<contact>[a-fA-F0-9]{32})/details/$', ContactDetailsView.as_view(), name='contact_details'),
    url(r'^contact/(?P<contact>[a-fA-F0-9]{32})/edit/$', ContactEditView.as_view(), name='contact_edit'),
    url(r'^contact/(?P<contact>[a-fA-F0-9]{32})/delete/$', ContactDeleteView.as_view(), name='contact_delete'),
    url(r'^contact/(?P<contact>[a-fA-F0-9]{32})/files/$', ContactFilesView.as_view(), name='contact_files'),
    #url(r'^contact/(?P<contact>[a-fA-F0-9]{32})/fileserve/$', ContactFileServeView.as_view(), name='contact_fileserve'),

    # addresses
    url(r'^contact/(?P<contact>[a-fA-F0-9]{32})/address/add/$', ContactAddressAddView.as_view(), name='contact_address_add'),
    url(r'^contact/address/(?P<object>[a-fA-F0-9]{32})/edit/$', ContactAddressEditView.as_view(), name='contact_address_edit'),
    url(r'^contact/address/(?P<object>[a-fA-F0-9]{32})/delete/$', ContactAddressDeleteView.as_view(), name='contact_address_delete'),

    # phones
    url(r'^contact/(?P<contact>[a-fA-F0-9]{32})/phone/add/$', ContactPhoneAddView.as_view(), name='contact_phone_add'),
    url(r'^contact/phone/(?P<object>[a-fA-F0-9]{32})/edit/$', ContactPhoneEditView.as_view(), name='contact_phone_edit'),
    url(r'^contact/phone/(?P<object>[a-fA-F0-9]{32})/delete/$', ContactPhoneDeleteView.as_view(), name='contact_phone_delete'),

    # emails
    url(r'^contact/(?P<contact>[a-fA-F0-9]{32})/email/add/$', ContactEmailAddView.as_view(), name='contact_email_add'),
    url(r'^contact/email/(?P<object>[a-fA-F0-9]{32})/edit/$', ContactEmailEditView.as_view(), name='contact_email_edit'),
    url(r'^contact/email/(?P<object>[a-fA-F0-9]{32})/delete/$', ContactEmailDeleteView.as_view(), name='contact_email_delete'),

    # websites
    url(r'^contact/(?P<contact>[a-fA-F0-9]{32})/websites/add/$', ContactWebsiteAddView.as_view(), name='contact_website_add'),
    url(r'^contact/websites/(?P<object>[a-fA-F0-9]{32})/edit/$', ContactWebsiteEditView.as_view(), name='contact_website_edit'),
    url(r'^contact/websites/(?P<object>[a-fA-F0-9]{32})/delete/$', ContactWebsiteDeleteView.as_view(), name='contact_website_delete'),

    # groups
    url(r'^contact/(?P<contact>[a-fA-F0-9]{32})/group/add/$', ContactGroupAddView.as_view(), name='contact_group_add'),
    url(r'^contact/group/(?P<object>[a-fA-F0-9]{32})/edit/$', ContactGroupEditView.as_view(), name='contact_group_edit'),
    url(r'^contact/group/(?P<object>[a-fA-F0-9]{32})/delete/$', ContactGroupDeleteView.as_view(), name='contact_group_delete'),

    # subscriptions
    url(r'^contact/(?P<contact>[a-fA-F0-9]{32})/subscriptions/$', ContactSubscriptionView.as_view(), name='contact_subscriptions'),
    url(r'^contact/(?P<contact>[a-fA-F0-9]{32})/subscription/add/$', ContactSubscriptionAddView.as_view(), name='contact_subscription_add'),
    url(r'^contact/subscription/(?P<object>[a-fA-F0-9]{32})/edit/$', ContactSubscriptionEditView.as_view(), name='contact_subscription_edit'),
    url(r'^contact/subscription/(?P<object>[a-fA-F0-9]{32})/delete/$', ContactSubscriptionDeleteView.as_view(), name='contact_subscription_delete'),

    # partecipations
    url(r'^contact/(?P<contact>[a-fA-F0-9]{32})/partecipations/$', ContactPartecipationView.as_view(), name='contact_partecipations'),

    # relationships
    url(r'^contact/(?P<contact>[a-fA-F0-9]{32})/relationships/$', ContactRelationshipView.as_view(), name='contact_relationships'),
    url(r'^contact/(?P<contact>[a-fA-F0-9]{32})/relationship/add/$', ContactRelationshipAddView.as_view(), name='contact_relationship_add'),
    url(r'^contact/relationship/(?P<object>[a-fA-F0-9]{32})/edit/$', ContactRelationshipEditView.as_view(), name='contact_relationship_edit'),
    url(r'^contact/relationship/(?P<object>[a-fA-F0-9]{32})/delete/$', ContactRelationshipDeleteView.as_view(), name='contact_relationship_delete'),
)
